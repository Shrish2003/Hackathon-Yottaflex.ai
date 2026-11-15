"""
Transaction exploration endpoints for Accounts, Orders, Invoices, Payments, and Disputes.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.o2c import Account, SalesOrder, Invoice, Payment, Dispute
from app.schemas.transactions import (
    AccountItem,
    PaginatedAccountsResponse,
    OrderItem,
    PaginatedOrdersResponse,
    InvoiceItem,
    PaginatedInvoicesResponse,
    PaymentItem,
    PaginatedPaymentsResponse,
    DisputeItem,
    PaginatedDisputesResponse,
)

router = APIRouter(tags=["Transactions"])


# 1. Accounts
@router.get("/accounts", response_model=PaginatedAccountsResponse, summary="List Customer Accounts")
def list_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search account number or name"),
    db: Session = Depends(get_db),
):
    query = select(Account)
    if search:
        query = query.where(
            or_(
                Account.account_number.ilike(f"%{search}%"),
                Account.account_name.ilike(f"%{search}%"),
            )
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    records = db.scalars(
        query.order_by(Account.account_number.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    items = [
        AccountItem(
            account_id=r.account_id,
            account_number=r.account_number,
            account_name=r.account_name,
            credit_limit=float(r.credit_limit),
            payment_terms=r.payment_terms,
            currency=r.currency,
            status=r.status,
            created_at=r.created_at,
        )
        for r in records
    ]
    pages = math.ceil(total / limit) if total > 0 else 1
    return PaginatedAccountsResponse(items=items, total=total, page=page, limit=limit, pages=pages)


# 2. Sales Orders
@router.get("/orders", response_model=PaginatedOrdersResponse, summary="List Sales Orders")
def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (CONFIRMED, FULFILLED, CLOSED, etc.)"),
    search: Optional[str] = Query(None, description="Search by business ID"),
    db: Session = Depends(get_db),
):
    query = select(SalesOrder)
    if status:
        query = query.where(SalesOrder.status == status.upper())
    if search:
        query = query.where(SalesOrder.business_id.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    records = db.scalars(
        query.order_by(SalesOrder.order_date.desc(), SalesOrder.business_id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    items = [
        OrderItem(
            order_id=r.order_id,
            business_id=r.business_id,
            account_id=r.account_id,
            quote_id=r.quote_id,
            status=r.status,
            total_order_value=float(r.total_order_value),
            currency=r.currency,
            order_date=r.order_date,
            created_at=r.created_at,
        )
        for r in records
    ]
    pages = math.ceil(total / limit) if total > 0 else 1
    return PaginatedOrdersResponse(items=items, total=total, page=page, limit=limit, pages=pages)


# 3. Invoices
@router.get("/invoices", response_model=PaginatedInvoicesResponse, summary="List Invoices")
def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (ISSUED, PAID, PARTIALLY_PAID, etc.)"),
    search: Optional[str] = Query(None, description="Search by business ID"),
    db: Session = Depends(get_db),
):
    query = select(Invoice)
    if status:
        query = query.where(Invoice.status == status.upper())
    if search:
        query = query.where(Invoice.business_id.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    records = db.scalars(
        query.order_by(Invoice.issue_date.desc(), Invoice.business_id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    items = [
        InvoiceItem(
            invoice_id=r.invoice_id,
            business_id=r.business_id,
            order_id=r.order_id,
            account_id=r.account_id,
            status=r.status,
            total_invoiced_amount=float(r.total_invoiced_amount),
            paid_amount=float(r.paid_amount),
            outstanding_balance=float(r.outstanding_balance),
            currency=r.currency,
            issue_date=r.issue_date,
            due_date=r.due_date,
            created_at=r.created_at,
        )
        for r in records
    ]
    pages = math.ceil(total / limit) if total > 0 else 1
    return PaginatedInvoicesResponse(items=items, total=total, page=page, limit=limit, pages=pages)


# 4. Payments
@router.get("/payments", response_model=PaginatedPaymentsResponse, summary="List Treasury Payments")
def list_payments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (ALLOCATED, PARTIALLY_ALLOCATED, RECEIVED)"),
    search: Optional[str] = Query(None, description="Search by business ID or reference"),
    db: Session = Depends(get_db),
):
    query = select(Payment)
    if status:
        query = query.where(Payment.status == status.upper())
    if search:
        query = query.where(
            or_(
                Payment.business_id.ilike(f"%{search}%"),
                Payment.payment_reference.ilike(f"%{search}%"),
            )
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    records = db.scalars(
        query.order_by(Payment.payment_date.desc(), Payment.business_id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    items = [
        PaymentItem(
            payment_id=r.payment_id,
            business_id=r.business_id,
            account_id=r.account_id,
            payment_method=r.payment_method,
            payment_reference=r.payment_reference,
            amount_received=float(r.amount_received),
            amount_allocated=float(r.amount_allocated),
            unallocated_amount=float(r.unallocated_amount),
            currency=r.currency,
            status=r.status,
            payment_date=r.payment_date,
            created_at=r.created_at,
        )
        for r in records
    ]
    pages = math.ceil(total / limit) if total > 0 else 1
    return PaginatedPaymentsResponse(items=items, total=total, page=page, limit=limit, pages=pages)


# 5. Disputes
@router.get("/disputes", response_model=PaginatedDisputesResponse, summary="List Customer Disputes")
def list_disputes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (LODGED, UNDER_INVESTIGATION, etc.)"),
    search: Optional[str] = Query(None, description="Search by business ID"),
    db: Session = Depends(get_db),
):
    query = select(Dispute)
    if status:
        query = query.where(Dispute.status == status.upper())
    if search:
        query = query.where(Dispute.business_id.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    records = db.scalars(
        query.order_by(Dispute.lodged_at.desc(), Dispute.business_id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    items = [
        DisputeItem(
            dispute_id=r.dispute_id,
            business_id=r.business_id,
            invoice_id=r.invoice_id,
            dispute_reason=r.dispute_reason,
            disputed_amount=float(r.disputed_amount),
            status=r.status,
            lodged_at=r.lodged_at,
            resolved_at=r.resolved_at,
            created_at=r.created_at,
        )
        for r in records
    ]
    pages = math.ceil(total / limit) if total > 0 else 1
    return PaginatedDisputesResponse(items=items, total=total, page=page, limit=limit, pages=pages)
