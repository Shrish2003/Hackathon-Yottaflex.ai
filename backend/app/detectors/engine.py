"""
Orchestration Engine for O2C Revenue Leakage Detection.
Executes all 12 deterministic detection rules, persists results and evidence,
and calculates comprehensive aggregate metrics.
CRITICAL: Never reads, queries, imports or uses ground_truth_anomalies.
"""

import json
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import engine, SessionLocal
from app.detectors.base import BaseDetector, DetectionResult
from app.detectors.rules import (
    OverbillingQuantityDetector,
    OverbillingAmountDetector,
    UnderbillingDetector,
    DuplicateInvoiceDetector,
    DuplicatePaymentAllocationDetector,
    ExcessivePaymentAllocationDetector,
    PrematureOrderClosureDetector,
    InvalidStatusTransitionDetector,
    DisputeARDisconnectDetector,
    ShortPaymentDetector,
    SLAAgingBreachDetector,
    OverdueUnpaidInvoiceDetector,
)
from app.models.detection import ExceptionRecord, ExceptionEvidence


class DetectionEngine:
    """Orchestrates deterministic execution of all 12 O2C anomaly detection rules."""

    def __init__(self, simulation_date: Optional[datetime] = None):
        self.simulation_date = simulation_date or datetime(
            2026, 10, 31, 23, 59, 59, tzinfo=timezone.utc
        )
        self.detectors: List[BaseDetector] = [
            OverbillingQuantityDetector(),
            OverbillingAmountDetector(),
            UnderbillingDetector(),
            DuplicateInvoiceDetector(),
            DuplicatePaymentAllocationDetector(),
            ExcessivePaymentAllocationDetector(),
            PrematureOrderClosureDetector(),
            InvalidStatusTransitionDetector(),
            DisputeARDisconnectDetector(),
            ShortPaymentDetector(),
            SLAAgingBreachDetector(),
            OverdueUnpaidInvoiceDetector(),
        ]

    def run(self, session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Executes all 12 detectors against the operational database.
        Persists results into exception_records and exception_evidence tables.
        Returns aggregate metrics summary.
        """
        t0 = time.time()
        should_close_session = False

        if session is None:
            session = SessionLocal()
            should_close_session = True

        try:
            print(f"\n==================================================================")
            print(f"🔍 O2C REVENUE LEAKAGE DETECTION ENGINE")
            print(f"==================================================================")
            print(f"• Registered Rules:       {len(self.detectors)}")
            print(f"• Simulation 'As-Of' Date:{self.simulation_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"------------------------------------------------------------------")

            # 1. Clear previous exception records to guarantee idempotency and avoid duplicates
            session.execute(text("TRUNCATE TABLE exception_evidence, exception_records CASCADE;"))
            session.commit()

            all_results: List[DetectionResult] = []

            # 2. Run each detection rule
            for detector in self.detectors:
                rule_t0 = time.time()
                rule_results = detector.detect(session, self.simulation_date)
                rule_dur = time.time() - rule_t0
                all_results.extend(rule_results)
                print(f"   ✓ {detector.issue_type:<32}: {len(rule_results):>4} exceptions ({rule_dur:.3f}s)")

            # 3. Persist results and evidence into PostgreSQL
            print("⏳ Persisting exception records and evidence into PostgreSQL...")
            exc_records_to_insert = []
            evidence_to_insert = []

            for res in all_results:
                exc_id = uuid.uuid4()
                exc_records_to_insert.append({
                    "exception_id": exc_id,
                    "issue_type": res.issue_type,
                    "severity": res.severity,
                    "entity_type": res.entity_type,
                    "entity_id": res.entity_id,
                    "business_id": res.business_id,
                    "account_id": res.account_id,
                    "order_id": res.order_id,
                    "invoice_id": res.invoice_id,
                    "payment_id": res.payment_id,
                    "dispute_id": res.dispute_id,
                    "leakage_amount": res.leakage_amount,
                    "detected_at": res.detected_at,
                    "explanation": res.explanation,
                    "recommended_action": res.recommended_action,
                })

                for ev in res.evidence_items:
                    evidence_to_insert.append({
                        "evidence_id": uuid.uuid4(),
                        "exception_id": exc_id,
                        "evidence_type": ev.evidence_type,
                        "source_table": ev.source_table,
                        "source_id": ev.source_id,
                        "conflicting_source_table": ev.conflicting_source_table,
                        "conflicting_source_id": ev.conflicting_source_id,
                        "expected_value": ev.expected_value,
                        "actual_value": ev.actual_value,
                        "discrepancy_delta": ev.discrepancy_delta,
                        "evidence_payload": json.dumps(ev.evidence_payload),
                        "created_at": res.detected_at,
                    })

            # Bulk insert using SQLAlchemy Core
            if exc_records_to_insert:
                session.execute(ExceptionRecord.__table__.insert(), exc_records_to_insert)
            if evidence_to_insert:
                session.execute(ExceptionEvidence.__table__.insert(), evidence_to_insert)
            session.commit()

            # 4. Compute aggregate metrics
            elapsed = time.time() - t0
            total_leakage = sum(
                (r.leakage_amount or Decimal("0.00")) for r in all_results
            )

            by_type = {}
            for r in all_results:
                by_type[r.issue_type] = by_type.get(r.issue_type, 0) + 1

            by_severity = {}
            for r in all_results:
                by_severity[r.severity] = by_severity.get(r.severity, 0) + 1

            summary = {
                "execution_timestamp": datetime.now(timezone.utc).isoformat(),
                "simulation_as_of_date": self.simulation_date.isoformat(),
                "duration_seconds": round(elapsed, 3),
                "total_exceptions": len(all_results),
                "total_evidence_records": len(evidence_to_insert),
                "total_financial_leakage_inr": float(total_leakage),
                "by_issue_type": by_type,
                "by_severity": by_severity,
            }

            print(f"\n==================================================================")
            print(f"🎉 DETECTION COMPLETED IN {elapsed:.2f}s")
            print(f"• Total Exceptions Detected: {len(all_results):,}")
            print(f"• Total Evidence Records:    {len(evidence_to_insert):,}")
            print(f"• Total Identified Leakage:  ₹{total_leakage:,.2f}")
            print(f"------------------------------------------------------------------")
            print(f"Breakdown by Severity:")
            for sev, cnt in sorted(by_severity.items()):
                print(f"  - {sev:<12}: {cnt:>4}")
            print(f"==================================================================\n")

            return summary

        finally:
            if should_close_session:
                session.close()
