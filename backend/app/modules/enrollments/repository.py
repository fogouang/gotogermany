"""
app/modules/enrollments/repository.py
"""
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.enrollments.models import (
    Cursus, LevelEnrollment, FormationPayment,
    CursusStatus, LevelEnrollmentStatus, FormationPaymentType,
)
from app.modules.centers.models import Branch
from app.shared.database.repository import BaseRepository


class CursusRepository(BaseRepository[Cursus]):
    def __init__(self, db: AsyncSession):
        super().__init__(Cursus, db)

    async def find_by_center(self, center_id: UUID) -> list[Cursus]:
        """Vue directeur — tous les cursus du centre, toutes branches confondues."""
        result = await self.db.execute(
            select(Cursus)
            .join(Branch, Cursus.branch_id == Branch.id)
            .where(Branch.center_id == center_id)
            .options(selectinload(Cursus.student), selectinload(Cursus.level_enrollments))
        )
        return list(result.scalars().all())

    async def find_by_branch(self, branch_id: UUID) -> list[Cursus]:
        """Vue secrétaire — restreinte à sa branche."""
        result = await self.db.execute(
            select(Cursus)
            .where(Cursus.branch_id == branch_id)
            .options(selectinload(Cursus.student), selectinload(Cursus.level_enrollments))
        )
        return list(result.scalars().all())

    async def get_by_id_scoped(
        self, cursus_id: UUID, center_id: UUID, branch_id: UUID | None = None
    ) -> Cursus | None:
        """Jamais d'accès par id seul dans ce module — toujours scopé au centre,
        et en plus à la branche si fourni (branch_id=None = directeur, tout le centre).
        Garantit l'étanchéité entre centres ET entre branches d'un même centre."""
        conditions = [Cursus.id == cursus_id, Branch.center_id == center_id]
        if branch_id is not None:
            conditions.append(Cursus.branch_id == branch_id)

        result = await self.db.execute(
            select(Cursus)
            .join(Branch, Cursus.branch_id == Branch.id)
            .where(*conditions)
            .options(selectinload(Cursus.student), selectinload(Cursus.level_enrollments))
        )
        return result.scalar_one_or_none()


class LevelEnrollmentRepository(BaseRepository[LevelEnrollment]):
    def __init__(self, db: AsyncSession):
        super().__init__(LevelEnrollment, db)

    async def get_by_id_scoped(
        self, enrollment_id: UUID, center_id: UUID, branch_id: UUID | None = None
    ) -> LevelEnrollment | None:
        """Même principe que CursusRepository.get_by_id_scoped : scopé centre +
        branche optionnelle, jamais d'accès par id seul."""
        conditions = [LevelEnrollment.id == enrollment_id, Branch.center_id == center_id]
        if branch_id is not None:
            conditions.append(Cursus.branch_id == branch_id)

        result = await self.db.execute(
            select(LevelEnrollment)
            .join(Cursus, LevelEnrollment.cursus_id == Cursus.id)
            .join(Branch, Cursus.branch_id == Branch.id)
            .where(*conditions)
            .options(selectinload(LevelEnrollment.payments))
        )
        return result.scalar_one_or_none()


class FormationPaymentRepository(BaseRepository[FormationPayment]):
    def __init__(self, db: AsyncSession):
        super().__init__(FormationPayment, db)

    async def sum_paid(self, enrollment_id: UUID, payment_type: FormationPaymentType) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(FormationPayment.amount), 0)).where(
                FormationPayment.enrollment_id == enrollment_id,
                FormationPayment.payment_type == payment_type,
            )
        )
        return result.scalar_one()

    async def find_by_enrollment(self, enrollment_id: UUID) -> list[FormationPayment]:
        result = await self.db.execute(
            select(FormationPayment)
            .where(FormationPayment.enrollment_id == enrollment_id)
            .order_by(FormationPayment.paid_at.desc())
        )
        return list(result.scalars().all())

    async def count_for_center(self, center_id: UUID) -> int:
        """Utilisé pour générer un numéro de facture séquentiel par centre."""
        result = await self.db.execute(
            select(func.count(FormationPayment.id))
            .join(LevelEnrollment, FormationPayment.enrollment_id == LevelEnrollment.id)
            .join(Cursus, LevelEnrollment.cursus_id == Cursus.id)
            .join(Branch, Cursus.branch_id == Branch.id)
            .where(Branch.center_id == center_id)
        )
        return result.scalar_one()
    

    async def get_by_level_enrollment(self, enrollment_id: UUID) -> Cursus | None:
        result = await self.db.execute(
            select(Cursus)
            .join(LevelEnrollment, LevelEnrollment.cursus_id == Cursus.id)
            .where(LevelEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()
    

    async def sum_for_center(self, center_id: UUID) -> int:
        """Revenu total encaissé (tous types de paiement confondus) pour un centre."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(FormationPayment.amount), 0))
            .join(LevelEnrollment, FormationPayment.enrollment_id == LevelEnrollment.id)
            .join(Cursus, LevelEnrollment.cursus_id == Cursus.id)
            .join(Branch, Cursus.branch_id == Branch.id)
            .where(Branch.center_id == center_id)
        )
        return result.scalar_one()

    async def sum_by_branch_for_center(self, center_id: UUID) -> dict[str, int]:
        """Revenu total par succursale, pour la vue directeur."""
        result = await self.db.execute(
            select(Branch.name, func.coalesce(func.sum(FormationPayment.amount), 0))
            .join(Cursus, Cursus.branch_id == Branch.id)
            .join(LevelEnrollment, LevelEnrollment.cursus_id == Cursus.id)
            .join(FormationPayment, FormationPayment.enrollment_id == LevelEnrollment.id)
            .where(Branch.center_id == center_id)
            .group_by(Branch.name)
        )
        return {name: total for name, total in result.all()}