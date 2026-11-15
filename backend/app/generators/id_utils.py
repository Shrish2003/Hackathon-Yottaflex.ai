"""
Deterministic UUID and Business Identifier utilities for O2C data generation.
Uses UUIDv5 with a fixed namespace to guarantee 100% reproducible identifiers.
"""

import uuid
from typing import Optional

# Fixed Namespace UUID for deterministic O2C surrogate primary keys
O2C_NAMESPACE = uuid.UUID("a67b45f2-901c-4b5b-80df-269e8b15d91a")


def deterministic_uuid(entity_type: str, business_id: str) -> uuid.UUID:
    """Derive a reproducible UUIDv5 from entity type and business identifier."""
    name = f"{entity_type}:{business_id}"
    return uuid.uuid5(O2C_NAMESPACE, name)


def format_account_num(idx: int) -> str:
    """Format: ACC-2026-000001"""
    return f"ACC-2026-{idx:06d}"


def format_quote_id(idx: int) -> str:
    """Format: QTE-2026-000001"""
    return f"QTE-2026-{idx:06d}"


def format_order_id(idx: int) -> str:
    """Format: SO-2026-000001"""
    return f"SO-2026-{idx:06d}"


def format_shipment_id(idx: int) -> str:
    """Format: SHP-2026-000001"""
    return f"SHP-2026-{idx:06d}"


def format_invoice_id(idx: int) -> str:
    """Format: INV-2026-000001"""
    return f"INV-2026-{idx:06d}"


def format_payment_id(idx: int) -> str:
    """Format: PAY-2026-000001"""
    return f"PAY-2026-{idx:06d}"


def format_dispute_id(idx: int) -> str:
    """Format: DSP-2026-000001"""
    return f"DSP-2026-{idx:06d}"


def format_event_id(idx: int) -> str:
    """Format: EVT-2026-000001"""
    return f"EVT-2026-{idx:06d}"


def format_adjustment_id(idx: int) -> str:
    """Format: ADJ-2026-000001"""
    return f"ADJ-2026-{idx:06d}"


def format_allocation_id(idx: int) -> str:
    """Format: ALC-2026-000001"""
    return f"ALC-2026-{idx:06d}"


def format_anomaly_id(idx: int) -> str:
    """Format: ANM-2026-000001"""
    return f"ANM-2026-{idx:06d}"
