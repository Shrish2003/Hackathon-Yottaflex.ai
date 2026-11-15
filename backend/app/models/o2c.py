"""
SQLAlchemy 2.x declarative models for the O2C Revenue Assurance Platform.
Covers all 13 core and supporting entities with real foreign keys,
UUID primary keys, numeric precision (INR currency), and timestamp tracking.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    String,
    Numeric,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ==============================================================================
# 1. ACCOUNT
# ==============================================================================
class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_number: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    payment_terms: Mapped[str] = mapped_column(
        String(32), default="NET30", nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    quotes: Mapped[List["Quote"]] = relationship("Quote", back_populates="account")
    sales_orders: Mapped[List["SalesOrder"]] = relationship(
        "SalesOrder", back_populates="account"
    )
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="account")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="account")


# ==============================================================================
# 2. QUOTE & QUOTE LINE
# ==============================================================================
class Quote(Base):
    __tablename__ = "quotes"

    quote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), default="DRAFT", nullable=False, index=True
    )
    total_gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    total_discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    total_net_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    valid_to: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="quotes")
    lines: Mapped[List["QuoteLine"]] = relationship(
        "QuoteLine", back_populates="quote", cascade="all, delete-orphan"
    )
    sales_order: Mapped[Optional["SalesOrder"]] = relationship(
        "SalesOrder", back_populates="quote", uselist=False
    )


class QuoteLine(Base):
    __tablename__ = "quote_lines"

    quote_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quote_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quotes.quote_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    product_sku: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit_list_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    line_net_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("quote_id", "line_number", name="uq_quote_line_number"),
    )

    # Relationships
    quote: Mapped["Quote"] = relationship("Quote", back_populates="lines")


# ==============================================================================
# 3. SALES ORDER & ORDER LINE
# ==============================================================================
class SalesOrder(Base):
    __tablename__ = "sales_orders"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    quote_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quotes.quote_id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), default="DRAFT", nullable=False, index=True
    )
    total_order_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    quote: Mapped["Quote"] = relationship("Quote", back_populates="sales_order")
    account: Mapped["Account"] = relationship("Account", back_populates="sales_orders")
    lines: Mapped[List["OrderLine"]] = relationship(
        "OrderLine", back_populates="order", cascade="all, delete-orphan"
    )
    shipments: Mapped[List["Shipment"]] = relationship(
        "Shipment", back_populates="order"
    )
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="order")


class OrderLine(Base):
    __tablename__ = "order_lines"

    order_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sales_orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quote_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("quote_lines.quote_line_id", ondelete="SET NULL"),
        nullable=True,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    product_sku: Mapped[str] = mapped_column(String(64), nullable=False)
    ordered_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    line_total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="PENDING", nullable=False
    )

    __table_args__ = (
        UniqueConstraint("order_id", "line_number", name="uq_order_line_number"),
    )

    # Relationships
    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="lines")
    shipment_lines: Mapped[List["ShipmentLine"]] = relationship(
        "ShipmentLine", back_populates="order_line"
    )
    invoice_lines: Mapped[List["InvoiceLine"]] = relationship(
        "InvoiceLine", back_populates="order_line"
    )


# ==============================================================================
# 4. SHIPMENT & SHIPMENT LINE (Partial & Multi-Shipment Support)
# ==============================================================================
class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sales_orders.order_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    carrier: Mapped[str] = mapped_column(String(64), nullable=False)
    tracking_number: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="PENDING", nullable=False, index=True
    )
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="shipments")
    lines: Mapped[List["ShipmentLine"]] = relationship(
        "ShipmentLine", back_populates="shipment", cascade="all, delete-orphan"
    )


class ShipmentLine(Base):
    __tablename__ = "shipment_lines"

    shipment_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    shipment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("shipments.shipment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_line_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("order_lines.order_line_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    shipped_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="lines")
    order_line: Mapped["OrderLine"] = relationship(
        "OrderLine", back_populates="shipment_lines"
    )
    invoice_lines: Mapped[List["InvoiceLine"]] = relationship(
        "InvoiceLine", back_populates="shipment_line"
    )


# ==============================================================================
# 5. INVOICE, INVOICE LINE & INVOICE ADJUSTMENT (Consolidated / Partial Invoicing)
# ==============================================================================
class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sales_orders.order_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), default="DRAFT", nullable=False, index=True
    )
    total_invoiced_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    outstanding_balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    issue_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="invoices")
    account: Mapped["Account"] = relationship("Account", back_populates="invoices")
    lines: Mapped[List["InvoiceLine"]] = relationship(
        "InvoiceLine", back_populates="invoice", cascade="all, delete-orphan"
    )
    allocations: Mapped[List["PaymentAllocation"]] = relationship(
        "PaymentAllocation", back_populates="invoice"
    )
    disputes: Mapped[List["Dispute"]] = relationship("Dispute", back_populates="invoice")
    adjustments: Mapped[List["InvoiceAdjustment"]] = relationship(
        "InvoiceAdjustment", back_populates="invoice"
    )


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    invoice_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.invoice_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_line_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("order_lines.order_line_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    shipment_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("shipment_lines.shipment_line_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    invoiced_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    line_total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("invoice_id", "line_number", name="uq_invoice_line_number"),
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="lines")
    order_line: Mapped["OrderLine"] = relationship(
        "OrderLine", back_populates="invoice_lines"
    )
    shipment_line: Mapped[Optional["ShipmentLine"]] = relationship(
        "ShipmentLine", back_populates="invoice_lines"
    )


class InvoiceAdjustment(Base):
    __tablename__ = "invoice_adjustments"

    adjustment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.invoice_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dispute_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("disputes.dispute_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    adjustment_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # CREDIT_MEMO, DEBIT_MEMO, WRITE_OFF
    adjustment_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="adjustments")
    dispute: Mapped[Optional["Dispute"]] = relationship(
        "Dispute", back_populates="adjustments"
    )


# ==============================================================================
# 6. PAYMENT & PAYMENT ALLOCATION (M:N Split / Multi-Invoice Remittance)
# ==============================================================================
class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.account_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payment_method: Mapped[str] = mapped_column(
        String(32), default="WIRE", nullable=False
    )
    payment_reference: Mapped[str] = mapped_column(String(128), nullable=False)
    amount_received: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    amount_allocated: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    unallocated_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="RECEIVED", nullable=False, index=True
    )
    payment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="payments")
    allocations: Mapped[List["PaymentAllocation"]] = relationship(
        "PaymentAllocation", back_populates="payment", cascade="all, delete-orphan"
    )


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    allocation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("payments.payment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.invoice_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    allocation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default="ACTIVE", nullable=False
    )  # ACTIVE, REVERSED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="allocations")


# ==============================================================================
# 7. DISPUTE
# ==============================================================================
class Dispute(Base):
    __tablename__ = "disputes"

    dispute_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("invoices.invoice_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    dispute_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    disputed_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="LODGED", nullable=False, index=True
    )
    lodged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="disputes")
    adjustments: Mapped[List["InvoiceAdjustment"]] = relationship(
        "InvoiceAdjustment", back_populates="dispute"
    )


# ==============================================================================
# 8. STATUS EVENT (Append-Only Audit History with Enforceable FKs)
# ==============================================================================
class StatusEvent(Base):
    __tablename__ = "status_events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_type: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # Quote, SalesOrder, Shipment, Invoice, Payment, Dispute

    # Concrete foreign keys for referential integrity
    quote_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("quotes.quote_id", ondelete="CASCADE"), nullable=True, index=True
    )
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("sales_orders.order_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    shipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("shipments.shipment_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("invoices.invoice_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("payments.payment_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    dispute_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("disputes.dispute_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    business_id: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )
    previous_state: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    new_state: Mapped[str] = mapped_column(String(32), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN quote_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN order_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN shipment_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN invoice_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN payment_id IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN dispute_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="chk_status_event_exact_one_fk",
        ),
    )
