"""
Billing Generator: Invoices and Invoice Lines.
Generates invoices for delivered shipments and fulfilled order deliverables.
"""

import random
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from app.generators.config import GeneratorConfig
from app.generators.id_utils import deterministic_uuid, format_invoice_id


def generate_billing_data(
    config: GeneratorConfig,
    orders: List[Dict[str, Any]],
    order_lines: List[Dict[str, Any]],
    shipments: List[Dict[str, Any]],
    shipment_lines: List[Dict[str, Any]],
    accounts: List[Dict[str, Any]],
    rng: random.Random,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Invoices and Invoice Lines mapping to delivered shipments.
    Returns: (invoices_data, invoice_lines_data)
    """
    # Quick lookup maps
    order_map = {o["order_id"]: o for o in orders}
    ol_map = {ol["order_line_id"]: ol for ol in order_lines}
    acc_map = {a["account_id"]: a for a in accounts}

    # Group shipment lines by shipment_id
    sl_by_shipment: Dict[Any, List[Dict[str, Any]]] = {}
    for sl in shipment_lines:
        sl_by_shipment.setdefault(sl["shipment_id"], []).append(sl)

    invoices: List[Dict[str, Any]] = []
    invoice_lines: List[Dict[str, Any]] = []

    delivered_shipments = [s for s in shipments if s["status"] == "DELIVERED"]
    inv_idx = 1

    # 1. Generate one invoice per delivered shipment
    for shp in delivered_shipments:
        if inv_idx > config.num_invoices:
            break

        order = order_map.get(shp["order_id"])
        if not order:
            continue

        account = acc_map.get(order["account_id"])
        terms_str = account["payment_terms"] if account else "NET30"
        terms_days = 30
        if "15" in terms_str:
            terms_days = 15
        elif "60" in terms_str:
            terms_days = 60
        elif "45" in terms_str:
            terms_days = 45

        inv_biz_id = format_invoice_id(inv_idx)
        inv_id = deterministic_uuid("Invoice", inv_biz_id)
        inv_idx += 1

        deliv_date = shp["delivered_at"] or shp["dispatched_at"]
        issue_date = deliv_date + timedelta(days=rng.randint(1, 2), hours=rng.randint(1, 6))
        due_date = issue_date + timedelta(days=terms_days)

        s_lines = sl_by_shipment.get(shp["shipment_id"], [])
        inv_total = Decimal("0.00")

        for l_no, sl in enumerate(s_lines, start=1):
            il_biz_id = f"{inv_biz_id}-L{l_no:02d}"
            il_id = deterministic_uuid("InvoiceLine", il_biz_id)

            ol = ol_map.get(sl["order_line_id"])
            if not ol:
                continue

            inv_qty = sl["shipped_quantity"]
            unit_price = ol["unit_price"]
            line_tot = (inv_qty * unit_price).quantize(Decimal("0.01"))
            inv_total += line_tot

            invoice_lines.append({
                "invoice_line_id": il_id,
                "invoice_id": inv_id,
                "order_line_id": ol["order_line_id"],
                "shipment_line_id": sl["shipment_line_id"],
                "line_number": l_no,
                "invoiced_quantity": inv_qty,
                "unit_price": unit_price,
                "line_total_amount": line_tot,
            })

        invoices.append({
            "invoice_id": inv_id,
            "business_id": inv_biz_id,
            "order_id": order["order_id"],
            "account_id": order["account_id"],
            "shipment_id": shp["shipment_id"],
            "status": "ISSUED",  # Will be adjusted to PAID / PARTIALLY_PAID during payment allocation
            "total_invoiced_amount": inv_total,
            "paid_amount": Decimal("0.00"),
            "outstanding_balance": inv_total,
            "currency": "INR",
            "issue_date": issue_date,
            "due_date": due_date,
            "created_at": issue_date,
            "updated_at": issue_date,
        })

    # 2. If target invoices > delivered shipments, generate milestone / consolidated invoices
    # for eligible fulfilled orders until num_invoices is reached
    extra_needed = config.num_invoices - len(invoices)
    if extra_needed > 0:
        for ord_extra in orders[:extra_needed]:
            if inv_idx > config.num_invoices:
                break

            account = acc_map.get(ord_extra["account_id"])
            inv_biz_id = format_invoice_id(inv_idx)
            inv_id = deterministic_uuid("Invoice", inv_biz_id)
            inv_idx += 1

            issue_date = ord_extra["order_date"] + timedelta(days=rng.randint(3, 7))
            due_date = issue_date + timedelta(days=30)

            # Bill first line item
            lines = [ol for ol in order_lines if ol["order_id"] == ord_extra["order_id"]]
            if not lines:
                continue

            inv_total = Decimal("0.00")
            for l_no, ol in enumerate(lines[:1], start=1):
                il_biz_id = f"{inv_biz_id}-L{l_no:02d}"
                il_id = deterministic_uuid("InvoiceLine", il_biz_id)
                inv_qty = ol["ordered_quantity"]
                unit_price = ol["unit_price"]
                line_tot = (inv_qty * unit_price).quantize(Decimal("0.01"))
                inv_total += line_tot

                invoice_lines.append({
                    "invoice_line_id": il_id,
                    "invoice_id": inv_id,
                    "order_line_id": ol["order_line_id"],
                    "shipment_line_id": None,
                    "line_number": l_no,
                    "invoiced_quantity": inv_qty,
                    "unit_price": unit_price,
                    "line_total_amount": line_tot,
                })

            invoices.append({
                "invoice_id": inv_id,
                "business_id": inv_biz_id,
                "order_id": ord_extra["order_id"],
                "account_id": ord_extra["account_id"],
                "shipment_id": None,
                "status": "ISSUED",
                "total_invoiced_amount": inv_total,
                "paid_amount": Decimal("0.00"),
                "outstanding_balance": inv_total,
                "currency": "INR",
                "issue_date": issue_date,
                "due_date": due_date,
                "created_at": issue_date,
                "updated_at": issue_date,
            })

    return invoices, invoice_lines
