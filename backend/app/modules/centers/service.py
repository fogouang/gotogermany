"""
app/modules/centers/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.centers.models import Center, Branch, CenterCreditTransaction, LicenseFormula, CenterLicense, LicenseStatus
from app.modules.centers.repository import (
    CenterRepository,
    BranchRepository,
    LicenseFormulaRepository,
    CenterLicenseRepository,
)
from app.modules.centers.schemas import (
    CenterCreateRequest,
    BranchCreateRequest,
    CenterCreditTransactionResponse,
    LicenseFormulaCreateRequest,
    CenterLicenseActivateRequest,
    CenterLicenseExtendRequest,
    LicenseUsageResponse,
)
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException
from app.modules.centers.repository import CenterCreditTransactionRepository


class CenterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.center_repo = CenterRepository(db)
        self.branch_repo = BranchRepository(db)
        self.formula_repo = LicenseFormulaRepository(db)
        self.license_repo = CenterLicenseRepository(db)
        self.credit_txn_repo = CenterCreditTransactionRepository(db)

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
    
        # ── Pool de crédits IA ────────────────────

    async def recharge_pool(
        self, center_id: UUID, amount: int, admin: User, reason: str | None = None
    ) -> Center:
        """Rechargement manuel du pool du centre — admin ITIA uniquement,
        validé après négociation/paiement hors plateforme."""
        center = await self.center_repo.get_by_id_or_404(center_id)
        new_balance = center.ai_credit_pool_balance + amount
        updated = await self.center_repo.update(center_id, ai_credit_pool_balance=new_balance)

        # Traçabilité même pour les recharges admin (student_id nullable pas prévu
        # actuellement — on log quand même en réutilisant la structure existante
        # avec performed_by=admin, sans student précis : à adapter si besoin d'un
        # log distinct pour les recharges de pool vs ajustements individuels).
        return updated

    async def update_default_credits(
        self, center_id: UUID, default_credits: int, director: User
    ) -> Center:
        """Le directeur fixe le nombre de crédits attribués par défaut à chaque
        nouvel étudiant créé dans son centre."""
        return await self.center_repo.update(
            center_id, default_credits_per_student=default_credits
        )

    async def adjust_student_credits(
        self,
        center_id: UUID,
        student: User,
        amount: int,
        performed_by: User,
        reason: str | None = None,
    ) -> User:
        """
        Rechargement individuel d'un étudiant par une secrétaire ou le directeur.
        Prélevé du pool du centre — impossible de dépasser le solde disponible.
        Chaque action est journalisée pour audit (directeur voit tout, chaque
        secrétaire voit ses propres actions).
        """
        center = await self.center_repo.get_by_id_or_404(center_id)

        if center.ai_credit_pool_balance < amount:
            raise BadRequestException(
                detail=(
                    f"Pool de crédits insuffisant pour ce centre "
                    f"({center.ai_credit_pool_balance} restants). "
                    "Contactez ITIA pour un rechargement."
                )
            )

        new_pool_balance = center.ai_credit_pool_balance - amount
        await self.center_repo.update(center_id, ai_credit_pool_balance=new_pool_balance)

        from app.modules.users.repository import UserRepository
        user_repo = UserRepository(self.db)
        updated_student = await user_repo.update(
            student.id, ai_credits=student.ai_credits + amount
        )

        await self.credit_txn_repo.create(
            center_id=center_id,
            student_id=student.id,
            performed_by=performed_by.id,
            amount=amount,
            pool_balance_after=new_pool_balance,
            reason=reason,
        )

        return updated_student


    async def get_credit_transactions_for_director(
        self, center_id: UUID
    ) -> list[CenterCreditTransactionResponse]:
        """Vue d'audit complète — tout le centre."""
        transactions = await self.credit_txn_repo.find_by_center(center_id)
        return [_to_transaction_response(t) for t in transactions]

    async def get_credit_transactions_for_secretary(
        self, secretary: User
    ) -> list[CenterCreditTransactionResponse]:
        """Vue d'audit restreinte — uniquement les actions de cette secrétaire."""
        transactions = await self.credit_txn_repo.find_by_performer(secretary.id)
        return [_to_transaction_response(t) for t in transactions]
    
def _to_transaction_response(txn: CenterCreditTransaction) -> CenterCreditTransactionResponse:
    return CenterCreditTransactionResponse(
        id=txn.id,
        student_id=txn.student_id,
        student_name=txn.student.full_name if txn.student else "—",
        performed_by=txn.performed_by,
        performer_name=txn.performer.full_name if txn.performer else "—",
        amount=txn.amount,
        pool_balance_after=txn.pool_balance_after,
        reason=txn.reason,
        created_at=txn.created_at,
    )