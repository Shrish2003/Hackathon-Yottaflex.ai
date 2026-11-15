"""
Health check endpoints for application and PostgreSQL database.
"""

from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.db.database import check_db_connection

router = APIRouter()


@router.get("", summary="Application Health Check")
@router.get("/", include_in_schema=False)
def get_health():
    """
    Returns basic application health status, name, and environment.
    """
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "debug": settings.debug,
    }


@router.get("/db", summary="PostgreSQL Database Health Check")
def get_db_health(response: Response):
    """
    Performs a real SELECT 1 query to verify active PostgreSQL connectivity.
    Returns HTTP 200 if connected; returns HTTP 503 if disconnected.
    """
    result = check_db_connection()
    if not result.get("connected", False):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        response.status_code = status.HTTP_200_OK
    return result
