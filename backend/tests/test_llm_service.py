"""
Tests for LLM Service
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm_service import LLMService
from app.models.schemas import SymptomCheckRequest


class TestLLMService:
    """Test cases for LLM Service"""
    
    @pytest.fixture
    def llm_service(self):
        return LLMService()
    
    @pytest.fixture
    def sample_request(self):
        return SymptomCheckRequest(
            symptoms="I have a headache and fever",
            age=30,
            sex="male",
            duration_days=2,
            severity="moderate"
        )
    
    @pytest.mark.asyncio
    async def test_analyze_symptoms_success(self, llm_service, sample_request):
        """Test successful symptom analysis"""
        mock_response = {
            "probable_conditions": [
                {
                    "condition": "Viral infection",
                    "confidence": 0.7,
                    "rationale": "Headache and fever are common symptoms of viral infections"
                }
            ],
            "recommended_next_steps": [
                {
                    "type": "self_care",
                    "text": "Rest, stay hydrated, and monitor symptoms"
                },
                {
                    "type": "see_physician",
                    "text": "See a doctor if symptoms worsen or persist"
                }
            ],
            "red_flags": [],
            "disclaimer": "This is educational information only and not a substitute for professional medical advice."
        }
        
        # Mock provider-agnostic internal call
        with patch.object(LLMService, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = str(mock_response).replace("'", '"')

            result = await llm_service.analyze_symptoms(sample_request)
            
            assert result is not None
            assert len(result.probable_conditions) > 0
            assert len(result.recommended_next_steps) > 0
            assert result.disclaimer is not None
            assert "educational" in result.disclaimer.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_symptoms_with_red_flags(self, llm_service):
        """Test symptom analysis with red flags"""
        request = SymptomCheckRequest(
            symptoms="I have severe chest pain and difficulty breathing",
            age=45,
            sex="male"
        )
        
        mock_response = {
            "probable_conditions": [
                {
                    "condition": "Possible cardiac event",
                    "confidence": 0.8,
                    "rationale": "Chest pain with breathing difficulty requires immediate evaluation"
                }
            ],
            "recommended_next_steps": [
                {
                    "type": "urgent_care",
                    "text": "Seek immediate medical attention"
                }
            ],
            "red_flags": ["Chest pain", "Difficulty breathing"],
            "disclaimer": "This is educational information only and not a substitute for professional medical advice."
        }
        
        with patch.object(LLMService, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = str(mock_response).replace("'", '"')

            result = await llm_service.analyze_symptoms(request)
            
            assert len(result.red_flags) > 0
            assert any("urgent_care" in step.type for step in result.recommended_next_steps)
    
    def test_detect_red_flags(self, llm_service):
        """Test red flag detection"""
        symptoms = "I have chest pain and can't breathe properly"
        red_flags = llm_service._detect_red_flags(symptoms)
        
        assert len(red_flags) > 0
        assert any("chest pain" in flag.lower() for flag in red_flags)
    
    def test_validate_and_structure_response(self, llm_service, sample_request):
        """Test response validation and structuring"""
        llm_data = {
            "probable_conditions": [
                {
                    "condition": "Test condition",
                    "confidence": 0.8,
                    "rationale": "Test rationale"
                }
            ],
            "recommended_next_steps": [
                {
                    "type": "see_physician",
                    "text": "See a doctor"
                }
            ],
            "red_flags": [],
            "disclaimer": "Educational only"
        }
        
        result = llm_service._validate_and_structure_response(llm_data, sample_request)
        
        assert result is not None
        assert len(result.probable_conditions) == 1
        assert result.probable_conditions[0].condition == "Test condition"
        assert result.probable_conditions[0].confidence == 0.8
        assert len(result.recommended_next_steps) == 1
        assert result.recommended_next_steps[0].type == "see_physician"
