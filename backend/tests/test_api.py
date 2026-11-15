"""
Integration tests for Stage 5 Backend APIs.
Tests dashboard summary, exceptions list & detail, transactional endpoints, and detection run.
"""

import sys
import os
import uuid
from decimal import Decimal
import pytest
import httpx

from app.main import app
from app.models.detection import ExceptionRecord


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_dashboard_summary_api():
    """Verify GET /api/dashboard/summary returns valid counts and leakage metrics."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/dashboard/summary")
        assert response.status_code == 200
        data = response.json()

        assert "total_accounts" in data
        assert "total_quotes" in data
        assert "total_sales_orders" in data
        assert "total_shipments" in data
        assert "total_invoices" in data
        assert "total_payments" in data
        assert "total_detected_exceptions" in data
        assert "total_identified_leakage_amount" in data
        assert "exception_counts_by_severity" in data
        assert "exception_counts_by_anomaly_type" in data
        assert isinstance(data["total_identified_leakage_amount"], (int, float))


@pytest.mark.anyio
async def test_exceptions_list_and_filter_api():
    """Verify GET /api/exceptions returns paginated results with filtering."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Default list
        response = await client.get("/api/exceptions?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert data["page"] == 1
        assert data["limit"] == 10

        # Filter by severity
        sev_response = await client.get("/api/exceptions?severity=HIGH")
        assert sev_response.status_code == 200
        sev_data = sev_response.json()
        for item in sev_data["items"]:
            assert item["severity"] == "HIGH"

        # Filter by anomaly issue_type
        type_response = await client.get("/api/exceptions?anomaly_type=OVERBILLING_QUANTITY")
        assert type_response.status_code == 200
        type_data = type_response.json()
        for item in type_data["items"]:
            assert item["issue_type"] == "OVERBILLING_QUANTITY"


@pytest.mark.anyio
async def test_exception_detail_api():
    """Verify GET /api/exceptions/{id} returns details and 404 for unknown ID."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Get one existing exception ID
        list_res = await client.get("/api/exceptions?limit=1")
        assert list_res.status_code == 200
        items = list_res.json()["items"]

        if items:
            target_id = items[0]["exception_id"]
            detail_res = await client.get(f"/api/exceptions/{target_id}")
            assert detail_res.status_code == 200
            detail_data = detail_res.json()
            assert detail_data["exception_id"] == target_id
            assert "evidence_items" in detail_data
            assert "explanation" in detail_data
            assert "recommended_action" in detail_data

        # Nonexistent ID returns 404
        fake_id = str(uuid.uuid4())
        not_found_res = await client.get(f"/api/exceptions/{fake_id}")
        assert not_found_res.status_code == 404


@pytest.mark.anyio
async def test_transactional_apis():
    """Verify all transactional endpoints return paginated data."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Accounts
        acc_res = await client.get("/api/accounts?limit=5")
        assert acc_res.status_code == 200
        assert "items" in acc_res.json()

        # Orders
        ord_res = await client.get("/api/orders?limit=5")
        assert ord_res.status_code == 200
        assert "items" in ord_res.json()

        # Invoices
        inv_res = await client.get("/api/invoices?limit=5")
        assert inv_res.status_code == 200
        assert "items" in inv_res.json()

        # Payments
        pay_res = await client.get("/api/payments?limit=5")
        assert pay_res.status_code == 200
        assert "items" in pay_res.json()

        # Disputes
        dsp_res = await client.get("/api/disputes?limit=5")
        assert dsp_res.status_code == 200
        assert "items" in dsp_res.json()


@pytest.mark.anyio
async def test_detection_run_api():
    """Verify POST /api/detection/run executes and returns summary."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/detection/run")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert "total_exceptions" in data
        assert "duration_seconds" in data
        assert "by_issue_type" in data
        assert "by_severity" in data
