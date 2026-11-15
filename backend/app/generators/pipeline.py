"""
Master Generation Pipeline.
Orchestrates dependency-ordered synthetic data synthesis, anomaly injection,
high-performance chunked PostgreSQL loading, and manifest export.
"""

import csv
import hashlib
import json
import random
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine
from app.generators.config import GeneratorConfig
from app.generators.master_generator import generate_master_data
from app.generators.order_generator import generate_orders_data
from app.generators.fulfillment_generator import generate_shipments_data
from app.generators.billing_generator import generate_billing_data
from app.generators.treasury_generator import generate_treasury_data
from app.generators.dispute_generator import generate_disputes_data
from app.generators.event_generator import generate_status_events_data
from app.generators.anomaly_injector import inject_anomalies

# Import models for table references
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


def bulk_insert_chunked(table, records: List[Dict[str, Any]], batch_size: int = 2500):
    """Executes high-performance chunked batch inserts using SQLAlchemy Core."""
    if not records:
        return
    with engine.begin() as conn:
        for i in range(0, len(records), batch_size):
            chunk = records[i : i + batch_size]
            conn.execute(table.insert(), chunk)


def export_records_to_csv(filepath: Path, records: List[Dict[str, Any]]):
    """Utility to export generated record dictionaries to standard CSV."""
    if not records:
        return
    keys = list(records[0].keys())
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in records:
            # Format UUID and datetime cleanly
            row = {}
            for k, v in r.items():
                if isinstance(v, (datetime, Decimal)):
                    row[k] = str(v)
                else:
                    row[k] = v
            writer.writerow(row)


