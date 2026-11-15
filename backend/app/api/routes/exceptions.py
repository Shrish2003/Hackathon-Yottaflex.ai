"""
Exceptions API endpoints for reviewing detected anomalies and associated evidence.
"""

import math
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session, selectinload

from app.db.database import get_db
from app.models.detection import ExceptionRecord, ExceptionEvidence
from app.schemas.exceptions import (
    ExceptionRecordResponse,
    ExceptionDetailResponse,
    PaginatedExceptionsResponse,
    EvidenceItemResponse,
)

router = APIRouter(prefix="/exceptions", tags=["Exceptions"])


@router.get("", response_model=PaginatedExceptionsResponse, summary="List Detected Exceptions")
def list_exceptions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly issue type"),
    issue_type: Optional[str] = Query(None, description="Alias filter for issue type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (Invoice, Payment, etc.)"),
    search: Optional[str] = Query(None, description="Search by business ID or explanation"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of detected exception records with optional filtering and search.
    """
    query = select(ExceptionRecord)

    # Filtering
    if severity:
        query = query.where(ExceptionRecord.severity == severity.upper())

    target_type = anomaly_type or issue_type
    if target_type:
        query = query.where(ExceptionRecord.issue_type == target_type)

    if entity_type:
        query = query.where(ExceptionRecord.entity_type == entity_type)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                ExceptionRecord.business_id.ilike(search_pattern),
                ExceptionRecord.explanation.ilike(search_pattern),
            )
        )

    # Total count query
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Pagination & Ordering
    offset = (page - 1) * limit
    paged_query = (
        query.order_by(ExceptionRecord.detected_at.desc(), ExceptionRecord.business_id.asc())
        .offset(offset)
        .limit(limit)
    )

    records = db.scalars(paged_query).all()

    # Pre-fetch evidence counts for the returned exception IDs to avoid N+1
    exc_ids = [r.exception_id for r in records]
    evidence_counts = {}
    if exc_ids:
        count_rows = db.execute(
            select(ExceptionEvidence.exception_id, func.count(ExceptionEvidence.evidence_id))
            .where(ExceptionEvidence.exception_id.in_(exc_ids))
            .group_by(ExceptionEvidence.exception_id)
        ).fetchall()
        evidence_counts = {row[0]: row[1] for row in count_rows}

    items = []
    for r in records:
        items.append(
            ExceptionRecordResponse(
                exception_id=r.exception_id,
                issue_type=r.issue_type,
                severity=r.severity,
                entity_type=r.entity_type,
                entity_id=r.entity_id,
                business_id=r.business_id,
                account_id=r.account_id,
                order_id=r.order_id,
                invoice_id=r.invoice_id,
                payment_id=r.payment_id,
                dispute_id=r.dispute_id,
                leakage_amount=float(r.leakage_amount) if r.leakage_amount is not None else None,
                detected_at=r.detected_at,
                explanation=r.explanation,
                recommended_action=r.recommended_action,
                evidence_count=evidence_counts.get(r.exception_id, 0),
            )
        )

    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedExceptionsResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/{exception_id}", response_model=ExceptionDetailResponse, summary="Get Exception Dossier with Evidence")
def get_exception_detail(
    exception_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Returns full details for a specific exception record including all associated evidence items.
    """
    stmt = (
        select(ExceptionRecord)
        .options(selectinload(ExceptionRecord.evidence_items))
        .where(ExceptionRecord.exception_id == exception_id)
    )
    record = db.scalar(stmt)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exception with ID '{exception_id}' not found.",
        )

    evidence_list = [
        EvidenceItemResponse(
            evidence_id=ev.evidence_id,
            exception_id=ev.exception_id,
            evidence_type=ev.evidence_type,
            source_table=ev.source_table,
            source_id=ev.source_id,
            conflicting_source_table=ev.conflicting_source_table,
            conflicting_source_id=ev.conflicting_source_id,
            expected_value=float(ev.expected_value) if ev.expected_value is not None else None,
            actual_value=float(ev.actual_value) if ev.actual_value is not None else None,
            discrepancy_delta=float(ev.discrepancy_delta) if ev.discrepancy_delta is not None else None,
            evidence_payload=ev.evidence_payload,
            created_at=ev.created_at,
        )
        for ev in record.evidence_items
    ]

    return ExceptionDetailResponse(
        exception_id=record.exception_id,
        issue_type=record.issue_type,
        severity=record.severity,
        entity_type=record.entity_type,
        entity_id=record.entity_id,
        business_id=record.business_id,
        account_id=record.account_id,
        order_id=record.order_id,
        invoice_id=record.invoice_id,
        payment_id=record.payment_id,
        dispute_id=record.dispute_id,
        leakage_amount=float(record.leakage_amount) if record.leakage_amount is not None else None,
        detected_at=record.detected_at,
        explanation=record.explanation,
        recommended_action=record.recommended_action,
        evidence_count=len(evidence_list),
        evidence_items=evidence_list,
    )
