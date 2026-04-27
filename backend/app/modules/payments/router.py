"""
app/modules/payments/router.py

Endpoints :
  POST /payments/initiate              → initier un paiement
  GET  /payments/status/{ref}          → polling statut (frontend)
  GET  /payments/me                    → historique paiements user
  GET  /payments/{payment_id}          → détail d'un paiement
  POST /payments/webhook/{secret}      → callback My-CoolPay
  GET  /payments/admin/summary         → stats admin
"""
import logging
from uuid import UUID

from fastapi import Depends, Request
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.payments.schemas import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentResponse,
    PaymentStatusResponse,
    PaymentSummaryResponse,
    WebhookPayload,
)
from app.modules.payments.service import PaymentService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# ── User ─────────────────────────────────────────────────

@router.post("", response_model=PaymentInitiateResponse, status_code=201)
async def initiate_payment(
    data: PaymentInitiateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Initie un paiement mobile money pour l'accès à un exam.

    - `exam_id` : l'exam que l'étudiant veut débloquer
    - `plan_id` : durée choisie (7j, 1 mois, 3 mois…)
    - `operator` : "MTN" | "ORANGE"
    - `phone_number` : numéro mobile money
    - `promo_code` : code partenaire optionnel

    Retourne un code USSD à composer sur le téléphone.
    """
    result = await PaymentService(db).initiate_payment(data, current_user)
    return PaymentInitiateResponse(**result)


@router.get("/status/{transaction_reference}", response_model=PaymentStatusResponse)
async def get_payment_status(
    transaction_reference: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Polling statut d'un paiement.
    Appelé toutes les 5s par le frontend jusqu'à COMPLETED ou FAILED.
    Retourne aussi `exam_access_granted` pour savoir si l'accès est actif.
    """
    result = await PaymentService(db).get_status(transaction_reference, current_user)
    return PaymentStatusResponse(**result)


@router.get("/me", response_model=list[PaymentResponse])
async def get_my_payments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Historique des paiements de l'utilisateur connecté."""
    payments = await PaymentService(db).get_my_payments(current_user)
    return [PaymentResponse.model_validate(p) for p in payments]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Détail d'un paiement."""
    payment = await PaymentService(db).get_by_id(payment_id)
    return PaymentResponse.model_validate(payment)


# ── Webhook My-CoolPay ────────────────────────────────────

# URL obfusquée — ne pas documenter publiquement
_WEBHOOK_SECRET = "jkdKo0Lp8lsdfjk4j0HJhskfak93d"

@router.post(f"/webhook/{_WEBHOOK_SECRET}", include_in_schema=False)
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Callback My-CoolPay — appelé après confirmation paiement.
    ⚠️  Pas d'auth — sécurisé par signature MD5 + URL secrète.
    """
    try:
        body = await request.json()
        webhook_data = WebhookPayload(**body)
        await PaymentService(db).handle_webhook(webhook_data)
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "KO"}


# ── Admin ─────────────────────────────────────────────────

@router.get("/admin/summary", response_model=PaymentSummaryResponse)
async def get_summary(
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Stats paiements — admin uniquement."""
    summary = await PaymentService(db).repo.get_summary()
    return PaymentSummaryResponse(**summary)