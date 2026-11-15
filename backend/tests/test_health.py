"""
Tests for FastAPI application health and PostgreSQL database connectivity endpoints.
Uses httpx.AsyncClient with ASGITransport for native, non-blocking ASGI testing.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import httpx
from unittest.mock import patch
from app.main import app
from app.core.config import settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_app_health_endpoint():
    """Verify that GET /health returns 200 OK and expected environment metadata."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app_name"] == settings.app_name
        assert data["environment"] == settings.app_env
        assert "debug" in data


@pytest.mark.anyio
async def test_api_v1_health_endpoint():
    """Verify that GET /api/v1/health returns 200 OK."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.anyio
async def test_db_health_mock_connected():
    """Verify that GET /health/db returns 200 OK when database is connected."""
    mock_result = {
        "connected": True,
        "status": "connected",
        "database": "o2c_revenue_db",
        "message": "PostgreSQL connection verified successfully via SELECT 1 query.",
    }
    with patch("app.main.check_db_connection", return_value=mock_result):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health/db")
            assert response.status_code == 200
            data = response.json()
            assert data["connected"] is True
            assert data["status"] == "connected"
            assert data["database"] == "o2c_revenue_db"


@pytest.mark.anyio
async def test_db_health_mock_disconnected():
    """Verify that GET /health/db returns 503 Service Unavailable when database is unreachable."""
    mock_result = {
        "connected": False,
        "status": "disconnected",
        "database": "o2c_revenue_db",
        "error": "Connection refused",
        "message": "Failed to connect to PostgreSQL server.",
    }
    with patch("app.main.check_db_connection", return_value=mock_result):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health/db")
            assert response.status_code == 503
            data = response.json()
            assert data["connected"] is False
            assert data["status"] == "disconnected"


@pytest.mark.anyio
async def test_db_health_real_execution_no_credential_leak():
    """
    Executes real database check (whether PostgreSQL is up or down) and asserts:
    1. Returns either 200 or 503.
    2. Response never leaks passwords or raw credentials.
    """
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/db")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "connected" in data
        assert "status" in data
        response_text = str(data)
        assert "YOUR_PASSWORD" not in response_text
        assert "postgres:" not in response_text


if __name__ == "__main__":
    import asyncio

    print("Running test_app_health_endpoint...")
    asyncio.run(test_app_health_endpoint())
    print("PASS: test_app_health_endpoint")

    print("Running test_api_v1_health_endpoint...")
    asyncio.run(test_api_v1_health_endpoint())
    print("PASS: test_api_v1_health_endpoint")

    print("Running test_db_health_mock_connected...")
    asyncio.run(test_db_health_mock_connected())
    print("PASS: test_db_health_mock_connected")

    print("Running test_db_health_mock_disconnected...")
    asyncio.run(test_db_health_mock_disconnected())
    print("PASS: test_db_health_mock_disconnected")

    print("Running test_db_health_real_execution_no_credential_leak...")
    asyncio.run(test_db_health_real_execution_no_credential_leak())
    print("PASS: test_db_health_real_execution_no_credential_leak")

    print("\n>>> ALL 5 HEALTH AND DATABASE CONNECTIVITY TESTS PASSED! <<<")
