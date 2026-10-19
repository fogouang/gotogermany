"""
app/modules/centers/repository.py
"""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.centers.models import Center, Branch, CenterCreditTransaction
from app.shared.database.repository import BaseRepository


class CenterRepository(BaseRepository[Center]):
    def __init__(self, db: AsyncSession):
        super().__init__(Center, db)

    async def find_by_join_token(self, token: str) -> Center | None:
        result = await self.db.execute(select(Center).where(Center.join_token == token))
        return result.scalar_one_or_none()


class BranchRepository(BaseRepository[Branch]):
    def __init__(self, db: AsyncSession):
        super().__init__(Branch, db)

    async def find_by_center(self, center_id: UUID) -> list[Branch]:
        result = await self.db.execute(
            select(Branch).where(Branch.center_id == center_id)
        )
        return list(result.scalars().all())


class CenterCreditTransactionRepository(BaseRepository[CenterCreditTransaction]):
    def __init__(self, db: AsyncSession):
        super().__init__(CenterCreditTransaction, db)

    async def find_by_center(self, center_id: UUID) -> list[CenterCreditTransaction]:
        """Vue directeur : tout l'historique du centre."""
        result = await self.db.execute(
            select(CenterCreditTransaction)
            .options(
                selectinload(CenterCreditTransaction.student),
                selectinload(CenterCreditTransaction.performer),
            )
            .where(CenterCreditTransaction.center_id == center_id)
            .order_by(CenterCreditTransaction.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_by_performer(self, performer_id: UUID) -> list[CenterCreditTransaction]:
        """Vue secrétaire : uniquement ses propres actions."""
        result = await self.db.execute(
            select(CenterCreditTransaction)
            .options(
                selectinload(CenterCreditTransaction.student),
                selectinload(CenterCreditTransaction.performer),
            )
            .where(CenterCreditTransaction.performed_by == performer_id)
            .order_by(CenterCreditTransaction.created_at.desc())
        )
        return list(result.scalars().all())