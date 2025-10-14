"""
API Routes for Healthcare Symptom Checker
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models.schemas import (
    SymptomCheckRequest, 
    SymptomCheckResponse, 
    HistoryResponse,
    ErrorResponse
)
from app.services.llm_service import LLMService
from app.database import get_db, QueryRecord
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
llm_service = LLMService()
history_service = HistoryService()


@router.post("/check", response_model=SymptomCheckResponse)
async def check_symptoms(
    request: SymptomCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze symptoms and return probable conditions with recommendations.
    
    This endpoint accepts symptom descriptions and returns:
    - List of probable medical conditions with confidence scores
    - Recommended next steps (self-care, see physician, urgent care)
    - Red flag symptoms that require immediate attention
    - Educational disclaimer
    
    **Important**: This is for educational purposes only and is NOT a substitute 
    for professional medical advice, diagnosis, or treatment.
    """
    try:
        logger.info(f"Received symptom check request: {request.symptoms[:100]}...")
        
        # Analyze symptoms using LLM
        response = await llm_service.analyze_symptoms(request)
        
        # Save to history
        await history_service.save_query(db, request, response)
        
        logger.info("Successfully processed symptom check request")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in symptom check: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in symptom check: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while analyzing symptoms. Please try again later."
        )


@router.get("/history", response_model=HistoryResponse)
async def get_query_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieve query history with pagination.
    
    Returns a paginated list of previous symptom check queries.
    """
    try:
        logger.info(f"Retrieving query history - page: {page}, size: {page_size}")
        
        history = await history_service.get_history(db, page, page_size)
        
        logger.info(f"Retrieved {len(history.queries)} queries from history")
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving query history: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving query history."
        )


@router.get("/history/{query_id}")
async def get_query_by_id(
    query_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific query by ID.
    """
    try:
        logger.info(f"Retrieving query with ID: {query_id}")
        
        query = await history_service.get_query_by_id(db, query_id)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        return query
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving the query."
        )


@router.delete("/history/{query_id}")
async def delete_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific query from history.
    """
    try:
        logger.info(f"Deleting query with ID: {query_id}")
        
        success = await history_service.delete_query(db, query_id)
        if not success:
            raise HTTPException(status_code=404, detail="Query not found")
        
        return {"message": "Query deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting query {query_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the query."
        )
