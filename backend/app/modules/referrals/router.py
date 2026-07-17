"""
app/modules/referrals/router.py
"""
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import CurrentAdmin, CurrentAmbassador
from app.modules.referrals.schemas import ReferralDashboardResponse, SetAmbassadorRequest
from app.modules.referrals.service import ReferralService
from app.shared.database.session import get_db
from app.shared.schemas.responses import SuccessResponse

router = APIRouter()


@router.get("/me", response_model=ReferralDashboardResponse)
async def my_referral_dashboard(
    ambassador: CurrentAmbassador,
    db: AsyncSession = Depends(get_db),
):
    """Lien de parrainage, liste des filleuls, et gains cumulés —
    réservé aux ambassadeurs."""
    return await ReferralService(db).get_dashboard(ambassador.id)


@router.post("/admin/set-ambassador", response_model=SuccessResponse)
async def set_ambassador_status(
    data: SetAmbassadorRequest,
    _: CurrentAdmin,
    db: AsyncSession = Depends(get_db),
):
    """Admin : active ou désactive le statut ambassadeur pour un user."""
    await ReferralService(db).set_ambassador_status(data.user_id, data.is_ambassador)
    return SuccessResponse(
        message=f"Statut ambassadeur {'activé' if data.is_ambassador else 'désactivé'}."
    )