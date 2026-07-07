"""
app/modules/centers/repository.py
"""
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.centers.models import Center, Branch, LicenseFormula, CenterLicense, LicenseStatus
from app.modules.users.models import User, UserRole
from app.shared.database.repository import BaseRepository


class CenterRepository(BaseRepository[Center]):
    def __init__(self, db: AsyncSession):
        super().__init__(Center, db)


class BranchRepository(BaseRepository[Branch]):
    def __init__(self, db: AsyncSession):
        super().__init__(Branch, db)

    async def find_by_center(self, center_id: UUID) -> list[Branch]:
        result = await self.db.execute(
            select(Branch).where(Branch.center_id == center_id)
        )
        return list(result.scalars().all())


class LicenseFormulaRepository(BaseRepository[LicenseFormula]):
    def __init__(self, db: AsyncSession):
        super().__init__(LicenseFormula, db)

    async def get_active_formulas(self) -> list[LicenseFormula]:
        result = await self.db.execute(
            select(LicenseFormula).where(LicenseFormula.is_active == True)
        )
        return list(result.scalars().all())


class CenterLicenseRepository(BaseRepository[CenterLicense]):
    def __init__(self, db: AsyncSession):
        super().__init__(CenterLicense, db)

    async def get_active_for_center(self, center_id: UUID) -> CenterLicense | None:
        result = await self.db.execute(
            select(CenterLicense).where(
                CenterLicense.center_id == center_id,
                CenterLicense.status == LicenseStatus.active,
            )
        )
        return result.scalar_one_or_none()

    async def count_students_for_center(self, center_id: UUID) -> int:
        """Cumulatif et permanent — compte tous les students jamais créés pour ce centre,
        actifs ou expirés (le quota n'est jamais libéré, cf. règle métier)."""
        result = await self.db.execute(
            select(func.count(User.id))
            .join(Branch, Branch.id == User.branch_id)
            .where(
                Branch.center_id == center_id,
                User.role == UserRole.student,
            )
        )
        return result.scalar_one()

    async def count_students_for_branch(self, branch_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(User.id)).where(
                User.branch_id == branch_id,
                User.role == UserRole.student,
            )
        )
        return result.scalar_one()
    
    async def find_secretaries_by_center(self, center_id: UUID) -> list[User]:
        from app.modules.centers.models import Branch
        result = await self.db.execute(
            select(User)
            .join(Branch, Branch.id == User.branch_id)
            .where(
                Branch.center_id == center_id,
                User.role == UserRole.branch_secretary,
            )
        )
        return list(result.scalars().all())