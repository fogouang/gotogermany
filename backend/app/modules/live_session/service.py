"""
app/modules/live_session/service.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.centers.models import Branch
from app.modules.users.models import User, UserRole
from app.shared.exceptions.http import BadRequestException, NotFoundException

from .models import LiveSession, LiveSessionStatus

SPRECHEN_SLUGS = ("sprechen", "muendlicher_ausdruck")


class LiveSessionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Lecture ──────────────────────────────────────────

    async def get_or_404(self, live_session_id: UUID) -> LiveSession:
        result = await self.db.execute(
            select(LiveSession).where(LiveSession.id == live_session_id)
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise NotFoundException(resource="LiveSession", identifier=str(live_session_id))
        return session

    async def list_for_student(
        self, student_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[LiveSession], int]:
        """Sessions du student, plus récentes d'abord — c'est ici que
        l'étudiant retrouve les notes de l'examinateur une fois la
        session terminée."""
        base = select(LiveSession).where(LiveSession.student_id == student_id)
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        result = await self.db.execute(
            base.order_by(LiveSession.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    async def list_for_examiner(
        self, examiner_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[LiveSession], int]:
        """Sessions lancées par cet examinateur — utile pour le dashboard du centre."""
        base = select(LiveSession).where(LiveSession.examiner_id == examiner_id)
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()
        result = await self.db.execute(
            base.order_by(LiveSession.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all()), total

    # ── Création ─────────────────────────────────────────

    async def create_session(
        self, examiner_id: UUID, student_id: UUID, subject_id: UUID
    ) -> LiveSession:
        examiner = await self._get_user_or_404(examiner_id)
        if examiner.role not in (UserRole.branch_secretary, UserRole.center_director):
            raise BadRequestException(
                detail="Seul un membre du staff du centre peut lancer une session live."
            )

        student = await self._get_user_or_404(student_id)
        if not await self._same_center(examiner, student):
            raise BadRequestException(
                detail="Cet étudiant n'appartient pas à votre centre."
            )

        await self._check_subject_has_sprechen(subject_id)

        session = LiveSession(
            examiner_id=examiner_id,
            student_id=student_id,
            subject_id=subject_id,
            status=LiveSessionStatus.waiting,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    # ── Transitions de statut ────────────────────────────

    async def mark_preparing(self, live_session_id: UUID) -> LiveSession:
        """Appelée quand le candidat se connecte — démarre le chrono de
        préparation unique (20min/3 Teile). No-op si la session a déjà
        dépassé "waiting" (ex: reconnexion après une brève coupure)."""
        session = await self.get_or_404(live_session_id)
        if session.status != LiveSessionStatus.waiting:
            return session
        session.status = LiveSessionStatus.preparing
        session.prep_started_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def mark_live(self, live_session_id: UUID) -> LiveSession:
        """Appelé quand l'étudiant envoie ready_to_start après sa prépa."""
        session = await self.get_or_404(live_session_id)
        now = datetime.now(timezone.utc)
        if session.prep_started_at is None:
            session.prep_started_at = now
        session.status = LiveSessionStatus.live
        session.live_started_at = now
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def mark_ended(self, live_session_id: UUID) -> LiveSession:
        session = await self.get_or_404(live_session_id)
        if session.status == LiveSessionStatus.ended:
            return session
        session.status = LiveSessionStatus.ended
        session.ended_at = datetime.now(timezone.utc)
        # Si l'examinateur avait déjà rédigé des notes avant la fin de
        # session, elles deviennent visibles au student dès maintenant.
        if session.examiner_notes and session.notes_sent_at is None:
            session.notes_sent_at = session.ended_at
        await self.db.commit()
        await self.db.refresh(session)
        return session

    # ── Notes de l'examinateur ───────────────────────────

    async def submit_notes(
        self, live_session_id: UUID, examiner_id: UUID, notes: str
    ) -> LiveSession:
        session = await self.get_or_404(live_session_id)
        if session.examiner_id != examiner_id:
            raise BadRequestException(detail="Vous n'êtes pas l'examinateur de cette session.")

        session.examiner_notes = notes
        # Si la session est déjà terminée au moment où les notes arrivent,
        # elles sont immédiatement visibles au student.
        if session.status == LiveSessionStatus.ended and session.notes_sent_at is None:
            session.notes_sent_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(session)
        return session

    # ── Helpers internes ─────────────────────────────────

    async def _get_user_or_404(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException(resource="User", identifier=str(user_id))
        return user

    async def _same_center(self, examiner: User, student: User) -> bool:
        """
        branch_secretary : l'étudiant doit être dans la même filiale.
        center_director : l'étudiant peut être dans N'IMPORTE QUELLE filiale
        du centre du directeur — student.center_id n'est JAMAIS renseigné
        pour un student (voir User.center_id: "Renseigné uniquement pour
        role=center_director"), donc on ne peut pas comparer directement ;
        il faut résoudre student.branch_id -> Branch.center_id.
        """
        if examiner.role == UserRole.branch_secretary:
            return student.branch_id == examiner.branch_id

        if examiner.role == UserRole.center_director:
            if student.branch_id is None:
                return False
            result = await self.db.execute(
                select(Branch.center_id).where(Branch.id == student.branch_id)
            )
            student_center_id = result.scalar_one_or_none()
            return student_center_id == examiner.center_id

        return False

    async def _check_subject_has_sprechen(self, subject_id: UUID) -> None:
        from app.modules.exams.repository import SubjectRepository

        subject = await SubjectRepository(self.db).get_with_modules(subject_id)
        if subject is None:
            raise NotFoundException(resource="Subject", identifier=str(subject_id))

        has_sprechen = any(m.slug in SPRECHEN_SLUGS for m in subject.modules)
        if not has_sprechen:
            raise BadRequestException(detail="Ce sujet n'a pas de module Sprechen.")

    async def get_subject_content(self, live_session_id: UUID) -> dict:
        """
        Contenu du sujet Sprechen (instructions/thèmes/points par Teil) à
        afficher au candidat pendant sa prépa et à l'examinateur pour s'y
        référer — même logique d'extraction que
        sprechen_agent/router.py::get_subject_data(), réutilisée ici en
        REST simple puisqu'il n'y a pas d'agent IA qui orchestre teil par
        teil dans ce mode.
        """
        from app.modules.exams.repository import (
            ExamRepository,
            LevelRepository,
            SubjectRepository,
        )

        session = await self.get_or_404(live_session_id)

        subject = await SubjectRepository(self.db).get_with_modules(session.subject_id)
        if subject is None:
            raise NotFoundException(resource="Subject", identifier=str(session.subject_id))

        level = await LevelRepository(self.db).get_by_id_or_404(subject.level_id)
        exam = await ExamRepository(self.db).get_by_id_or_404(level.exam_id)

        sprechen_module = next(
            (m for m in subject.modules if m.slug in SPRECHEN_SLUGS), None
        )
        if sprechen_module is None:
            raise BadRequestException(detail="Ce sujet n'a pas de module Sprechen.")

        teile = []
        for teil in sprechen_module.teile:
            teil_dict: dict = dict(teil.config or {})
            teil_dict["teil_number"] = teil.teil_number
            if teil.instructions is not None:
                teil_dict.setdefault("instructions", teil.instructions)

            # Le contenu variable (leitpunkte/prompts/tasks/scenario/
            # themes/kandidat_a/kandidat_b) vit sur la Question du Teil,
            # PAS sur teil.config — même piège déjà rencontré et corrigé
            # côté sprechen_agent (teil.config n'est peuplé que pour les
            # images, jamais pour le contenu oral parsé).
            question = next(iter(teil.questions), None)
            if question is not None:
                teil_dict.update(question.content or {})

            content_points = (
                teil_dict.get("content_points")
                or teil_dict.get("leitpunkte")
                or teil_dict.get("prompts")
                or []
            )

            teile.append({
                "teil_number": teil.teil_number,
                "name": teil_dict.get("name") or teil_dict.get("titel"),
                "instructions": teil_dict.get("instructions"),
                "content_points": content_points,
                "themes": teil_dict.get("themes"),
                "diskussion_titel": teil_dict.get("diskussion_titel"),
                "diskussion_thema": teil_dict.get("diskussion_thema"),
                "scenario": teil_dict.get("scenario"),
                "tasks": teil_dict.get("tasks") or [],
            })

        teile.sort(key=lambda t: t["teil_number"])

        return {
            "subject_id": session.subject_id,
            "provider": exam.provider,
            "level": level.cefr_code,
            "teile": teile,
        }