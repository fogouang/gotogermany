"""
app/modules/exam_access/service.py

Logique d'accès :
  - Sujet privé : admin, devoir en cours, ou élève indépendant (règles normales).
    Jamais pour un élève de centre en dehors d'un devoir.
  - Élève indépendant : sujets 1 à 3 libres, puis ExamAccess actif sur le niveau.
  - Élève de centre : ExamAccess actif ET classe active, sans aperçu gratuit.
  - Start Deutsch (A1, A2) : mêmes règles, avec un accès sur sd_level au lieu de level_id.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exam_access.models import ExamAccess
from app.modules.exam_access.repository import ExamAccessRepository
from app.modules.exam_access.schemas import (
    AccessCheckResponse,
    ExamAccessWithLevelResponse,
    UserLevelsResponse,
)
from app.modules.exam_access.visibility import can_see_private
from app.modules.exams.models import Exam, Subject
from app.modules.exams.repository import ExamRepository, LevelRepository
from app.modules.exams.schemas import ExamCatalogResponse, LevelAccessResponse
from app.modules.users.models import User, UserRole
from app.shared.exceptions.http import ForbiddenException


class ExamAccessService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamAccessRepository(db)
        self.exam_repo = ExamRepository(db)
        self.level_repo = LevelRepository(db)

    # ── Élèves de centre ─────────────────────────────────

    @staticmethod
    def _is_center_student(user: User | None) -> bool:
        return bool(user and user.role == UserRole.student and user.branch_id)

    async def _get_user(self, user_id: UUID) -> User | None:
        from app.modules.users.repository import UserRepository

        return await UserRepository(self.db).get_by_id(user_id)

    async def _has_active_class(self, user_id: UUID) -> bool:
        """L'élève est-il dans au moins une classe en cours ?"""
        from app.modules.training_sessions.models import (
            TrainingSession,
            TrainingSessionStudent,
        )

        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(func.count(TrainingSessionStudent.id))
            .join(
                TrainingSession,
                TrainingSession.id == TrainingSessionStudent.training_session_id,
            )
            .where(
                TrainingSessionStudent.student_id == user_id,
                TrainingSessionStudent.ended_at.is_(None),
                (TrainingSession.end_date.is_(None)) | (TrainingSession.end_date > now),
            )
        )
        return result.scalar_one() > 0

    # ── Vérification d'accès ─────────────────────────────

    async def check_subject_access(self, user_id: UUID, subject: Subject) -> bool:
        """
        - Sujet privé : admin, devoir non rendu sur ce sujet, ou élève indépendant
          (il suit alors les règles normales ci-dessous).
        - Élève indépendant : 3 premiers sujets libres, puis ExamAccess actif.
        - Élève de centre : ExamAccess actif ET classe active, pas d'aperçu gratuit.
        """
        from app.modules.settings.service import AppSettingsService

        user = await self._get_user(user_id)

        if subject.is_private:
            if user and user.is_admin:
                return True
            # Devoir non rendu sur ce sujet : toujours accessible
            from app.modules.assignments.service import AssignmentService

            if await AssignmentService(self.db).student_has_open_assignment(
                user_id, subject.id
            ):
                return True
            # Élève de centre : les sujets privés sont réservés aux devoirs
            if not can_see_private(user):
                return False
            # Élève indépendant : sujet comme les autres, règles ci-dessous

        if await AppSettingsService(self.db).is_free_access_mode():
            return True

        if self._is_center_student(user):
            if not await self.repo.user_has_access(user_id, subject.level_id):
                return False
            return await self._has_active_class(user_id)

        if subject.subject_number <= 3:
            return True

        return await self.repo.user_has_access(user_id, subject.level_id)

    async def require_subject_access(self, user_id: UUID, subject: Subject) -> None:
        if await self.check_subject_access(user_id, subject):
            return

        user = await self._get_user(user_id)
        if self._is_center_student(user) and await self.repo.user_has_access(
            user_id, subject.level_id
        ):
            raise ForbiddenException(
                detail="Votre centre doit vous affecter à une classe pour accéder aux sujets."
            )
        raise ForbiddenException(detail="Accès requis : veuillez souscrire à ce niveau.")

    # ── Start Deutsch (A1, A2) ───────────────────────────

    async def check_sd_subject_access(self, user: User | None, subject) -> bool:
        """
        Mêmes règles que les sujets d'examen, sur le niveau Start Deutsch du sujet :
        - indépendant : sujets 1 à 3 libres, puis accès A1 ou A2 actif ;
        - élève de centre : accès A1 ou A2 actif ET classe en cours, sans aperçu.
        Les sujets privés (devoirs) sont traités avant, dans start_deutsch.access.
        """
        from app.modules.settings.service import AppSettingsService

        if user is None:
            return False
        if user.is_admin or await AppSettingsService(self.db).is_free_access_mode():
            return True

        if self._is_center_student(user):
            if not await self.repo.user_has_sd_access(user.id, subject.level):
                return False
            return await self._has_active_class(user.id)

        if subject.subject_number <= 3:
            return True
        return await self.repo.user_has_sd_access(user.id, subject.level)

    async def require_sd_subject_access(self, user: User, subject) -> None:
        if await self.check_sd_subject_access(user, subject):
            return
        if self._is_center_student(user) and await self.repo.user_has_sd_access(
            user.id, subject.level
        ):
            raise ForbiddenException(
                detail="Votre centre doit vous affecter à une classe pour accéder aux sujets."
            )
        raise ForbiddenException(detail="Accès requis : veuillez souscrire à ce niveau.")

    async def locked_sd_subject_ids(self, user: User, subjects: list) -> set:
        """Sujets Start Deutsch fermés pour cet utilisateur (cadenas du catalogue)."""
        locked = set()
        for subject in subjects:
            if not await self.check_sd_subject_access(user, subject):
                locked.add(subject.id)
        return locked

    async def grant_admin_sd_access(
        self, user_id: UUID, sd_level: str, days: int | None = None
    ) -> ExamAccess:
        """Comme grant_admin_access, pour un niveau Start Deutsch."""
        now = datetime.now(timezone.utc)
        existing = await self.repo.find_by_user_and_sd_level(user_id, sd_level)

        if days is None:
            expires_at = None
        else:
            if existing and existing.expires_at is None:
                return existing
            start = (
                existing.expires_at
                if existing and existing.expires_at and existing.expires_at > now
                else now
            )
            expires_at = start + timedelta(days=days)

        if existing:
            return await self.repo.update(
                existing.id, access_type="admin", expires_at=expires_at, granted_at=now
            )
        return await self.repo.create(
            user_id=user_id,
            sd_level=sd_level,
            access_type="admin",
            payment_id=None,
            expires_at=expires_at,
            granted_at=now,
        )

    async def check_level_access(
        self, user_id: UUID, level_id: UUID
    ) -> AccessCheckResponse:
        access = await self.repo.get_active_by_user_and_level(user_id, level_id)
        if not access:
            return AccessCheckResponse(
                level_id=level_id,
                has_access=False,
                access_type=None,
                expires_at=None,
                reason="Accès requis : veuillez souscrire à ce niveau.",
            )

        user = await self._get_user(user_id)
        if self._is_center_student(user) and not await self._has_active_class(user_id):
            return AccessCheckResponse(
                level_id=level_id,
                has_access=False,
                access_type=access.access_type,
                expires_at=access.expires_at,
                reason="Votre centre doit vous affecter à une classe pour accéder aux sujets.",
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
        days: int | None = None,
    ) -> ExamAccess:
        """
        Accès accordé par l'admin, sans paiement ni vente.
        - days=None : accès permanent.
        - days=N    : N jours ajoutés à l'accès encore actif, sinon à partir d'aujourd'hui.
        Un accès existant (même expiré) est mis à jour, jamais refusé.
        """
        await self.level_repo.get_by_id_or_404(level_id)
        now = datetime.now(timezone.utc)
        existing = await self.repo.find_by_user_and_level(user_id, level_id)

        if days is None:
            expires_at = None
        else:
            if existing and existing.expires_at is None:
                # Déjà permanent : rien à prolonger
                return existing
            start = (
                existing.expires_at
                if existing and existing.expires_at and existing.expires_at > now
                else now
            )
            expires_at = start + timedelta(days=days)

        if existing:
            return await self.repo.update(
                existing.id,
                access_type="admin",
                expires_at=expires_at,
                granted_at=now,
            )

        return await self.repo.create(
            user_id=user_id,
            level_id=level_id,
            access_type="admin",
            payment_id=None,
            expires_at=expires_at,
            granted_at=now,
        )

    # ── Listing ──────────────────────────────────────────

    async def get_user_levels(self, user_id: UUID) -> UserLevelsResponse:
        """Tous les niveaux accessibles d'un utilisateur."""
        accesses = await self.repo.get_all_by_user(user_id)

        paid_levels = [
            ExamAccessWithLevelResponse(
                id=access.id,
                level_id=access.level_id,
                sd_level=access.sd_level,
                access_type=access.access_type,
                granted_at=access.granted_at,
                expires_at=access.expires_at,
                is_active=access.is_active,
                cefr_code=(
                    access.sd_level
                    or (access.level.cefr_code if access.level else "")
                ),
                exam_name=(
                    f"Start Deutsch {access.sd_level}"
                    if access.sd_level
                    else (access.level.exam.name if access.level and access.level.exam else "")
                ),
                exam_provider=(
                    "start_deutsch"
                    if access.sd_level
                    else (
                        access.level.exam.provider
                        if access.level and access.level.exam
                        else ""
                    )
                ),
            )
            for access in accesses
        ]

        return UserLevelsResponse(paid_levels=paid_levels, total=len(accesses))

    # ── Catalogue enrichi ────────────────────────────────

    async def enrich_catalog(
        self, exams: list[Exam], user_id: UUID
    ) -> list[ExamCatalogResponse]:
        """
        Enrichit le catalogue avec :
        - has_access    : ExamAccess actif sur le niveau (et classe active pour un élève de centre)
        - subject_count : sujets visibles par l'utilisateur (privés inclus pour un indépendant)
        """
        from app.modules.settings.service import AppSettingsService

        free_access_mode = await AppSettingsService(self.db).is_free_access_mode()

        user_accesses = await self.repo.get_all_by_user(user_id)
        # Seuls les accès non expirés comptent
        accessible_level_ids = {a.level_id for a in user_accesses if a.is_active}

        # Élève de centre sans classe active : aucun niveau ouvert
        user = await self._get_user(user_id)
        if self._is_center_student(user) and not await self._has_active_class(user_id):
            accessible_level_ids = set()

        level_ids = [level.id for exam in exams for level in exam.levels]
        subject_counts: dict[UUID, int] = {}
        if level_ids:
            conditions = [Subject.level_id.in_(level_ids), Subject.is_active == True]
            if not can_see_private(user):
                conditions.append(Subject.is_private == False)
            result = await self.db.execute(
                select(Subject.level_id, func.count(Subject.id))
                .where(*conditions)
                .group_by(Subject.level_id)
            )
            subject_counts = {row[0]: row[1] for row in result.all()}

        catalog = []
        for exam in exams:
            levels = [
                LevelAccessResponse(
                    id=level.id,
                    cefr_code=level.cefr_code,
                    total_pass_score=level.total_pass_score,
                    display_order=level.display_order,
                    is_free=level.is_free,
                    has_access=free_access_mode or (level.id in accessible_level_ids),
                    subject_count=subject_counts.get(level.id, 0),
                    price=None,
                )
                for level in exam.levels
            ]
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