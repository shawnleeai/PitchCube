"""
Health check endpoints
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": "pitchcube-api",
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with database connectivity."""
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "service": "pitchcube-api",
        "checks": {
            "api": "healthy",
            "mongodb": "unknown",
            "redis": "unknown",
        },
    }
    
    # Check MongoDB
    try:
        from app.db.mongodb import db
        if db.client:
            await db.client.admin.command('ping')
            health_status["checks"]["mongodb"] = "healthy"
        else:
            health_status["checks"]["mongodb"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        health_status["checks"]["mongodb"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        from app.db.redis import redis_client
        if redis_client:
            await redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(content=health_status, status_code=status_code)
