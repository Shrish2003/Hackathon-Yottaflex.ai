"""
Detection API endpoint to trigger anomaly detection runs on-demand.
CRITICAL: Never reads, queries, imports or uses ground_truth_anomalies.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.detectors.engine import DetectionEngine
from app.schemas.detection import DetectionRunResponse

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/run", response_model=DetectionRunResponse, summary="Execute Anomaly Detection Engine")
def run_detection(db: Session = Depends(get_db)):
    """
    Executes the 12 deterministic anomaly detection rules against the operational database.
    Updates exception records and evidence tables, and returns aggregate execution metrics.
    """
    try:
        engine = DetectionEngine()
        summary = engine.run(session=db)

        return DetectionRunResponse(
            status="SUCCESS",
            execution_timestamp=summary["execution_timestamp"],
            simulation_as_of_date=summary["simulation_as_of_date"],
            duration_seconds=summary["duration_seconds"],
            total_exceptions=summary["total_exceptions"],
            total_evidence_records=summary["total_evidence_records"],
            total_financial_leakage_inr=summary["total_financial_leakage_inr"],
            by_issue_type=summary["by_issue_type"],
            by_severity=summary["by_severity"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection run failed: {str(exc)}",
        )
