"""
app/modules/partners/repository.py
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partners.models import Partner
from app.shared.database.repository import BaseRepository


class PartnerRepository(BaseRepository[Partner]):

    def __init__(self, db: AsyncSession):
        super().__init__(Partner, db)

    async def find_by_email(self, email: str) -> Partner | None:
        result = await self.db.execute(
            select(Partner).where(Partner.contact_email == email)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Partner]:
        result = await self.db.execute(
            select(Partner)
            .where(Partner.is_active == True)
            .order_by(Partner.name)
        )
        return list(result.scalars().all())