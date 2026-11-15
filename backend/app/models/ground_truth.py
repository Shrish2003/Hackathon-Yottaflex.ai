"""
SQLAlchemy 2.x declarative model for Ground Truth Anomalies.
Stores isolated ground-truth labels for injected anomalies during synthetic generation.
CRITICAL: This table must remain physically and logically isolated from detection engines.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String,
    Numeric,
    Text,
    DateTime,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GroundTruthAnomaly(Base):
    """
    Isolated Ground Truth table populated strictly by the synthetic data generator.
    The anomaly detection engine must NOT query this table.
    Only the evaluation engine may query this table to compute Precision, Recall, and F1.
    """
    __tablename__ = "ground_truth_anomalies"

    anomaly_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    issue_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # e.g., OVERBILLING_QUANTITY, DUPLICATE_INVOICE, etc.
    entity_type: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # e.g., Invoice, InvoiceLine, SalesOrder, PaymentAllocation
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    business_id: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    leakage_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    injected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        Index("ix_ground_truth_issue_entity", "issue_type", "entity_type", "business_id"),
    )
