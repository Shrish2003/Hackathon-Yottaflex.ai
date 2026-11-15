"""
API routes package aggregating all operational and detection endpoints.
"""

from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.exceptions import router as exceptions_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.detection import router as detection_router

api_router = APIRouter()

# Mount all feature routers
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(dashboard_router)
api_router.include_router(exceptions_router)
api_router.include_router(transactions_router)
api_router.include_router(detection_router)
