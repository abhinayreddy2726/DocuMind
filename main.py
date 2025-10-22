"""
Main FastAPI application entry point
PAN & Aadhaar Card Details Extractor using Moondream AI
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import settings
from app.api.endpoints import health, extract, batch

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Moondream endpoint: {settings.MOONDREAM_ENDPOINT}")
    print(f"API documentation: http://{settings.HOST}:{settings.PORT}/docs")
    settings.ensure_directories()
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.PROJECT_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Extract details from PAN and Aadhaar cards using Moondream AI",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "pan_extraction": f"{settings.API_V1_PREFIX}/extract/pan",
            "aadhaar_extraction": f"{settings.API_V1_PREFIX}/extract/aadhaar",
            "generic_extraction": f"{settings.API_V1_PREFIX}/extract",
            "batch_extraction": f"{settings.API_V1_PREFIX}/batch/extract",
            "async_batch_extraction": f"{settings.API_V1_PREFIX}/batch/extract/async"
        }
    }


# Include routers
app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Health"]
)

app.include_router(
    extract.router,
    prefix=f"{settings.API_V1_PREFIX}/extract",
    tags=["Extraction"]
)

app.include_router(
    batch.router,
    prefix=f"{settings.API_V1_PREFIX}/batch",
    tags=["Batch Processing"]
)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "error": "Endpoint not found",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info" if settings.DEBUG else "warning"
    )

