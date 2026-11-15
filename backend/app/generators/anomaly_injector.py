"""
Controlled Anomaly Injection Engine.
Injects 12 documented anomaly types across clean baseline O2C records and creates
physically isolated ground_truth_anomalies records for benchmark evaluation.
"""

import json
import random
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from app.generators.config import GeneratorConfig
from app.generators.id_utils import (
    deterministic_uuid,
    format_anomaly_id,
    format_invoice_id,
    format_allocation_id,
    format_event_id,
)


def inject_anomalies(
    config: GeneratorConfig,
    quotes: List[Dict[str, Any]],
    orders: List[Dict[str, Any]],
    order_lines: List[Dict[str, Any]],
    shipments: List[Dict[str, Any]],
    shipment_lines: List[Dict[str, Any]],
    invoices: List[Dict[str, Any]],
    invoice_lines: List[Dict[str, Any]],
    payments: List[Dict[str, Any]],
    payment_allocations: List[Dict[str, Any]],
    disputes: List[Dict[str, Any]],
    status_events: List[Dict[str, Any]],
    rng: random.Random,
) -> List[Dict[str, Any]]:
    """
    Injects 12 controlled anomaly types into baseline operational records.
    Returns: ground_truth_records list to be inserted into ground_truth_anomalies table.
    """
    ground_truth: List[Dict[str, Any]] = []
    anom_idx = 1

    # Number of anomaly instances per category scales with profile
    count_per_type = max(3, int(35 * config.scale))

    # Lookup helpers
    inv_line_map = {}
    for il in invoice_lines:
        inv_line_map.setdefault(il["invoice_id"], []).append(il)

    ord_line_map = {ol["order_line_id"]: ol for ol in order_lines}
    shp_line_map = {sl["shipment_line_id"]: sl for sl in shipment_lines}
    inv_map = {i["invoice_id"]: i for i in invoices}
    ord_map = {o["order_id"]: o for o in orders}

    # --------------------------------------------------------------------------
    # 1. ANOM-001: OVERBILLING_QUANTITY
    # Invoiced quantity exceeds shipped/delivered quantity
    # --------------------------------------------------------------------------
    candidate_invs = [i for i in invoices if i["shipment_id"] is not None]
    chosen_invs_q = candidate_invs[:count_per_type]

    for inv in chosen_invs_q:
        lines = inv_line_map.get(inv["invoice_id"], [])
        if not lines:
            continue
        target_line = lines[0]
        sl = shp_line_map.get(target_line["shipment_line_id"])
        delivered_qty = sl["shipped_quantity"] if sl else target_line["invoiced_quantity"]

        # Inflate invoiced quantity by +3 to +10 units
        qty_inflation = Decimal(rng.randint(3, 10))
        new_invoiced_qty = delivered_qty + qty_inflation
        unit_price = target_line["unit_price"]

        old_line_total = target_line["line_total_amount"]
        new_line_total = (new_invoiced_qty * unit_price).quantize(Decimal("0.01"))
        leakage = new_line_total - old_line_total

        # Apply change to operational record
        target_line["invoiced_quantity"] = new_invoiced_qty
        target_line["line_total_amount"] = new_line_total
        inv["total_invoiced_amount"] = (inv["total_invoiced_amount"] + leakage).quantize(Decimal("0.01"))
        inv["outstanding_balance"] = (inv["outstanding_balance"] + leakage).quantize(Decimal("0.01"))

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "OVERBILLING_QUANTITY",
            "entity_type": "Invoice",
            "entity_id": inv["invoice_id"],
            "business_id": inv["business_id"],
            "severity": "HIGH",
            "leakage_amount": leakage,
            "description": (
                f"Invoice line billed {new_invoiced_qty} units but only {delivered_qty} units "
                f"were delivered. Quantity delta: +{qty_inflation} units."
            ),
            "details": json.dumps({
                "line_id": str(target_line["invoice_line_id"]),
                "delivered_quantity": float(delivered_qty),
                "invoiced_quantity": float(new_invoiced_qty),
                "unit_price": float(unit_price),
                "leakage_amount": float(leakage),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 2. ANOM-002: OVERBILLING_AMOUNT
    # Invoiced unit price exceeds contracted order unit price
    # --------------------------------------------------------------------------
    chosen_invs_amt = candidate_invs[count_per_type : count_per_type * 2]
    for inv in chosen_invs_amt:
        lines = inv_line_map.get(inv["invoice_id"], [])
        if not lines:
            continue
        target_line = lines[0]
        ol = ord_line_map.get(target_line["order_line_id"])
        contract_price = ol["unit_price"] if ol else target_line["unit_price"]

        # Inflate unit price by 15% - 25%
        price_delta = (contract_price * Decimal("0.20")).quantize(Decimal("0.01"))
        new_unit_price = contract_price + price_delta
        invoiced_qty = target_line["invoiced_quantity"]

        old_line_total = target_line["line_total_amount"]
        new_line_total = (invoiced_qty * new_unit_price).quantize(Decimal("0.01"))
        leakage = new_line_total - old_line_total

        # Apply change to operational record
        target_line["unit_price"] = new_unit_price
        target_line["line_total_amount"] = new_line_total
        inv["total_invoiced_amount"] = (inv["total_invoiced_amount"] + leakage).quantize(Decimal("0.01"))
        inv["outstanding_balance"] = (inv["outstanding_balance"] + leakage).quantize(Decimal("0.01"))

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "OVERBILLING_AMOUNT",
            "entity_type": "Invoice",
            "entity_id": inv["invoice_id"],
            "business_id": inv["business_id"],
            "severity": "HIGH",
            "leakage_amount": leakage,
            "description": (
                f"Invoice unit price ₹{new_unit_price} exceeds contracted sales order unit price "
                f"₹{contract_price}. Unit price discrepancy: +₹{price_delta}."
            ),
            "details": json.dumps({
                "line_id": str(target_line["invoice_line_id"]),
                "contract_unit_price": float(contract_price),
                "invoiced_unit_price": float(new_unit_price),
                "invoiced_quantity": float(invoiced_qty),
                "leakage_amount": float(leakage),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 3. ANOM-003: UNDERBILLING
    # Invoiced unit price lower than contracted price (revenue leakage / margin loss)
    # --------------------------------------------------------------------------
    chosen_invs_under = candidate_invs[count_per_type * 2 : count_per_type * 3]
    for inv in chosen_invs_under:
        lines = inv_line_map.get(inv["invoice_id"], [])
        if not lines:
            continue
        target_line = lines[0]
        ol = ord_line_map.get(target_line["order_line_id"])
        contract_price = ol["unit_price"] if ol else target_line["unit_price"]

        # Discount unit price by 20%
        price_drop = (contract_price * Decimal("0.20")).quantize(Decimal("0.01"))
        new_unit_price = max(Decimal("10.00"), contract_price - price_drop)
        invoiced_qty = target_line["invoiced_quantity"]

        leakage = (price_drop * invoiced_qty).quantize(Decimal("0.01"))
        old_line_total = target_line["line_total_amount"]
        new_line_total = (invoiced_qty * new_unit_price).quantize(Decimal("0.01"))

        # Apply change to operational record
        target_line["unit_price"] = new_unit_price
        target_line["line_total_amount"] = new_line_total
        inv["total_invoiced_amount"] = (inv["total_invoiced_amount"] - leakage).quantize(Decimal("0.01"))
        inv["outstanding_balance"] = max(Decimal("0.00"), inv["outstanding_balance"] - leakage).quantize(Decimal("0.01"))

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "UNDERBILLING",
            "entity_type": "Invoice",
            "entity_id": inv["invoice_id"],
            "business_id": inv["business_id"],
            "severity": "MEDIUM",
            "leakage_amount": leakage,
            "description": (
                f"Invoice unit price ₹{new_unit_price} is lower than contracted sales order unit price "
                f"₹{contract_price}. Unbilled margin erosion: ₹{leakage}."
            ),
            "details": json.dumps({
                "line_id": str(target_line["invoice_line_id"]),
                "contract_unit_price": float(contract_price),
                "invoiced_unit_price": float(new_unit_price),
                "invoiced_quantity": float(invoiced_qty),
                "leakage_amount": float(leakage),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 4. ANOM-004: DUPLICATE_INVOICE
    # Multiple distinct invoices generated for the exact same order lines
    # --------------------------------------------------------------------------
    chosen_invs_dup = invoices[count_per_type * 3 : count_per_type * 4]
    dup_counter = len(invoices) + 1

    for orig_inv in chosen_invs_dup:
        dup_biz = format_invoice_id(dup_counter)
        dup_id = deterministic_uuid("Invoice", dup_biz)
        dup_counter += 1

        dup_total = orig_inv["total_invoiced_amount"]
        dup_invoice = {
            "invoice_id": dup_id,
            "business_id": dup_biz,
            "order_id": orig_inv["order_id"],
            "account_id": orig_inv["account_id"],
            "shipment_id": orig_inv["shipment_id"],
            "status": "ISSUED",
            "total_invoiced_amount": dup_total,
            "paid_amount": Decimal("0.00"),
            "outstanding_balance": dup_total,
            "currency": "INR",
            "issue_date": orig_inv["issue_date"] + timedelta(days=1),
            "due_date": orig_inv["due_date"] + timedelta(days=1),
            "created_at": orig_inv["issue_date"] + timedelta(days=1),
            "updated_at": orig_inv["issue_date"] + timedelta(days=1),
        }
        invoices.append(dup_invoice)

        # Duplicate the invoice lines
        orig_lines = inv_line_map.get(orig_inv["invoice_id"], [])
        for l_no, ol_line in enumerate(orig_lines, start=1):
            dup_line_biz = f"{dup_biz}-L{l_no:02d}"
            invoice_lines.append({
                "invoice_line_id": deterministic_uuid("InvoiceLine", dup_line_biz),
                "invoice_id": dup_id,
                "order_line_id": ol_line["order_line_id"],
                "shipment_line_id": ol_line["shipment_line_id"],
                "line_number": l_no,
                "invoiced_quantity": ol_line["invoiced_quantity"],
                "unit_price": ol_line["unit_price"],
                "line_total_amount": ol_line["line_total_amount"],
            })

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "DUPLICATE_INVOICE",
            "entity_type": "Invoice",
            "entity_id": dup_id,
            "business_id": dup_biz,
            "severity": "CRITICAL",
            "leakage_amount": dup_total,
            "description": (
                f"Duplicate invoice {dup_biz} generated for sales order "
                f"{orig_inv['order_id']}, replicating items from {orig_inv['business_id']}."
            ),
            "details": json.dumps({
                "original_invoice_id": str(orig_inv["invoice_id"]),
                "original_business_id": orig_inv["business_id"],
                "duplicate_business_id": dup_biz,
                "leakage_amount": float(dup_total),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 5. ANOM-005: DUPLICATE_PAYMENT_ALLOCATION
    # Exact same payment allocated twice to the same invoice
    # --------------------------------------------------------------------------
    chosen_allocs = payment_allocations[:count_per_type]
    alloc_counter = len(payment_allocations) + 1

    for orig_alloc in chosen_allocs:
        dup_alc_biz = format_allocation_id(alloc_counter)
        dup_alc_id = deterministic_uuid("PaymentAllocation", dup_alc_biz)
        alloc_counter += 1

        allocated_amt = orig_alloc["allocated_amount"]
        dup_alloc = {
            "allocation_id": dup_alc_id,
            "payment_id": orig_alloc["payment_id"],
            "invoice_id": orig_alloc["invoice_id"],
            "allocated_amount": allocated_amt,
            "allocation_date": orig_alloc["allocation_date"],
            "status": "ACTIVE",
            "created_at": orig_alloc["created_at"],
        }
        payment_allocations.append(dup_alloc)

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "DUPLICATE_PAYMENT_ALLOCATION",
            "entity_type": "PaymentAllocation",
            "entity_id": dup_alc_id,
            "business_id": dup_alc_biz,
            "severity": "HIGH",
            "leakage_amount": allocated_amt,
            "description": (
                f"Duplicate payment allocation {dup_alc_biz} for payment "
                f"{orig_alloc['payment_id']} on invoice {orig_alloc['invoice_id']}."
            ),
            "details": json.dumps({
                "original_allocation_id": str(orig_alloc["allocation_id"]),
                "payment_id": str(orig_alloc["payment_id"]),
                "invoice_id": str(orig_alloc["invoice_id"]),
                "duplicated_amount": float(allocated_amt),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 6. ANOM-006: EXCESSIVE_PAYMENT_ALLOCATION
    # Cumulative allocated amounts exceed received cash
    # --------------------------------------------------------------------------
    chosen_pays = [p for p in payments if p["status"] == "ALLOCATED"][:count_per_type]
    for pay in chosen_pays:
        # Find allocations for this payment
        allocs = [a for a in payment_allocations if a["payment_id"] == pay["payment_id"]]
        if not allocs:
            continue
        target_a = allocs[0]

        # Over-allocate by ₹25,000
        excess = Decimal("25000.00")
        target_a["allocated_amount"] = (target_a["allocated_amount"] + excess).quantize(Decimal("0.01"))
        # Do not increase pay["amount_received"] to trigger the check rule
        pay["amount_allocated"] = (pay["amount_allocated"] + excess).quantize(Decimal("0.01"))

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "EXCESSIVE_PAYMENT_ALLOCATION",
            "entity_type": "Payment",
            "entity_id": pay["payment_id"],
            "business_id": pay["business_id"],
            "severity": "HIGH",
            "leakage_amount": excess,
            "description": (
                f"Cumulative allocation for payment {pay['business_id']} exceeds "
                f"amount received (₹{pay['amount_received']}) by ₹{excess}."
            ),
            "details": json.dumps({
                "payment_business_id": pay["business_id"],
                "amount_received": float(pay["amount_received"]),
                "total_allocated": float(pay["amount_allocated"]),
                "excess_amount": float(excess),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 7. ANOM-007: PREMATURE_ORDER_CLOSURE
    # Order marked CLOSED while invoice remains unpaid
    # --------------------------------------------------------------------------
    # Find orders that have unpaid or partially paid invoices
    orders_with_unpaid_inv = []
    for inv in invoices:
        if inv["outstanding_balance"] > Decimal("1000.00") and inv["order_id"] in ord_map:
            orders_with_unpaid_inv.append((ord_map[inv["order_id"]], inv))

    chosen_premature = orders_with_unpaid_inv[:count_per_type]
    for order, inv in chosen_premature:
        order["status"] = "CLOSED"
        unpaid = inv["outstanding_balance"]

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "PREMATURE_ORDER_CLOSURE",
            "entity_type": "SalesOrder",
            "entity_id": order["order_id"],
            "business_id": order["business_id"],
            "severity": "CRITICAL",
            "leakage_amount": unpaid,
            "description": (
                f"Sales Order {order['business_id']} marked CLOSED while invoice "
                f"{inv['business_id']} has outstanding collectible balance ₹{unpaid}."
            ),
            "details": json.dumps({
                "order_business_id": order["business_id"],
                "unpaid_invoice_business_id": inv["business_id"],
                "outstanding_balance": float(unpaid),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 8. ANOM-008: INVALID_STATUS_TRANSITION
    # Illegal lifecycle hop in status_events (e.g. SalesOrder jumping directly from DRAFT to CLOSED)
    # --------------------------------------------------------------------------
    chosen_orders_transit = orders[count_per_type * 2 : count_per_type * 3]
    for order in chosen_orders_transit:
        evt_biz = format_event_id(len(status_events) + 1)
        evt_id = deterministic_uuid("StatusEvent", evt_biz)

        illegal_event = {
            "event_id": evt_id,
            "entity_type": "SalesOrder",
            "quote_id": None,
            "order_id": order["order_id"],
            "shipment_id": None,
            "invoice_id": None,
            "payment_id": None,
            "dispute_id": None,
            "business_id": order["business_id"],
            "previous_state": "DRAFT",
            "new_state": "CLOSED",  # Illegal direct jump skipping CONFIRMED, IN_FULFILLMENT, FULFILLED
            "event_timestamp": order["order_date"] + timedelta(minutes=15),
            "actor_id": None,
            "reason": "ILLEGAL_JUMP: direct draft to closed transition",
        }
        status_events.append(illegal_event)

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "INVALID_STATUS_TRANSITION",
            "entity_type": "StatusEvent",
            "entity_id": evt_id,
            "business_id": order["business_id"],
            "severity": "MEDIUM",
            "leakage_amount": Decimal("0.00"),
            "description": (
                f"Invalid lifecycle transition detected for Sales Order {order['business_id']}: "
                f"direct leap from DRAFT to CLOSED without intermediate fulfillment."
            ),
            "details": json.dumps({
                "event_id": str(evt_id),
                "business_id": order["business_id"],
                "previous_state": "DRAFT",
                "new_state": "CLOSED",
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 9. ANOM-009: DISPUTE_AR_DISCONNECT
    # Active dispute (LODGED/UNDER_INVESTIGATION) not reflected or isolated in receivables
    # --------------------------------------------------------------------------
    active_disputes = [d for d in disputes if d["status"] in ("LODGED", "UNDER_INVESTIGATION")][:count_per_type]
    for dsp in active_disputes:
        target_inv = inv_map.get(dsp["invoice_id"])
        if not target_inv:
            continue

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "DISPUTE_AR_DISCONNECT",
            "entity_type": "Dispute",
            "entity_id": dsp["dispute_id"],
            "business_id": dsp["business_id"],
            "severity": "HIGH",
            "leakage_amount": dsp["disputed_amount"],
            "description": (
                f"Active dispute {dsp['business_id']} (status: {dsp['status']}) on invoice "
                f"{target_inv['business_id']} has disputed balance ₹{dsp['disputed_amount']} "
                f"unisolated from collections aging."
            ),
            "details": json.dumps({
                "dispute_business_id": dsp["business_id"],
                "invoice_business_id": target_inv["business_id"],
                "disputed_amount": float(dsp["disputed_amount"]),
                "dispute_status": dsp["status"],
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 10. ANOM-010: SHORT_PAYMENT
    # Invoice partially paid, past due date, zero disputes and zero credit adjustments
    # --------------------------------------------------------------------------
    short_pay_candidates = [
        inv for inv in invoices
        if inv["due_date"] < config.simulation_date
    ][count_per_type * 4 : count_per_type * 5]

    for inv in short_pay_candidates:
        total_val = inv["total_invoiced_amount"]
        partial_paid = (total_val * Decimal("0.70")).quantize(Decimal("0.01"))
        unpaid = total_val - partial_paid
        inv["paid_amount"] = partial_paid
        inv["outstanding_balance"] = unpaid
        inv["status"] = "PARTIALLY_PAID"

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "SHORT_PAYMENT",
            "entity_type": "Invoice",
            "entity_id": inv["invoice_id"],
            "business_id": inv["business_id"],
            "severity": "MEDIUM",
            "leakage_amount": unpaid,
            "description": (
                f"Short payment detected on invoice {inv['business_id']}: partial cash received (₹{partial_paid}), "
                f"collectible balance ₹{unpaid} remains past due date with zero dispute lodged."
            ),
            "details": json.dumps({
                "invoice_business_id": inv["business_id"],
                "total_invoiced": float(total_val),
                "paid_amount": float(partial_paid),
                "outstanding_balance": float(unpaid),
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 11. ANOM-011: SLA_AGING_BREACH
    # Operational timeline delay exceeding agreed SLA threshold
    # --------------------------------------------------------------------------
    chosen_sla_shps = shipments[count_per_type : count_per_type * 2]
    for shp in chosen_sla_shps:
        order = ord_map.get(shp["order_id"])
        if not order:
            continue
        # Artificial breach: dispatch occurred 14 days after order date (SLA is 3 days)
        breached_dispatch = order["order_date"] + timedelta(days=14)
        shp["dispatched_at"] = breached_dispatch
        if shp["delivered_at"]:
            shp["delivered_at"] = breached_dispatch + timedelta(days=2)

        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "SLA_AGING_BREACH",
            "entity_type": "Shipment",
            "entity_id": shp["shipment_id"],
            "business_id": shp["business_id"],
            "severity": "LOW",
            "leakage_amount": Decimal("0.00"),
            "description": (
                f"Fulfillment SLA breached for shipment {shp['business_id']}: dispatch took "
                f"14 days from order booking, exceeding the 3-day SLA threshold."
            ),
            "details": json.dumps({
                "shipment_business_id": shp["business_id"],
                "order_business_id": order["business_id"],
                "days_to_dispatch": 14,
                "sla_threshold_days": 3,
            }),
            "injected_at": config.simulation_date,
        })

    # --------------------------------------------------------------------------
    # 12. ANOM-012: OVERDUE_UNPAID_INVOICE
    # 100% unpaid invoice past due date with zero disputes
    # --------------------------------------------------------------------------
    unpaid_invs = [
        inv for inv in invoices
        if inv["status"] == "ISSUED" and inv["paid_amount"] == Decimal("0.00") and inv["due_date"] < config.simulation_date
    ][:count_per_type]

    for inv in unpaid_invs:
        total_val = inv["total_invoiced_amount"]
        anm_biz = format_anomaly_id(anom_idx)
        anom_idx += 1
        ground_truth.append({
            "anomaly_id": deterministic_uuid("GroundTruthAnomaly", anm_biz),
            "issue_type": "OVERDUE_UNPAID_INVOICE",
            "entity_type": "Invoice",
            "entity_id": inv["invoice_id"],
            "business_id": inv["business_id"],
            "severity": "HIGH",
            "leakage_amount": total_val,
            "description": (
                f"Invoice {inv['business_id']} for ₹{total_val} is severely overdue (due "
                f"{inv['due_date'].strftime('%Y-%m-%d')}) with zero cash collections."
            ),
            "details": json.dumps({
                "invoice_business_id": inv["business_id"],
                "total_invoiced_amount": float(total_val),
                "due_date": inv["due_date"].isoformat(),
            }),
            "injected_at": config.simulation_date,
        })

    return ground_truth
