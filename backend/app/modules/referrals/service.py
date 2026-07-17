"""
app/modules/referrals/service.py
"""
from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.referrals.models import ReferralEarning
from app.modules.referrals.schemas import ReferralDashboardResponse, ReferredUserItem
from app.modules.users.models import User
from app.config import get_settings

settings = get_settings()

# Taux de commission de parrainage, en % du montant du paiement.
# Constante globale pour l'instant — pas de taux par ambassadeur.
REFERRAL_COMMISSION_RATE = 10.0


class ReferralService:

    def __init__(self, db: AsyncSession):
        self.db = db

    def build_referral_link(self, user_id: uuid.UUID) -> str:
        code = self._code_for(user_id)
        base_url = settings.FRONTEND_BASE_URL.rstrip("/")
        return f"{base_url}/register?ref={code}"

    @staticmethod
    def _code_for(user_id: uuid.UUID) -> str:
        return str(user_id)[:8].upper()

    async def resolve_referrer(self, code: str) -> User | None:
        """Retrouve l'ambassadeur depuis le code présent dans l'URL
        d'inscription. Recherche par préfixe d'UUID puisque le code
        affiché n'est qu'un raccourci du user_id complet. Ne retourne
        un résultat que si l'utilisateur trouvé est bien ambassadeur —
        un ancien code d'un utilisateur qui a perdu ce statut ne doit
        plus créditer personne."""
        result = await self.db.execute(
            select(User).where(User.is_ambassador == True)
        )
        candidates = result.scalars().all()
        code_upper = code.upper()
        for candidate in candidates:
            if self._code_for(candidate.id) == code_upper:
                return candidate
        return None

    async def record_signup(self, new_user_id: uuid.UUID, referrer_id: uuid.UUID) -> None:
        """Appelé une seule fois, juste après la création du compte,
        si un code de parrainage valide était présent à l'inscription."""
        user = await self.db.get(User, new_user_id)
        if user is None or user.referred_by_user_id is not None:
            return  # jamais réécrit après coup
        user.referred_by_user_id = referrer_id
        await self.db.flush()

    async def record_payment_earning(
        self, *, payment_id: uuid.UUID, payer_user_id: uuid.UUID, payment_amount: int
    ) -> None:
        """Appelé après un paiement complété (automatique ou manuel).
        Ne fait rien si le payeur n'a pas de parrain, ou si ce paiement
        a déjà généré un gain (contrainte unique sur payment_id)."""
        payer = await self.db.get(User, payer_user_id)
        if payer is None or payer.referred_by_user_id is None:
            return

        existing = await self.db.execute(
            select(ReferralEarning).where(ReferralEarning.payment_id == payment_id)
        )
        if existing.scalar_one_or_none() is not None:
            return

        amount = int(payment_amount * REFERRAL_COMMISSION_RATE / 100)
        if amount <= 0:
            return

        earning = ReferralEarning(
            referrer_user_id=payer.referred_by_user_id,
            referred_user_id=payer_user_id,
            payment_id=payment_id,
            amount=amount,
        )
        self.db.add(earning)
        await self.db.flush()

    async def get_dashboard(self, ambassador_id: uuid.UUID) -> ReferralDashboardResponse:
        result = await self.db.execute(
            select(User).where(User.referred_by_user_id == ambassador_id)
        )
        referred_users = list(result.scalars().all())

        earnings_result = await self.db.execute(
            select(ReferralEarning).where(ReferralEarning.referrer_user_id == ambassador_id)
        )
        earnings = list(earnings_result.scalars().all())
        earnings_by_referred: dict[uuid.UUID, int] = {}
        for e in earnings:
            earnings_by_referred[e.referred_user_id] = (
                earnings_by_referred.get(e.referred_user_id, 0) + e.amount
            )

        items = [
            ReferredUserItem(
                user_id=ru.id,
                name=getattr(ru, "full_name", None) or ru.email,
                joined_at=ru.created_at,
                has_paid=ru.id in earnings_by_referred,
                total_earned_from_this_user=earnings_by_referred.get(ru.id, 0),
            )
            for ru in referred_users
        ]

        return ReferralDashboardResponse(
            referral_link=self.build_referral_link(ambassador_id),
            referral_code=self._code_for(ambassador_id),
            referred_count=len(referred_users),
            total_earnings=sum(e.amount for e in earnings),
            referred_users=items,
        )

    async def set_ambassador_status(self, user_id: uuid.UUID, is_ambassador: bool) -> None:
        """Admin uniquement — active/désactive le statut ambassadeur."""
        user = await self.db.get(User, user_id)
        if user is None:
            from app.shared.exceptions.http import NotFoundException
            raise NotFoundException(resource="User", identifier=str(user_id))
        user.is_ambassador = is_ambassador
        await self.db.commit()