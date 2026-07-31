"""
app/modules/enrollments/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.enrollments.models import (
    Cursus, LevelEnrollment, FormationPayment,
    CursusStatus, LevelEnrollmentStatus, FormationPaymentType,
)
from app.modules.enrollments.repository import (
    CursusRepository, LevelEnrollmentRepository, FormationPaymentRepository,
)
from app.modules.enrollments.schemas import (
    CursusCreateRequest, LevelEnrollmentCreateRequest, PaymentCreateRequest,
)
from app.modules.centers.repository import BranchRepository
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException, ForbiddenException
from app.modules.enrollments.dependencies import CenterScope
import logging

logger = logging.getLogger(__name__)


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cursus_repo = CursusRepository(db)
        self.enrollment_repo = LevelEnrollmentRepository(db)
        self.payment_repo = FormationPaymentRepository(db)
        self.branch_repo = BranchRepository(db)

    # ── Cursus ────────────────────────────────

    async def create_cursus(self, scope: CenterScope, data: CursusCreateRequest) -> Cursus:
        branches = await self.branch_repo.find_by_center(scope.center_id)
        if data.branch_id not in [b.id for b in branches]:
            raise ForbiddenException(detail="Cette succursale n'appartient pas à votre centre.")

        # Une secrétaire ne peut créer un cursus que pour SA branche, pas une autre du même centre
        if not scope.is_director and data.branch_id != scope.branch_id:
            raise ForbiddenException(detail="Vous ne pouvez créer un cursus que pour votre propre succursale.")

        return await self.cursus_repo.create(
            student_id=data.student_id,
            branch_id=data.branch_id,
            start_level=data.start_level,
            target_level=data.target_level,
            status=CursusStatus.in_progress,
        )

    async def list_cursus_for_staff(self, scope: CenterScope) -> list[Cursus]:
        if scope.is_director:
            return await self.cursus_repo.find_by_center(scope.center_id)
        return await self.cursus_repo.find_by_branch(scope.branch_id)

    # ── Level enrollments ─────────────────────

    async def create_level_enrollment(
        self, scope: CenterScope, cursus_id: UUID, data: LevelEnrollmentCreateRequest
    ) -> LevelEnrollment:
        cursus = await self.cursus_repo.get_by_id_scoped(cursus_id, scope.center_id, scope.branch_id)
        if not cursus:
            raise NotFoundException(detail="Cursus introuvable pour votre périmètre.")

        return await self.enrollment_repo.create(
            cursus_id=cursus.id,
            level=data.level,
            inscription_fee_amount=data.inscription_fee_amount,
            formation_fee_amount=data.formation_fee_amount,
            status=LevelEnrollmentStatus.pending_inscription,
        )

    # ── Paiements ──────────────────────────────

    async def record_payment(
        self, scope: CenterScope, enrollment_id: UUID, data: PaymentCreateRequest, recorded_by: User
    ) -> FormationPayment:
        enrollment = await self.enrollment_repo.get_by_id_scoped(
            enrollment_id, scope.center_id, scope.branch_id
        )
        if not enrollment:
            raise NotFoundException(detail="Inscription introuvable pour votre périmètre.")

        # Règle bloquante : impossible de payer la formation avant d'avoir soldé l'inscription
        if data.payment_type == FormationPaymentType.formation:
            if enrollment.status == LevelEnrollmentStatus.pending_inscription:
                raise BadRequestException(
                    detail="Les frais d'inscription doivent être réglés avant tout paiement de formation."
                )

        # Règle bloquante : le paiement ne peut jamais dépasser le reste à payer
        already_paid = await self.payment_repo.sum_paid(enrollment.id, data.payment_type)
        due_amount = (
            enrollment.inscription_fee_amount
            if data.payment_type == FormationPaymentType.inscription
            else enrollment.formation_fee_amount
        )
        remaining = due_amount - already_paid
        if data.amount > remaining:
            raise BadRequestException(
                detail=f"Le montant dépasse le reste à payer ({remaining:,} FCFA)."
            )

        invoice_number = await self._generate_invoice_number(scope.center_id)

        payment = await self.payment_repo.create(
            enrollment_id=enrollment.id,
            payment_type=data.payment_type,
            amount=data.amount,
            paid_at=datetime.now(timezone.utc),
            recorded_by=recorded_by.id,
            notes=data.notes,
            invoice_number=invoice_number,
        )

        await self._refresh_enrollment_status(enrollment)

        from app.modules.invoices.service import InvoiceService
        try:
            invoice_url = await InvoiceService(self.db).generate_invoice_for_formation_payment(payment.id)
            payment = await self.payment_repo.update(payment.id, invoice_url=invoice_url)
        except Exception:
            logger.exception(
                "Échec de génération du reçu pour le paiement %s — paiement quand même enregistré.",
                payment.id,
            )

        return payment

    async def _refresh_enrollment_status(self, enrollment: LevelEnrollment) -> None:
        """Recalcule le statut à partir des paiements réels — jamais géré à la main
        par le staff, pour éviter toute incohérence entre montants saisis et statut affiché.
        Remonte aussi le statut au Cursus parent si le niveau visé vient d'être soldé."""
        inscription_paid = await self.payment_repo.sum_paid(
            enrollment.id, FormationPaymentType.inscription
        )
        formation_paid = await self.payment_repo.sum_paid(
            enrollment.id, FormationPaymentType.formation
        )

        new_status = enrollment.status
        if enrollment.status == LevelEnrollmentStatus.pending_inscription:
            if inscription_paid >= enrollment.inscription_fee_amount:
                new_status = LevelEnrollmentStatus.active
        elif enrollment.status == LevelEnrollmentStatus.active:
            if formation_paid >= enrollment.formation_fee_amount:
                new_status = LevelEnrollmentStatus.completed

        if new_status != enrollment.status:
            await self.enrollment_repo.update(enrollment.id, status=new_status)

            # Le cursus global passe à "terminé" seulement quand le niveau
            # complété est bien le niveau VISÉ (target_level) — atteindre un
            # niveau intermédiaire ne clôture pas le cursus.
            if new_status == LevelEnrollmentStatus.completed:
                cursus = await self.cursus_repo.get_by_level_enrollment(enrollment.id)
                if cursus and enrollment.level == cursus.target_level:
                    await self.cursus_repo.update(cursus.id, status=CursusStatus.completed)
                    

    async def _generate_invoice_number(self, center_id: UUID) -> str:
        """Séquentiel par centre — ex. INV-<center_id court>-000042.
        Pas de collision inter-centre puisque préfixé par center_id."""
        count = await self.payment_repo.count_for_center(center_id)
        short_id = str(center_id)[:8].upper()
        return f"INV-{short_id}-{count + 1:06d}"

    # ── Consultation ───────────────────────────

    async def get_balance_summary(self, scope: CenterScope, enrollment_id: UUID) -> dict:
        enrollment = await self.enrollment_repo.get_by_id_scoped(
            enrollment_id, scope.center_id, scope.branch_id
        )
        if not enrollment:
            raise NotFoundException(detail="Inscription introuvable pour votre périmètre.")

        inscription_paid = await self.payment_repo.sum_paid(
            enrollment.id, FormationPaymentType.inscription
        )
        formation_paid = await self.payment_repo.sum_paid(
            enrollment.id, FormationPaymentType.formation
        )

        return {
            "inscription_due": enrollment.inscription_fee_amount,
            "inscription_paid": inscription_paid,
            "inscription_remaining": max(enrollment.inscription_fee_amount - inscription_paid, 0),
            "formation_due": enrollment.formation_fee_amount,
            "formation_paid": formation_paid,
            "formation_remaining": max(enrollment.formation_fee_amount - formation_paid, 0),
            "status": enrollment.status,
        }
        
    
    async def list_payments_for_enrollment(
        self, scope: CenterScope, enrollment_id: UUID
    ) -> list[FormationPayment]:
        enrollment = await self.enrollment_repo.get_by_id_scoped(
            enrollment_id, scope.center_id, scope.branch_id
        )
        if not enrollment:
            raise NotFoundException(detail="Inscription introuvable pour votre périmètre.")
        return await self.payment_repo.find_by_enrollment(enrollment.id)
    
    
    async def get_revenue_summary(self, center_id: UUID) -> dict:
        """Vue directeur — revenu total du centre et répartition par succursale."""
        total = await self.payment_repo.sum_for_center(center_id)
        breakdown = await self.payment_repo.sum_by_branch_for_center(center_id)
        return {"total_revenue": total, "branches_breakdown": breakdown}