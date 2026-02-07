"""
PitchCube API - Main Application
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.logging import logger
from app.db.mongodb import connect_mongodb, close_mongodb
from app.db.redis import connect_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up PitchCube API...")
    
    # Connect to databases
    try:
        await connect_mongodb()
    except Exception as exc:
        logger.warning(f"MongoDB unavailable, continuing without DB: {exc}")
    await connect_redis()
    
    logger.info("PitchCube API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PitchCube API...")
    
    # Close database connections
    await close_mongodb()
    await close_redis()
    
    logger.info("PitchCube API shutdown complete!")


def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(api_v1_router, prefix="/api/v1")

    # Static files
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except RuntimeError:
        logger.warning("Static directory not found, skipping static files mount")
    
    # Generated files download
    import os
    os.makedirs("generated", exist_ok=True)
    app.mount("/download", StaticFiles(directory="generated"), name="generated")

    return app


app = create_application()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.VERSION,
        },
        status_code=200,
    )


@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2024-01-01T00:00:00Z",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
