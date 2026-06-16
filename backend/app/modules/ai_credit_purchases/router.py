"""
app/modules/ai_credit_purchases/router.py

GET  /ai-credits/pricing       → prix par crédit
GET  /ai-credits/balance       → solde utilisateur
POST /ai-credits/purchase      → acheter via MyCoolPay
GET  /ai-credits/history       → historique achats
POST /ai-credits/admin/grant   → accord manuel admin
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_credit_purchases.schemas import (
    CreditBalanceResponse,
    CreditPricingResponse,
    CreditPurchaseHistoryItem,
    CreditPurchaseHistoryResponse,
    CreditPurchaseRequest,
    CreditPurchaseResponse,
    ManualCreditGrantRequest,
    ManualCreditGrantResponse,
)
from app.modules.ai_credit_purchases.service import AICreditPurchaseService
from app.modules.auth.dependencies import CurrentAdmin, CurrentUser
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter(prefix="/ai-credits", tags=["AI Credits"])


async def get_service(db: AsyncSession = Depends(get_db)) -> AICreditPurchaseService:
    return AICreditPurchaseService(db)

Service = Annotated[AICreditPurchaseService, Depends(get_service)]


# ── User ─────────────────────────────────────────────────────────────────────

@router.get("/pricing", response_model=SuccessResponse[CreditPricingResponse])
async def get_pricing(service: Service):
    return SuccessResponse(data=service.get_pricing_info(), message="OK")


@router.get("/balance", response_model=SuccessResponse[CreditBalanceResponse])
async def get_balance(service: Service, current_user: CurrentUser):
    balance = await service.get_balance(current_user.id)
    return SuccessResponse(data=balance, message="OK")


@router.post("/purchase", response_model=SuccessResponse[CreditPurchaseResponse], status_code=201)
async def purchase_credits(data: CreditPurchaseRequest, service: Service, current_user: CurrentUser):
    result = await service.purchase_credits(user_id=current_user.id, data=data)
    return SuccessResponse(data=result, message="Paiement initié")


@router.get("/history", response_model=SuccessResponse[CreditPurchaseHistoryResponse])
async def get_history(service: Service, current_user: CurrentUser):
    history = await service.get_purchase_history(current_user.id)
    return SuccessResponse(data=history, message="OK")


# ── Admin ─────────────────────────────────────────────────────────────────────

@router.post("/admin/grant", response_model=SuccessResponse[ManualCreditGrantResponse], status_code=201)
async def admin_grant(data: ManualCreditGrantRequest, service: Service, current_admin: CurrentAdmin):
    result = await service.grant_manual(data=data, admin_id=current_admin.id)
    return SuccessResponse(data=result, message=f"{data.credits} crédits accordés")

@router.get(
    "/admin/history",
    response_model=SuccessResponse[list[CreditPurchaseHistoryItem]],
    summary="[Admin] Historique des crédits accordés manuellement",
)
async def admin_history(
    service: Service,
    current_admin: CurrentAdmin,
    limit: int = 20,
):
    """
    Liste tous les crédits IA accordés manuellement (operator=MANUAL).
    Utilisé dans la page admin/paiements-manuels.
    """
    data = await service.get_admin_history(limit=limit)
    return SuccessResponse(data=data, message="OK")