"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models.schemas import SymptomCheckRequest, SymptomCheckResponse, Condition, NextStep

client = TestClient(app)


class TestAPI:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "disclaimer" in data
        assert "educational" in data["disclaimer"].lower()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @patch('app.api.routes.llm_service.analyze_symptoms')
    @patch('app.api.routes.history_service.save_query')
    def test_check_symptoms_success(self, mock_save, mock_analyze):
        """Test successful symptom check"""
        # Mock LLM response
        mock_response = SymptomCheckResponse(
            probable_conditions=[
                Condition(
                    condition="Test condition",
                    confidence=0.8,
                    rationale="Test rationale"
                )
            ],
            recommended_next_steps=[
                NextStep(
                    type="see_physician",
                    text="See a doctor"
                )
            ],
            red_flags=[],
            disclaimer="Educational only"
        )
        mock_analyze.return_value = mock_response
        mock_save.return_value = AsyncMock()
        
        # Test request
        request_data = {
            "symptoms": "I have a headache",
            "age": 30,
            "sex": "male"
        }
        
        response = client.post("/api/v1/check", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "probable_conditions" in data
        assert "recommended_next_steps" in data
        assert "red_flags" in data
        assert "disclaimer" in data
    
    def test_check_symptoms_validation_error(self):
        """Test symptom check with validation error"""
        request_data = {
            "symptoms": "",  # Empty symptoms should fail validation
            "age": 30
        }
        
        response = client.post("/api/v1/check", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_check_symptoms_missing_required_field(self):
        """Test symptom check with missing required field"""
        request_data = {
            "age": 30
            # Missing symptoms field
        }
        
        response = client.post("/api/v1/check", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.routes.history_service.get_history')
    def test_get_history_success(self, mock_get_history):
        """Test successful history retrieval"""
        from app.models.schemas import QueryHistory, HistoryResponse
        
        mock_response = HistoryResponse(
            queries=[],
            total=0,
            page=1,
            page_size=10
        )
        mock_get_history.return_value = mock_response
        
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        
        data = response.json()
        assert "queries" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_get_history_with_pagination(self):
        """Test history retrieval with pagination parameters"""
        with patch('app.api.routes.history_service.get_history') as mock_get_history:
            from app.models.schemas import HistoryResponse
            
            mock_response = HistoryResponse(
                queries=[],
                total=0,
                page=2,
                page_size=5
            )
            mock_get_history.return_value = mock_response
            
            response = client.get("/api/v1/history?page=2&page_size=5")
            assert response.status_code == 200
            
            data = response.json()
            assert data["page"] == 2
            assert data["page_size"] == 5
