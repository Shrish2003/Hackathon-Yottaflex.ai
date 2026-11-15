"""
Sales Order and Order Line Generator.
Converts accepted quotes into sales orders with 1:1 order line mappings.
"""

import random
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from app.generators.config import GeneratorConfig
from app.generators.id_utils import deterministic_uuid, format_order_id


def generate_orders_data(
    config: GeneratorConfig,
    quotes: List[Dict[str, Any]],
    quote_lines: List[Dict[str, Any]],
    rng: random.Random,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Sales Orders and Order Lines from ACCEPTED quotes.
    Returns: (orders_data, order_lines_data)
    """
    # Group quote lines by quote_id
    ql_by_quote: Dict[Any, List[Dict[str, Any]]] = {}
    for ql in quote_lines:
        ql_by_quote.setdefault(ql["quote_id"], []).append(ql)

    orders: List[Dict[str, Any]] = []
    order_lines: List[Dict[str, Any]] = []

    # Filter accepted quotes
    accepted_quotes = [q for q in quotes if q["status"] == "ACCEPTED"][: config.num_orders]

    for ord_idx, quote in enumerate(accepted_quotes, start=1):
        so_biz_id = format_order_id(ord_idx)
        so_id = deterministic_uuid("SalesOrder", so_biz_id)

        # Order confirmed 1 to 3 days after quote creation
        order_date = quote["created_at"] + timedelta(
            days=rng.randint(1, 3), hours=rng.randint(1, 12)
        )

        # Determine order lifecycle status
        # Most orders progress to FULFILLED or CLOSED; some remain IN_FULFILLMENT or CONFIRMED
        if ord_idx <= int(config.num_orders * 0.65):
            status = "CLOSED"
        elif ord_idx <= int(config.num_orders * 0.85):
            status = "FULFILLED"
        elif ord_idx <= int(config.num_orders * 0.95):
            status = "IN_FULFILLMENT"
        else:
            status = "CONFIRMED"

        q_lines = ql_by_quote.get(quote["quote_id"], [])
        total_order_val = Decimal("0.00")

        for line_no, ql in enumerate(q_lines, start=1):
            ol_biz_id = f"{so_biz_id}-L{line_no:02d}"
            ol_id = deterministic_uuid("OrderLine", ol_biz_id)

            ordered_qty = ql["quantity"]
            # Effective net unit price = line_net_amount / quantity
            unit_price = (ql["line_net_amount"] / ordered_qty).quantize(Decimal("0.01"))
            line_total = (ordered_qty * unit_price).quantize(Decimal("0.01"))
            total_order_val += line_total

            line_status = "FULFILLED" if status in ("FULFILLED", "CLOSED") else "PENDING"

            order_lines.append({
                "order_line_id": ol_id,
                "order_id": so_id,
                "quote_line_id": ql["quote_line_id"],
                "line_number": line_no,
                "product_sku": ql["product_sku"],
                "ordered_quantity": ordered_qty,
                "unit_price": unit_price,
                "line_total_amount": line_total,
                "status": line_status,
                "created_at": order_date,
            })

        orders.append({
            "order_id": so_id,
            "business_id": so_biz_id,
            "quote_id": quote["quote_id"],
            "account_id": quote["account_id"],
            "status": status,
            "total_order_value": total_order_val,
            "currency": "INR",
            "order_date": order_date,
            "created_at": order_date,
            "updated_at": order_date + timedelta(days=2),
        })

    return orders, order_lines
