"""
app/modules/promo_codes/repository.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promo_codes.models import PromoCode
from app.shared.database.repository import BaseRepository


class PromoCodeRepository(BaseRepository[PromoCode]):

    def __init__(self, db: AsyncSession):
        super().__init__(PromoCode, db)

    async def find_by_code(self, code: str) -> PromoCode | None:
        result = await self.db.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def get_by_partner(self, partner_id: UUID) -> list[PromoCode]:
        result = await self.db.execute(
            select(PromoCode)
            .where(PromoCode.partner_id == partner_id)
            .order_by(PromoCode.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_active(self) -> list[PromoCode]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(PromoCode)
            .where(
                PromoCode.is_active == True,
                (PromoCode.expires_at == None) | (PromoCode.expires_at > now),
            )
            .order_by(PromoCode.created_at.desc())
        )
        return list(result.scalars().all())

    async def increment_used_count(self, promo_code_id: UUID) -> PromoCode:
        """Incrémente used_count après un paiement complété."""
        code = await self.get_by_id_or_404(promo_code_id)
        return await self.update(promo_code_id, used_count=code.used_count + 1)