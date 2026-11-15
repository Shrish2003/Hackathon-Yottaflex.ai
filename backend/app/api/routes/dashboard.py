"""
Dashboard API endpoints for executive summary and high-level KPIs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.o2c import Account, Quote, SalesOrder, Shipment, Invoice, Payment
from app.models.detection import ExceptionRecord
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse, summary="Get Executive Dashboard Summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns aggregate counts across the 7 O2C lifecycle stages,
    total detected exceptions, total financial leakage, and breakdowns.
    """
    # Operational counts
    total_accounts = db.scalar(select(func.count(Account.account_id))) or 0
    total_quotes = db.scalar(select(func.count(Quote.quote_id))) or 0
    total_sales_orders = db.scalar(select(func.count(SalesOrder.order_id))) or 0
    total_shipments = db.scalar(select(func.count(Shipment.shipment_id))) or 0
    total_invoices = db.scalar(select(func.count(Invoice.invoice_id))) or 0
    total_payments = db.scalar(select(func.count(Payment.payment_id))) or 0

    # Detection counts & leakage
    total_exceptions = db.scalar(select(func.count(ExceptionRecord.exception_id))) or 0
    total_leakage = db.scalar(select(func.coalesce(func.sum(ExceptionRecord.leakage_amount), 0.0))) or 0.0

    # Breakdown by severity
    severity_rows = db.execute(
        select(ExceptionRecord.severity, func.count(ExceptionRecord.exception_id))
        .group_by(ExceptionRecord.severity)
    ).fetchall()
    by_severity = {row[0]: row[1] for row in severity_rows}

    # Breakdown by anomaly type
    type_rows = db.execute(
        select(ExceptionRecord.issue_type, func.count(ExceptionRecord.exception_id))
        .group_by(ExceptionRecord.issue_type)
    ).fetchall()
    by_type = {row[0]: row[1] for row in type_rows}

    return DashboardSummaryResponse(
        total_accounts=total_accounts,
        total_quotes=total_quotes,
        total_sales_orders=total_sales_orders,
        total_shipments=total_shipments,
        total_invoices=total_invoices,
        total_payments=total_payments,
        total_detected_exceptions=total_exceptions,
        total_identified_leakage_amount=float(total_leakage),
        exception_counts_by_severity=by_severity,
        exception_counts_by_anomaly_type=by_type,
    )
