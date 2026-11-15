"""
Pydantic v2 schemas for Executive Dashboard API.
"""

from typing import Dict
from pydantic import BaseModel, Field, ConfigDict


class DashboardSummaryResponse(BaseModel):
    """Aggregate executive summary for O2C operations and revenue leakage KPIs."""

    total_accounts: int = Field(..., description="Total active customer accounts")
    total_quotes: int = Field(..., description="Total commercial quotes generated")
    total_sales_orders: int = Field(..., description="Total sales orders booked")
    total_shipments: int = Field(..., description="Total shipments dispatched")
    total_invoices: int = Field(..., description="Total invoices issued")
    total_payments: int = Field(..., description="Total cash settlements ingested")
    total_detected_exceptions: int = Field(..., description="Total detected compliance and revenue leakage exceptions")
    total_identified_leakage_amount: float = Field(..., description="Total identified financial leakage amount in INR")
    exception_counts_by_severity: Dict[str, int] = Field(default_factory=dict, description="Exception counts grouped by severity")
    exception_counts_by_anomaly_type: Dict[str, int] = Field(default_factory=dict, description="Exception counts grouped by anomaly issue type")

    model_config = ConfigDict(from_attributes=True)