def run_pipeline(config: GeneratorConfig) -> Dict[str, Any]:
    """
    Executes the complete deterministic O2C data generation and loading pipeline.
    """
    start_wall_time = time.time()
    rng = random.Random(config.seed)

    print(f"\n==================================================================")
    print(f"🚀 O2C REVENUE ASSURANCE - SYNTHETIC DATA GENERATION PIPELINE")
    print(f"==================================================================")
    print(f"• Random Seed:            {config.seed}")
    print(f"• Profile / Scale:        {config.profile} (Scale: {config.scale})")
    print(f"• Simulation 'As-Of' Date:{config.simulation_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"• Batch Insert Size:      {config.batch_size}")
    print(f"------------------------------------------------------------------")

    # 1. Truncate existing data cleanly (preserving schema and migration state)
    print("⏳ Resetting existing operational and ground-truth tables...")
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE accounts, quotes, quote_lines, sales_orders, "
                "order_lines, shipments, shipment_lines, invoices, invoice_lines, "
                "payments, payment_allocations, disputes, invoice_adjustments, "
                "status_events, ground_truth_anomalies CASCADE;"
            )
        )
    print("✅ Tables truncated cleanly.")

    # 2. Master Data (Accounts, Quotes, QuoteLines)
    print("⏳ Stage 1: Generating Accounts, Quotes, and Quote Lines...")
    accounts, quotes, quote_lines = generate_master_data(config, rng)
    print(f"   -> Accounts: {len(accounts):,}")
    print(f"   -> Quotes:   {len(quotes):,}")
    print(f"   -> Lines:    {len(quote_lines):,}")

    # 3. Sales Orders & Order Lines
    print("⏳ Stage 2: Converting Accepted Quotes to Sales Orders...")
    orders, order_lines = generate_orders_data(config, quotes, quote_lines, rng)
    print(f"   -> Sales Orders: {len(orders):,}")
    print(f"   -> Order Lines:  {len(order_lines):,}")

    # 4. Shipments & Shipment Lines
    print("⏳ Stage 3: Generating Shipments & Fulfillment Lines...")
    shipments, shipment_lines = generate_shipments_data(config, orders, order_lines, rng)
    print(f"   -> Shipments:      {len(shipments):,}")
    print(f"   -> Shipment Lines: {len(shipment_lines):,}")

    # 5. Invoices & Invoice Lines
    print("⏳ Stage 4: Generating Invoices & Billing Lines...")
    invoices, invoice_lines = generate_billing_data(
        config, orders, order_lines, shipments, shipment_lines, accounts, rng
    )
    print(f"   -> Invoices:      {len(invoices):,}")
    print(f"   -> Invoice Lines: {len(invoice_lines):,}")

    # 6. Payments & Payment Allocations
    print("⏳ Stage 5: Generating Treasury Payments & Payment Allocations...")
    payments, payment_allocations = generate_treasury_data(config, accounts, invoices, rng)
    print(f"   -> Payments:            {len(payments):,}")
    print(f"   -> Payment Allocations: {len(payment_allocations):,}")

    # 7. Disputes & Adjustments
    print("⏳ Stage 6: Generating Disputes & Credit Memo Adjustments...")
    disputes, adjustments = generate_disputes_data(config, invoices, rng)
    print(f"   -> Disputes:            {len(disputes):,}")
    print(f"   -> Invoice Adjustments: {len(adjustments):,}")

    # 8. Status Events Audit History
    print("⏳ Stage 7: Generating Status Events Audit Trail...")
    status_events = generate_status_events_data(
        config, quotes, orders, shipments, invoices, payments, disputes
    )
    print(f"   -> Status Events: {len(status_events):,}")

    # 9. Anomaly Injection & Ground Truth Recording
    print("⏳ Stage 8: Injecting 12 Anomaly Types & Recording Ground Truth...")
    ground_truth = inject_anomalies(
        config,
        quotes,
        orders,
        order_lines,
        shipments,
        shipment_lines,
        invoices,
        invoice_lines,
        payments,
        payment_allocations,
        disputes,
        status_events,
        rng,
    )
    print(f"   -> Injected Ground Truth Anomalies: {len(ground_truth):,}")

    # 10. High-Performance Chunked Database Loading
    print("⏳ Stage 9: Executing Chunked Batch Inserts to PostgreSQL...")
    insert_plan = [
        ("accounts", Account.__table__, accounts),
        ("quotes", Quote.__table__, quotes),
        ("quote_lines", QuoteLine.__table__, quote_lines),
        ("sales_orders", SalesOrder.__table__, orders),
        ("order_lines", OrderLine.__table__, order_lines),
        ("shipments", Shipment.__table__, shipments),
        ("shipment_lines", ShipmentLine.__table__, shipment_lines),
        ("invoices", Invoice.__table__, invoices),
        ("invoice_lines", InvoiceLine.__table__, invoice_lines),
        ("payments", Payment.__table__, payments),
        ("payment_allocations", PaymentAllocation.__table__, payment_allocations),
        ("disputes", Dispute.__table__, disputes),
        ("invoice_adjustments", InvoiceAdjustment.__table__, adjustments),
        ("status_events", StatusEvent.__table__, status_events),
        ("ground_truth_anomalies", GroundTruthAnomaly.__table__, ground_truth),
    ]

    for tbl_name, tbl_obj, recs in insert_plan:
        t0 = time.time()
        bulk_insert_chunked(tbl_obj, recs, config.batch_size)
        dur = time.time() - t0
        print(f"   ✓ Inserted {len(recs):>7,} rows into '{tbl_name}' ({dur:.2f}s)")

    # 11. Compute Manifest Metrics & Hashes
    elapsed_total = time.time() - start_wall_time
    total_leakage = sum(
        Decimal(str(gt["leakage_amount"] or 0)) for gt in ground_truth
    )

    # Anomaly breakdown
    anom_breakdown = {}
    for gt in ground_truth:
        itype = gt["issue_type"]
        anom_breakdown[itype] = anom_breakdown.get(itype, 0) + 1

    # Checksum of generated business IDs
    all_biz_ids = (
        [a["account_number"] for a in accounts]
        + [q["business_id"] for q in quotes]
        + [o["business_id"] for o in orders]
        + [s["business_id"] for s in shipments]
        + [i["business_id"] for i in invoices]
        + [p["business_id"] for p in payments]
        + [d["business_id"] for d in disputes]
    )
    biz_hash = hashlib.sha256("".join(sorted(all_biz_ids)).encode("utf-8")).hexdigest()

    manifest_data = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": config.seed,
        "profile": config.profile,
        "scale_factor": config.scale,
        "simulation_as_of_date": config.simulation_date.isoformat(),
        "execution_duration_seconds": round(elapsed_total, 2),
        "total_records_created": sum(len(r) for _, _, r in insert_plan),
        "record_counts": {tbl: len(r) for tbl, _, r in insert_plan},
        "ground_truth_breakdown": anom_breakdown,
        "total_injected_leakage_inr": float(total_leakage),
        "dataset_checksum_sha256": biz_hash,
    }

    manifest_file = config.output_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    # Also save a copy to docs for persistent visibility
    docs_manifest = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "DATA_MANIFEST.json"
    with open(docs_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    # Optional CSV Exports
    if config.export_csv:
        print("⏳ Exporting records to CSV...")
        csv_dir = config.output_dir / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        for tbl_name, _, recs in insert_plan:
            export_records_to_csv(csv_dir / f"{tbl_name}.csv", recs)
        print(f"✅ CSV exports saved to {csv_dir}")

    print(f"\n==================================================================")
    print(f"🎉 GENERATION COMPLETED SUCCESSFULLY IN {elapsed_total:.2f}s")
    print(f"• Total Records Inserted: {manifest_data['total_records_created']:,}")
    print(f"• Ground Truth Anomalies: {len(ground_truth):,}")
    print(f"• Total Injected Leakage: ₹{total_leakage:,.2f}")
    print(f"• Dataset SHA-256:        {biz_hash[:16]}...")
    print(f"• Manifest Saved:         {manifest_file}")
    print(f"==================================================================\n")

    return manifest_data
