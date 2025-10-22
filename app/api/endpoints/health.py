"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

from app.core.config import settings
from app.models.response import HealthResponse
from app.services.extractor import extractor

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def root_health():
    """Root health check endpoint"""
    moondream_connected = await extractor.check_connection()
    
    return HealthResponse(
        status="healthy" if moondream_connected else "degraded",
        timestamp=datetime.now(),
        version=settings.VERSION,
        moondream_connected=moondream_connected
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint"""
    moondream_connected = await extractor.check_connection()
    
    return HealthResponse(
        status="healthy" if moondream_connected else "degraded",
        timestamp=datetime.now(),
        version=settings.VERSION,
        moondream_connected=moondream_connected
    )

