"""
Pydantic v2 schemas for core O2C transactional entity APIs.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# 1. Accounts
class AccountItem(BaseModel):
    account_id: uuid.UUID
    account_number: str
    account_name: str
    credit_limit: float
    payment_terms: str
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAccountsResponse(BaseModel):
    items: List[AccountItem]
    total: int
    page: int
    limit: int
    pages: int


# 2. Sales Orders
class OrderItem(BaseModel):
    order_id: uuid.UUID
    business_id: str
    account_id: uuid.UUID
    quote_id: Optional[uuid.UUID] = None
    status: str
    total_order_value: float
    currency: str
    order_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedOrdersResponse(BaseModel):
    items: List[OrderItem]
    total: int
    page: int
    limit: int
    pages: int


# 3. Invoices
class InvoiceItem(BaseModel):
    invoice_id: uuid.UUID
    business_id: str
    order_id: uuid.UUID
    account_id: uuid.UUID
    status: str
    total_invoiced_amount: float
    paid_amount: float
    outstanding_balance: float
    currency: str
    issue_date: datetime
    due_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedInvoicesResponse(BaseModel):
    items: List[InvoiceItem]
    total: int
    page: int
    limit: int
    pages: int


# 4. Payments
class PaymentItem(BaseModel):
    payment_id: uuid.UUID
    business_id: str
    account_id: uuid.UUID
    payment_method: str
    payment_reference: str
    amount_received: float
    amount_allocated: float
    unallocated_amount: float
    currency: str
    status: str
    payment_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedPaymentsResponse(BaseModel):
    items: List[PaymentItem]
    total: int
    page: int
    limit: int
    pages: int


# 5. Disputes
class DisputeItem(BaseModel):
    dispute_id: uuid.UUID
    business_id: str
    invoice_id: uuid.UUID
    dispute_reason: str
    disputed_amount: float
    status: str
    lodged_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedDisputesResponse(BaseModel):
    items: List[DisputeItem]
    total: int
    page: int
    limit: int
    pages: int
