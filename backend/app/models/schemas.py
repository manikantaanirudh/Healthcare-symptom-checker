"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime


class SymptomCheckRequest(BaseModel):
    """Request model for symptom checking"""
    symptoms: str = Field(..., min_length=1, max_length=2000, description="Description of symptoms")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    sex: Optional[Literal["male", "female", "other"]] = Field(None, description="Sex")
    duration_days: Optional[int] = Field(None, ge=0, le=3650, description="Duration of symptoms in days")
    severity: Optional[Literal["mild", "moderate", "severe"]] = Field(None, description="Severity level")
    context: Optional[str] = Field(None, max_length=1000, description="Additional context")

    @validator('symptoms')
    def validate_symptoms(cls, v):
        if not v.strip():
            raise ValueError('Symptoms description cannot be empty')
        return v.strip()


class Condition(BaseModel):
    """Model for a probable medical condition"""
    condition: str = Field(..., description="Name of the condition")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    rationale: str = Field(..., description="Brief explanation for this condition")


class NextStep(BaseModel):
    """Model for recommended next steps"""
    type: Literal["self_care", "see_physician", "urgent_care"] = Field(..., description="Type of next step")
    text: str = Field(..., description="Description of the next step")


class SymptomCheckResponse(BaseModel):
    """Response model for symptom checking"""
    probable_conditions: List[Condition] = Field(..., description="List of probable conditions")
    recommended_next_steps: List[NextStep] = Field(..., description="Recommended next steps")
    red_flags: List[str] = Field(..., description="List of red flag symptoms detected")
    disclaimer: str = Field(..., description="Educational disclaimer")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class QueryHistory(BaseModel):
    """Model for query history"""
    id: int
    symptoms: str
    age: Optional[int]
    sex: Optional[str]
    duration_days: Optional[int]
    severity: Optional[str]
    context: Optional[str]
    response: SymptomCheckResponse
    created_at: datetime


class HistoryResponse(BaseModel):
    """Response model for query history"""
    queries: List[QueryHistory]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    disclaimer: str = "This tool is for educational purposes only and is NOT a substitute for professional medical advice."
