"""
SQLAlchemy Domain Models for Order-to-Cash (O2C) Platform.
Exports all core and supporting O2C entities.
"""

from app.db.database import Base
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
from app.models.ground_truth import GroundTruthAnomaly
from app.models.detection import ExceptionRecord, ExceptionEvidence

__all__ = [
    "Base",
    "Account",
    "Quote",
    "QuoteLine",
    "SalesOrder",
    "OrderLine",
    "Shipment",
    "ShipmentLine",
    "Invoice",
    "InvoiceLine",
    "Payment",
    "PaymentAllocation",
    "Dispute",
    "InvoiceAdjustment",
    "StatusEvent",
    "GroundTruthAnomaly",
    "ExceptionRecord",
    "ExceptionEvidence",
]
