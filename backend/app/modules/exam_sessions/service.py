"""
app/modules/exam_sessions/service.py

Notation : une seule règle pour tous les fournisseurs, le barème vit dans les
données (teil.max_score, module.max_score), pas dans le code.
  - points d'un Teil   : ramenés à teil.max_score
  - points d'un module : ramenés à module.max_score
  - score global       : total des points de l'écrit / total possible
  - réussite           : lue dans level.exam_config (scoring_model / pass_rule)
Les modules oraux sans réponse sont ignorés : ils sont évalués en session orale.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

logger = logging.getLogger(__name__)

# Modules oraux : évalués en session orale avec l'examinateur, pas dans le lecteur
ORAL_SLUGS = {"sprechen", "muendlicher_ausdruck", "mündlicher_ausdruck"}


class ExamSessionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamSessionRepository(db)
        self.answer_repo = ExamSessionAnswerRepository(db)
        self.exam_repo = ExamRepository(db)
        self.access_service = ExamAccessService(db)

    # ── Démarrage ────────────────────────────────────────

    async def start_session(
        self, user_id: UUID, exam_id: UUID, subject_id: UUID | None = None, module_slugs: list[str] | None = None,
    ) -> SessionStartResponse:

        requested_slugs = self._normalize_slugs(module_slugs)

        # 1. Déterminer le subject cible (explicite ou auto-pick)
        if subject_id:
            subject_obj = await self._get_subject(subject_id)
            if not subject_obj:
                raise NotFoundException(resource="Subject", identifier=str(subject_id))
            await self.access_service.require_subject_access(user_id, subject_obj)
        else:
            subject_obj = await self._pick_subject(user_id, exam_id, None)
            await self.access_service.require_subject_access(user_id, subject_obj)

        # 2. Réutiliser la session active SEULEMENT si elle porte sur ce subject précis
        active = await self.repo.get_active_session(user_id, exam_id, subject_obj.id)
        # Une session en cours sur une autre sélection de modules n'est pas reprise
        if active and self._normalize_slugs(active.module_slugs) != requested_slugs:
            await self.repo.update(active.id, status="ABANDONED")
            active = None
        if active:
            subject = await self._load_subject_full(active.subject_id)
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

        # 3. Nouvelle session sur le subject demandé
        #    (pas de session active, ou session active sur un AUTRE subject)
        subject = await self._load_subject_full(subject_obj.id)
        exam = await self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise NotFoundException(resource="Exam", identifier=str(exam_id))

        session = await self.repo.create(
            user_id=user_id,
            exam_id=exam_id,
            subject_id=subject.id,
            status="IN_PROGRESS",
            started_at=datetime.now(timezone.utc),
            module_slugs=requested_slugs,
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
            correct_answer=None,
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

    # ── Règles de réussite ───────────────────────────────

    @staticmethod
    def _pass_rules(level: Level | None, provider: str) -> dict:
        """Règle de réussite lue dans level.exam_config.

        scoring_model = per_module_100      (Goethe) : chaque module >= seuil
        scoring_model = per_module_weighted (TELC)   : total de l'écrit >= seuil
        Un 'pass_rule' explicite dans exam_config reste prioritaire
        (each_module, tdn_levels, global_and_modules, global).
        """
        rules = dict((level.exam_config or {}) if level else {})
        if "pass_rule" not in rules:
            if rules.get("scoring_model") == "per_module_100":
                rules["pass_rule"] = "each_module"
            else:
                rules["pass_rule"] = "global"
        if rules.get("pass_threshold") and "module_min" not in rules:
            rules["module_min"] = rules["pass_threshold"]
        return rules

    @staticmethod
    def _tdn_level(score: float | None, rules: dict) -> str | None:
        if score is None:
            return None
        thresholds = rules.get("tdn_thresholds") or {"5": 78, "4": 63, "3": 45}
        for tdn in ("5", "4", "3"):
            if score >= thresholds.get(tdn, 101):
                return f"TDN {tdn}"
        return "unter TDN 3"

    # ── Soumission finale ────────────────────────────────

    async def _evaluate(
        self,
        subject: Subject,
        exam: Exam | None,
        answers: list[ExamSessionAnswer],
        module_slugs: list[str] | None = None,
    ) -> dict:
        """Score par module, score global, statut et réussite (logique commune
        à la soumission et à la correction par l'enseignant)."""
        provider = exam.provider if exam else "TELC"
        modules = self._scoped_modules(subject, module_slugs)
        score_breakdown, has_pending = self._compute_scores(
            subject, answers, provider=provider, modules=modules
        )

        # Total des points de l'écrit / total possible (TELC B2 : x / 225, ÖSD B2 : x / 70)
        global_score = self._weighted_global(subject, answers, modules=modules)

        level = await self._get_level(subject.level_id)
        total_pass_score = level.total_pass_score if level else None

        rules = self._pass_rules(level, provider)
        module_scores = [v for v in score_breakdown.values() if v is not None]
        module_min = rules.get("module_min", 60)

        passed = None
        if not has_pending and global_score is not None and level:
            rule = rules["pass_rule"]
            if rule == "each_module":          # Goethe / ECL : chaque module >= seuil
                passed = all(v >= module_min for v in module_scores)
            elif rule == "tdn_levels":         # TestDaF : pas de réussite globale
                passed = None
            elif rule == "global_and_modules": # total + minimum par module
                passed = global_score >= total_pass_score and all(
                    v >= module_min for v in module_scores
                )
            else:                              # TELC / ÖSD : total de l'écrit
                passed = global_score >= total_pass_score

        return {
            "status": "PENDING_REVIEW" if has_pending else "COMPLETED",
            "score": global_score,
            "score_breakdown": score_breakdown,
            "passed": passed,
            "total_pass_score": total_pass_score,
        }

    async def rescore_session(self, session_id: UUID) -> ExamSession:
        """Recalcule une session après correction manuelle (enseignant)."""
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise NotFoundException(resource="Session", identifier=str(session_id))
        answers = await self.answer_repo.get_by_session(session_id)
        subject = await self._load_subject_full(session.subject_id)
        exam = await self.exam_repo.get_by_id(session.exam_id)
        ev = await self._evaluate(subject, exam, answers, session.module_slugs)
        return await self.repo.update(
            session_id,
            status=ev["status"],
            score=ev["score"],
            score_breakdown=ev["score_breakdown"],
            passed=ev["passed"],
        )

    def _private_result(
        self, session: ExamSession, exam: Exam | None, subject: Subject, total_pass_score: int | None
    ) -> SessionResultResponse:
        """Réponse élève pour un devoir : aucun détail, seulement le statut."""
        graded = session.status == "COMPLETED"
        return SessionResultResponse(
            session_id=session.id,
            exam_id=session.exam_id,
            exam_name=exam.name if exam else "",
            subject_id=session.subject_id,
            subject_number=subject.subject_number,
            status=session.status,
            score=session.score if graded else None,
            score_breakdown=None,
            passed=None,
            total_pass_score=total_pass_score or 0,
            started_at=session.started_at,
            submitted_at=session.submitted_at,
            duration_seconds=session.duration_seconds,
            modules=[],
            result_message=(
                "Devoir rendu et noté. Retrouvez votre note finale dans vos devoirs."
                if graded
                else "Devoir rendu. Votre enseignant va le corriger : votre note apparaîtra dans vos devoirs."
            ),
        )

    async def submit_session(
        self, session_id: UUID, user_id: UUID
    ) -> SessionResultResponse:
        session = await self._get_session_or_403(session_id, user_id)

        if session.status != "IN_PROGRESS":
            raise BadRequestException(detail="Cette session est déjà soumise.")

        answers = await self.answer_repo.get_by_session(session_id)
        subject = await self._load_subject_full(session.subject_id)
        exam = await self.exam_repo.get_by_id(session.exam_id)

        ev = await self._evaluate(subject, exam, answers, session.module_slugs)

        now = datetime.now(timezone.utc)
        session = await self.repo.update(
            session_id,
            status=ev["status"],
            score=ev["score"],
            score_breakdown=ev["score_breakdown"],
            passed=ev["passed"],
            submitted_at=now,
            duration_seconds=int((now - session.started_at).total_seconds()),
        )

        # Devoir (sujet privé) : on met à jour la copie et on ne révèle rien
        if subject.is_private:
            from app.modules.assignments.service import AssignmentService
            await AssignmentService(self.db).on_session_submitted(session)
            return self._private_result(session, exam, subject, ev["total_pass_score"])

        return await self._build_result_response(
            session, exam, subject, answers, ev["total_pass_score"]
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

        if subject.is_private:
            raise ForbiddenException(
                detail="Le résultat de ce devoir se consulte dans votre espace Devoirs."
            )

        exam = await self.exam_repo.get_by_id(session.exam_id)
        level = await self._get_level(subject.level_id)
        total_pass_score = level.total_pass_score if level else None

        return await self._build_result_response(
            session, exam, subject, answers, total_pass_score
        )

    async def get_result_for_staff(
        self, session_id: UUID, student_id: UUID
    ) -> SessionResultResponse:
        """Variante de get_result sans contrainte 'requester == owner' : le
        contrôle d'accès (directeur/secrétaire/enseignant scopé) est fait
        en amont, dans le service appelant."""
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise NotFoundException(resource="Session", identifier=str(session_id))
        if session.user_id != student_id:
            raise ForbiddenException(detail="Cette session n'appartient pas à cet étudiant.")
        if session.status == "IN_PROGRESS":
            raise BadRequestException(detail="La session n'est pas encore soumise.")

        answers = await self.answer_repo.get_by_session(session_id)
        subject = await self._load_subject_full(session.subject_id)
        exam = await self.exam_repo.get_by_id(session.exam_id)
        level = await self._get_level(subject.level_id)
        total_pass_score = level.total_pass_score if level else None

        return await self._build_result_response(
            session, exam, subject, answers, total_pass_score,
            include_empty_free_text=True,
        )

    async def get_my_sessions(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[SessionListResponse]:
        sessions = await self.repo.get_by_user(user_id, skip=skip, limit=limit)
        result = []
        for s in sessions:
            exam = await self.exam_repo.get_by_id(s.exam_id)
            subject = await self._get_subject(s.subject_id)
            # Les devoirs ont leur propre espace : pas dans l'historique d'entraînement
            if subject and subject.is_private:
                continue
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
                module_slugs=s.module_slugs,
                 score_breakdown=s.score_breakdown,
            ))
        return result

    # ── Helpers privés : accès DB ────────────────────────

    async def _get_session_or_403(self, session_id: UUID, user_id: UUID) -> ExamSession:
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise NotFoundException(resource="Session", identifier=str(session_id))
        if session.user_id != user_id:
            raise ForbiddenException(detail="Accès refusé à cette session.")
        return session

    async def _get_question(self, question_id: UUID) -> Question:
        result = await self.db.execute(select(Question).where(Question.id == question_id))
        q = result.scalar_one_or_none()
        if not q:
            raise NotFoundException(resource="Question", identifier=str(question_id))
        return q

    async def _get_subject(self, subject_id: UUID) -> Subject:
        result = await self.db.execute(select(Subject).where(Subject.id == subject_id))
        return result.scalar_one_or_none()

    async def _get_level(self, level_id: UUID) -> Level | None:
        result = await self.db.execute(select(Level).where(Level.id == level_id))
        return result.scalar_one_or_none()

    async def _load_subject_full(self, subject_id: UUID) -> Subject | None:
        # Expirer le cache pour forcer un vrai chargement
        await self.db.execute(select(Subject).where(Subject.id == subject_id))

        result = await self.db.execute(
            select(Subject)
            .options(
                selectinload(Subject.modules)
                .selectinload(Module.teile)
                .selectinload(Teil.questions)
            )
            .where(Subject.id == subject_id)
            .execution_options(populate_existing=True)
        )
        subject = result.scalar_one_or_none()

        logger.info(
            f"_load_subject_full: subject_id={subject_id}, "
            f"modules={len(subject.modules) if subject else 'None'}"
        )
        return subject

    async def _load_exam_by_subject(self, subject_id: UUID) -> Exam | None:
        result = await self.db.execute(
            select(Exam)
            .join(Level, Level.exam_id == Exam.id)
            .join(Subject, Subject.level_id == Level.id)
            .where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()

    async def _pick_subject(self, user_id: UUID, exam_id: UUID, subject_id: UUID | None) -> Subject:
        if subject_id:
            subject = await self._get_subject(subject_id)
            if not subject:
                raise NotFoundException(resource="Subject", identifier=str(subject_id))
            return subject

        result = await self.db.execute(
            select(Subject)
            .join(Level, Level.id == Subject.level_id)
            .where(Level.exam_id == exam_id, Subject.is_active == True, Subject.is_private == False)
            .order_by(Subject.subject_number)
        )
        all_subjects = list(result.scalars().all())

        if not all_subjects:
            raise NotFoundException(
                resource="Subject",
                identifier=f"Aucun sujet disponible pour l'exam {exam_id}"
            )

        done_ids = await self.repo.get_done_subject_ids(user_id, exam_id)
        for subject in all_subjects:
            if subject.id not in done_ids:
                return subject
        return all_subjects[0]

    # ── Helpers privés : contenu ─────────────────────────

    def _build_modules_content(self, subject: Subject) -> list[dict]:
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

    # ── Helpers privés : sélection de modules ────────────

    @staticmethod
    def _normalize_slugs(slugs: list[str] | None) -> list[str] | None:
        cleaned = sorted({s.strip().lower() for s in (slugs or []) if s and s.strip()})
        return cleaned or None

    @staticmethod
    def _scoped_modules(subject: Subject, module_slugs: list[str] | None) -> list[Module]:
        """Modules réellement passés : tous (examen complet) ou la sélection
        (module seul). Même règle que le front : le slug du module contient
        le slug demandé."""
        if not module_slugs:
            return list(subject.modules)
        targets = [s.lower() for s in module_slugs]
        return [m for m in subject.modules if any(t in m.slug.lower() for t in targets)]

    # ── Helpers privés : notation ────────────────────────

    @staticmethod
    def _teil_points(teil: Teil, answer_map: dict) -> tuple[float, float, bool]:
        """Points obtenus, points max et état 'en attente' d'un Teil.

        Les points bruts sont ramenés au barème officiel du Teil (teil.max_score),
        quel que soit le nombre de questions ou les points stockés par question.
        Ex. TELC Lesen T3 : 10 questions -> 25 pts, soit 2,5 pts par question.
        """
        raw = 0.0
        raw_max = 0.0
        pending = False
        for q in teil.questions:
            raw_max += float(q.points or 0)
            a = answer_map.get(q.id)
            if not a:
                continue
            if a.score_obtained is not None:
                raw += float(a.score_obtained)
            elif not q.is_auto_correctable:
                pending = True
        if teil.max_score and raw_max > 0:
            return raw / raw_max * teil.max_score, float(teil.max_score), pending
        return raw, raw_max, pending

    def _module_points(
        self, module: Module, answer_map: dict
    ) -> tuple[float, float, bool]:
        """Points du module ramenés à module.max_score.

        TELC / ÖSD : la somme des Teile vaut déjà le max du module.
        Goethe     : 30 items -> 100 pts (équivalent du x 3,33).
        """
        got = total = 0.0
        pending = False
        for teil in module.teile:
            g, t, p = self._teil_points(teil, answer_map)
            got += g
            total += t
            pending = pending or p
        if total > 0 and module.max_score:
            return got / total * module.max_score, float(module.max_score), pending
        return got, total, pending

    @staticmethod
    def _skip_module(module: Module, answer_map: dict) -> bool:
        """Module oral sans aucune réponse : évalué en session orale, ignoré ici."""
        if module.slug not in ORAL_SLUGS:
            return False
        return not any(q.id in answer_map for t in module.teile for q in t.questions)

    def _weighted_global(
        self,
        subject: Subject,
        answers: list[ExamSessionAnswer],
        modules: list[Module] | None = None,
    ) -> float | None:
        """Somme des points de l'écrit / total possible, en %."""
        answer_map = {a.question_id: a for a in answers}
        got = total = 0.0
        for module in (modules if modules is not None else subject.modules):
            if self._skip_module(module, answer_map):
                continue
            g, t, pending = self._module_points(module, answer_map)
            if pending:
                continue
            got += g
            total += t
        return round(got / total * 100, 2) if total > 0 else None

    def _compute_scores(
        self,
        subject: Subject,
        answers: list[ExamSessionAnswer],
        provider: str = "TELC",
        modules: list[Module] | None = None,
    ) -> tuple[dict, bool]:
        """Score par module, en %, selon le barème officiel des Teile.

        Même règle pour tous les fournisseurs : le barème vit dans les données
        (teil.max_score, module.max_score), pas dans le code.
        """
        answer_map = {a.question_id: a for a in answers}
        score_breakdown: dict = {}
        has_pending = False

        for module in (modules if modules is not None else subject.modules):
            if self._skip_module(module, answer_map):
                continue
            got, total, pending = self._module_points(module, answer_map)
            if pending:
                score_breakdown[module.slug] = None
                has_pending = True
            elif total <= 0:
                score_breakdown[module.slug] = 0.0
            else:
                score_breakdown[module.slug] = round(got / total * 100, 2)

        return score_breakdown, has_pending

    # ── Construction du résultat ─────────────────────────

    @staticmethod
    def _free_text_instruction(question, teil) -> tuple[str | None, list[str]]:
        """Même logique que AssignmentService._schreiben_parts : consigne et Leitpunkte."""
        if question.question_type != "free_text":
            return None, []
        content = question.content or {}
        instruction = (
            content.get("scenario")
            or content.get("instruction")
            or content.get("topic")
            or teil.instructions
            or ""
        )
        prompts = content.get("prompts") or content.get("leitpunkte") or []
        if not isinstance(prompts, list):
            prompts = []
        return (
            instruction if isinstance(instruction, str) and instruction else None,
            [p for p in prompts if isinstance(p, str)],
        )

    async def _build_result_response(
        self,
        session: ExamSession,
        exam: Exam,
        subject: Subject,
        answers: list[ExamSessionAnswer],
        total_pass_score: int | None,
        include_empty_free_text: bool = False,
    ) -> SessionResultResponse:
        """include_empty_free_text : vue staff, une production écrite laissée vide
        est renvoyée avec une réponse vide pour que l'enseignant puisse la noter."""
        answer_map = {a.question_id: a for a in answers}
        modules_result = []
        provider = exam.provider if exam else "TELC"
        level = await self._get_level(subject.level_id)
        rules = self._pass_rules(level, provider)
        is_tdn = rules["pass_rule"] == "tdn_levels"

        for module in self._scoped_modules(subject, session.module_slugs):
            if self._skip_module(module, answer_map):
                continue  # Sprechen : évalué en session orale

            teil_results = []
            module_points = 0.0
            module_total = 0.0
            module_is_corrected = True
            questions_correct = 0
            questions_incorrect = 0
            questions_total = 0

            for teil in module.teile:
                answer_details = []

                for question in sorted(teil.questions, key=lambda x: x.question_number):
                    questions_total += 1
                    answer = answer_map.get(question.id)
                    if answer:
                        if answer.is_correct is True:
                            questions_correct += 1
                        elif answer.is_correct is False:
                            questions_incorrect += 1

                        instruction, prompts = self._free_text_instruction(question, teil)
                        answer_details.append(AnswerDetailResponse(
                            instruction=instruction,
                            prompts=prompts,
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
                    elif include_empty_free_text and question.question_type == "free_text":
                        instruction, prompts = self._free_text_instruction(question, teil)
                        answer_details.append(AnswerDetailResponse(
                            instruction=instruction,
                            prompts=prompts,
                            question_id=question.id,
                            question_number=question.question_number,
                            question_type=question.question_type,
                            user_answer={},
                            correct_answer=question.correct_answer,
                            is_correct=None,
                            score_obtained=None,
                            points_possible=question.points,
                            feedback=None,
                            corrected_at=None,
                        ))

                t_points, t_total, t_pending = self._teil_points(teil, answer_map)
                if t_pending:
                    module_is_corrected = False

                teil_results.append(TeilResultResponse(
                    teil_number=teil.teil_number,
                    format_type=teil.format_type,
                    max_score=teil.max_score,
                    score_obtained=round(t_points, 2),
                    answers=answer_details,
                ))
                module_points += t_points
                module_total += t_total

            if module_is_corrected and module_total > 0:
                score_on_100 = round(module_points / module_total * 100, 2)
                points_obtained = (
                    round(score_on_100 * module.max_score / 100, 2)
                    if module.max_score else round(module_points, 2)
                )
            elif module_is_corrected:
                score_on_100 = 0.0
                points_obtained = 0.0
            else:
                score_on_100 = None
                points_obtained = None

            modules_result.append(ModuleResultResponse(
                slug=module.slug,
                name=module.name,
                max_score=module.max_score,
                score_obtained=score_on_100,
                points_obtained=points_obtained,
                is_corrected=module_is_corrected,
                questions_correct=questions_correct,
                questions_incorrect=questions_incorrect,
                questions_total=questions_total,
                teile=teil_results,
                tdn_level=self._tdn_level(score_on_100, rules) if is_tdn else None,
            ))

        module_min = rules.get("module_min", 60)

        # Mode module seul : réussite du module
        module_passed = None
        if len(modules_result) == 1 and not is_tdn:
            m = modules_result[0]
            if m.score_obtained is not None:
                module_passed = m.score_obtained >= module_min

        # Messages
        result_message = None
        if len(modules_result) == 1:
            m = modules_result[0]
            if m.score_obtained is not None:
                score_txt = (
                    f"{m.points_obtained:g}/{m.max_score} pts"
                    if m.points_obtained is not None
                    else f"{m.score_obtained:.0f} %"
                )
                if module_passed:
                    result_message = f"Excellent ! Vous avez réussi le module {m.name} avec {score_txt}."
                else:
                    result_message = (
                        f"Vous n'avez pas atteint {module_min:g} % au module {m.name} "
                        f"({score_txt}). Continuez à pratiquer !"
                    )
            elif session.status == "PENDING_REVIEW":
                result_message = f"Module {m.name} en attente de correction IA."
        else:
            if session.passed is True:
                result_message = "Félicitations ! Vous avez réussi cet examen."
            elif session.passed is False:
                weak_modules = [
                    m.name for m in modules_result
                    if m.score_obtained is not None and m.score_obtained < module_min
                ]
                if weak_modules:
                    result_message = f"Score insuffisant. Module(s) à renforcer : {', '.join(weak_modules)}."
                else:
                    result_message = "Vous n'avez pas atteint le score requis. Continuez à vous entraîner !"
            elif session.status == "PENDING_REVIEW":
                result_message = "Résultat partiel, certaines parties sont en attente de correction."

        if is_tdn and session.status == "COMPLETED":
            levels = ", ".join(f"{m.name} : {m.tdn_level}" for m in modules_result if m.tdn_level)
            result_message = f"Niveaux estimés : {levels}. Les seuils officiels varient légèrement selon la session."

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
            module_passed=module_passed,
            total_pass_score=total_pass_score or 0,
            started_at=session.started_at,
            submitted_at=session.submitted_at,
            duration_seconds=session.duration_seconds,
            modules=modules_result,
            result_message=result_message,
            module_slugs=session.module_slugs,
        )