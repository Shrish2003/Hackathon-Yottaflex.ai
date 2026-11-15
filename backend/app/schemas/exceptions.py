"""
Pydantic v2 schemas for Exceptions and Evidence APIs.
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class EvidenceItemResponse(BaseModel):
    """Substantiating evidence record linked to an exception."""

    evidence_id: uuid.UUID
    exception_id: uuid.UUID
    evidence_type: str
    source_table: str
    source_id: uuid.UUID
    conflicting_source_table: Optional[str] = None
    conflicting_source_id: Optional[uuid.UUID] = None
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    discrepancy_delta: Optional[float] = None
    evidence_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    @field_validator("evidence_payload", mode="before")
    @classmethod
    def parse_payload(cls, val):
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return {"raw": val}
        return val or {}

    model_config = ConfigDict(from_attributes=True)


class ExceptionRecordResponse(BaseModel):
    """Summary representation of a detected exception record."""

    exception_id: uuid.UUID
    issue_type: str
    severity: str
    entity_type: str
    entity_id: uuid.UUID
    business_id: str
    account_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None
    payment_id: Optional[uuid.UUID] = None
    dispute_id: Optional[uuid.UUID] = None
    leakage_amount: Optional[float] = None
    detected_at: datetime
    explanation: str
    recommended_action: str
    evidence_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ExceptionDetailResponse(ExceptionRecordResponse):
    """Detailed exception representation including all evidence records."""

    evidence_items: List[EvidenceItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PaginatedExceptionsResponse(BaseModel):
    """Paginated envelope for exception record lists."""

    items: List[ExceptionRecordResponse]
    total: int
    page: int
    limit: int
    pages: int
