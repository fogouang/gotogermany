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
    ManualPaymentRequest,
    ManualPaymentResponse,
    PawapayCallbackPayload,
    PaymentAdminResponse,
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentResponse,
    PaymentStatusResponse,
    PaymentSummaryResponse,
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

from app.modules.auth.dependencies import CurrentAmbassador

@router.post("/manual/ambassador", response_model=dict)
async def create_ambassador_manual_payment(
    data: ManualPaymentRequest,
    ambassador: CurrentAmbassador,
    db: AsyncSession = Depends(get_db),
):
    """Permet à un ambassadeur de confirmer manuellement un paiement
    pour l'un de ses propres filleuls, quand pawaPay est instable —
    scope volontairement limité à ses filleuls, contrairement à la
    route admin équivalente."""
    return await PaymentService(db).create_manual_payment(
        data, admin=ambassador, require_referral_match=True
    )
    
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

# Remplacer tout le bloc webhook par :
@router.post(f"/callback/{_WEBHOOK_SECRET}", include_in_schema=False)
async def payment_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.json()
    app_tag = (body.get("metadata") or {}).get("app")

    if app_tag == "lumina":
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                await client.post(
                    "https://lumina-tcf.online/api/v1/payments/callback/jkdKo0Lp8lsdfjk4j0HJhskfak93d",
                    json=body,
                )
                return {"status": "OK"}
            except Exception as e:
                logger.error(f"Échec relais vers Lumina: {e}")
                return {"status": "KO"}

    try:
        payload = PawapayCallbackPayload(**body)
        await PaymentService(db).handle_callback(payload)
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Callback error: {e}")
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



@router.post(
    "/admin/manual",
    response_model=ManualPaymentResponse,
    status_code=201,
    summary="[Admin] Valider un paiement manuellement",
)
async def create_manual_payment(
    data: ManualPaymentRequest,
    current_admin: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """
    Crée un paiement validé manuellement sans passer par My-CoolPay.

    Cas d'usage :
    - My-CoolPay indisponible
    - Paiement par virement bancaire
    - Paiement cash en présentiel
    - Accès offert / correction admin

    L'ExamAccess est créé immédiatement (même flow que le webhook).
    La facture PDF est générée automatiquement.
    """
    result = await PaymentService(db).create_manual_payment(data, current_admin)
    return ManualPaymentResponse(**result)


@router.get("/admin/manual-list", response_model=list[PaymentAdminResponse])
async def list_manual_payments(
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """
    Liste tous les paiements manuels d'exam — admin uniquement.
    operator=MANUAL + exam_id non null (exclut les crédits IA).
    """
    payments = await PaymentService(db).get_manual_payments()
    return [PaymentAdminResponse.model_validate(p) for p in payments]