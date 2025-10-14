"""
Healthcare Symptom Checker API
Educational Purpose Only - Not for Medical Diagnosis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.api.routes import router
from app.database import init_db
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Healthcare Symptom Checker API")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Healthcare Symptom Checker API")


app = FastAPI(
    title="Healthcare Symptom Checker API",
    description="Educational symptom analysis tool - NOT for medical diagnosis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://healthcare-symptom-checker-frontend.onrender.com",
        "https://*.onrender.com"  # Allow all Render domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with educational disclaimer"""
    return {
        "message": "Healthcare Symptom Checker API",
        "disclaimer": "This tool is for educational purposes only and is NOT a substitute for professional medical advice, diagnosis, or treatment.",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "healthcare-symptom-checker"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "disclaimer": "This tool is for educational purposes only and is NOT a substitute for professional medical advice."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
