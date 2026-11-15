"""
Lifecycle Status Event Generator.
Produces 80,000+ append-only immutable audit trail records for entity state transitions,
enforcing exact foreign key referential integrity on status_events table.
"""

from datetime import timedelta
from typing import List, Dict, Any

from app.generators.config import GeneratorConfig
from app.generators.id_utils import deterministic_uuid, format_event_id


def generate_status_events_data(
    config: GeneratorConfig,
    quotes: List[Dict[str, Any]],
    orders: List[Dict[str, Any]],
    shipments: List[Dict[str, Any]],
    invoices: List[Dict[str, Any]],
    payments: List[Dict[str, Any]],
    disputes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generates append-only StatusEvent audit records for all entity lifecycles.
    Enforces check constraint: exactly one FK is non-null.
    """
    events: List[Dict[str, Any]] = []
    evt_idx = 1

    # 1. Quote Events
    for q in quotes:
        created = q["created_at"]
        final_state = q["status"]

        # Initial Draft
        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "Quote",
            "quote_id": q["quote_id"],
            "order_id": None,
            "shipment_id": None,
            "invoice_id": None,
            "payment_id": None,
            "dispute_id": None,
            "business_id": q["business_id"],
            "previous_state": None,
            "new_state": "DRAFT",
            "event_timestamp": created,
            "actor_id": None,
            "reason": "Initial quote draft created",
        })

        # Submitted
        t1 = created + timedelta(hours=1)
        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "Quote",
            "quote_id": q["quote_id"],
            "order_id": None,
            "shipment_id": None,
            "invoice_id": None,
            "payment_id": None,
            "dispute_id": None,
            "business_id": q["business_id"],
            "previous_state": "DRAFT",
            "new_state": "SUBMITTED",
            "event_timestamp": t1,
            "actor_id": None,
            "reason": "Submitted for sales management approval",
        })

        if final_state in ("APPROVED", "ACCEPTED", "REJECTED", "EXPIRED"):
            t2 = t1 + timedelta(hours=2)
            evt_biz = format_event_id(evt_idx)
            evt_idx += 1
            events.append({
                "event_id": deterministic_uuid("StatusEvent", evt_biz),
                "entity_type": "Quote",
                "quote_id": q["quote_id"],
                "order_id": None,
                "shipment_id": None,
                "invoice_id": None,
                "payment_id": None,
                "dispute_id": None,
                "business_id": q["business_id"],
                "previous_state": "SUBMITTED",
                "new_state": "APPROVED",
                "event_timestamp": t2,
                "actor_id": None,
                "reason": "Commercial pricing terms approved",
            })

            if final_state != "APPROVED":
                t3 = t2 + timedelta(hours=4)
                evt_biz = format_event_id(evt_idx)
                evt_idx += 1
                events.append({
                    "event_id": deterministic_uuid("StatusEvent", evt_biz),
                    "entity_type": "Quote",
                    "quote_id": q["quote_id"],
                    "order_id": None,
                    "shipment_id": None,
                    "invoice_id": None,
                    "payment_id": None,
                    "dispute_id": None,
                    "business_id": q["business_id"],
                    "previous_state": "APPROVED",
                    "new_state": final_state,
                    "event_timestamp": t3,
                    "actor_id": None,
                    "reason": f"Customer response: {final_state}",
                })

    # 2. Sales Order Events
    for ord_row in orders:
        created = ord_row["created_at"]
        final_state = ord_row["status"]

        # Initial Draft -> Confirmed
        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "SalesOrder",
            "quote_id": None,
            "order_id": ord_row["order_id"],
            "shipment_id": None,
            "invoice_id": None,
            "payment_id": None,
            "dispute_id": None,
            "business_id": ord_row["business_id"],
            "previous_state": None,
            "new_state": "CONFIRMED",
            "event_timestamp": created,
            "actor_id": None,
            "reason": "Order booked from accepted quotation",
        })

        if final_state in ("IN_FULFILLMENT", "PARTIALLY_FULFILLED", "FULFILLED", "CLOSED"):
            t1 = created + timedelta(hours=4)
            evt_biz = format_event_id(evt_idx)
            evt_idx += 1
            events.append({
                "event_id": deterministic_uuid("StatusEvent", evt_biz),
                "entity_type": "SalesOrder",
                "quote_id": None,
                "order_id": ord_row["order_id"],
                "shipment_id": None,
                "invoice_id": None,
                "payment_id": None,
                "dispute_id": None,
                "business_id": ord_row["business_id"],
                "previous_state": "CONFIRMED",
                "new_state": "IN_FULFILLMENT",
                "event_timestamp": t1,
                "actor_id": None,
                "reason": "Released to warehouse for fulfillment",
            })

            if final_state in ("FULFILLED", "CLOSED"):
                t2 = t1 + timedelta(days=2)
                evt_biz = format_event_id(evt_idx)
                evt_idx += 1
                events.append({
                    "event_id": deterministic_uuid("StatusEvent", evt_biz),
                    "entity_type": "SalesOrder",
                    "quote_id": None,
                    "order_id": ord_row["order_id"],
                    "shipment_id": None,
                    "invoice_id": None,
                    "payment_id": None,
                    "dispute_id": None,
                    "business_id": ord_row["business_id"],
                    "previous_state": "IN_FULFILLMENT",
                    "new_state": "FULFILLED",
                    "event_timestamp": t2,
                    "actor_id": None,
                    "reason": "All ordered line items delivered",
                })

                if final_state == "CLOSED":
                    t3 = t2 + timedelta(days=5)
                    evt_biz = format_event_id(evt_idx)
                    evt_idx += 1
                    events.append({
                        "event_id": deterministic_uuid("StatusEvent", evt_biz),
                        "entity_type": "SalesOrder",
                        "quote_id": None,
                        "order_id": ord_row["order_id"],
                        "shipment_id": None,
                        "invoice_id": None,
                        "payment_id": None,
                        "dispute_id": None,
                        "business_id": ord_row["business_id"],
                        "previous_state": "FULFILLED",
                        "new_state": "CLOSED",
                        "event_timestamp": t3,
                        "actor_id": None,
                        "reason": "Order lifecycle concluded",
                    })

    # 3. Shipment Events
    for shp in shipments:
        disp = shp["dispatched_at"]
        final_state = shp["status"]

        # PENDING -> DISPATCHED
        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "Shipment",
            "quote_id": None,
            "order_id": None,
            "shipment_id": shp["shipment_id"],
            "invoice_id": None,
            "payment_id": None,
            "dispute_id": None,
            "business_id": shp["business_id"],
            "previous_state": None,
            "new_state": "DISPATCHED",
            "event_timestamp": disp,
            "actor_id": None,
            "reason": f"Dispatched via carrier {shp['carrier']}",
        })

        if final_state in ("IN_TRANSIT", "DELIVERED", "LOST", "RETURNED"):
            t1 = disp + timedelta(hours=12)
            evt_biz = format_event_id(evt_idx)
            evt_idx += 1
            events.append({
                "event_id": deterministic_uuid("StatusEvent", evt_biz),
                "entity_type": "Shipment",
                "quote_id": None,
                "order_id": None,
                "shipment_id": shp["shipment_id"],
                "invoice_id": None,
                "payment_id": None,
                "dispute_id": None,
                "business_id": shp["business_id"],
                "previous_state": "DISPATCHED",
                "new_state": "IN_TRANSIT",
                "event_timestamp": t1,
                "actor_id": None,
                "reason": "Carrier scan: parcel in transit to destination hub",
            })

            if final_state == "DELIVERED" and shp["delivered_at"]:
                evt_biz = format_event_id(evt_idx)
                evt_idx += 1
                events.append({
                    "event_id": deterministic_uuid("StatusEvent", evt_biz),
                    "entity_type": "Shipment",
                    "quote_id": None,
                    "order_id": None,
                    "shipment_id": shp["shipment_id"],
                    "invoice_id": None,
                    "payment_id": None,
                    "dispute_id": None,
                    "business_id": shp["business_id"],
                    "previous_state": "IN_TRANSIT",
                    "new_state": "DELIVERED",
                    "event_timestamp": shp["delivered_at"],
                    "actor_id": None,
                    "reason": "Proof of delivery signed by recipient",
                })

    # 4. Invoice Events
    for inv in invoices:
        issued = inv["issue_date"]
        final_state = inv["status"]

        # ISSUED
        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "Invoice",
            "quote_id": None,
            "order_id": None,
            "shipment_id": None,
            "invoice_id": inv["invoice_id"],
            "payment_id": None,
            "dispute_id": None,
            "business_id": inv["business_id"],
            "previous_state": None,
            "new_state": "ISSUED",
            "event_timestamp": issued,
            "actor_id": None,
            "reason": "Invoice published and delivered to customer",
        })

        if final_state in ("PARTIALLY_PAID", "PAID"):
            t1 = issued + timedelta(days=10)
            evt_biz = format_event_id(evt_idx)
            evt_idx += 1
            events.append({
                "event_id": deterministic_uuid("StatusEvent", evt_biz),
                "entity_type": "Invoice",
                "quote_id": None,
                "order_id": None,
                "shipment_id": None,
                "invoice_id": inv["invoice_id"],
                "payment_id": None,
                "dispute_id": None,
                "business_id": inv["business_id"],
                "previous_state": "ISSUED",
                "new_state": final_state,
                "event_timestamp": t1,
                "actor_id": None,
                "reason": f"Payment applied, invoice status updated to {final_state}",
            })

    # 5. Payment Events
    for pay in payments:
        p_date = pay["payment_date"]
        final_state = pay["status"]

        # RECEIVED
        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "Payment",
            "quote_id": None,
            "order_id": None,
            "shipment_id": None,
            "invoice_id": None,
            "payment_id": pay["payment_id"],
            "dispute_id": None,
            "business_id": pay["business_id"],
            "previous_state": None,
            "new_state": "RECEIVED",
            "event_timestamp": p_date,
            "actor_id": None,
            "reason": f"Cash settlement ingested via {pay['payment_method']}",
        })

        if final_state in ("PARTIALLY_ALLOCATED", "ALLOCATED"):
            t1 = p_date + timedelta(hours=2)
            evt_biz = format_event_id(evt_idx)
            evt_idx += 1
            events.append({
                "event_id": deterministic_uuid("StatusEvent", evt_biz),
                "entity_type": "Payment",
                "quote_id": None,
                "order_id": None,
                "shipment_id": None,
                "invoice_id": None,
                "payment_id": pay["payment_id"],
                "dispute_id": None,
                "business_id": pay["business_id"],
                "previous_state": "RECEIVED",
                "new_state": final_state,
                "event_timestamp": t1,
                "actor_id": None,
                "reason": f"Cash allocated to customer receivables ({final_state})",
            })

    # 6. Dispute Events
    for dsp in disputes:
        lodged = dsp["lodged_at"]
        final_state = dsp["status"]

        evt_biz = format_event_id(evt_idx)
        evt_idx += 1
        events.append({
            "event_id": deterministic_uuid("StatusEvent", evt_biz),
            "entity_type": "Dispute",
            "quote_id": None,
            "order_id": None,
            "shipment_id": None,
            "invoice_id": None,
            "payment_id": None,
            "dispute_id": dsp["dispute_id"],
            "business_id": dsp["business_id"],
            "previous_state": None,
            "new_state": "LODGED",
            "event_timestamp": lodged,
            "actor_id": None,
            "reason": f"Customer claim opened: {dsp['dispute_reason']}",
        })

        if final_state in ("RESOLVED_ACCEPTED", "RESOLVED_REJECTED") and dsp["resolved_at"]:
            evt_biz = format_event_id(evt_idx)
            evt_idx += 1
            events.append({
                "event_id": deterministic_uuid("StatusEvent", evt_biz),
                "entity_type": "Dispute",
                "quote_id": None,
                "order_id": None,
                "shipment_id": None,
                "invoice_id": None,
                "payment_id": None,
                "dispute_id": dsp["dispute_id"],
                "business_id": dsp["business_id"],
                "previous_state": "LODGED",
                "new_state": final_state,
                "event_timestamp": dsp["resolved_at"],
                "actor_id": None,
                "reason": f"Dispute resolution reached: {final_state}",
            })

    return events
