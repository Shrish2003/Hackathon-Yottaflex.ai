"""
Master Data Generator: Accounts, Quotes, and Quote Lines.
"""

import random
from datetime import timedelta, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple

from app.generators.config import GeneratorConfig
from app.generators.id_utils import (
    deterministic_uuid,
    format_account_num,
    format_quote_id,
)
from app.generators.catalog import get_accounts_master, PRODUCT_CATALOG


def generate_master_data(
    config: GeneratorConfig, rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates deterministic Accounts, Quotes, and QuoteLines.
    Returns: (accounts_data, quotes_data, quote_lines_data)
    """
    # 1. Generate Accounts
    account_templates = get_accounts_master(config.num_accounts)
    accounts: List[Dict[str, Any]] = []

    for idx, tpl in enumerate(account_templates, start=1):
        acc_num = format_account_num(idx)
        acc_id = deterministic_uuid("Account", acc_num)
        # Stagger account creation across the first 30 days
        created_at = config.start_date + timedelta(
            days=idx % 30, hours=idx % 24, minutes=(idx * 7) % 60
        )
        accounts.append({
            "account_id": acc_id,
            "account_number": acc_num,
            "account_name": tpl["name"],
            "credit_limit": tpl["credit_limit"],
            "payment_terms": tpl["payment_terms"],
            "currency": tpl["currency"],
            "status": tpl["status"],
            "created_at": created_at,
            "updated_at": created_at,
        })

    # 2. Generate Quotes & QuoteLines
    quotes: List[Dict[str, Any]] = []
    quote_lines: List[Dict[str, Any]] = []

    # Time span for quote issuance: from start_date to simulation_date - 45 days
    total_quote_days = max(1, (config.simulation_date - config.start_date).days - 45)

    # First `config.num_orders` quotes will be ACCEPTED to convert into Sales Orders
    for q_idx in range(1, config.num_quotes + 1):
        q_biz_id = format_quote_id(q_idx)
        q_id = deterministic_uuid("Quote", q_biz_id)

        # Distribute quotes among accounts
        acc = accounts[(q_idx - 1) % len(accounts)]
        acc_id = acc["account_id"]

        # Timestamp progression
        day_offset = (q_idx * total_quote_days) // config.num_quotes
        q_created = config.start_date + timedelta(
            days=day_offset,
            hours=(q_idx * 3) % 24,
            minutes=(q_idx * 13) % 60,
        )
        valid_from = q_created
        valid_to = valid_from + timedelta(days=30)

        # Status distribution: the first num_orders quotes are ACCEPTED
        if q_idx <= config.num_orders:
            status = "ACCEPTED"
        else:
            dice = rng.random()
            if dice < 0.40:
                status = "REJECTED"
            elif dice < 0.70:
                status = "EXPIRED"
            elif dice < 0.85:
                status = "APPROVED"
            else:
                status = "DRAFT"

        # 1 to 4 items per quote
        num_items = rng.randint(1, 4)
        selected_products = rng.sample(PRODUCT_CATALOG, min(num_items, len(PRODUCT_CATALOG)))

        gross_total = Decimal("0.00")
        discount_total = Decimal("0.00")

        for line_no, prod in enumerate(selected_products, start=1):
            line_biz_id = f"{q_biz_id}-L{line_no:02d}"
            line_id = deterministic_uuid("QuoteLine", line_biz_id)

            qty = Decimal(rng.randint(1, 10))
            list_price = prod["unit_price"]

            # Discount 0%, 5%, 10%, 15%, or 20%
            disc_pct = Decimal(rng.choice([0, 5, 10, 15, 20]))
            line_gross = (qty * list_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            line_disc = ((line_gross * disc_pct) / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            line_net = line_gross - line_disc

            gross_total += line_gross
            discount_total += line_disc

            quote_lines.append({
                "quote_line_id": line_id,
                "quote_id": q_id,
                "line_number": line_no,
                "product_sku": prod["sku"],
                "quantity": qty,
                "unit_list_price": list_price,
                "discount_pct": disc_pct,
                "discount_amount": line_disc,
                "line_net_amount": line_net,
            })

        net_total = gross_total - discount_total

        quotes.append({
            "quote_id": q_id,
            "business_id": q_biz_id,
            "account_id": acc_id,
            "status": status,
            "total_gross_amount": gross_total,
            "total_discount_amount": discount_total,
            "total_net_amount": net_total,
            "currency": "INR",
            "valid_from": valid_from,
            "valid_to": valid_to,
            "created_at": q_created,
            "updated_at": q_created + timedelta(hours=2),
        })

    return accounts, quotes, quote_lines
