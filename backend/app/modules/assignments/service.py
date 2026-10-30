"""
app/modules/assignments/service.py

Devoirs : banque de sujets privés, attribution, passage via le moteur
d'examen (B1/B2) ou le lecteur Start Deutsch (A1/A2), correction par
l'enseignant, copies Schreiben en PDF.
"""
from __future__ import annotations

import io
import logging
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from xml.sax.saxutils import escape

from fastapi import UploadFile
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assignments.models import Assignment, AssignmentSubmission, AssignmentTarget
from app.modules.assignments.schemas import (
    AssignmentCreate,
    AssignmentDetailResponse,
    AssignmentSummaryResponse,
    AssignmentTargetResponse,
    BankSubjectResponse,
    GradeRequest,
    StudentAssignmentResponse,
    SubmissionGradingResponse,
    SubmissionRowResponse,
    StudentScoreSheet,
    StudentModuleScore
)
from app.modules.exam_sessions.models import ExamSession, ExamSessionAnswer
from app.modules.exams.models import Exam, Level, Module, Subject
from app.modules.start_deutsch.models import (
    StartDeutschAnswer,
    StartDeutschModule,
    StartDeutschSchreibenCorrection,
    StartDeutschSession,
    StartDeutschSubject,
)
from app.modules.training_sessions.models import (
    TrainingSession,
    TrainingSessionStudent,
    TrainingSessionTeacher,
)
from app.modules.users.models import User, UserRole
from app.shared.exceptions.http import BadRequestException, ForbiddenException, NotFoundException

logger = logging.getLogger(__name__)

ANNOTATED_DIR = Path("storage/assignments")
ANNOTATED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ANNOTATED_MAX_BYTES = 10 * 1024 * 1024
DONE_STATUSES = ("submitted", "graded")

SD_MODULE_LABELS = {"lesen": "Lesen", "hoeren": "Hören", "schreiben": "Schreiben", "sprechen": "Sprechen"}


def _sd_exam_name(level: str) -> str:
    """A1 -> Start Deutsch 1, A2 -> Start Deutsch 2."""
    return f"Start Deutsch {level[-1]}" if level else "Start Deutsch"


def _sd_all_corrected(result: dict) -> bool:
    return bool(result["modules"]) and all(m["is_corrected"] for m in result["modules"])


def _sd_percent(result: dict) -> float:
    """Score Start Deutsch ramené sur 100, comme ExamSession.score."""
    total_max = sum(float(m["max_score"]) for m in result["modules"])
    return round(float(result["score"]) * 100 / total_max, 1) if total_max else 0.0


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _html(text: str) -> str:
    return escape(text or "").replace("\n", "<br/>")


def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "eleve"


class AssignmentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Helpers de périmètre ─────────────────────────────

    async def _teacher_center_id(self, teacher: User) -> UUID:
        from app.modules.centers.models import Branch

        if teacher.role != UserRole.teacher or not teacher.branch_id:
            raise ForbiddenException(detail="Action réservée aux enseignants.")
        branch = await self.db.get(Branch, teacher.branch_id)
        if not branch:
            raise ForbiddenException(detail="Action réservée aux enseignants.")
        return branch.center_id

    async def _assert_student_of_center(self, student_id: UUID, center_id: UUID) -> None:
        from app.modules.centers.models import Branch

        student = await self.db.get(User, student_id)
        if not student or student.role != UserRole.student or not student.branch_id:
            raise BadRequestException(detail="Élève introuvable.")
        branch = await self.db.get(Branch, student.branch_id)
        if not branch or branch.center_id != center_id:
            raise ForbiddenException(detail="Cet élève n'appartient pas à votre centre.")

    async def _get_teacher_assignment(self, teacher: User, assignment_id: UUID) -> Assignment:
        assignment = await self.db.get(Assignment, assignment_id)
        if not assignment or assignment.created_by != teacher.id:
            raise NotFoundException(resource="Devoir", identifier=str(assignment_id))
        return assignment

    def _targeting_condition(self, student_id: UUID):
        """Le devoir vise l'élève directement, ou une classe où il est encore actif."""
        return or_(
            AssignmentTarget.student_id == student_id,
            TrainingSessionStudent.id.isnot(None),
        )

    def _targets_query(self, student_id: UUID):
        return (
            select(Assignment.id)
            .join(AssignmentTarget, AssignmentTarget.assignment_id == Assignment.id)
            .outerjoin(
                TrainingSessionStudent,
                and_(
                    TrainingSessionStudent.training_session_id == AssignmentTarget.training_session_id,
                    TrainingSessionStudent.student_id == student_id,
                    TrainingSessionStudent.ended_at.is_(None),
                ),
            )
            .where(Assignment.is_cancelled == False, self._targeting_condition(student_id))
        )

    async def _is_targeted(self, assignment_id: UUID, student_id: UUID) -> bool:
        result = await self.db.execute(
            self._targets_query(student_id).where(Assignment.id == assignment_id).limit(1)
        )
        return result.scalar_one_or_none() is not None

    # ── Données communes ─────────────────────────────────

    async def _subject_info(self, subject_id: UUID) -> tuple[Subject, Level, Exam]:
        row = (
            await self.db.execute(
                select(Subject, Level, Exam)
                .join(Level, Level.id == Subject.level_id)
                .join(Exam, Exam.id == Level.exam_id)
                .where(Subject.id == subject_id)
            )
        ).one()
        return row[0], row[1], row[2]

    async def _info(self, a: Assignment) -> tuple[str, str, str]:
        """(nom du sujet, nom de l'examen, niveau CECR), quel que soit le type de devoir."""
        if a.sd_subject_id:
            sd = await self.db.get(StartDeutschSubject, a.sd_subject_id)
            return sd.title, _sd_exam_name(sd.level), sd.level
        subject, level, exam = await self._subject_info(a.subject_id)
        return subject.name or f"Sujet {subject.subject_number}", exam.name, level.cefr_code

    async def _targets(self, assignment_id: UUID) -> list[AssignmentTargetResponse]:
        rows = (
            await self.db.execute(
                select(AssignmentTarget, TrainingSession, User)
                .outerjoin(TrainingSession, TrainingSession.id == AssignmentTarget.training_session_id)
                .outerjoin(User, User.id == AssignmentTarget.student_id)
                .where(AssignmentTarget.assignment_id == assignment_id)
            )
        ).all()
        out: list[AssignmentTargetResponse] = []
        for _, ts, user in rows:
            if ts:
                out.append(AssignmentTargetResponse(
                    type="class", id=ts.id, name=ts.label or f"Classe du {ts.start_date:%d/%m/%Y}"
                ))
            elif user:
                out.append(AssignmentTargetResponse(type="student", id=user.id, name=user.full_name))
        return out

    async def _expected_student_ids(self, assignment_id: UUID) -> set[UUID]:
        targets = (
            await self.db.execute(
                select(AssignmentTarget).where(AssignmentTarget.assignment_id == assignment_id)
            )
        ).scalars().all()
        ids = {t.student_id for t in targets if t.student_id}
        class_ids = [t.training_session_id for t in targets if t.training_session_id]
        if class_ids:
            result = await self.db.execute(
                select(TrainingSessionStudent.student_id).where(
                    TrainingSessionStudent.training_session_id.in_(class_ids),
                    TrainingSessionStudent.ended_at.is_(None),
                )
            )
            ids |= set(result.scalars().all())
        return ids

    async def _submissions(self, assignment_id: UUID) -> dict[UUID, AssignmentSubmission]:
        subs = (
            await self.db.execute(
                select(AssignmentSubmission).where(AssignmentSubmission.assignment_id == assignment_id)
            )
        ).scalars().all()
        return {s.student_id: s for s in subs}

    async def _get_submission(self, assignment_id: UUID, student_id: UUID) -> AssignmentSubmission | None:
        return (
            await self.db.execute(
                select(AssignmentSubmission).where(
                    AssignmentSubmission.assignment_id == assignment_id,
                    AssignmentSubmission.student_id == student_id,
                )
            )
        ).scalar_one_or_none()

    async def _summary(self, a: Assignment) -> AssignmentSummaryResponse:
        subject_name, exam_name, cefr_code = await self._info(a)
        expected = await self._expected_student_ids(a.id)
        subs = await self._submissions(a.id)
        return AssignmentSummaryResponse(
            id=a.id,
            kind=a.kind,
            title=a.title,
            instructions=a.instructions,
            subject_id=a.subject_id or a.sd_subject_id,
            subject_name=subject_name,
            exam_name=exam_name,
            cefr_code=cefr_code,
            due_at=a.due_at,
            is_cancelled=a.is_cancelled,
            created_at=a.created_at,
            targets=await self._targets(a.id),
            expected_count=len(expected | set(subs)),
            submitted_count=sum(1 for s in subs.values() if s.status in DONE_STATUSES),
            graded_count=sum(1 for s in subs.values() if s.status == "graded"),
        )

    @staticmethod
    def _row(
        a: Assignment,
        student_id: UUID,
        user: User | None,
        sub: AssignmentSubmission | None,
        sessions: dict[UUID, ExamSession],
    ) -> SubmissionRowResponse:
        status = sub.status if sub else "pending"
        submitted_at = sub.submitted_at if sub else None
        is_late = bool(
            a.due_at
            and ((submitted_at and submitted_at > a.due_at) or (not submitted_at and _now() > a.due_at))
        )
        session = sessions.get(sub.exam_session_id) if sub and sub.exam_session_id else None
        return SubmissionRowResponse(
            student_id=student_id,
            student_name=user.full_name if user else "",
            status=status,
            exam_session_id=sub.exam_session_id if sub else None,
            sd_session_id=sub.sd_session_id if sub else None,
            started_at=sub.started_at if sub else None,
            submitted_at=submitted_at,
            graded_at=sub.graded_at if sub else None,
            is_late=is_late,
            score_breakdown=session.score_breakdown if session and status in DONE_STATUSES else None,
            final_score=sub.final_score if sub else None,
            has_annotated_file=bool(sub and sub.annotated_file),
        )

    # ── Enseignant : banque, création, suivi ─────────────

    async def bank(self, teacher: User, level_id: UUID | None = None) -> list[BankSubjectResponse]:
        await self._teacher_center_id(teacher)
        q = (
            select(Subject, Level, Exam)
            .join(Level, Level.id == Subject.level_id)
            .join(Exam, Exam.id == Level.exam_id)
            .where(Subject.is_private == True, Subject.is_active == True)
            .order_by(Exam.provider, Level.cefr_code, Subject.subject_number)
        )
        if level_id:
            q = q.where(Subject.level_id == level_id)
        rows = (await self.db.execute(q)).all()

        modules: dict[UUID, list[str]] = {}
        if rows:
            result = await self.db.execute(
                select(Module.subject_id, Module.name)
                .where(Module.subject_id.in_([r[0].id for r in rows]))
                .order_by(Module.display_order)
            )
            for subject_id, name in result.all():
                modules.setdefault(subject_id, []).append(name)

        bank = [
            BankSubjectResponse(
                subject_id=s.id,
                subject_name=s.name or f"Sujet {s.subject_number}",
                subject_number=s.subject_number,
                exam_id=e.id,
                exam_name=e.name,
                provider=e.provider,
                level_id=l.id,
                cefr_code=l.cefr_code,
                modules=modules.get(s.id, []),
            )
            for s, l, e in rows
        ]
        if not level_id:
            bank += await self._sd_bank()
        return bank

    async def _sd_bank(self) -> list[BankSubjectResponse]:
        """Sujets Start Deutsch privés. Le Sprechen n'est pas évalué en devoir."""
        subjects = (
            await self.db.execute(
                select(StartDeutschSubject)
                .where(StartDeutschSubject.is_private == True, StartDeutschSubject.is_active == True)
                .order_by(StartDeutschSubject.level, StartDeutschSubject.subject_number)
            )
        ).scalars().all()
        if not subjects:
            return []

        modules: dict[UUID, list[str]] = {}
        result = await self.db.execute(
            select(StartDeutschModule.subject_id, StartDeutschModule.slug)
            .where(StartDeutschModule.subject_id.in_([s.id for s in subjects]))
            .order_by(StartDeutschModule.order)
        )
        for subject_id, slug in result.all():
            if slug != "sprechen":
                modules.setdefault(subject_id, []).append(SD_MODULE_LABELS.get(slug, slug))

        return [
            BankSubjectResponse(
                kind="start_deutsch",
                subject_id=s.id,
                subject_name=s.title,
                subject_number=s.subject_number,
                exam_name=_sd_exam_name(s.level),
                provider="start_deutsch",
                cefr_code=s.level,
                modules=modules.get(s.id, []),
            )
            for s in subjects
        ]

    async def create(self, teacher: User, data: AssignmentCreate) -> AssignmentDetailResponse:
        center_id = await self._teacher_center_id(teacher)

        # Le type se déduit du sujet : la page de création n'a pas à envoyer kind
        subject = await self.db.get(Subject, data.subject_id)
        kind = "exam"
        if subject is None:
            subject = await self.db.get(StartDeutschSubject, data.subject_id)
            kind = "start_deutsch"
        if not subject or not subject.is_private or not subject.is_active:
            raise BadRequestException(detail="Ce sujet ne fait pas partie de la banque de sujets.")

        class_ids = list(dict.fromkeys(data.class_ids))
        student_ids = list(dict.fromkeys(data.student_ids))

        for class_id in class_ids:
            link = (
                await self.db.execute(
                    select(TrainingSessionTeacher.id).where(
                        TrainingSessionTeacher.training_session_id == class_id,
                        TrainingSessionTeacher.teacher_id == teacher.id,
                    )
                )
            ).scalar_one_or_none()
            if not link:
                raise ForbiddenException(detail="Vous n'enseignez pas dans l'une des classes choisies.")
        for student_id in student_ids:
            await self._assert_student_of_center(student_id, center_id)

        assignment = Assignment(
            center_id=center_id,
            subject_id=subject.id if kind == "exam" else None,
            sd_subject_id=subject.id if kind == "start_deutsch" else None,
            created_by=teacher.id,
            title=data.title.strip(),
            instructions=data.instructions,
            due_at=data.due_at,
        )
        self.db.add(assignment)
        await self.db.flush()

        for class_id in class_ids:
            self.db.add(AssignmentTarget(assignment_id=assignment.id, training_session_id=class_id))
        for student_id in student_ids:
            self.db.add(AssignmentTarget(assignment_id=assignment.id, student_id=student_id))
        await self.db.commit()

        return await self.get_detail(teacher, assignment.id)

    async def list_for_teacher(self, teacher: User) -> list[AssignmentSummaryResponse]:
        assignments = (
            await self.db.execute(
                select(Assignment)
                .where(Assignment.created_by == teacher.id)
                .order_by(Assignment.created_at.desc())
            )
        ).scalars().all()
        return [await self._summary(a) for a in assignments]

    async def get_detail(self, teacher: User, assignment_id: UUID) -> AssignmentDetailResponse:
        a = await self._get_teacher_assignment(teacher, assignment_id)
        summary = await self._summary(a)

        subs = await self._submissions(a.id)
        ids = await self._expected_student_ids(a.id) | set(subs)

        users: dict[UUID, User] = {}
        if ids:
            users = {
                u.id: u
                for u in (await self.db.execute(select(User).where(User.id.in_(ids)))).scalars().all()
            }
        session_ids = [s.exam_session_id for s in subs.values() if s.exam_session_id]
        sessions: dict[UUID, ExamSession] = {}
        if session_ids:
            sessions = {
                s.id: s
                for s in (
                    await self.db.execute(select(ExamSession).where(ExamSession.id.in_(session_ids)))
                ).scalars().all()
            }

        rows = [self._row(a, sid, users.get(sid), subs.get(sid), sessions) for sid in ids]
        rows.sort(key=lambda r: r.student_name.lower())
        return AssignmentDetailResponse(**summary.model_dump(), submissions=rows)

    async def cancel(self, teacher: User, assignment_id: UUID) -> None:
        a = await self._get_teacher_assignment(teacher, assignment_id)
        a.is_cancelled = True
        await self.db.commit()

    # ── Élève ────────────────────────────────────────────

    async def _score_sheet(self, subject_id: UUID, session_id: UUID | None) -> StudentScoreSheet | None:
        """Points par module (score_breakdown en % ramené au max du module)."""
        from app.modules.exams.models import Module

        session = await self.db.get(ExamSession, session_id) if session_id else None
        if not session or session.status == "IN_PROGRESS" or not session.score_breakdown:
            return None

        breakdown = session.score_breakdown
        modules = (
            await self.db.execute(
                select(Module)
                .where(Module.subject_id == subject_id)
                .order_by(Module.display_order)
            )
        ).scalars().all()

        rows: list[StudentModuleScore] = []
        total = total_max = 0.0
        for m in modules:
            if m.slug not in breakdown:  # module non passé (oral, mode module seul)
                continue
            pct = breakdown[m.slug]
            max_score = float(m.max_score or 0)
            points = None if pct is None else round(float(pct) * max_score / 100, 1)
            rows.append(StudentModuleScore(name=m.name, points=points, max_score=max_score))
            total_max += max_score
            if points is not None:
                total += points

        if not rows:
            return None
        is_final = session.status == "COMPLETED"
        return StudentScoreSheet(
            modules=rows,
            total_points=round(total, 1),
            total_max=total_max,
            is_final=is_final,
            passed=session.passed if is_final else None,
        )

    async def list_for_student(self, student: User) -> list[StudentAssignmentResponse]:
        if student.role != UserRole.student:
            raise ForbiddenException(detail="Espace réservé aux élèves.")

        targeted_ids = select(self._targets_query(student.id).subquery().c.id)
        submitted_ids = select(AssignmentSubmission.assignment_id).where(
            AssignmentSubmission.student_id == student.id
        )
        assignments = (
            await self.db.execute(
                select(Assignment)
                .where(
                    Assignment.is_cancelled == False,
                    or_(Assignment.id.in_(targeted_ids), Assignment.id.in_(submitted_ids)),
                )
                .order_by(Assignment.created_at.desc())
            )
        ).scalars().all()

        out: list[StudentAssignmentResponse] = []
        for a in assignments:
            _, exam_name, cefr_code = await self._info(a)
            teacher = await self.db.get(User, a.created_by)
            sub = await self._get_submission(a.id, student.id)
            status = sub.status if sub else "pending"
            submitted_at = sub.submitted_at if sub else None
            if sub and status in DONE_STATUSES:
                score_sheet = (
                    await self._sd_score_sheet(sub.sd_session_id)
                    if a.sd_subject_id
                    else await self._score_sheet(a.subject_id, sub.exam_session_id)
                )
            else:
                score_sheet = None
            out.append(StudentAssignmentResponse(
                id=a.id,
                kind=a.kind,
                title=a.title,
                instructions=a.instructions,
                exam_name=exam_name,
                cefr_code=cefr_code,
                teacher_name=teacher.full_name if teacher else "",
                due_at=a.due_at,
                is_late=bool(
                    a.due_at
                    and ((submitted_at and submitted_at > a.due_at) or (not submitted_at and _now() > a.due_at))
                ),
                status=status,
                final_score=sub.final_score if sub and status == "graded" else None,
                score_sheet=score_sheet,
            ))
        return out

    async def student_has_open_assignment(self, user_id: UUID, subject_id: UUID) -> bool:
        """Utilisé par ExamAccessService : l'élève a-t-il un devoir non rendu sur ce sujet privé ?"""
        ids = set(
            (
                await self.db.execute(
                    self._targets_query(user_id).where(Assignment.subject_id == subject_id)
                )
            ).scalars().all()
        )
        if not ids:
            return False
        done = set(
            (
                await self.db.execute(
                    select(AssignmentSubmission.assignment_id).where(
                        AssignmentSubmission.assignment_id.in_(ids),
                        AssignmentSubmission.student_id == user_id,
                        AssignmentSubmission.status.in_(DONE_STATUSES),
                    )
                )
            ).scalars().all()
        )
        return bool(ids - done)

    async def start(self, student: User, assignment_id: UUID):
        from app.modules.exam_sessions.service import ExamSessionService

        a, sub = await self._open_submission(student, assignment_id)
        if a.sd_subject_id:
            raise BadRequestException(detail="Ce devoir Start Deutsch se lance depuis son propre lecteur.")

        exam_id = (
            await self.db.execute(
                select(Level.exam_id).join(Subject, Subject.level_id == Level.id).where(Subject.id == a.subject_id)
            )
        ).scalar_one()

        result = await ExamSessionService(self.db).start_session(
            user_id=student.id, exam_id=exam_id, subject_id=a.subject_id
        )

        sub.exam_session_id = result.session_id
        if sub.status == "pending":
            sub.status = "in_progress"
            sub.started_at = _now()
        await self.db.commit()
        return result

    async def _open_submission(
        self, student: User, assignment_id: UUID
    ) -> tuple[Assignment, AssignmentSubmission]:
        """Vérifie que l'élève peut passer le devoir et crée sa copie au premier démarrage."""
        if student.role != UserRole.student:
            raise ForbiddenException(detail="Espace réservé aux élèves.")
        a = await self.db.get(Assignment, assignment_id)
        if not a or a.is_cancelled or not await self._is_targeted(a.id, student.id):
            raise NotFoundException(resource="Devoir", identifier=str(assignment_id))

        sub = await self._get_submission(a.id, student.id)
        if sub and sub.status in DONE_STATUSES:
            raise BadRequestException(detail="Vous avez déjà rendu ce devoir.")
        if not sub:
            sub = AssignmentSubmission(assignment_id=a.id, student_id=student.id, status="pending")
            self.db.add(sub)
            await self.db.flush()
        return a, sub

    # ── Start Deutsch ────────────────────────────────────

    async def student_has_open_sd_assignment(self, user_id: UUID, sd_subject_id: UUID) -> bool:
        """Utilisé par l'accès Start Deutsch : devoir non rendu sur ce sujet privé ?"""
        ids = set(
            (
                await self.db.execute(
                    self._targets_query(user_id).where(Assignment.sd_subject_id == sd_subject_id)
                )
            ).scalars().all()
        )
        if not ids:
            return False
        done = set(
            (
                await self.db.execute(
                    select(AssignmentSubmission.assignment_id).where(
                        AssignmentSubmission.assignment_id.in_(ids),
                        AssignmentSubmission.student_id == user_id,
                        AssignmentSubmission.status.in_(DONE_STATUSES),
                    )
                )
            ).scalars().all()
        )
        return bool(ids - done)

    async def start_start_deutsch(self, student: User, assignment_id: UUID) -> StartDeutschSession:
        """Démarre ou reprend un devoir Start Deutsch : renvoie la session du lecteur A1/A2."""
        from app.modules.start_deutsch.service import StartDeutschSessionService

        a, sub = await self._open_submission(student, assignment_id)
        if not a.sd_subject_id:
            raise BadRequestException(detail="Ce devoir ne concerne pas Start Deutsch.")

        if sub.sd_session_id:
            current = await self.db.get(StartDeutschSession, sub.sd_session_id)
            if current and current.status == "IN_PROGRESS":
                return current

        # start_session vérifie l'accès au sujet privé (devoir ouvert) et valide la transaction
        session = await StartDeutschSessionService(self.db).start_session(student, a.sd_subject_id)

        sub.sd_session_id = session.id
        if sub.status == "pending":
            sub.status = "in_progress"
            sub.started_at = _now()
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def _sd_sync(self, session: StartDeutschSession, sub: AssignmentSubmission, teacher_id: UUID | None) -> None:
        """Recalcule une copie Start Deutsch (sans le Sprechen) et met à jour session et copie."""
        from app.modules.start_deutsch.service import StartDeutschSessionService

        result = await StartDeutschSessionService(self.db).get_result_for_staff(session.id)
        now = _now()
        session.score = float(result["score"])
        if _sd_all_corrected(result):
            session.status = "COMPLETED"
            session.passed = result["passed"]
            sub.status = "graded"
            sub.final_score = _sd_percent(result)
            sub.graded_at = now
            if teacher_id:
                sub.graded_by = teacher_id
        else:
            session.status = "PENDING_REVIEW"
            session.passed = None
            sub.status = "submitted"

    async def on_sd_session_submitted(self, session: StartDeutschSession) -> None:
        """Appelé par StartDeutschSessionService.submit_session pour une copie de devoir."""
        subs = (
            await self.db.execute(
                select(AssignmentSubmission).where(AssignmentSubmission.sd_session_id == session.id)
            )
        ).scalars().all()
        for sub in subs:
            sub.submitted_at = _now()
            await self._sd_sync(session, sub, teacher_id=None)
        await self.db.commit()

    async def _sd_score_sheet(self, sd_session_id: UUID | None) -> StudentScoreSheet | None:
        """Relevé Start Deutsch : points par module, sans le Sprechen."""
        from app.modules.start_deutsch.service import StartDeutschSessionService

        session = await self.db.get(StartDeutschSession, sd_session_id) if sd_session_id else None
        if not session or session.status == "IN_PROGRESS":
            return None
        result = await StartDeutschSessionService(self.db).get_result_for_staff(session.id)

        rows = [
            StudentModuleScore(
                name=SD_MODULE_LABELS.get(m["slug"], m["slug"]),
                points=round(float(m["score_obtained"]), 1) if m["is_corrected"] else None,
                max_score=float(m["max_score"]),
            )
            for m in result["modules"]
        ]
        if not rows:
            return None
        is_final = _sd_all_corrected(result)
        return StudentScoreSheet(
            modules=rows,
            total_points=round(sum(r.points or 0 for r in rows), 1),
            total_max=sum(r.max_score for r in rows),
            is_final=is_final,
            passed=result["passed"] if is_final else None,
        )

    async def _grade_sd(
        self, teacher: User, a: Assignment, sub: AssignmentSubmission, data: GradeRequest
    ) -> None:
        """Note du Schreiben Start Deutsch : enregistrée comme correction du Teil."""
        from app.modules.start_deutsch.repository import SubjectRepository
        from app.modules.start_deutsch.service import StartDeutschSchreibenCorrectionService

        subject = await SubjectRepository(self.db).get_full_tree(a.sd_subject_id)
        questions = {
            q.id: (q, t)
            for m in subject.modules
            if m.slug != "sprechen"
            for t in m.teile
            for q in t.questions
        }
        answers = {
            ans.question_id: ans
            for ans in (
                await self.db.execute(
                    select(StartDeutschAnswer).where(StartDeutschAnswer.session_id == sub.sd_session_id)
                )
            ).scalars().all()
        }
        corrections = {
            c.teil_id: c
            for c in (
                await self.db.execute(
                    select(StartDeutschSchreibenCorrection).where(
                        StartDeutschSchreibenCorrection.session_id == sub.sd_session_id
                    )
                )
            ).scalars().all()
        }

        for item in data.answers:
            found = questions.get(item.question_id)
            if not found:
                raise BadRequestException(detail="Question inconnue pour ce sujet.")
            question, teil = found
            if teil.format_type != "free_text":
                raise BadRequestException(
                    detail=f"Le Teil {teil.teil_number} est corrigé automatiquement."
                )
            max_score = float(teil.max_score)
            if item.score > max_score:
                raise BadRequestException(
                    detail=f"Note supérieure au maximum ({max_score:g}) pour le Teil {teil.teil_number}."
                )

            answer = answers.get(question.id)
            text = (answer.user_answer or {}).get("text", "") if answer else ""
            if item.criteria:
                criteria = {
                    name: {"grade": "", "points": float(points), "label": name}
                    for name, points in item.criteria.items()
                }
            else:
                criteria = {
                    "enseignant": {
                        "grade": StartDeutschSchreibenCorrectionService._points_to_grade(item.score, max_score),
                        "points": float(item.score),
                        "label": "Note de l'enseignant",
                        "feedback": item.comment,
                    }
                }

            correction = corrections.get(teil.id)
            if correction is None:
                correction = StartDeutschSchreibenCorrection(
                    session_id=sub.sd_session_id, teil_id=teil.id, submitted_text=text or ""
                )
                self.db.add(correction)
            correction.submitted_text = text or ""
            correction.criteria_scores = criteria
            correction.overall_score = float(item.score)
            correction.max_score = max_score
            correction.feedback = item.comment

        await self.db.commit()
        # Les corrections viennent d'être écrites : on relit tout avant de recalculer
        self.db.expire_all()

        session = await self.db.get(StartDeutschSession, sub.sd_session_id)
        sub = await self._get_submission(a.id, sub.student_id)
        if data.teacher_comment is not None:
            sub.teacher_comment = data.teacher_comment
        await self._sd_sync(session, sub, teacher_id=teacher.id)
        await self.db.commit()

    async def _sd_schreiben_parts(self, sd_subject_id: UUID, sd_session_id: UUID | None) -> list[dict]:
        from app.modules.start_deutsch.repository import SubjectRepository

        subject = await SubjectRepository(self.db).get_full_tree(sd_subject_id)
        answers = {}
        if sd_session_id:
            answers = {
                ans.question_id: ans
                for ans in (
                    await self.db.execute(
                        select(StartDeutschAnswer).where(StartDeutschAnswer.session_id == sd_session_id)
                    )
                ).scalars().all()
            }

        parts: list[dict] = []
        for module in sorted(subject.modules, key=lambda m: m.order):
            for teil in sorted(module.teile, key=lambda t: t.teil_number):
                if teil.format_type != "free_text":
                    continue
                for q in sorted(teil.questions, key=lambda x: x.question_number):
                    content = q.content or {}
                    answer = answers.get(q.id)
                    text = (answer.user_answer or {}).get("text", "") if answer else ""
                    parts.append({
                        "teil": teil.teil_number,
                        "words": len(text.split()),
                        "instruction": content.get("prompt") or teil.instructions or "",
                        "prompts": [p for p in content.get("content_points") or [] if isinstance(p, str)],
                        "text": text,
                    })
        return parts

    # ── Moteur d'examen B1/B2 ────────────────────────────

    async def on_session_submitted(self, session: ExamSession) -> None:
        """Appelé par ExamSessionService.submit_session pour un sujet privé."""
        subs = (
            await self.db.execute(
                select(AssignmentSubmission).where(AssignmentSubmission.exam_session_id == session.id)
            )
        ).scalars().all()
        now = _now()
        for sub in subs:
            sub.submitted_at = now
            if session.status == "COMPLETED":
                # Sujet sans Schreiben/Sprechen : noté automatiquement
                sub.status = "graded"
                sub.final_score = session.score
                sub.graded_at = now
            else:
                sub.status = "submitted"
        await self.db.commit()

    # ── Enseignant : correction ──────────────────────────

    async def get_submission_for_grading(
        self, teacher: User, assignment_id: UUID, student_id: UUID
    ) -> SubmissionGradingResponse:
        from app.modules.exam_sessions.service import ExamSessionService

        a = await self._get_teacher_assignment(teacher, assignment_id)
        sub = await self._get_submission(a.id, student_id)
        user = await self.db.get(User, student_id)

        sessions: dict[UUID, ExamSession] = {}
        result = None
        sd_result = None
        if a.sd_subject_id:
            from app.modules.start_deutsch.service import StartDeutschSessionService

            if sub and sub.sd_session_id and sub.status in DONE_STATUSES:
                sd_result = await StartDeutschSessionService(self.db).get_result_for_staff(sub.sd_session_id)
        elif sub and sub.exam_session_id:
            session = await self.db.get(ExamSession, sub.exam_session_id)
            if session:
                sessions[session.id] = session
            if sub.status in DONE_STATUSES:
                result = await ExamSessionService(self.db).get_result_for_staff(
                    sub.exam_session_id, student_id
                )

        return SubmissionGradingResponse(
            submission=self._row(a, student_id, user, sub, sessions),
            teacher_comment=sub.teacher_comment if sub else None,
            result=result,
            sd_result=sd_result,
        )

    async def grade(
        self, teacher: User, assignment_id: UUID, student_id: UUID, data: GradeRequest
    ) -> SubmissionGradingResponse:
        from app.modules.exam_sessions.service import ExamSessionService

        a = await self._get_teacher_assignment(teacher, assignment_id)
        sub = await self._get_submission(a.id, student_id)
        session_id = sub.sd_session_id if sub and a.sd_subject_id else (sub.exam_session_id if sub else None)
        if not sub or not session_id or sub.status not in DONE_STATUSES:
            raise BadRequestException(detail="Ce devoir n'a pas encore été rendu.")

        if a.sd_subject_id:
            await self._grade_sd(teacher, a, sub, data)
            return await self.get_submission_for_grading(teacher, assignment_id, student_id)

        ess = ExamSessionService(self.db)
        subject = await ess._load_subject_full(a.subject_id)
        questions = {q.id: q for m in subject.modules for t in m.teile for q in t.questions}
        answers = {
            ans.question_id: ans for ans in await ess.answer_repo.get_by_session(sub.exam_session_id)
        }

        now = _now()
        for item in data.answers:
            question = questions.get(item.question_id)
            if not question:
                raise BadRequestException(detail="Question inconnue pour ce sujet.")
            if question.is_auto_correctable:
                raise BadRequestException(
                    detail=f"La question {question.question_number} est corrigée automatiquement."
                )
            if item.score > question.points:
                raise BadRequestException(
                    detail=f"Note supérieure au maximum ({question.points}) pour la question {question.question_number}."
                )

            answer = answers.get(question.id)
            if answer is None:
                # Question laissée vide par l'élève : on enregistre quand même la note
                answer = ExamSessionAnswer(
                    session_id=sub.exam_session_id, question_id=question.id, user_answer={}
                )
                self.db.add(answer)
            answer.score_obtained = float(item.score)
            answer.is_correct = None
            answer.corrected_at = now
            answer.feedback = {
                "teacher": {
                    "comment": item.comment,
                    "criteria": item.criteria,
                    "graded_by": str(teacher.id),
                }
            }
        await self.db.flush()

        session = await ess.rescore_session(sub.exam_session_id)

        if data.teacher_comment is not None:
            sub.teacher_comment = data.teacher_comment
        if session.status == "COMPLETED":
            sub.status = "graded"
            sub.final_score = session.score
            sub.graded_at = now
            sub.graded_by = teacher.id
        else:
            sub.status = "submitted"  # correction partielle
        await self.db.commit()

        return await self.get_submission_for_grading(teacher, assignment_id, student_id)

    # ── Copies Schreiben (PDF / ZIP) ─────────────────────

    async def _schreiben_parts(self, subject_id: UUID, session_id: UUID | None) -> list[dict]:
        from app.modules.exam_sessions.service import ExamSessionService

        ess = ExamSessionService(self.db)
        subject = await ess._load_subject_full(subject_id)
        answers = {}
        if session_id:
            answers = {a.question_id: a for a in await ess.answer_repo.get_by_session(session_id)}

        parts: list[dict] = []
        for module in sorted(subject.modules, key=lambda m: m.display_order):
            for teil in sorted(module.teile, key=lambda t: t.teil_number):
                for q in sorted(teil.questions, key=lambda x: x.question_number):
                    if q.question_type != "free_text":
                        continue
                    content = q.content or {}
                    answer = answers.get(q.id)
                    text = (answer.user_answer or {}).get("text", "") if answer else ""
                    instruction = (
                        content.get("scenario")
                        or content.get("instruction")
                        or content.get("topic")
                        or teil.instructions
                        or ""
                    )
                    prompts = content.get("prompts") or content.get("leitpunkte") or []
                    parts.append({
                        "teil": teil.teil_number,
                        "words": len(text.split()),
                        "instruction": instruction if isinstance(instruction, str) else "",
                        "prompts": [p for p in prompts if isinstance(p, str)],
                        "text": text,
                    })
        return parts

    @staticmethod
    def _render_schreiben_pdf(
        *, student_name: str, title: str, exam_label: str, submitted_at: datetime | None, parts: list[dict]
    ) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
            title=f"Copie Schreiben - {student_name}",
        )
        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, spaceAfter=4)
        meta = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#52525b"))
        teil_h = ParagraphStyle("Teil", parent=styles["Heading2"], fontSize=12, spaceBefore=6, spaceAfter=6)
        consigne = ParagraphStyle(
            "Consigne", parent=styles["Normal"], fontSize=9.5, leading=13, textColor=colors.HexColor("#3f3f46")
        )
        # Double interligne + marge droite de 5 cm pour les annotations
        answer = ParagraphStyle(
            "Answer", parent=styles["Normal"], fontSize=11, leading=24,
            rightIndent=5 * cm, borderWidth=0.5, borderColor=colors.HexColor("#a1a1aa"), borderPadding=8,
        )

        story = [
            Paragraph(_html(title), h1),
            Paragraph(_html(f"{student_name}  |  {exam_label}"), meta),
            Paragraph(
                f"Rendu le {submitted_at:%d/%m/%Y à %H:%M}" if submitted_at else "Non rendu", meta
            ),
            Spacer(1, 0.6 * cm),
        ]
        for i, part in enumerate(parts):
            if i > 0:
                story.append(PageBreak())
            story.append(Paragraph(f"Teil {part['teil']}  ({part['words']} mots)", teil_h))
            if part["instruction"]:
                story.append(Paragraph(_html(part["instruction"]), consigne))
            for prompt in part["prompts"]:
                story.append(Paragraph("• " + _html(prompt), consigne))
            story.append(Spacer(1, 0.5 * cm))
            story.append(Paragraph(_html(part["text"]) or "<i>(aucune réponse)</i>", answer))

        doc.build(story)
        return buffer.getvalue()

    async def schreiben_pdf(self, teacher: User, assignment_id: UUID, student_id: UUID) -> tuple[str, bytes]:
        a = await self._get_teacher_assignment(teacher, assignment_id)
        sub = await self._get_submission(a.id, student_id)
        if not sub or sub.status not in DONE_STATUSES:
            raise BadRequestException(detail="Ce devoir n'a pas encore été rendu.")
        return await self._build_pdf_for(a, sub)

    async def _build_pdf_for(self, a: Assignment, sub: AssignmentSubmission) -> tuple[str, bytes]:
        _, exam_name, cefr_code = await self._info(a)
        student = await self.db.get(User, sub.student_id)
        if a.sd_subject_id:
            parts = await self._sd_schreiben_parts(a.sd_subject_id, sub.sd_session_id)
        else:
            parts = await self._schreiben_parts(a.subject_id, sub.exam_session_id)
        if not parts:
            raise BadRequestException(detail="Ce sujet ne contient pas de Schreiben.")
        name = student.full_name if student else "Eleve"
        pdf = self._render_schreiben_pdf(
            student_name=name,
            title=a.title,
            exam_label=f"{exam_name} ({cefr_code})",
            submitted_at=sub.submitted_at,
            parts=parts,
        )
        return f"schreiben_{_slug(name)}.pdf", pdf

    async def schreiben_zip(self, teacher: User, assignment_id: UUID) -> tuple[str, bytes]:
        a = await self._get_teacher_assignment(teacher, assignment_id)
        subs = [s for s in (await self._submissions(a.id)).values() if s.status in DONE_STATUSES]
        if not subs:
            raise BadRequestException(detail="Aucune copie rendue pour ce devoir.")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            used: set[str] = set()
            for sub in subs:
                filename, pdf = await self._build_pdf_for(a, sub)
                if filename in used:
                    filename = filename.replace(".pdf", f"_{str(sub.student_id)[:6]}.pdf")
                used.add(filename)
                zf.writestr(filename, pdf)
        return f"copies_{_slug(a.title)}.zip", buffer.getvalue()

    # ── Copie annotée (interne) ──────────────────────────

    async def upload_annotated(
        self, teacher: User, assignment_id: UUID, student_id: UUID, file: UploadFile
    ) -> None:
        a = await self._get_teacher_assignment(teacher, assignment_id)
        sub = await self._get_submission(a.id, student_id)
        if not sub or sub.status not in DONE_STATUSES:
            raise BadRequestException(detail="Ce devoir n'a pas encore été rendu.")

        ext = Path(file.filename or "").suffix.lower()
        if ext not in ANNOTATED_EXTENSIONS:
            raise BadRequestException(detail="Format accepté : PDF, PNG ou JPG.")
        content = await file.read()
        if len(content) > ANNOTATED_MAX_BYTES:
            raise BadRequestException(detail="Fichier trop volumineux (10 Mo maximum).")

        folder = ANNOTATED_DIR / str(sub.id)
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("copie_annotee.*"):
            old.unlink(missing_ok=True)
        path = folder / f"copie_annotee{ext}"
        path.write_bytes(content)

        sub.annotated_file = str(path)
        await self.db.commit()

    async def annotated_path(self, teacher: User, assignment_id: UUID, student_id: UUID) -> Path:
        a = await self._get_teacher_assignment(teacher, assignment_id)
        sub = await self._get_submission(a.id, student_id)
        if not sub or not sub.annotated_file or not Path(sub.annotated_file).exists():
            raise NotFoundException(resource="Copie annotée", identifier=str(student_id))
        return Path(sub.annotated_file)