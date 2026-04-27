"""
app/modules/exam_sessions/service.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.modules.exam_access.service import ExamAccessService
from app.modules.exam_sessions.models import ExamSession, ExamSessionAnswer
from app.modules.exam_sessions.repository import (
    ExamSessionRepository,
    ExamSessionAnswerRepository,
)
from app.modules.exam_sessions.schemas import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    BulkAnswerSubmitRequest,
    SessionListResponse,
    SessionResultResponse,
    SessionStartResponse,
    ModuleResultResponse,
    TeilResultResponse,
    AnswerDetailResponse,
)
from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.modules.exams.repository import ExamRepository
from app.modules.questions.models import Question
from app.shared.exceptions.http import BadRequestException, ForbiddenException, NotFoundException


class ExamSessionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamSessionRepository(db)
        self.answer_repo = ExamSessionAnswerRepository(db)
        self.exam_repo = ExamRepository(db)
        self.access_service = ExamAccessService(db)

    # ── Démarrage ────────────────────────────────────────

    async def start_session(
        self, user_id: UUID, exam_id: UUID, subject_id: UUID | None = None
        ) -> SessionStartResponse:
        # 1. Vérifier accès
        await self.access_service.require_access(user_id, exam_id)

        # 2. Session active existante → reprendre
        active = await self.repo.get_active_session(user_id, exam_id)
        if active:
            subject = await self._load_subject_full(active.subject_id)  # ← fix
            exam = await self._load_exam_by_subject(active.subject_id)
            modules_data = self._build_modules_content(subject)
            answers = await self.answer_repo.get_by_session(active.id)
            existing = {
                str(a.question_id): {"answer": a.user_answer}
                for a in answers
            }
            return SessionStartResponse(
                session_id=active.id,
                exam_id=exam.id,
                exam_name=exam.name,
                subject_id=subject.id,
                subject_number=subject.subject_number,
                subject_name=subject.name,
                status=active.status,
                started_at=active.started_at,
                modules=modules_data,
                existing_answers=existing,
            )

        # 3. Choisir le sujet
        subject = await self._pick_subject(user_id, exam_id, subject_id)
        subject = await self._load_subject_full(subject.id)  # ← fix
        exam = await self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise NotFoundException(resource="Exam", identifier=str(exam_id))

        # 4. Créer une nouvelle session
        session = await self.repo.create(
            user_id=user_id,
            exam_id=exam_id,
            subject_id=subject.id,
            status="IN_PROGRESS",
            started_at=datetime.now(timezone.utc),
        )

        modules_data = self._build_modules_content(subject)

        return SessionStartResponse(
            session_id=session.id,
            exam_id=exam.id,
            exam_name=exam.name,
            subject_id=subject.id,
            subject_number=subject.subject_number,
            subject_name=subject.name,
            status=session.status,
            started_at=session.started_at,
            modules=modules_data,
    )
        
        
    # ── Réponses ─────────────────────────────────────────

    async def submit_answer(
        self,
        session_id: UUID,
        user_id: UUID,
        data: AnswerSubmitRequest,
    ) -> AnswerSubmitResponse:
        session = await self._get_session_or_403(session_id, user_id)

        if session.status != "IN_PROGRESS":
            raise BadRequestException(detail="Cette session est déjà soumise.")

        question = await self._get_question(data.question_id)

        answer = await self.answer_repo.upsert(
            session_id=session_id,
            question_id=data.question_id,
            user_answer=data.user_answer,
        )

        is_correct = None
        score_obtained = None
        correct_answer = None

        if question.is_auto_correctable:
            is_correct = self._auto_correct(question, data.user_answer)
            score_obtained = float(question.points) if is_correct else 0.0

            await self.answer_repo.update(
                answer.id,
                is_correct=is_correct,
                score_obtained=score_obtained,
            )

        return AnswerSubmitResponse(
            question_id=data.question_id,
            user_answer=data.user_answer,
            is_correct=is_correct,
            score_obtained=score_obtained,
            correct_answer=correct_answer,
        )

    async def submit_bulk_answers(
        self,
        session_id: UUID,
        user_id: UUID,
        data: BulkAnswerSubmitRequest,
    ) -> list[AnswerSubmitResponse]:
        return [
            await self.submit_answer(session_id, user_id, answer)
            for answer in data.answers
        ]

    # ── Soumission finale ────────────────────────────────

    async def submit_session(
        self, session_id: UUID, user_id: UUID
    ) -> SessionResultResponse:
        session = await self._get_session_or_403(session_id, user_id)

        if session.status != "IN_PROGRESS":
            raise BadRequestException(detail="Cette session est déjà soumise.")

        answers = await self.answer_repo.get_by_session(session_id)
        subject = await self._load_subject_full(session.subject_id)
        exam = await self.exam_repo.get_by_id(session.exam_id)

        score_breakdown, has_pending = self._compute_scores(subject, answers)

        corrected_scores = [v for v in score_breakdown.values() if v is not None]
        global_score = (
            sum(corrected_scores) / len(corrected_scores)
            if corrected_scores else None
        )

        status = "PENDING_REVIEW" if has_pending else "COMPLETED"

        passed = None
        total_pass_score = None
        if not has_pending and global_score is not None:
            level = subject.level if hasattr(subject, "level") else None
            if not level:
                level = await self._get_level(subject.level_id)
            if level:
                total_pass_score = level.total_pass_score
                passed = global_score >= total_pass_score

        now = datetime.now(timezone.utc)
        duration = int((now - session.started_at).total_seconds())

        session = await self.repo.update(
            session_id,
            status=status,
            score=global_score,
            score_breakdown=score_breakdown,
            passed=passed,
            submitted_at=now,
            duration_seconds=duration,
        )

        return await self._build_result_response(
            session, exam, subject, answers, total_pass_score
        )

    # ── Résultat ─────────────────────────────────────────

    async def get_result(
        self, session_id: UUID, user_id: UUID
    ) -> SessionResultResponse:
        session = await self._get_session_or_403(session_id, user_id)

        if session.status == "IN_PROGRESS":
            raise BadRequestException(detail="La session n'est pas encore soumise.")

        answers = await self.answer_repo.get_by_session(session_id)
        subject = await self._load_subject_full(session.subject_id)
        exam = await self.exam_repo.get_by_id(session.exam_id)
        level = await self._get_level(subject.level_id)
        total_pass_score = level.total_pass_score if level else None

        return await self._build_result_response(
            session, exam, subject, answers, total_pass_score
        )

    async def get_my_sessions(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[SessionListResponse]:
        sessions = await self.repo.get_by_user(user_id, skip=skip, limit=limit)
        result = []
        for s in sessions:
            exam = await self.exam_repo.get_by_id(s.exam_id)
            subject = await self._get_subject(s.subject_id)
            result.append(SessionListResponse(
                id=s.id,
                exam_id=s.exam_id,
                exam_name=exam.name if exam else "",
                exam_slug=exam.slug if exam else "",
                subject_id=s.subject_id,
                subject_number=subject.subject_number if subject else 0,
                status=s.status,
                score=s.score,
                passed=s.passed,
                started_at=s.started_at,
                submitted_at=s.submitted_at,
                duration_seconds=s.duration_seconds,
            ))
        return result

    # ── Helpers privés ───────────────────────────────────

    async def _get_session_or_403(
        self, session_id: UUID, user_id: UUID
    ) -> ExamSession:
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise NotFoundException(resource="Session", identifier=str(session_id))
        if session.user_id != user_id:
            raise ForbiddenException(detail="Accès refusé à cette session.")
        return session

    async def _get_question(self, question_id: UUID) -> Question:
        result = await self.db.execute(
            select(Question).where(Question.id == question_id)
        )
        q = result.scalar_one_or_none()
        if not q:
            raise NotFoundException(resource="Question", identifier=str(question_id))
        return q

    async def _get_subject(self, subject_id: UUID) -> Subject:
        result = await self.db.execute(
            select(Subject).where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()

    async def _get_level(self, level_id: UUID) -> Level | None:
        result = await self.db.execute(
            select(Level).where(Level.id == level_id)
        )
        return result.scalar_one_or_none()

    async def _load_subject_full(self, subject_id: UUID) -> Subject | None:
        """Charge subject + modules + teile + questions."""
        result = await self.db.execute(
            select(Subject)
            .options(
                selectinload(Subject.modules)
                .selectinload(Module.teile)
                .selectinload(Teil.questions)
            )
            .where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()

    async def _load_exam_by_subject(self, subject_id: UUID) -> Exam | None:
        """Remonte exam depuis subject_id."""
        result = await self.db.execute(
            select(Exam)
            .join(Level, Level.exam_id == Exam.id)
            .join(Subject, Subject.level_id == Level.id)
            .where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()

    async def _pick_subject(
        self, user_id: UUID, exam_id: UUID, subject_id: UUID | None
    ) -> Subject:
        """
        Choisit le sujet à jouer :
        - Si subject_id fourni → utiliser ce sujet
        - Sinon → prochain sujet non encore complété par ce user
        - Si tous faits → revenir au premier
        """
        if subject_id:
            subject = await self._get_subject(subject_id)
            if not subject:
                raise NotFoundException(resource="Subject", identifier=str(subject_id))
            return subject

        # Récupérer tous les subjects du level de cet exam
        result = await self.db.execute(
            select(Subject)
            .join(Level, Level.id == Subject.level_id)
            .where(Level.exam_id == exam_id, Subject.is_active == True)
            .order_by(Subject.subject_number)
        )
        all_subjects = list(result.scalars().all())

        if not all_subjects:
            raise NotFoundException(
                resource="Subject",
                identifier=f"Aucun sujet disponible pour l'exam {exam_id}"
            )

        # Sujets déjà complétés par ce user
        done_ids = await self.repo.get_done_subject_ids(user_id, exam_id)

        # Prochain sujet non fait
        for subject in all_subjects:
            if subject.id not in done_ids:
                return subject

        # Tous faits → revenir au premier
        return all_subjects[0]

    def _build_modules_content(self, subject: Subject) -> list[dict]:
        """Construit la liste de modules pour SessionStartResponse."""
        modules = []
        for module in subject.modules:
            teile_data = []
            for teil in module.teile:
                questions_data = [
                    {
                        "id": str(q.id),
                        "question_number": q.question_number,
                        "question_type": q.question_type,
                        "content": q.content,
                        "points": q.points,
                        "audio_file": q.audio_file,
                    }
                    for q in sorted(teil.questions, key=lambda x: x.question_number)
                ]
                teile_data.append({
                    "id": str(teil.id),
                    "teil_number": teil.teil_number,
                    "format_type": teil.format_type,
                    "instructions": teil.instructions,
                    "max_score": teil.max_score,
                    "time_minutes": teil.time_minutes,
                    "config": teil.config,
                    "questions": questions_data,
                })
            modules.append({
                "id": str(module.id),
                "slug": module.slug,
                "name": module.name,
                "time_limit_minutes": module.time_limit_minutes,
                "max_score": module.max_score,
                "display_order": module.display_order,
                "teile": sorted(teile_data, key=lambda x: x["teil_number"]),
            })
        return sorted(modules, key=lambda x: x["display_order"])

    def _auto_correct(self, question: Question, user_answer: dict) -> bool:
        try:
            expected = question.correct_answer.get("answer", "").strip().lower()
            given = str(user_answer.get("answer", "")).strip().lower()
            return expected == given
        except Exception:
            return False

    def _compute_scores(
        self,
        subject: Subject,
        answers: list[ExamSessionAnswer],
    ) -> tuple[dict, bool]:
        answer_map = {a.question_id: a for a in answers}
        score_breakdown = {}
        has_pending = False

        for module in subject.modules:
            module_score = 0.0
            module_pending = False

            for teil in module.teile:
                for question in teil.questions:
                    answer = answer_map.get(question.id)
                    if not answer:
                        continue
                    if answer.score_obtained is not None:
                        module_score += answer.score_obtained
                    elif not question.is_auto_correctable:
                        module_pending = True

            if module_pending:
                score_breakdown[module.slug] = None
                has_pending = True
            else:
                total_points = sum(
                    q.points
                    for teil in module.teile
                    for q in teil.questions
                )
                if total_points > 0:
                    score_breakdown[module.slug] = round(
                        (module_score / total_points) * 100, 2
                    )
                else:
                    score_breakdown[module.slug] = 0.0

        return score_breakdown, has_pending

    async def _build_result_response(
        self,
        session: ExamSession,
        exam: Exam,
        subject: Subject,
        answers: list[ExamSessionAnswer],
        total_pass_score: int | None,
    ) -> SessionResultResponse:
        answer_map = {a.question_id: a for a in answers}
        modules_result = []

        for module in subject.modules:
            teil_results = []
            module_score = 0.0
            module_is_corrected = True

            for teil in module.teile:
                teil_score = 0.0
                answer_details = []

                for question in sorted(teil.questions, key=lambda x: x.question_number):
                    answer = answer_map.get(question.id)
                    if answer:
                        if answer.score_obtained is not None:
                            teil_score += answer.score_obtained
                        elif not question.is_auto_correctable:
                            module_is_corrected = False

                        answer_details.append(AnswerDetailResponse(
                            question_id=question.id,
                            question_number=question.question_number,
                            question_type=question.question_type,
                            user_answer=answer.user_answer,
                            correct_answer=question.correct_answer,
                            is_correct=answer.is_correct,
                            score_obtained=answer.score_obtained,
                            points_possible=question.points,
                            feedback=answer.feedback,
                            corrected_at=answer.corrected_at,
                        ))

                teil_results.append(TeilResultResponse(
                    teil_number=teil.teil_number,
                    format_type=teil.format_type,
                    max_score=teil.max_score,
                    score_obtained=round(teil_score, 2),
                    answers=answer_details,
                ))
                module_score += teil_score

            modules_result.append(ModuleResultResponse(
                slug=module.slug,
                name=module.name,
                max_score=module.max_score,
                score_obtained=round(module_score, 2) if module_is_corrected else None,
                is_corrected=module_is_corrected,
                teile=teil_results,
            ))

        result_message = None
        if session.passed is True:
            result_message = "Félicitations ! Vous avez réussi cet examen."
        elif session.passed is False:
            result_message = "Vous n'avez pas atteint le score requis. Continuez à vous entraîner !"
        elif session.status == "PENDING_REVIEW":
            result_message = "Résultat partiel — certaines parties sont en attente de correction."

        return SessionResultResponse(
            session_id=session.id,
            exam_id=session.exam_id,
            exam_name=exam.name if exam else "",
            subject_id=session.subject_id,
            subject_number=subject.subject_number,
            status=session.status,
            score=session.score,
            score_breakdown=session.score_breakdown,
            passed=session.passed,
            total_pass_score=total_pass_score or 0,
            started_at=session.started_at,
            submitted_at=session.submitted_at,
            duration_seconds=session.duration_seconds,
            modules=modules_result,
            result_message=result_message,
        )