"""
app/modules/exam_access/service.py

Logique d'accès :
  - Sujets 1, 2, 3 de chaque level → libres pour tous
  - Sujet 4+ → réservé aux abonnés du level
  - L'achat cible un Level précis (ex: B1 OSD, B2 Goethe)
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exam_access.models import ExamAccess
from app.modules.exam_access.repository import ExamAccessRepository
from app.modules.exam_access.schemas import (
    AccessCheckResponse,
    ExamAccessWithLevelResponse,
    UserLevelsResponse,
)
from app.modules.exams.models import Exam, Level, Subject
from app.modules.exams.repository import ExamRepository, LevelRepository
from app.modules.exams.schemas import ExamCatalogResponse, LevelAccessResponse
from app.shared.exceptions.http import BadRequestException, ForbiddenException


class ExamAccessService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamAccessRepository(db)
        self.exam_repo = ExamRepository(db)
        self.level_repo = LevelRepository(db)

    # ── Vérification d'accès ─────────────────────────────

    async def check_subject_access(
        self, user_id: UUID, subject: Subject
    ) -> bool:
        """
        Accès libre si subject_number <= 3.
        Sinon vérifie ExamAccess pour ce level.
        """
        if subject.subject_number <= 3:
            return True
        return await self.repo.user_has_access(user_id, subject.level_id)

    async def require_subject_access(
        self, user_id: UUID, subject: Subject
    ) -> None:
        """
        Guard — lève ForbiddenException si pas d'accès au subject.
        À utiliser dans exam_sessions avant de démarrer une session.
        """
        has_access = await self.check_subject_access(user_id, subject)
        if not has_access:
            raise ForbiddenException(
                detail="Accès requis — veuillez souscrire à ce niveau."
            )

    async def check_level_access(
        self, user_id: UUID, level_id: UUID
    ) -> AccessCheckResponse:
        """Vérifie si un user a un accès payant à un level."""
        access = await self.repo.get_active_by_user_and_level(user_id, level_id)
        if not access:
            return AccessCheckResponse(
                level_id=level_id,
                has_access=False,
                access_type=None,
                expires_at=None,
                reason="Accès requis — veuillez souscrire à ce niveau.",
            )
        return AccessCheckResponse(
            level_id=level_id,
            has_access=True,
            access_type=access.access_type,
            expires_at=access.expires_at,
            reason="Accès payant actif.",
        )

    # ── Création d'accès ─────────────────────────────────

    async def grant_paid_access(
        self,
        user_id: UUID,
        level_id: UUID,
        payment_id: UUID,
        expires_at: datetime | None = None,
    ) -> ExamAccess:
        """
        Crée ou renouvelle un accès payant après confirmation du paiement.
        Appelé depuis le callback pawaPay.
        """
        existing = await self.repo.find_by_user_and_level(user_id, level_id)
        if existing:
            return await self.repo.update(
                existing.id,
                access_type="paid",
                payment_id=payment_id,
                expires_at=expires_at,
                granted_at=datetime.now(timezone.utc),
            )

        return await self.repo.create(
            user_id=user_id,
            level_id=level_id,
            access_type="paid",
            payment_id=payment_id,
            expires_at=expires_at,
            granted_at=datetime.now(timezone.utc),
        )

    async def grant_admin_access(
        self,
        user_id: UUID,
        level_id: UUID,
    ) -> ExamAccess:
        """
        Accorde manuellement un accès à un level — admin uniquement.
        """
        await self.level_repo.get_by_id_or_404(level_id)

        existing = await self.repo.find_by_user_and_level(user_id, level_id)
        if existing:
            raise BadRequestException(
                detail="L'utilisateur a déjà un accès pour ce niveau."
            )

        return await self.repo.create(
            user_id=user_id,
            level_id=level_id,
            access_type="paid",
            payment_id=None,
            expires_at=None,
            granted_at=datetime.now(timezone.utc),
        )

    # ── Listing ──────────────────────────────────────────

    async def get_user_levels(self, user_id: UUID) -> UserLevelsResponse:
        """Tous les levels accessibles d'un user."""
        accesses = await self.repo.get_all_by_user(user_id)

        paid_levels = []
        for access in accesses:
            paid_levels.append(
                ExamAccessWithLevelResponse(
                    id=access.id,
                    level_id=access.level_id,
                    access_type=access.access_type,
                    granted_at=access.granted_at,
                    expires_at=access.expires_at,
                    is_active=access.is_active,
                    cefr_code=access.level.cefr_code if access.level else "",
                    exam_name=access.level.exam.name if access.level and access.level.exam else "",
                    exam_provider=access.level.exam.provider if access.level and access.level.exam else "",
                )
            )

        return UserLevelsResponse(
            paid_levels=paid_levels,
            total=len(accesses),
        )

    # ── Catalogue enrichi ────────────────────────────────

    async def enrich_catalog(
        self, exams: list[Exam], user_id: UUID
    ) -> list[ExamCatalogResponse]:
        """
        Enrichit le catalogue avec :
        - has_access : user a un ExamAccess pour ce level
        - subject_count : nb de sujets disponibles
        """
        # Vérifier le mode accès libre
        from app.modules.settings.service import AppSettingsService
        free_access_mode = await AppSettingsService(self.db).is_free_access_mode()

        user_accesses = await self.repo.get_all_by_user(user_id)
        # Indexer par level_id
        accessible_level_ids = {a.level_id for a in user_accesses}

        # Compter les subjects actifs par level
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

        catalog = []
        for exam in exams:
            levels = []
            for level in exam.levels:
                # Si free_access_mode → tout le monde a accès complet
                has_access = free_access_mode or (level.id in accessible_level_ids)
                levels.append(
                    LevelAccessResponse(
                        id=level.id,
                        cefr_code=level.cefr_code,
                        total_pass_score=level.total_pass_score,
                        display_order=level.display_order,
                        is_free=level.is_free,
                        has_access=has_access,
                        subject_count=subject_counts.get(level.id, 0),
                        price=None,
                    )
                )
            catalog.append(
                ExamCatalogResponse(
                    id=exam.id,
                    provider=exam.provider,
                    name=exam.name,
                    slug=exam.slug,
                    description=exam.description,
                    levels=levels,
                )
            )
        return catalog
    
    
    async def check_subject_access(
        self, user_id: UUID, subject: Subject
    ) -> bool:
        # Vérifier le mode accès libre
        from app.modules.settings.service import AppSettingsService
        if await AppSettingsService(self.db).is_free_access_mode():
            return True
        # Logique normale
        if subject.subject_number <= 3:
            return True
        return await self.repo.user_has_access(user_id, subject.level_id)