"""
app/modules/invoices/router.py
"""
from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentUser
from app.modules.invoices.schemas import InvoiceResponse
from app.modules.invoices.service import InvoiceService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


@router.post("/generate/{payment_id}", status_code=201)
async def generate_invoice(
    payment_id: UUID,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Génère ou régénère la facture PDF d'un paiement."""
    invoice_url = await InvoiceService(db).generate_invoice_for_payment(payment_id)
    return SuccessResponse(message="Facture générée.", data={"invoice_url": invoice_url})


@router.get("/payment/{payment_id}", response_model=InvoiceResponse)
async def get_invoice(
    payment_id: UUID,
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Détails de la facture d'un paiement."""
    data = await InvoiceService(db).get_invoice_by_payment(payment_id)
    return InvoiceResponse(**data)