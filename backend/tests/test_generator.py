"""
Unit tests for deterministic O2C synthetic data generator.
Verifies seed repeatability, UUIDv5 determinism, volume scaling, and anomaly injection.
"""

import random
from decimal import Decimal
import pytest

from app.generators.config import GeneratorConfig
from app.generators.id_utils import deterministic_uuid, format_quote_id, O2C_NAMESPACE
from app.generators.master_generator import generate_master_data
from app.generators.order_generator import generate_orders_data
from app.generators.fulfillment_generator import generate_shipments_data
from app.generators.billing_generator import generate_billing_data
from app.generators.treasury_generator import generate_treasury_data
from app.generators.dispute_generator import generate_disputes_data
from app.generators.event_generator import generate_status_events_data
from app.generators.anomaly_injector import inject_anomalies


def test_deterministic_uuidv5():
    """Verify that deterministic_uuid produces identical UUIDs for identical inputs."""
    u1 = deterministic_uuid("Invoice", "INV-2026-000001")
    u2 = deterministic_uuid("Invoice", "INV-2026-000001")
    assert u1 == u2
    assert u1.version == 5

    # Different entity types produce different UUIDs even for same ID
    u3 = deterministic_uuid("Shipment", "INV-2026-000001")
    assert u1 != u3


def test_generator_config_defaults():
    """Verify config defaults match solution architecture."""
    cfg = GeneratorConfig()
    assert cfg.seed == 20261022
    assert cfg.simulation_date.year == 2026
    assert cfg.simulation_date.month == 10
    assert cfg.simulation_date.day == 31
    assert cfg.base_quotes == 10000
    assert cfg.base_orders == 7000
    assert cfg.base_shipments == 7500
    assert cfg.base_invoices == 8000
    assert cfg.base_payments == 15000
    assert cfg.base_allocations == 20000
    assert cfg.base_disputes == 500


def test_reproducible_generation():
    """Verify that running generation with same seed produces identical results."""
    cfg = GeneratorConfig(seed=20261022, profile="test")
    rng1 = random.Random(cfg.seed)
    acc1, q1, ql1 = generate_master_data(cfg, rng1)

    rng2 = random.Random(cfg.seed)
    acc2, q2, ql2 = generate_master_data(cfg, rng2)

    assert len(acc1) == len(acc2)
    assert len(q1) == len(q2)
    assert [q["business_id"] for q in q1] == [q["business_id"] for q in q2]
    assert [q["total_net_amount"] for q in q1] == [q["total_net_amount"] for q in q2]


def test_anomaly_injection_coverage():
    """Verify that anomaly injection covers all 12 documented anomaly types."""
    cfg = GeneratorConfig(seed=20261022, profile="test")
    rng = random.Random(cfg.seed)

    accounts, quotes, quote_lines = generate_master_data(cfg, rng)
    orders, order_lines = generate_orders_data(cfg, quotes, quote_lines, rng)
    shipments, shipment_lines = generate_shipments_data(cfg, orders, order_lines, rng)
    invoices, invoice_lines = generate_billing_data(
        cfg, orders, order_lines, shipments, shipment_lines, accounts, rng
    )
    payments, allocations = generate_treasury_data(cfg, accounts, invoices, rng)
    disputes, adjustments = generate_disputes_data(cfg, invoices, rng)
    events = generate_status_events_data(
        cfg, quotes, orders, shipments, invoices, payments, disputes
    )

    ground_truth = inject_anomalies(
        cfg,
        quotes,
        orders,
        order_lines,
        shipments,
        shipment_lines,
        invoices,
        invoice_lines,
        payments,
        allocations,
        disputes,
        events,
        rng,
    )

    assert len(ground_truth) > 0
    injected_types = {gt["issue_type"] for gt in ground_truth}

    expected_types = {
        "OVERBILLING_QUANTITY",
        "OVERBILLING_AMOUNT",
        "UNDERBILLING",
        "DUPLICATE_INVOICE",
        "DUPLICATE_PAYMENT_ALLOCATION",
        "EXCESSIVE_PAYMENT_ALLOCATION",
        "PREMATURE_ORDER_CLOSURE",
        "INVALID_STATUS_TRANSITION",
        "DISPUTE_AR_DISCONNECT",
        "SHORT_PAYMENT",
        "SLA_AGING_BREACH",
        "OVERDUE_UNPAID_INVOICE",
    }

    assert expected_types.issubset(injected_types), f"Missing: {expected_types - injected_types}"
