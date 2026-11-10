import logging
from fastapi import APIRouter
from app.database import check_db_connection
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Check the health of the AudienceFlow API and its database connection.

    Returns:
        status   — Overall application status
        service  — Service name
        version  — API version
        database — Database connectivity status (connected / disconnected)
    """
    try:
        db_connected = check_db_connection()
    except Exception as exc:
        logger.warning("Health check DB probe failed: %s", exc)
        db_connected = False

    return {
        "status": "healthy",
        "service": "AudienceFlow API",
        "version": settings.APP_VERSION,
        "database": "connected" if db_connected else "disconnected",
    }
