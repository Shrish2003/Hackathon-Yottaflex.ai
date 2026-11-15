"""
SQLAlchemy 2.x declarative models for Exception Records and Exception Evidence.
Stores detected revenue leakage and operational compliance exceptions.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    String,
    Numeric,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ExceptionRecord(Base):
    """Primary operational exception record produced by the detection engine."""
    __tablename__ = "exception_records"

    exception_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    issue_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # e.g., OVERBILLING_QUANTITY, DUPLICATE_INVOICE, etc.
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False, index=True
    )  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    entity_type: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # e.g., Invoice, Payment, SalesOrder, etc.
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    business_id: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )

    # Optional concrete foreign keys for referential traceability
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("sales_orders.order_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("invoices.invoice_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("payments.payment_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    dispute_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("disputes.dispute_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    leakage_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)

    evidence_items: Mapped[List["ExceptionEvidence"]] = relationship(
        "ExceptionEvidence",
        back_populates="exception_record",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_exception_records_issue_severity", "issue_type", "severity"),
    )


class ExceptionEvidence(Base):
    """Substantiating documentary and mathematical evidence for an exception."""
    __tablename__ = "exception_evidence"

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exception_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exception_records.exception_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_table: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    conflicting_source_table: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    conflicting_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    expected_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    actual_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    discrepancy_delta: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    evidence_payload: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON-encoded payload
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    exception_record: Mapped["ExceptionRecord"] = relationship(
        "ExceptionRecord", back_populates="evidence_items"
    )
