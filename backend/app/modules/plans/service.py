"""
app/modules/plans/service.py
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.plans.models import Plan
from app.modules.plans.repository import PlanRepository
from app.modules.plans.schemas import PlanCreate, PlanUpdate
from app.shared.exceptions.http import NotFoundException


class PlanService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PlanRepository(db)

    async def get_active_plans(self) -> list[Plan]:
        return await self.repo.get_active_plans()

    async def get_by_id(self, plan_id: UUID) -> Plan:
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise NotFoundException(resource="Plan", identifier=str(plan_id))
        return plan

    async def create(self, data: PlanCreate) -> Plan:
        return await self.repo.create(**data.model_dump())

    async def update(self, plan_id: UUID, data: PlanUpdate) -> Plan:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.repo.get_by_id_or_404(plan_id)
        return await self.repo.update(plan_id, **update_data)

    async def delete(self, plan_id: UUID) -> bool:
        return await self.repo.delete(plan_id)