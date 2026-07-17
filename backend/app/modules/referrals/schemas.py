"""
app/modules/referrals/schemas.py
"""
import uuid
from datetime import datetime
from app.shared.schemas.base import BaseSchema


class ReferredUserItem(BaseSchema):
    """Une ligne dans la liste des filleuls de l'ambassadeur."""
    user_id: uuid.UUID
    name: str
    joined_at: datetime
    has_paid: bool
    total_earned_from_this_user: int  # somme des gains liés à ce filleul, en FCFA


class ReferralDashboardResponse(BaseSchema):
    """Vue complète du dashboard parrainage d'un ambassadeur."""
    referral_link: str
    referral_code: str
    referred_count: int
    total_earnings: int  # somme de tous les gains, en FCFA
    referred_users: list[ReferredUserItem]


class SetAmbassadorRequest(BaseSchema):
    """Admin : active/désactive le statut ambassadeur pour un user."""
    user_id: uuid.UUID
    is_ambassador: bool