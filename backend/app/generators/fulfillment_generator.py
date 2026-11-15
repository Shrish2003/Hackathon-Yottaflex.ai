"""
Fulfillment Generator: Shipments and Shipment Lines.
Generates single and partial shipments against Sales Orders.
"""

import random
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from app.generators.config import GeneratorConfig
from app.generators.id_utils import deterministic_uuid, format_shipment_id

CARRIERS = ["BLUE_DART", "DELHIVERY", "FEDEX", "DHL", "DTDC"]


def generate_shipments_data(
    config: GeneratorConfig,
    orders: List[Dict[str, Any]],
    order_lines: List[Dict[str, Any]],
    rng: random.Random,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Shipments and Shipment Lines for confirmed/fulfilled orders.
    Supports partial fulfillment where certain orders split into multiple shipments.
    Returns: (shipments_data, shipment_lines_data)
    """
    # Group order lines by order_id
    ol_by_order: Dict[Any, List[Dict[str, Any]]] = {}
    for ol in order_lines:
        ol_by_order.setdefault(ol["order_id"], []).append(ol)

    shipments: List[Dict[str, Any]] = []
    shipment_lines: List[Dict[str, Any]] = []

    # Filter orders eligible for fulfillment (exclude purely CONFIRMED that haven't started dispatch)
    fulfillable_orders = [o for o in orders if o["status"] != "CONFIRMED"]
    if not fulfillable_orders:
        fulfillable_orders = orders

    shp_idx = 1
    carrier_idx = 0

    # How many split shipments do we need to reach config.num_shipments?
    # Target total shipments = config.num_shipments
    # We iterate through orders, assigning 1 shipment to each, and for some orders a 2nd partial shipment
    extra_shipments_needed = max(0, config.num_shipments - len(fulfillable_orders))

    for ord_i, order in enumerate(fulfillable_orders):
        if shp_idx > config.num_shipments:
            break

        lines = ol_by_order.get(order["order_id"], [])
        if not lines:
            continue

        carrier = CARRIERS[carrier_idx % len(CARRIERS)]
        carrier_idx += 1

        # Check if this order gets split into two partial shipments
        is_split = (ord_i < extra_shipments_needed) and (shp_idx + 1 <= config.num_shipments)

        # 1st Shipment
        shp_biz_id = format_shipment_id(shp_idx)
        shp_id = deterministic_uuid("Shipment", shp_biz_id)
        shp_idx += 1

        dispatch_time = order["order_date"] + timedelta(
            days=rng.randint(1, 3), hours=rng.randint(1, 10)
        )
        deliver_time = dispatch_time + timedelta(
            days=rng.randint(1, 4), hours=rng.randint(1, 8)
        )

        status = "DELIVERED"
        if order["status"] == "IN_FULFILLMENT" and ord_i > len(fulfillable_orders) * 0.9:
            status = rng.choice(["IN_TRANSIT", "DISPATCHED"])
            deliver_time = None

        shipments.append({
            "shipment_id": shp_id,
            "business_id": shp_biz_id,
            "order_id": order["order_id"],
            "carrier": carrier,
            "tracking_number": f"TRK-{carrier[:3]}-{shp_biz_id[-8:]}",
            "status": status,
            "dispatched_at": dispatch_time,
            "delivered_at": deliver_time,
            "created_at": dispatch_time,
            "updated_at": deliver_time or dispatch_time,
        })

        if not is_split:
            # 100% of quantity shipped in this shipment
            for l_no, ol in enumerate(lines, start=1):
                sl_biz_id = f"{shp_biz_id}-L{l_no:02d}"
                sl_id = deterministic_uuid("ShipmentLine", sl_biz_id)
                shipment_lines.append({
                    "shipment_line_id": sl_id,
                    "shipment_id": shp_id,
                    "order_line_id": ol["order_line_id"],
                    "shipped_quantity": ol["ordered_quantity"],
                    "created_at": dispatch_time,
                })
        else:
            # 1st partial shipment ships 50-60% of quantities
            for l_no, ol in enumerate(lines, start=1):
                sl_biz_id = f"{shp_biz_id}-L{l_no:02d}"
                sl_id = deterministic_uuid("ShipmentLine", sl_biz_id)
                part1_qty = max(Decimal("1.0000"), (ol["ordered_quantity"] * Decimal("0.60")).quantize(Decimal("1.0000")))
                if part1_qty > ol["ordered_quantity"]:
                    part1_qty = ol["ordered_quantity"]

                shipment_lines.append({
                    "shipment_line_id": sl_id,
                    "shipment_id": shp_id,
                    "order_line_id": ol["order_line_id"],
                    "shipped_quantity": part1_qty,
                    "created_at": dispatch_time,
                })

            # 2nd Shipment completes remaining quantity
            shp2_biz_id = format_shipment_id(shp_idx)
            shp2_id = deterministic_uuid("Shipment", shp2_biz_id)
            shp_idx += 1

            dispatch2 = dispatch_time + timedelta(days=rng.randint(2, 4))
            deliver2 = dispatch2 + timedelta(days=rng.randint(1, 3))

            shipments.append({
                "shipment_id": shp2_id,
                "business_id": shp2_biz_id,
                "order_id": order["order_id"],
                "carrier": carrier,
                "tracking_number": f"TRK-{carrier[:3]}-{shp2_biz_id[-8:]}",
                "status": "DELIVERED",
                "dispatched_at": dispatch2,
                "delivered_at": deliver2,
                "created_at": dispatch2,
                "updated_at": deliver2,
            })

            for l_no, ol in enumerate(lines, start=1):
                sl2_biz_id = f"{shp2_biz_id}-L{l_no:02d}"
                sl2_id = deterministic_uuid("ShipmentLine", sl2_biz_id)
                part1_qty = max(Decimal("1.0000"), (ol["ordered_quantity"] * Decimal("0.60")).quantize(Decimal("1.0000")))
                remaining_qty = max(Decimal("1.0000"), ol["ordered_quantity"] - part1_qty)

                shipment_lines.append({
                    "shipment_line_id": sl2_id,
                    "shipment_id": shp2_id,
                    "order_line_id": ol["order_line_id"],
                    "shipped_quantity": remaining_qty,
                    "created_at": dispatch2,
                })

    return shipments, shipment_lines
