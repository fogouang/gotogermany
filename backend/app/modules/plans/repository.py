"""
app/modules/plans/repository.py
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.plans.models import Plan
from app.shared.database.repository import BaseRepository


class PlanRepository(BaseRepository[Plan]):

    def __init__(self, db: AsyncSession):
        super().__init__(Plan, db)

    async def get_active_plans(self) -> list[Plan]:
        result = await self.db.execute(
            select(Plan)
            .where(Plan.is_active == True)
            .order_by(Plan.display_order, Plan.price)
        )
        return list(result.scalars().all())