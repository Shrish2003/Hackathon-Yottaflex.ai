"""
Pydantic schemas for Detection Execution API.
"""

from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field


class DetectionRunResponse(BaseModel):
    """Execution outcome summary from the anomaly detection engine."""

    status: str = Field(default="SUCCESS", description="Execution status")
    execution_timestamp: datetime = Field(..., description="Timestamp when detection executed")
    simulation_as_of_date: datetime = Field(..., description="Fixed simulation date used for detection")
    duration_seconds: float = Field(..., description="Duration in seconds")
    total_exceptions: int = Field(..., description="Total exceptions identified")
    total_evidence_records: int = Field(..., description="Total evidence items persisted")
    total_financial_leakage_inr: float = Field(..., description="Total quantified leakage in INR")
    by_issue_type: Dict[str, int] = Field(default_factory=dict, description="Exception counts by issue type")
    by_severity: Dict[str, int] = Field(default_factory=dict, description="Exception counts by severity level")
