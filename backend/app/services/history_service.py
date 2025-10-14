"""
History Service for managing query history
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import logging
from datetime import datetime
import json

from app.models.schemas import SymptomCheckRequest, SymptomCheckResponse, QueryHistory, HistoryResponse
from app.database import QueryRecord

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for managing query history"""
    
    async def save_query(
        self, 
        db: Session, 
        request: SymptomCheckRequest, 
        response: SymptomCheckResponse
    ) -> QueryRecord:
        """Save a query and response to history"""
        try:
            # Convert response to JSON-serializable dict (e.g., datetimes -> ISO strings)
            try:
                response_dict = response.model_dump(mode="json")  # pydantic v2
            except Exception:
                # Fallback for compatibility
                response_dict = json.loads(response.model_dump_json())
            
            # Create query record
            query_record = QueryRecord(
                symptoms=request.symptoms,
                age=request.age,
                sex=request.sex,
                duration_days=request.duration_days,
                severity=request.severity,
                context=request.context,
                response=response_dict
            )
            
            db.add(query_record)
            db.commit()
            db.refresh(query_record)
            
            logger.info(f"Saved query to history with ID: {query_record.id}")
            return query_record
            
        except Exception as e:
            logger.error(f"Error saving query to history: {e}")
            db.rollback()
            raise
    
    async def get_history(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 10
    ) -> HistoryResponse:
        """Get paginated query history"""
        try:
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get total count
            total = db.query(QueryRecord).count()
            
            # Get paginated results
            records = db.query(QueryRecord)\
                .order_by(desc(QueryRecord.created_at))\
                .offset(offset)\
                .limit(page_size)\
                .all()
            
            # Convert to response format
            queries = []
            for record in records:
                # Reconstruct response from stored JSON
                response = SymptomCheckResponse(**record.response)
                
                query = QueryHistory(
                    id=record.id,
                    symptoms=record.symptoms,
                    age=record.age,
                    sex=record.sex,
                    duration_days=record.duration_days,
                    severity=record.severity,
                    context=record.context,
                    response=response,
                    created_at=record.created_at
                )
                queries.append(query)
            
            return HistoryResponse(
                queries=queries,
                total=total,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            logger.error(f"Error retrieving query history: {e}")
            raise
    
    async def get_query_by_id(self, db: Session, query_id: int) -> Optional[QueryHistory]:
        """Get a specific query by ID"""
        try:
            record = db.query(QueryRecord).filter(QueryRecord.id == query_id).first()
            
            if not record:
                return None
            
            # Reconstruct response from stored JSON
            response = SymptomCheckResponse(**record.response)
            
            return QueryHistory(
                id=record.id,
                symptoms=record.symptoms,
                age=record.age,
                sex=record.sex,
                duration_days=record.duration_days,
                severity=record.severity,
                context=record.context,
                response=response,
                created_at=record.created_at
            )
            
        except Exception as e:
            logger.error(f"Error retrieving query {query_id}: {e}")
            raise
    
    async def delete_query(self, db: Session, query_id: int) -> bool:
        """Delete a query by ID"""
        try:
            record = db.query(QueryRecord).filter(QueryRecord.id == query_id).first()
            
            if not record:
                return False
            
            db.delete(record)
            db.commit()
            
            logger.info(f"Deleted query with ID: {query_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting query {query_id}: {e}")
            db.rollback()
            raise
