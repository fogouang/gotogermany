"""
app/modules/exam_access/service.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exam_access.models import ExamAccess
from app.modules.exam_access.repository import ExamAccessRepository
from app.modules.exam_access.schemas import (
    AccessCheckResponse,
    ExamAccessWithExamResponse,
    UserExamsResponse,
)
from app.modules.exams.models import Exam
from app.modules.exams.repository import ExamRepository, LevelRepository
from app.modules.exams.schemas import ExamCatalogResponse, LevelAccessResponse
from app.shared.exceptions.http import BadRequestException, ForbiddenException
from sqlalchemy import select, func
from app.modules.exams.models import Subject


class ExamAccessService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamAccessRepository(db)
        self.exam_repo = ExamRepository(db)
        self.level_repo = LevelRepository(db)

    # ── Vérification d'accès ─────────────────────────────

    async def check_access(
        self, user_id: UUID, exam_id: UUID
    ) -> AccessCheckResponse:
        """Vérifie si un user a accès à un exam."""
        access = await self.repo.get_active_by_user_and_exam(user_id, exam_id)

        if not access:
            return AccessCheckResponse(
                exam_id=exam_id,
                has_access=False,
                access_type=None,
                expires_at=None,
                reason="Accès requis — veuillez acheter cet examen.",
            )

        return AccessCheckResponse(
            exam_id=exam_id,
            has_access=True,
            access_type=access.access_type,
            expires_at=access.expires_at,
            reason="Accès gratuit." if access.access_type == "free" else "Accès payant actif.",
        )

    async def require_access(self, user_id: UUID, exam_id: UUID) -> ExamAccess:
        """
        Retourne l'accès ou lève ForbiddenException.
        À utiliser comme guard dans exam_sessions.
        """
        access = await self.repo.get_active_by_user_and_exam(user_id, exam_id)
        if not access:
            raise ForbiddenException(
                detail="Vous n'avez pas accès à cet examen."
            )
        return access

    # ── Création d'accès ─────────────────────────────────

    async def grant_free_access(self, user_id: UUID) -> list[ExamAccess]:
        """
        Crée les accès gratuits pour tous les levels is_free=True.
        Appelé à l'inscription du user.
        """
        free_levels = await self.level_repo.get_free_levels()
        accesses = []

        for level in free_levels:
            # Éviter les doublons
            existing = await self.repo.find_by_user_and_exam(user_id, level.id)
            if existing:
                continue

            access = await self.repo.create(
                user_id=user_id,
                exam_id=level.id,  # on lie à l'exam via level
                access_type="free",
                payment_id=None,
                expires_at=None,
                granted_at=datetime.now(timezone.utc),
            )
            accesses.append(access)

        return accesses

    async def grant_paid_access(
        self,
        user_id: UUID,
        exam_id: UUID,
        payment_id: UUID,
    ) -> ExamAccess:
        """
        Crée un accès payant après confirmation du paiement.
        Appelé depuis le webhook handler My-CoolPay.
        """
        # Vérifier si accès existant — upgrade free → paid si nécessaire
        existing = await self.repo.find_by_user_and_exam(user_id, exam_id)
        if existing:
            if existing.access_type == "paid":
                raise BadRequestException(
                    detail="L'utilisateur a déjà un accès payant pour cet examen."
                )
            # Upgrade free → paid
            return await self.repo.update(
                existing.id,
                access_type="paid",
                payment_id=payment_id,
                granted_at=datetime.now(timezone.utc),
            )

        return await self.repo.create(
            user_id=user_id,
            exam_id=exam_id,
            access_type="paid",
            payment_id=payment_id,
            expires_at=None,
            granted_at=datetime.now(timezone.utc),
        )

    async def grant_admin_access(
        self,
        user_id: UUID,
        exam_id: UUID,
    ) -> ExamAccess:
        """
        Crée un accès manuellement depuis l'admin (pour tests ou cas spéciaux).
        """
        existing = await self.repo.find_by_user_and_exam(user_id, exam_id)
        if existing:
            raise BadRequestException(
                detail="L'utilisateur a déjà un accès pour cet examen."
            )

        await self.exam_repo.get_by_id_or_404(exam_id)

        return await self.repo.create(
            user_id=user_id,
            exam_id=exam_id,
            access_type="paid",
            payment_id=None,
            expires_at=None,
            granted_at=datetime.now(timezone.utc),
        )

    # ── Listing ──────────────────────────────────────────

    async def get_user_exams(self, user_id: UUID) -> UserExamsResponse:
        """Tous les examens accessibles d'un user, séparés free/paid."""
        accesses = await self.repo.get_all_by_user(user_id)

        free_exams = []
        paid_exams = []

        for access in accesses:
            item = ExamAccessWithExamResponse(
                id=access.id,
                exam_id=access.exam_id,
                access_type=access.access_type,
                granted_at=access.granted_at,
                expires_at=access.expires_at,
                is_active=access.is_active,
                exam_name=access.exam.name if access.exam else "",
                exam_slug=access.exam.slug if access.exam else "",
                exam_provider=access.exam.provider if access.exam else "",
                cefr_code="",  # TODO: charger via level si besoin
            )
            if access.access_type == "free":
                free_exams.append(item)
            else:
                paid_exams.append(item)

        return UserExamsResponse(
            free_exams=free_exams,
            paid_exams=paid_exams,
            total=len(accesses),
        )

    # ── Catalogue enrichi ────────────────────────────────



    async def enrich_catalog(
        self, exams: list[Exam], user_id: UUID
    ) -> list[ExamCatalogResponse]:
        user_accesses = await self.repo.get_all_by_user(user_id)
        accessible_exam_ids = {a.exam_id for a in user_accesses}

        # Compter les subjects par level en une seule requête
        level_ids = [
            level.id
            for exam in exams
            for level in exam.levels
        ]
        subject_counts: dict[UUID, int] = {}
        if level_ids:
            result = await self.db.execute(
                select(Subject.level_id, func.count(Subject.id))
                .where(Subject.level_id.in_(level_ids), Subject.is_active == True)
                .group_by(Subject.level_id)
            )
            subject_counts = {row[0]: row[1] for row in result.all()}

        result = []
        for exam in exams:
            levels = []
            for level in exam.levels:
                has_access = level.is_free or exam.id in accessible_exam_ids
                levels.append(
                    LevelAccessResponse(
                        id=level.id,
                        cefr_code=level.cefr_code,
                        total_pass_score=level.total_pass_score,
                        display_order=level.display_order,
                        is_free=level.is_free,
                        has_access=has_access,
                        subject_count=subject_counts.get(level.id, 0),  # ← ajouter
                        price=None,
                    )
                )
            result.append(
                ExamCatalogResponse(
                    id=exam.id,
                    provider=exam.provider,
                    name=exam.name,
                    slug=exam.slug,
                    description=exam.description,
                    levels=levels,
                )
            )
        return result