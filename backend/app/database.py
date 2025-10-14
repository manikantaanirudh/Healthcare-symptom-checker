"""
Database configuration and models
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./healthcare_symptom_checker.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class QueryRecord(Base):
    """Database model for storing query history"""
    __tablename__ = "query_records"

    id = Column(Integer, primary_key=True, index=True)
    symptoms = Column(Text, nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    duration_days = Column(Integer, nullable=True)
    severity = Column(String(20), nullable=True)
    context = Column(Text, nullable=True)
    response = Column(JSON, nullable=False)  # Store the full response as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())


async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
