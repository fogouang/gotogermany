"""
app/modules/payments/router.py

Endpoints :
  POST /payments                              → initier un paiement (Kratos Mobile Money)
  GET  /payments/status/{ref}                 → polling statut (frontend)
  GET  /payments/me                           → historique paiements user
  GET  /payments/{payment_id}                 → détail d'un paiement
  POST /payments/kratos/webhook/{secret}      → webhook Kratos Pay (signé HMAC)
  POST /payments/callback/{secret}            → callback pawaPay (anciens paiements + relais Lumina)
  GET  /payments/admin/summary                → stats admin
"""
import json
import logging
from uuid import UUID

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.modules.payments.kratos import KratosClient
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
    Initie un paiement Mobile Money (Kratos Pay) pour l'accès à un niveau.

    - `level_id` ou `sd_level` : le niveau à débloquer
    - `plan_id` : durée choisie (7j, 1 mois, 3 mois…)
    - `operator` : "MTN" | "ORANGE"
    - `phone_number` : numéro mobile money
    - `promo_code` : code partenaire optionnel

    L'élève confirme ensuite sur son téléphone.
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


# ── Webhooks ──────────────────────────────────────────────

# URL obfusquée — ne pas documenter publiquement
_WEBHOOK_SECRET = "jkdKo0Lp8lsdfjk4j0HJhskfak93d"


@router.post(f"/kratos/webhook/{_WEBHOOK_SECRET}", include_in_schema=False)
async def kratos_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook Kratos Pay. On garde le corps brut : la signature HMAC porte dessus.
    Tout est journalisé en entier tant que le format n'est pas confirmé.
    """
    raw_body = await request.body()
    signature = request.headers.get("x-mok-signature")
    logger.info(
        f"Webhook Kratos reçu — headers={dict(request.headers)} body={raw_body.decode('utf-8', 'replace')}"
    )

    if not KratosClient.verify_signature(raw_body, signature):
        if get_settings().KRATOS_WEBHOOK_STRICT:
            logger.warning("Webhook Kratos rejeté : signature absente ou invalide")
            # Pas de 200 sur une erreur de vérification (recommandation Kratos)
            return JSONResponse(status_code=401, content={"status": "invalid_signature"})
        logger.warning("Webhook Kratos : signature non vérifiée, traité quand même (KRATOS_WEBHOOK_STRICT=false)")

    try:
        payload = json.loads(raw_body or b"{}")
    except ValueError:
        logger.error("Webhook Kratos : corps JSON illisible")
        return JSONResponse(status_code=400, content={"status": "invalid_body"})

    try:
        found = await PaymentService(db).handle_kratos_webhook(payload)
    except Exception as e:
        logger.exception(f"Webhook Kratos : erreur de traitement : {e}")
        # 500 : Kratos pourra renvoyer l'événement
        return JSONResponse(status_code=500, content={"status": "error"})

    # Référence inconnue : 200 quand même, inutile que Kratos renvoie en boucle
    return {"status": "OK" if found else "ignored"}


def _metadata_app(body: dict) -> str | None:
    """Lit metadata.app, que pawaPay le renvoie en objet ou en liste d'objets."""
    metadata = body.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get("app")
    if isinstance(metadata, list):
        for item in metadata:
            if isinstance(item, dict) and "app" in item:
                return item["app"]
    return None


@router.post(f"/callback/{_WEBHOOK_SECRET}", include_in_schema=False)
async def payment_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Callback pawaPay : paiements lancés avant la bascule, et relais vers Lumina."""
    body = await request.json()
    app_tag = _metadata_app(body)

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
    Crée un paiement validé manuellement sans passer par l'opérateur de paiement.

    Cas d'usage :
    - Kratos indisponible
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