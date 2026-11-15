"""
FastAPI application entrypoint for O2C Revenue Assurance Platform.
"""

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes import api_router
from app.db.database import check_db_connection

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Enterprise Order-to-Cash (O2C) Revenue Assurance and Anomaly Detection Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health endpoints (as requested by STEP 2 requirements)
@app.get("/health", tags=["Health"], summary="Root Application Health Check")
def root_health():
    """Application health endpoint."""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "debug": settings.debug,
    }


@app.get("/health/db", tags=["Health"], summary="Root Database Health Check")
def root_db_health(response: Response):
    """PostgreSQL database connectivity check with real SELECT 1 query."""
    result = check_db_connection()
    if not result.get("connected", False):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        response.status_code = status.HTTP_200_OK
    return result


# Mount API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.app_env,
        "docs_url": "/docs",
        "health_url": "/health",
        "db_health_url": "/health/db",
    }
