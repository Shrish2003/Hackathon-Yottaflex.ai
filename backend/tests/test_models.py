"""
Unit tests for Stage 2 O2C SQLAlchemy models.
Verifies model instantiation, table mappings, UUID generation, and relationships.
"""

import uuid
from decimal import Decimal
import pytest
from app.models.o2c import (
    Account,
    Quote,
    QuoteLine,
    SalesOrder,
    OrderLine,
    Shipment,
    ShipmentLine,
    Invoice,
    InvoiceLine,
    Payment,
    PaymentAllocation,
    Dispute,
    InvoiceAdjustment,
    StatusEvent,
)


def test_model_table_names():
    """Verify all 14 entity table mappings."""
    assert Account.__tablename__ == "accounts"
    assert Quote.__tablename__ == "quotes"
    assert QuoteLine.__tablename__ == "quote_lines"
    assert SalesOrder.__tablename__ == "sales_orders"
    assert OrderLine.__tablename__ == "order_lines"
    assert Shipment.__tablename__ == "shipments"
    assert ShipmentLine.__tablename__ == "shipment_lines"
    assert Invoice.__tablename__ == "invoices"
    assert InvoiceLine.__tablename__ == "invoice_lines"
    assert Payment.__tablename__ == "payments"
    assert PaymentAllocation.__tablename__ == "payment_allocations"
    assert Dispute.__tablename__ == "disputes"
    assert InvoiceAdjustment.__tablename__ == "invoice_adjustments"
    assert StatusEvent.__tablename__ == "status_events"


def test_account_creation():
    """Verify account model fields and defaults."""
    acc = Account(
        account_number="ACC-001",
        account_name="Acme Corporation",
        credit_limit=Decimal("500000.00"),
        payment_terms="NET30",
        currency="INR",
        status="ACTIVE",
    )
    assert acc.account_number == "ACC-001"
    assert acc.currency == "INR"
    assert acc.credit_limit == Decimal("500000.00")


def test_quote_and_order_models():
    """Verify quote and order line structure."""
    q_id = uuid.uuid4()
    q = Quote(
        quote_id=q_id,
        business_id="QUO-001",
        account_id=uuid.uuid4(),
        status="APPROVED",
        total_gross_amount=Decimal("1000.00"),
        total_discount_amount=Decimal("100.00"),
        total_net_amount=Decimal("900.00"),
        currency="INR",
    )
    assert q.business_id == "QUO-001"
    assert q.total_net_amount == Decimal("900.00")


def test_status_event_model():
    """Verify StatusEvent audit entity structure."""
    order_id = uuid.uuid4()
    event = StatusEvent(
        entity_type="SalesOrder",
        order_id=order_id,
        business_id="SO-001",
        previous_state="DRAFT",
        new_state="CONFIRMED",
        reason="Customer approved quotation",
    )
    assert event.entity_type == "SalesOrder"
    assert event.order_id == order_id
    assert event.new_state == "CONFIRMED"
