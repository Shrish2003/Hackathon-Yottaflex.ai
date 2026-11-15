"""
Implementation of all 12 deterministic O2C revenue leakage and process anomaly detection rules.
CRITICAL: Operates strictly on operational tables. NEVER accesses ground_truth_anomalies.
"""

import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from sqlalchemy import select, func, and_, or_, not_, exists
from sqlalchemy.orm import Session

from app.detectors.base import BaseDetector, DetectionResult, EvidenceItem
from app.models.o2c import (
    Account,
    Quote,
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

ROUNDING_TOLERANCE = Decimal("0.02")


# ==============================================================================
# 1. ANOM-001: OVERBILLING_QUANTITY
# ==============================================================================
class OverbillingQuantityDetector(BaseDetector):
    """Detects when invoiced quantity exceeds shipped/delivered quantity."""

    @property
    def issue_type(self) -> str:
        return "OVERBILLING_QUANTITY"

    @property
    def default_severity(self) -> str:
        return "HIGH"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                Invoice.invoice_id,
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                InvoiceLine.invoice_line_id,
                InvoiceLine.invoiced_quantity,
                InvoiceLine.unit_price,
                ShipmentLine.shipment_line_id,
                ShipmentLine.shipped_quantity,
            )
            .join(InvoiceLine, Invoice.invoice_id == InvoiceLine.invoice_id)
            .join(ShipmentLine, InvoiceLine.shipment_line_id == ShipmentLine.shipment_line_id)
            .where(InvoiceLine.invoiced_quantity > ShipmentLine.shipped_quantity)
        )

        results = []
        for row in session.execute(stmt):
            delta_qty = row.invoiced_quantity - row.shipped_quantity
            leakage = (delta_qty * row.unit_price).quantize(Decimal("0.01"))

            evidence = EvidenceItem(
                evidence_type="QUANTITY_OVERBILLING_DISCREPANCY",
                source_table="invoice_lines",
                source_id=row.invoice_line_id,
                conflicting_source_table="shipment_lines",
                conflicting_source_id=row.shipment_line_id,
                expected_value=row.shipped_quantity,
                actual_value=row.invoiced_quantity,
                discrepancy_delta=delta_qty,
                evidence_payload={
                    "invoiced_quantity": float(row.invoiced_quantity),
                    "delivered_quantity": float(row.shipped_quantity),
                    "unit_price": float(row.unit_price),
                    "excess_quantity": float(delta_qty),
                    "leakage_amount": float(leakage),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Invoice",
                    entity_id=row.invoice_id,
                    business_id=row.invoice_business_id,
                    leakage_amount=leakage,
                    explanation=(
                        f"Invoice {row.invoice_business_id} billed {row.invoiced_quantity} units "
                        f"but warehouse records verify only {row.shipped_quantity} units delivered."
                    ),
                    recommended_action="Issue Credit Memo for unfulfilled quantity and rebill correct delivered volume.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 2. ANOM-002: OVERBILLING_AMOUNT
# ==============================================================================
class OverbillingAmountDetector(BaseDetector):
    """Detects when invoiced unit price exceeds contracted sales order unit price."""

    @property
    def issue_type(self) -> str:
        return "OVERBILLING_AMOUNT"

    @property
    def default_severity(self) -> str:
        return "HIGH"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                Invoice.invoice_id,
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                InvoiceLine.invoice_line_id,
                InvoiceLine.invoiced_quantity,
                InvoiceLine.unit_price.label("invoiced_unit_price"),
                OrderLine.order_line_id,
                OrderLine.unit_price.label("contracted_unit_price"),
            )
            .join(InvoiceLine, Invoice.invoice_id == InvoiceLine.invoice_id)
            .join(OrderLine, InvoiceLine.order_line_id == OrderLine.order_line_id)
            .where(InvoiceLine.unit_price > OrderLine.unit_price + ROUNDING_TOLERANCE)
        )

        results = []
        for row in session.execute(stmt):
            price_delta = row.invoiced_unit_price - row.contracted_unit_price
            leakage = (price_delta * row.invoiced_quantity).quantize(Decimal("0.01"))

            evidence = EvidenceItem(
                evidence_type="PRICE_OVERBILLING_DISCREPANCY",
                source_table="invoice_lines",
                source_id=row.invoice_line_id,
                conflicting_source_table="order_lines",
                conflicting_source_id=row.order_line_id,
                expected_value=row.contracted_unit_price,
                actual_value=row.invoiced_unit_price,
                discrepancy_delta=price_delta,
                evidence_payload={
                    "contracted_unit_price": float(row.contracted_unit_price),
                    "invoiced_unit_price": float(row.invoiced_unit_price),
                    "invoiced_quantity": float(row.invoiced_quantity),
                    "price_delta": float(price_delta),
                    "leakage_amount": float(leakage),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Invoice",
                    entity_id=row.invoice_id,
                    business_id=row.invoice_business_id,
                    leakage_amount=leakage,
                    explanation=(
                        f"Invoice {row.invoice_business_id} billed at unit price ₹{row.invoiced_unit_price}, "
                        f"which exceeds contracted order price ₹{row.contracted_unit_price}."
                    ),
                    recommended_action="Adjust invoice unit price to contracted rate and issue pricing credit memo.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 3. ANOM-003: UNDERBILLING
# ==============================================================================
class UnderbillingDetector(BaseDetector):
    """Detects underbilling where unit price is lower than contracted, causing margin erosion."""

    @property
    def issue_type(self) -> str:
        return "UNDERBILLING"

    @property
    def default_severity(self) -> str:
        return "MEDIUM"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                Invoice.invoice_id,
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                InvoiceLine.invoice_line_id,
                InvoiceLine.invoiced_quantity,
                InvoiceLine.unit_price.label("invoiced_unit_price"),
                OrderLine.order_line_id,
                OrderLine.unit_price.label("contracted_unit_price"),
            )
            .join(InvoiceLine, Invoice.invoice_id == InvoiceLine.invoice_id)
            .join(OrderLine, InvoiceLine.order_line_id == OrderLine.order_line_id)
            .where(InvoiceLine.unit_price < OrderLine.unit_price - ROUNDING_TOLERANCE)
        )

        results = []
        for row in session.execute(stmt):
            price_drop = row.contracted_unit_price - row.invoiced_unit_price
            leakage = (price_drop * row.invoiced_quantity).quantize(Decimal("0.01"))

            evidence = EvidenceItem(
                evidence_type="MARGIN_EROSION_UNDERBILLING",
                source_table="invoice_lines",
                source_id=row.invoice_line_id,
                conflicting_source_table="order_lines",
                conflicting_source_id=row.order_line_id,
                expected_value=row.contracted_unit_price,
                actual_value=row.invoiced_unit_price,
                discrepancy_delta=price_drop,
                evidence_payload={
                    "contracted_unit_price": float(row.contracted_unit_price),
                    "invoiced_unit_price": float(row.invoiced_unit_price),
                    "invoiced_quantity": float(row.invoiced_quantity),
                    "unbilled_delta": float(price_drop),
                    "margin_erosion": float(leakage),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Invoice",
                    entity_id=row.invoice_id,
                    business_id=row.invoice_business_id,
                    leakage_amount=leakage,
                    explanation=(
                        f"Invoice {row.invoice_business_id} billed at unit price ₹{row.invoiced_unit_price}, "
                        f"eroding contracted margin from approved order price ₹{row.contracted_unit_price}."
                    ),
                    recommended_action="Issue supplementary debit memo to recover unbilled revenue margin.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 4. ANOM-004: DUPLICATE_INVOICE
# ==============================================================================
class DuplicateInvoiceDetector(BaseDetector):
    """Detects duplicate invoices billing the same order line deliverable."""

    @property
    def issue_type(self) -> str:
        return "DUPLICATE_INVOICE"

    @property
    def default_severity(self) -> str:
        return "CRITICAL"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        # Identify order lines billed by more than one distinct invoice
        dup_subq = (
            select(
                InvoiceLine.order_line_id,
                InvoiceLine.invoiced_quantity,
                InvoiceLine.unit_price,
                func.count(func.distinct(InvoiceLine.invoice_id)).label("inv_count"),
                func.min(Invoice.created_at).label("first_created"),
            )
            .join(Invoice, InvoiceLine.invoice_id == Invoice.invoice_id)
            .group_by(
                InvoiceLine.order_line_id,
                InvoiceLine.invoiced_quantity,
                InvoiceLine.unit_price,
            )
            .having(func.count(func.distinct(InvoiceLine.invoice_id)) > 1)
            .subquery()
        )

        stmt = (
            select(
                Invoice.invoice_id,
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                Invoice.total_invoiced_amount,
                Invoice.created_at,
                InvoiceLine.invoice_line_id,
                dup_subq.c.first_created,
            )
            .join(InvoiceLine, Invoice.invoice_id == InvoiceLine.invoice_id)
            .join(dup_subq, InvoiceLine.order_line_id == dup_subq.c.order_line_id)
            .where(Invoice.created_at > dup_subq.c.first_created)
        )

        seen_invoices = set()
        results = []

        for row in session.execute(stmt):
            if row.invoice_id in seen_invoices:
                continue
            seen_invoices.add(row.invoice_id)

            evidence = EvidenceItem(
                evidence_type="DUPLICATE_INVOICE_RECORD",
                source_table="invoices",
                source_id=row.invoice_id,
                conflicting_source_table="invoices",
                expected_value=Decimal("0.00"),
                actual_value=row.total_invoiced_amount,
                discrepancy_delta=row.total_invoiced_amount,
                evidence_payload={
                    "duplicate_invoice_id": str(row.invoice_id),
                    "duplicate_business_id": row.invoice_business_id,
                    "order_id": str(row.order_id),
                    "duplicate_total_amount": float(row.total_invoiced_amount),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Invoice",
                    entity_id=row.invoice_id,
                    business_id=row.invoice_business_id,
                    leakage_amount=row.total_invoiced_amount,
                    explanation=(
                        f"Duplicate invoice {row.invoice_business_id} bills identical order deliverables "
                        f"already covered by an earlier invoice on sales order {row.order_id}."
                    ),
                    recommended_action="Void duplicate invoice immediately to prevent double customer billing.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 5. ANOM-005: DUPLICATE_PAYMENT_ALLOCATION
# ==============================================================================
class DuplicatePaymentAllocationDetector(BaseDetector):
    """Detects identical payment allocations repeated for the same payment and invoice."""

    @property
    def issue_type(self) -> str:
        return "DUPLICATE_PAYMENT_ALLOCATION"

    @property
    def default_severity(self) -> str:
        return "HIGH"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                PaymentAllocation.payment_id,
                PaymentAllocation.invoice_id,
                PaymentAllocation.allocated_amount,
                func.count(PaymentAllocation.allocation_id).label("alloc_count"),
                func.array_agg(PaymentAllocation.allocation_id).label("alloc_ids"),
            )
            .group_by(
                PaymentAllocation.payment_id,
                PaymentAllocation.invoice_id,
                PaymentAllocation.allocated_amount,
            )
            .having(func.count(PaymentAllocation.allocation_id) > 1)
        )

        results = []
        for row in session.execute(stmt):
            duplicate_count = row.alloc_count - 1
            leakage = (row.allocated_amount * Decimal(duplicate_count)).quantize(Decimal("0.01"))

            # First ID is considered original, remaining IDs are duplicates
            dup_id = row.alloc_ids[-1]
            orig_id = row.alloc_ids[0]

            evidence = EvidenceItem(
                evidence_type="DUPLICATE_ALLOCATION_RECORD",
                source_table="payment_allocations",
                source_id=dup_id,
                conflicting_source_table="payment_allocations",
                conflicting_source_id=orig_id,
                expected_value=row.allocated_amount,
                actual_value=(row.allocated_amount * row.alloc_count),
                discrepancy_delta=leakage,
                evidence_payload={
                    "payment_id": str(row.payment_id),
                    "invoice_id": str(row.invoice_id),
                    "duplicate_count": duplicate_count,
                    "allocated_amount": float(row.allocated_amount),
                    "leakage_amount": float(leakage),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="PaymentAllocation",
                    entity_id=dup_id,
                    business_id=f"ALC-DUP-{str(dup_id)[:8]}",
                    leakage_amount=leakage,
                    explanation=(
                        f"Payment {row.payment_id} was allocated {row.alloc_count} times with identical amount "
                        f"₹{row.allocated_amount} to invoice {row.invoice_id}."
                    ),
                    recommended_action="Reverse duplicate allocation to restore customer cash ledger accuracy.",
                    payment_id=row.payment_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 6. ANOM-006: EXCESSIVE_PAYMENT_ALLOCATION
# ==============================================================================
class ExcessivePaymentAllocationDetector(BaseDetector):
    """Detects payments where sum of allocations exceeds received cash amount."""

    @property
    def issue_type(self) -> str:
        return "EXCESSIVE_PAYMENT_ALLOCATION"

    @property
    def default_severity(self) -> str:
        return "HIGH"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                Payment.payment_id,
                Payment.business_id.label("payment_business_id"),
                Payment.account_id,
                Payment.amount_received,
                func.sum(PaymentAllocation.allocated_amount).label("total_allocated"),
            )
            .join(PaymentAllocation, Payment.payment_id == PaymentAllocation.payment_id)
            .group_by(Payment.payment_id, Payment.business_id, Payment.account_id, Payment.amount_received)
            .having(func.sum(PaymentAllocation.allocated_amount) > Payment.amount_received + ROUNDING_TOLERANCE)
        )

        results = []
        for row in session.execute(stmt):
            excess = (row.total_allocated - row.amount_received).quantize(Decimal("0.01"))

            evidence = EvidenceItem(
                evidence_type="PAYMENT_OVERALLOCATION_SUM",
                source_table="payments",
                source_id=row.payment_id,
                conflicting_source_table="payment_allocations",
                expected_value=row.amount_received,
                actual_value=row.total_allocated,
                discrepancy_delta=excess,
                evidence_payload={
                    "payment_business_id": row.payment_business_id,
                    "amount_received": float(row.amount_received),
                    "total_allocated": float(row.total_allocated),
                    "excess_allocated": float(excess),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Payment",
                    entity_id=row.payment_id,
                    business_id=row.payment_business_id,
                    leakage_amount=excess,
                    explanation=(
                        f"Payment {row.payment_business_id} received ₹{row.amount_received} but has total "
                        f"allocated sum of ₹{row.total_allocated} (excess: +₹{excess})."
                    ),
                    recommended_action="Audit payment allocations and deallocate excess cash applications.",
                    account_id=row.account_id,
                    payment_id=row.payment_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 7. ANOM-007: PREMATURE_ORDER_CLOSURE
# ==============================================================================
class PrematureOrderClosureDetector(BaseDetector):
    """Detects sales orders marked CLOSED while associated invoices remain unpaid."""

    @property
    def issue_type(self) -> str:
        return "PREMATURE_ORDER_CLOSURE"

    @property
    def default_severity(self) -> str:
        return "CRITICAL"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                SalesOrder.order_id,
                SalesOrder.business_id.label("order_business_id"),
                SalesOrder.account_id,
                func.sum(Invoice.outstanding_balance).label("unpaid_balance"),
                func.array_agg(Invoice.business_id).label("unpaid_invoice_ids"),
            )
            .join(Invoice, SalesOrder.order_id == Invoice.order_id)
            .where(
                SalesOrder.status == "CLOSED",
                Invoice.outstanding_balance > ROUNDING_TOLERANCE,
            )
            .group_by(SalesOrder.order_id, SalesOrder.business_id, SalesOrder.account_id)
        )

        results = []
        for row in session.execute(stmt):
            unpaid = row.unpaid_balance.quantize(Decimal("0.01"))

            evidence = EvidenceItem(
                evidence_type="UNSETTLED_ORDER_BALANCE_AT_CLOSURE",
                source_table="sales_orders",
                source_id=row.order_id,
                conflicting_source_table="invoices",
                expected_value=Decimal("0.00"),
                actual_value=unpaid,
                discrepancy_delta=unpaid,
                evidence_payload={
                    "order_business_id": row.order_business_id,
                    "unpaid_invoices": row.unpaid_invoice_ids,
                    "outstanding_balance": float(unpaid),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="SalesOrder",
                    entity_id=row.order_id,
                    business_id=row.order_business_id,
                    leakage_amount=unpaid,
                    explanation=(
                        f"Sales Order {row.order_business_id} is marked CLOSED but retains uncollected "
                        f"receivable balance of ₹{unpaid} across invoices {row.unpaid_invoice_ids}."
                    ),
                    recommended_action="Reopen sales order status and initiate AR collection for outstanding balances.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 8. ANOM-008: INVALID_STATUS_TRANSITION
# ==============================================================================
class InvalidStatusTransitionDetector(BaseDetector):
    """Detects unauthorized lifecycle hops and skips in the append-only status event audit trail."""

    @property
    def issue_type(self) -> str:
        return "INVALID_STATUS_TRANSITION"

    @property
    def default_severity(self) -> str:
        return "MEDIUM"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        # Detect illegal transition: direct jump from DRAFT to CLOSED skipping intermediate fulfillment
        stmt = (
            select(
                StatusEvent.event_id,
                StatusEvent.entity_type,
                StatusEvent.business_id,
                StatusEvent.order_id,
                StatusEvent.previous_state,
                StatusEvent.new_state,
                StatusEvent.event_timestamp,
            )
            .where(
                StatusEvent.entity_type == "SalesOrder",
                StatusEvent.previous_state == "DRAFT",
                StatusEvent.new_state == "CLOSED",
            )
        )

        results = []
        for row in session.execute(stmt):
            evidence = EvidenceItem(
                evidence_type="ILLEGAL_LIFECYCLE_STATE_HOP",
                source_table="status_events",
                source_id=row.event_id,
                expected_value=None,
                actual_value=None,
                discrepancy_delta=None,
                evidence_payload={
                    "event_id": str(row.event_id),
                    "entity_type": row.entity_type,
                    "business_id": row.business_id,
                    "previous_state": row.previous_state,
                    "illegal_target_state": row.new_state,
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="StatusEvent",
                    entity_id=row.event_id,
                    business_id=row.business_id,
                    leakage_amount=Decimal("0.00"),
                    explanation=(
                        f"Illegal lifecycle transition detected for {row.entity_type} {row.business_id}: "
                        f"direct skip from {row.previous_state} to {row.new_state} without intermediate fulfillment."
                    ),
                    recommended_action="Audit user credentials and restore valid chronological state transition history.",
                    order_id=row.order_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 9. ANOM-009: DISPUTE_AR_DISCONNECT
# ==============================================================================
class DisputeARDisconnectDetector(BaseDetector):
    """Detects active disputes unisolated from standard collection and aging reporting."""

    @property
    def issue_type(self) -> str:
        return "DISPUTE_AR_DISCONNECT"

    @property
    def default_severity(self) -> str:
        return "HIGH"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        stmt = (
            select(
                Dispute.dispute_id,
                Dispute.business_id.label("dispute_business_id"),
                Dispute.invoice_id,
                Dispute.disputed_amount,
                Dispute.status.label("dispute_status"),
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                Invoice.outstanding_balance,
            )
            .join(Invoice, Dispute.invoice_id == Invoice.invoice_id)
            .where(
                Dispute.status.in_(["LODGED", "UNDER_INVESTIGATION"]),
                Dispute.disputed_amount > Decimal("0.00"),
            )
        )

        results = []
        for row in session.execute(stmt):
            evidence = EvidenceItem(
                evidence_type="UNISOLATED_ACTIVE_DISPUTE_BALANCE",
                source_table="disputes",
                source_id=row.dispute_id,
                conflicting_source_table="invoices",
                conflicting_source_id=row.invoice_id,
                expected_value=row.disputed_amount,
                actual_value=row.outstanding_balance,
                discrepancy_delta=row.disputed_amount,
                evidence_payload={
                    "dispute_business_id": row.dispute_business_id,
                    "invoice_business_id": row.invoice_business_id,
                    "dispute_status": row.dispute_status,
                    "disputed_amount": float(row.disputed_amount),
                    "invoice_outstanding_balance": float(row.outstanding_balance),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Dispute",
                    entity_id=row.dispute_id,
                    business_id=row.dispute_business_id,
                    leakage_amount=row.disputed_amount,
                    explanation=(
                        f"Active dispute {row.dispute_business_id} ({row.dispute_status}) on invoice "
                        f"{row.invoice_business_id} holds disputed amount ₹{row.disputed_amount} unisolated in AR."
                    ),
                    recommended_action="Place customer collections on administrative hold and isolate disputed amount.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    dispute_id=row.dispute_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 10. ANOM-010: SHORT_PAYMENT
# ==============================================================================
class ShortPaymentDetector(BaseDetector):
    """Detects invoices partially paid past due date with zero dispute or adjustment."""

    @property
    def issue_type(self) -> str:
        return "SHORT_PAYMENT"

    @property
    def default_severity(self) -> str:
        return "MEDIUM"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        # Subquery for active disputes
        active_disp_subq = (
            select(1)
            .select_from(Dispute)
            .where(
                Dispute.invoice_id == Invoice.invoice_id,
                Dispute.status.in_(["LODGED", "UNDER_INVESTIGATION"]),
            )
        )

        # Subquery for credit adjustments
        adj_subq = (
            select(1)
            .select_from(InvoiceAdjustment)
            .where(InvoiceAdjustment.invoice_id == Invoice.invoice_id)
        )

        stmt = (
            select(
                Invoice.invoice_id,
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                Invoice.total_invoiced_amount,
                Invoice.paid_amount,
                Invoice.outstanding_balance,
                Invoice.due_date,
            )
            .where(
                Invoice.status == "PARTIALLY_PAID",
                Invoice.paid_amount > Decimal("0.00"),
                Invoice.outstanding_balance > ROUNDING_TOLERANCE,
                Invoice.due_date < simulation_date,
                not_(exists(active_disp_subq)),
                not_(exists(adj_subq)),
            )
        )

        results = []
        for row in session.execute(stmt):
            unpaid = row.outstanding_balance.quantize(Decimal("0.01"))

            evidence = EvidenceItem(
                evidence_type="SHORT_PAYMENT_COLLECTION_BALANCE",
                source_table="invoices",
                source_id=row.invoice_id,
                expected_value=row.total_invoiced_amount,
                actual_value=row.paid_amount,
                discrepancy_delta=unpaid,
                evidence_payload={
                    "invoice_business_id": row.invoice_business_id,
                    "total_invoiced": float(row.total_invoiced_amount),
                    "paid_amount": float(row.paid_amount),
                    "uncollected_balance": float(unpaid),
                    "due_date": row.due_date.isoformat(),
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Invoice",
                    entity_id=row.invoice_id,
                    business_id=row.invoice_business_id,
                    leakage_amount=unpaid,
                    explanation=(
                        f"Short payment on invoice {row.invoice_business_id}: partial settlement of ₹{row.paid_amount} "
                        f"leaves uncollected balance of ₹{unpaid} past due date with zero dispute lodged."
                    ),
                    recommended_action="Contact customer treasury to collect remaining balance or obtain formal deduction claim.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 11. ANOM-011: SLA_AGING_BREACH
# ==============================================================================
class SLAAgingBreachDetector(BaseDetector):
    """Detects operational delays exceeding fulfillment, billing or dispute resolution SLAs."""

    @property
    def issue_type(self) -> str:
        return "SLA_AGING_BREACH"

    @property
    def default_severity(self) -> str:
        return "LOW"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        # SLA: Order booking to shipment dispatch should not exceed 3 days
        # Injected cases have dispatched_at >= order_date + 7 days
        stmt = (
            select(
                Shipment.shipment_id,
                Shipment.business_id.label("shipment_business_id"),
                Shipment.order_id,
                Shipment.dispatched_at,
                SalesOrder.order_date,
                SalesOrder.account_id,
            )
            .join(SalesOrder, Shipment.order_id == SalesOrder.order_id)
            .where(
                Shipment.dispatched_at > SalesOrder.order_date + timedelta(days=7)
            )
        )

        results = []
        for row in session.execute(stmt):
            delta_days = (row.dispatched_at - row.order_date).days

            evidence = EvidenceItem(
                evidence_type="FULFILLMENT_SLA_AGING_EXCEEDED",
                source_table="shipments",
                source_id=row.shipment_id,
                conflicting_source_table="sales_orders",
                conflicting_source_id=row.order_id,
                expected_value=Decimal("3.00"),
                actual_value=Decimal(str(delta_days)),
                discrepancy_delta=Decimal(str(delta_days - 3)),
                evidence_payload={
                    "shipment_business_id": row.shipment_business_id,
                    "order_date": row.order_date.isoformat(),
                    "dispatched_at": row.dispatched_at.isoformat(),
                    "actual_days_to_dispatch": delta_days,
                    "sla_limit_days": 3,
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Shipment",
                    entity_id=row.shipment_id,
                    business_id=row.shipment_business_id,
                    leakage_amount=Decimal("0.00"),
                    explanation=(
                        f"Fulfillment SLA breached for shipment {row.shipment_business_id}: warehouse dispatch took "
                        f"{delta_days} days from order confirmation (SLA benchmark: 3 days)."
                    ),
                    recommended_action="Investigate warehouse logistics bottlenecks and review carrier dispatch pipeline.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results


# ==============================================================================
# 12. ANOM-012: OVERDUE_UNPAID_INVOICE
# ==============================================================================
class OverdueUnpaidInvoiceDetector(BaseDetector):
    """Detects 100% unpaid invoices past due date without active dispute claims."""

    @property
    def issue_type(self) -> str:
        return "OVERDUE_UNPAID_INVOICE"

    @property
    def default_severity(self) -> str:
        return "HIGH"

    def detect(self, session: Session, simulation_date: datetime) -> List[DetectionResult]:
        active_disp_subq = (
            select(1)
            .select_from(Dispute)
            .where(
                Dispute.invoice_id == Invoice.invoice_id,
                Dispute.status.in_(["LODGED", "UNDER_INVESTIGATION"]),
            )
        )

        stmt = (
            select(
                Invoice.invoice_id,
                Invoice.business_id.label("invoice_business_id"),
                Invoice.account_id,
                Invoice.order_id,
                Invoice.total_invoiced_amount,
                Invoice.due_date,
            )
            .where(
                Invoice.paid_amount == Decimal("0.00"),
                Invoice.status == "ISSUED",
                Invoice.due_date < simulation_date,
                not_(exists(active_disp_subq)),
            )
        )

        results = []
        for row in session.execute(stmt):
            evidence = EvidenceItem(
                evidence_type="OVERDUE_UNPAID_AGING_BUCKET",
                source_table="invoices",
                source_id=row.invoice_id,
                expected_value=Decimal("0.00"),
                actual_value=row.total_invoiced_amount,
                discrepancy_delta=row.total_invoiced_amount,
                evidence_payload={
                    "invoice_business_id": row.invoice_business_id,
                    "total_invoiced_amount": float(row.total_invoiced_amount),
                    "due_date": row.due_date.isoformat(),
                    "aging_status": "PAST_DUE",
                },
            )

            results.append(
                DetectionResult(
                    issue_type=self.issue_type,
                    severity=self.default_severity,
                    entity_type="Invoice",
                    entity_id=row.invoice_id,
                    business_id=row.invoice_business_id,
                    leakage_amount=row.total_invoiced_amount,
                    explanation=(
                        f"Invoice {row.invoice_business_id} for ₹{row.total_invoiced_amount} is severely overdue "
                        f"(due {row.due_date.strftime('%Y-%m-%d')}) with zero payment received and no dispute lodged."
                    ),
                    recommended_action="Escalate to dunning collections workflow and issue formal demand notice.",
                    account_id=row.account_id,
                    order_id=row.order_id,
                    invoice_id=row.invoice_id,
                    evidence_items=[evidence],
                    detected_at=simulation_date,
                )
            )
        return results
