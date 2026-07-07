"""
app/modules/centers/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.centers.models import Center, Branch, LicenseFormula, CenterLicense, LicenseStatus
from app.modules.centers.repository import (
    CenterRepository,
    BranchRepository,
    LicenseFormulaRepository,
    CenterLicenseRepository,
)
from app.modules.centers.schemas import (
    CenterCreateRequest,
    BranchCreateRequest,
    LicenseFormulaCreateRequest,
    CenterLicenseActivateRequest,
    CenterLicenseExtendRequest,
    LicenseUsageResponse,
)
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException


class CenterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.center_repo = CenterRepository(db)
        self.branch_repo = BranchRepository(db)
        self.formula_repo = LicenseFormulaRepository(db)
        self.license_repo = CenterLicenseRepository(db)

    # ── Admin ITIA ────────────────────────────

    async def create_center(self, data: CenterCreateRequest) -> Center:
        center = await self.center_repo.create(
            name=data.name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            is_active=True,
        )
        # Branch "principale" créée automatiquement, transparente pour le centre
        await self.branch_repo.create(
            center_id=center.id,
            name=f"{center.name} — Principal",
            is_main=True,
        )
        return center

    async def create_branch(self, center_id: UUID, data: BranchCreateRequest) -> Branch:
        center = await self.center_repo.get_by_id_or_404(center_id)
        return await self.branch_repo.create(
            center_id=center.id,
            name=data.name,
            is_main=data.is_main,
        )

    async def create_formula(self, data: LicenseFormulaCreateRequest) -> LicenseFormula:
        return await self.formula_repo.create(
            label=data.label,
            duration_months=data.duration_months,
            max_students=data.max_students,
            is_active=True,
        )

    async def activate_license(
        self, center_id: UUID, data: CenterLicenseActivateRequest, activated_by: User
    ) -> CenterLicense:
        center = await self.center_repo.get_by_id_or_404(center_id)
        formula = await self.formula_repo.get_by_id_or_404(data.formula_id)

        existing_active = await self.license_repo.get_active_for_center(center_id)
        if existing_active:
            raise BadRequestException(
                detail="Ce centre a déjà une licence active. Utilisez l'extension ou attendez l'expiration."
            )

        start_date = datetime.now(timezone.utc)
        end_date = start_date + relativedelta(months=formula.duration_months)

        return await self.license_repo.create(
            center_id=center.id,
            formula_id=formula.id,
            start_date=start_date,
            end_date=end_date,
            max_students=formula.max_students,
            status=LicenseStatus.active,
            payment_method=data.payment_method,
            payment_reference=data.payment_reference,
            activated_by=activated_by.id,
        )

    async def extend_license(
        self, center_id: UUID, data: CenterLicenseExtendRequest
    ) -> CenterLicense:
        license_ = await self.license_repo.get_active_for_center(center_id)
        if not license_:
            raise BadRequestException(detail="Aucune licence active pour ce centre.")

        return await self.license_repo.update(
            license_.id,
            max_students=license_.max_students + data.additional_students,
            payment_method=data.payment_method,
            payment_reference=data.payment_reference,
            # end_date inchangée — l'extension suit le prorata jusqu'à la licence existante
        )

    # ── Directeur ─────────────────────────────

    async def get_usage_for_center(self, center_id: UUID) -> LicenseUsageResponse:
            license_ = await self.license_repo.get_active_for_center(center_id)
            students_used = await self.license_repo.count_students_for_center(center_id)
            branches = await self.branch_repo.find_by_center(center_id)

            breakdown = {}
            for branch in branches:
                breakdown[branch.name] = await self.license_repo.count_students_for_branch(branch.id)

            days_remaining = None
            formula_label = None
            if license_:
                delta = license_.end_date - datetime.now(timezone.utc)
                days_remaining = max(delta.days, 0)

                formula = await self.formula_repo.get_by_id_or_404(license_.formula_id)
                formula_label = formula.label

            return LicenseUsageResponse(
                license=license_,
                formula_label=formula_label,          
                students_used=students_used,
                students_remaining=max((license_.max_students - students_used), 0) if license_ else 0,
                days_remaining=days_remaining,
                branches_breakdown=breakdown,
            )

    async def check_quota_available(self, center_id: UUID) -> None:
        """Lève une exception si le quota de la licence active est atteint.
        Appelé avant toute création de student par une secrétaire."""
        license_ = await self.license_repo.get_active_for_center(center_id)
        if not license_:
            raise BadRequestException(detail="Aucune licence active pour ce centre.")

        if license_.end_date < datetime.now(timezone.utc):
            raise BadRequestException(detail="La licence de ce centre a expiré.")

        used = await self.license_repo.count_students_for_center(center_id)
        if used >= license_.max_students:
            raise BadRequestException(
                detail="Quota d'étudiants atteint pour cette licence. Contactez votre direction pour une extension."
            )
            
    
    async def list_centers(self, skip: int = 0, limit: int = 100) -> list[Center]:
        return list(await self.center_repo.get_all(skip=skip, limit=limit))

    async def list_active_formulas(self) -> list[LicenseFormula]:
        return await self.formula_repo.get_active_formulas()
    
    async def list_my_branches(self, center_id: UUID) -> list[Branch]:
        return await self.branch_repo.find_by_center(center_id)
    