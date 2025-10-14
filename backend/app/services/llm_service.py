"""
LLM Service for Healthcare Symptom Analysis
Educational Purpose Only - Not for Medical Diagnosis
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import os
import asyncio
from functools import partial
from dotenv import load_dotenv

# Gemini (Google Generative AI) optional import
try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    genai = None  # type: ignore

from app.models.schemas import SymptomCheckRequest, SymptomCheckResponse, Condition, NextStep

load_dotenv()

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with an LLM for symptom analysis.

    Provider selection is environment-driven:
    - If GEMINI_API_KEY is set (and library available), uses Gemini.
    - Else if OPENAI_API_KEY is set, uses OpenAI Chat Completions.
    - Temperature kept low for determinism.
    """

    def __init__(self):
        self.temperature = 0.1  # Low temperature for deterministic results

        self._gemini_api_key = os.getenv("GEMINI_API_KEY")
        self._openai_api_key = os.getenv("OPENAI_API_KEY")
        self._provider: str = os.getenv("LLM_PROVIDER", "auto").lower()

        # Determine provider
        if self._provider == "gemini" or (
            self._provider == "auto" and self._gemini_api_key
        ):
            if genai is None:
                raise RuntimeError(
                    "google-generativeai is not installed; cannot use Gemini provider"
                )
            genai.configure(api_key=self._gemini_api_key)
            self._active_provider = "gemini"
            self._gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
            self.client = None  # not used for gemini
            logger.info("LLM provider set to Gemini")
        else:
            # Default to OpenAI
            if not self._openai_api_key:
                raise RuntimeError(
                    "No LLM API key found. Set GEMINI_API_KEY or OPENAI_API_KEY in environment."
                )
            self.client = AsyncOpenAI(api_key=self._openai_api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
            self._active_provider = "openai"
            logger.info("LLM provider set to OpenAI")
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for medical reasoning"""
        return """You are a medically-aware reasoning assistant for educational purposes only. 
Your goal is to help users understand potential causes of their symptoms 
and suggest safe next steps. You are NOT a doctor and cannot diagnose, treat, 
or prescribe. 

CRITICAL SAFETY REQUIREMENTS:
1. Always include a strong disclaimer: "This is educational information only and not a substitute for professional medical advice."
2. Detect and flag "red-flag" symptoms that require urgent care
3. Never prescribe medications or give specific treatment doses
4. Always recommend consulting healthcare professionals for serious symptoms
5. Be conservative in your recommendations - err on the side of caution

RED FLAG SYMPTOMS (require urgent care):
- Chest pain or pressure
- Severe difficulty breathing
- Signs of stroke (facial drooping, arm weakness, speech difficulties)
- Severe abdominal pain
- High fever with rash
- Signs of severe dehydration
- Severe headache with neck stiffness
- Loss of consciousness
- Severe allergic reactions
- Signs of heart attack
- Severe bleeding
- Signs of poisoning

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON matching the exact schema
- Include up to 5 possible conditions with confidence scores (0-1)
- Group next steps by urgency: self_care, see_physician, urgent_care
- Always include red flag detection
- Be specific but conservative in recommendations"""

    def _get_user_prompt(self, request: SymptomCheckRequest) -> str:
        """Generate user prompt from request"""
        prompt = f"""Symptoms: {request.symptoms}"""
        
        if request.age:
            prompt += f"\nAge: {request.age}"
        if request.sex:
            prompt += f"\nSex: {request.sex}"
        if request.duration_days:
            prompt += f"\nDuration (days): {request.duration_days}"
        if request.severity:
            prompt += f"\nSeverity: {request.severity}"
        if request.context:
            prompt += f"\nContext: {request.context}"
            
        prompt += """

Based on these inputs, provide:
1. Probable conditions with confidence and rationale
2. Recommended next steps
3. A clear disclaimer
4. Highlight any red flags

Output JSON strictly matching this schema:
{
  "probable_conditions": [{"condition": "", "confidence": 0.0, "rationale": ""}],
  "recommended_next_steps": [{"type": "self_care|see_physician|urgent_care", "text": ""}],
  "red_flags": [""],
  "disclaimer": ""
}"""
        
        return prompt

    async def analyze_symptoms(self, request: SymptomCheckRequest) -> SymptomCheckResponse:
        """Analyze symptoms using LLM and return structured response"""
        try:
            logger.info(f"Analyzing symptoms: {request.symptoms[:100]}...")
            
            # Compose prompts
            system_prompt = self._get_system_prompt()
            user_prompt = self._get_user_prompt(request)

            # Provider-agnostic call
            content = await self._call_llm(system_prompt, user_prompt)
            logger.info(f"LLM response received: {len(content)} characters")
            
            # Parse JSON response
            try:
                llm_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                raise ValueError("Invalid response format from LLM")
            
            # Validate and structure response
            response_data = self._validate_and_structure_response(llm_data, request)
            
            logger.info("Successfully analyzed symptoms")
            return response_data
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            # As a safety net, return a conservative fallback response instead of failing the request
            logger.info("Falling back to heuristic response due to LLM failure")
            return self._build_fallback_response(request)

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured LLM provider and return raw JSON string.

        Ensures JSON-only output using provider-specific controls.
        """
        if self._active_provider == "openai":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content

        # Gemini path: pass system as system_instruction and user as content
        generation_config = {
            "temperature": self.temperature,
            "response_mime_type": "application/json",
        }

        # google-generativeai is synchronous; run in thread to keep interface async
        def _gemini_call() -> str:
            try:
                model = genai.GenerativeModel(
                    model_name=self._gemini_model,
                    system_instruction=system_prompt,
                )
                resp = model.generate_content(
                    user_prompt,
                    generation_config=generation_config,
                    safety_settings=[
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUAL_CONTENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    ],
                )
                # Prefer resp.text
                if getattr(resp, "text", None):
                    return resp.text
                # Fallback: attempt to join parts
                try:
                    parts = resp.candidates[0].content.parts  # type: ignore[attr-defined]
                    texts = []
                    for p in parts:
                        t = getattr(p, "text", None)
                        if t:
                            texts.append(t)
                    if texts:
                        return "\n".join(texts)
                except Exception:
                    pass
                # Last resort: stringify
                return str(resp)
            except Exception as e:  # Normalize provider errors
                logger.error(f"Gemini provider error: {e}")
                raise ValueError("Gemini provider call failed")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _gemini_call)

    def _build_fallback_response(self, request: SymptomCheckRequest) -> SymptomCheckResponse:
        """Return a conservative, schema-compliant response when LLM fails."""
        red_flags = self._detect_red_flags(request.symptoms)
        next_steps: List[NextStep] = []
        if red_flags:
            next_steps.append(NextStep(
                type="urgent_care",
                text="Potential red flags detected. Seek urgent medical attention or call local emergency services."
            ))
        else:
            next_steps.extend([
                NextStep(
                    type="self_care",
                    text="Monitor symptoms, rest, hydrate, and consider over-the-counter remedies if appropriate."
                ),
                NextStep(
                    type="see_physician",
                    text="If symptoms persist, worsen, or you are concerned, consult a healthcare professional."
                ),
            ])

        disclaimer = (
            "This is educational information only and not a substitute for professional medical advice, "
            "diagnosis, or treatment. Always consult a qualified healthcare professional."
        )

        # Provide generic conditions with low confidence to avoid misleading certainty
        conditions: List[Condition] = [
            Condition(condition="Non-specific symptom complex", confidence=0.2, rationale="Symptoms are non-specific without clinical evaluation."),
        ]

        return SymptomCheckResponse(
            probable_conditions=conditions,
            recommended_next_steps=next_steps,
            red_flags=red_flags,
            disclaimer=disclaimer,
        )

        

    def _validate_and_structure_response(self, llm_data: Dict[str, Any], request: SymptomCheckRequest) -> SymptomCheckResponse:
        """Validate and structure the LLM response"""
        
        # Ensure required fields exist
        required_fields = ["probable_conditions", "recommended_next_steps", "red_flags", "disclaimer"]
        for field in required_fields:
            if field not in llm_data:
                logger.warning(f"Missing required field: {field}")
                llm_data[field] = [] if field != "disclaimer" else "This is educational information only and not a substitute for professional medical advice."
        
        # Validate and structure conditions
        conditions = []
        for condition_data in llm_data.get("probable_conditions", []):
            try:
                condition = Condition(
                    condition=condition_data.get("condition", "Unknown condition"),
                    confidence=float(condition_data.get("confidence", 0.0)),
                    rationale=condition_data.get("rationale", "No rationale provided")
                )
                conditions.append(condition)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid condition data: {e}")
                continue
        
        # Limit to 5 conditions
        conditions = conditions[:5]
        
        # Validate and structure next steps
        next_steps = []
        valid_types = ["self_care", "see_physician", "urgent_care"]
        for step_data in llm_data.get("recommended_next_steps", []):
            try:
                step_type = step_data.get("type", "see_physician")
                if step_type not in valid_types:
                    step_type = "see_physician"
                
                next_step = NextStep(
                    type=step_type,
                    text=step_data.get("text", "Consult with a healthcare professional")
                )
                next_steps.append(next_step)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid next step data: {e}")
                continue
        
        # Ensure we have at least one next step
        if not next_steps:
            next_steps.append(NextStep(
                type="see_physician",
                text="Consult with a healthcare professional for proper evaluation"
            ))
        
        # Validate red flags
        red_flags = llm_data.get("red_flags", [])
        if not isinstance(red_flags, list):
            red_flags = []
        
        # Ensure disclaimer is present and appropriate
        disclaimer = llm_data.get("disclaimer", "")
        if not disclaimer or "educational" not in disclaimer.lower():
            disclaimer = "This is educational information only and not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare professional."
        
        return SymptomCheckResponse(
            probable_conditions=conditions,
            recommended_next_steps=next_steps,
            red_flags=red_flags,
            disclaimer=disclaimer
        )

    def _detect_red_flags(self, symptoms: str) -> List[str]:
        """Detect potential red flag symptoms in the input"""
        red_flag_keywords = [
            "chest pain", "chest pressure", "heart attack",
            "difficulty breathing", "shortness of breath", "can't breathe",
            "stroke", "facial drooping", "arm weakness", "speech difficulties",
            "severe abdominal pain", "severe headache", "neck stiffness",
            "high fever", "rash", "dehydration", "unconscious", "fainting",
            "severe bleeding", "allergic reaction", "anaphylaxis",
            "poisoning", "overdose", "suicidal", "self harm"
        ]
        
        symptoms_lower = symptoms.lower()
        detected_flags = []
        
        for keyword in red_flag_keywords:
            if keyword in symptoms_lower:
                detected_flags.append(f"Potential red flag detected: {keyword}")
        
        return detected_flags
