"""
app/modules/invoices/schemas.py
"""
import uuid
from datetime import datetime
from typing import Any
from app.shared.schemas.base import BaseSchema


class PartnerInfoResponse(BaseSchema):
    code: str
    partner_name: str
    commission_due: float


class InvoiceResponse(BaseSchema):
    transaction_reference: str
    payment_id: uuid.UUID
    amount_gross: int
    amount_paid: int
    discount_amount: int
    operator: str | None
    payment_date: datetime
    invoice_url: str | None
    customer_name: str | None
    customer_email: str | None
    product_description: str
    partner_info: PartnerInfoResponse | None = None