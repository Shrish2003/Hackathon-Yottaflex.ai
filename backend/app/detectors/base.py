"""
Base interfaces and data structures for O2C anomaly detectors.
"""

import abc
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session


@dataclass
class EvidenceItem:
    """Substantiating documentary and mathematical evidence item."""
    evidence_type: str
    source_table: str
    source_id: uuid.UUID
    conflicting_source_table: Optional[str] = None
    conflicting_source_id: Optional[uuid.UUID] = None
    expected_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    discrepancy_delta: Optional[Decimal] = None
    evidence_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectionResult:
    """Structured detection outcome produced by a detector rule."""
    issue_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    entity_type: str  # Invoice, Payment, SalesOrder, etc.
    entity_id: uuid.UUID
    business_id: str
    leakage_amount: Optional[Decimal]
    explanation: str
    recommended_action: str
    account_id: Optional[uuid.UUID] = None
    order_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None
    payment_id: Optional[uuid.UUID] = None
    dispute_id: Optional[uuid.UUID] = None
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    detected_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class BaseDetector(abc.ABC):
    """Abstract base class for all deterministic anomaly detectors."""

    @property
    @abc.abstractmethod
    def issue_type(self) -> str:
        """Standardized issue type code (e.g. OVERBILLING_QUANTITY)."""
        pass

    @property
    @abc.abstractmethod
    def default_severity(self) -> str:
        """Default severity level (CRITICAL, HIGH, MEDIUM, LOW)."""
        pass

    @abc.abstractmethod
    def detect(
        self, session: Session, simulation_date: datetime
    ) -> List[DetectionResult]:
        """
        Executes deterministic detection rule using SQLAlchemy against operational tables.
        Returns list of DetectionResult objects.
        """
        pass
