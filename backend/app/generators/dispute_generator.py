"""
Dispute and Invoice Adjustment Generator.
Generates 400-600 Disputes on invoices with credit memo adjustments for accepted claims.
"""

import random
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple

from app.generators.config import GeneratorConfig
from app.generators.id_utils import (
    deterministic_uuid,
    format_dispute_id,
    format_adjustment_id,
)

DISPUTE_REASONS = [
    "PRICE_DISCREPANCY",
    "DAMAGED_GOODS",
    "MISSING_QUANTITY",
    "DELIVERY_DELAY",
    "INCORRECT_ITEM",
]

DISPUTE_STATUSES = [
    "RESOLVED_ACCEPTED",
    "RESOLVED_REJECTED",
    "UNDER_INVESTIGATION",
    "LODGED",
]


def generate_disputes_data(
    config: GeneratorConfig,
    invoices: List[Dict[str, Any]],
    rng: random.Random,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Disputes and associated Invoice Adjustments.
    Returns: (disputes_data, invoice_adjustments_data)
    """
    disputes: List[Dict[str, Any]] = []
    adjustments: List[Dict[str, Any]] = []

    adj_idx = 1
    total_disputes = config.num_disputes

    # Choose candidate invoices for disputes (e.g. from issued / partially paid invoices)
    candidate_invoices = invoices[: min(len(invoices), total_disputes * 2)]
    selected_invoices = rng.sample(candidate_invoices, min(total_disputes, len(candidate_invoices)))

    for d_idx, inv in enumerate(selected_invoices, start=1):
        dsp_biz_id = format_dispute_id(d_idx)
        dsp_id = deterministic_uuid("Dispute", dsp_biz_id)

        reason = DISPUTE_REASONS[d_idx % len(DISPUTE_REASONS)]

        # Status distribution: 40% resolved accepted, 30% resolved rejected, 20% under investigation, 10% lodged
        dice = rng.random()
        if dice < 0.40:
            status = "RESOLVED_ACCEPTED"
        elif dice < 0.70:
            status = "RESOLVED_REJECTED"
        elif dice < 0.90:
            status = "UNDER_INVESTIGATION"
        else:
            status = "LODGED"

        # Disputed amount: 10% to 50% of invoice total
        ratio = Decimal(rng.choice([10, 20, 25, 33, 50])) / Decimal(100)
        disp_amt = (inv["total_invoiced_amount"] * ratio).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if disp_amt <= Decimal("0.00"):
            disp_amt = Decimal("1000.00")

        lodged_at = inv["issue_date"] + timedelta(days=rng.randint(3, 14), hours=rng.randint(1, 8))
        resolved_at = None
        if status in ("RESOLVED_ACCEPTED", "RESOLVED_REJECTED"):
            resolved_at = lodged_at + timedelta(days=rng.randint(2, 10), hours=rng.randint(1, 6))
            if resolved_at > config.simulation_date:
                resolved_at = config.simulation_date - timedelta(hours=1)

        disputes.append({
            "dispute_id": dsp_id,
            "business_id": dsp_biz_id,
            "invoice_id": inv["invoice_id"],
            "dispute_reason": reason,
            "disputed_amount": disp_amt,
            "status": status,
            "lodged_at": lodged_at,
            "resolved_at": resolved_at,
            "created_at": lodged_at,
            "updated_at": resolved_at or lodged_at,
        })

        # If dispute was ACCEPTED, issue a Credit Memo Adjustment
        if status == "RESOLVED_ACCEPTED" and resolved_at:
            adj_biz_id = format_adjustment_id(adj_idx)
            adj_id = deterministic_uuid("InvoiceAdjustment", adj_biz_id)
            adj_idx += 1

            adjustments.append({
                "adjustment_id": adj_id,
                "invoice_id": inv["invoice_id"],
                "dispute_id": dsp_id,
                "adjustment_type": "CREDIT_MEMO",
                "adjustment_amount": disp_amt,
                "reason": f"Dispute {dsp_biz_id} resolved: {reason}",
                "created_at": resolved_at,
            })

    return disputes, adjustments
