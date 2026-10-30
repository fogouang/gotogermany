"""
app/modules/start_deutsch/service.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.start_deutsch.access import is_sd_assignment_session, require_sd_subject_access

from app.modules.start_deutsch.models import (
    FormatType,
    SessionStatus,
    StartDeutschQuestion,
    StartDeutschSession,
    StartDeutschSubject,
    StartDeutschTeil,
)
from app.modules.start_deutsch.repository import (
    AnswerRepository,
    QuestionRepository,
    SchreibenCorrectionRepository,
    SessionRepository,
    SubjectRepository,
    TeilRepository,
)
from app.modules.start_deutsch.schemas import (
    StartDeutschAnswerSubmit,
    StartDeutschSchreibenCorrectionRequest,
    StartDeutschSessionSubmitRequest,
    StartDeutschSubjectSummary,
    StartDeutschSubjectUpdate,
)
from app.modules.users.models import User
from app.modules.start_deutsch.prompts.a1_prompt import get_start_deutsch_a1_prompt
from app.modules.start_deutsch.prompts.a2_prompt import get_start_deutsch_a2_prompt
from app.shared.exceptions.http import BadRequestException, ForbiddenException, NotFoundException

# Formats sans correction automatique : free_text passe par la correction IA,
# les formats sprechen_* n'ont pas encore de correction
NON_AUTO_CORRECTABLE_FORMATS = {
    FormatType.FREE_TEXT,
    FormatType.SPRECHEN_GROUP_INTRO,
    FormatType.SPRECHEN_GROUP_WORD_CARD,
    FormatType.SPRECHEN_GROUP_IMAGE_CARD,
    FormatType.SPRECHEN_DUO_QUESTION_CARD,
    FormatType.SPRECHEN_DUO_MONOLOGUE_CARD,
    FormatType.SPRECHEN_DUO_NEGOTIATION,
}


class StartDeutschCatalogService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.subject_repo = SubjectRepository(db)

    async def list_subjects(self, user: User, level: str | None = None) -> list[StartDeutschSubjectSummary]:
        """Catalogue : sans les sujets privés pour l'élève de centre, avec le
        cadenas sur les sujets que l'utilisateur n'a pas encore payés."""
        from app.modules.exam_access.service import ExamAccessService
        from app.modules.exam_access.visibility import can_see_private

        subjects = await self.subject_repo.list_active(level)
        if not can_see_private(user):
            subjects = [s for s in subjects if not s.is_private]

        locked = await ExamAccessService(self.db).locked_sd_subject_ids(user, subjects)
        return [
            StartDeutschSubjectSummary.model_validate(s).model_copy(update={"is_locked": s.id in locked})
            for s in subjects
        ]

    async def get_subject_detail(self, user: User, subject_id: UUID) -> StartDeutschSubject:
        subject = await self.subject_repo.get_full_tree(subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet Start Deutsch introuvable.")
        await require_sd_subject_access(self.db, user, subject)
        return subject

    # ── Admin ────────────────────────────────────────────────────

    async def list_all_admin(self, level: str | None = None) -> list[StartDeutschSubject]:
        """Admin : tous les sujets, actifs ou non."""
        return await self.subject_repo.list_all(level)

    async def update_subject(self, subject_id: UUID, data: StartDeutschSubjectUpdate) -> StartDeutschSubject:
        subject = await self.subject_repo.get_by_id_or_404(subject_id)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(subject, key, value)
        await self.db.commit()
        await self.db.refresh(subject)
        return subject

    async def delete_subject(self, subject_id: UUID) -> None:
        """Supprime le sujet ; la cascade en base retire modules, Teile,
        questions, sessions, réponses et corrections. Refusé si un devoir
        l'utilise."""
        from app.modules.assignments.models import Assignment

        await self.subject_repo.get_by_id_or_404(subject_id)
        used = (
            await self.db.execute(
                select(func.count(Assignment.id)).where(Assignment.sd_subject_id == subject_id)
            )
        ).scalar() or 0
        if used:
            raise BadRequestException(
                detail=f"{used} devoir(s) utilisent ce sujet. Désactive-le plutôt que de le supprimer."
            )
        await self.subject_repo.delete(subject_id)
        await self.db.commit()


class StartDeutschSessionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.teil_repo = TeilRepository(db)
        self.question_repo = QuestionRepository(db)
        self.answer_repo = AnswerRepository(db)
        self.correction_repo = SchreibenCorrectionRepository(db)

    # ── Démarrage ────────────────────────────────────────────────

    async def start_session(self, user: User, subject_id: UUID) -> StartDeutschSession:
        subject = await self.subject_repo.get_by_id_or_404(subject_id)
        if not subject.is_active:
            raise BadRequestException(detail="Ce sujet n'est plus disponible.")
        await require_sd_subject_access(self.db, user, subject)
        return await self.session_repo.create(user_id=user.id, subject_id=subject_id)

    # ── Soumission ───────────────────────────────────────────────

    async def submit_session(
        self, session_id: UUID, user_id: UUID, data: StartDeutschSessionSubmitRequest
    ) -> StartDeutschSession:
        session = await self.session_repo.get_by_id_or_404(session_id)
        if session.user_id != user_id:
            raise BadRequestException(detail="Cette session ne vous appartient pas.")
        if session.status != SessionStatus.IN_PROGRESS:
            raise BadRequestException(detail="Cette session a déjà été soumise.")

        question_ids = [a.question_id for a in data.answers]
        questions = await self.question_repo.get_many_by_ids(question_ids)
        questions_by_id = {q.id: q for q in questions}

        answers_to_save: list[dict] = []
        total_score = 0.0
        total_max_score = 0.0
        has_pending_manual = False

        for answer in data.answers:
            question = questions_by_id.get(answer.question_id)
            if not question:
                raise BadRequestException(detail=f"Question {answer.question_id} introuvable.")

            format_type = question.teil.format_type if question.teil else None
            total_max_score += question.points

            if format_type in NON_AUTO_CORRECTABLE_FORMATS:
                # Reste à 0 en attendant la correction (IA pour le Schreiben)
                has_pending_manual = True
                is_correct, score_obtained = None, 0.0
            else:
                is_correct, score_obtained = self._score_answer(question, answer)
                total_score += score_obtained

            answers_to_save.append(
                {
                    "question_id": answer.question_id,
                    "user_answer": answer.user_answer,
                    "is_correct": is_correct,
                    "score_obtained": score_obtained,
                }
            )

        await self.answer_repo.bulk_upsert(session_id, answers_to_save)

        session.submitted_at = datetime.now(timezone.utc)
        session.score = total_score
        if has_pending_manual:
            session.status = SessionStatus.PENDING_REVIEW
            session.passed = None
        else:
            session.status = SessionStatus.COMPLETED
            # Seuil de 60 %, barème officiel (60 points sur 100)
            session.passed = total_max_score > 0 and (total_score / total_max_score) >= 0.6

        await self.db.commit()
        await self.db.refresh(session)

        # Devoir : la copie passe en « rendu », ou en « corrigé » s'il n'y a pas de Schreiben
        if await is_sd_assignment_session(self.db, session.id):
            from app.modules.assignments.service import AssignmentService

            await AssignmentService(self.db).on_sd_session_submitted(session)
            await self.db.refresh(session)
        return session

    def _score_answer(
        self, question: StartDeutschQuestion, answer: StartDeutschAnswerSubmit
    ) -> tuple[bool, float]:
        """Correction automatique. Réponses au format {"answer": "<valeur>"},
        sauf form_fill qui a un champ par numéro."""
        format_type = question.teil.format_type if question.teil else None
        correct = question.correct_answer or {}

        if format_type == FormatType.FORM_FILL:
            return self._score_form_fill(correct, answer.user_answer, question.points)

        expected = str(correct.get("answer", "")).strip().lower()
        given = str(answer.user_answer.get("answer", "")).strip().lower()
        is_correct = expected != "" and expected == given
        return is_correct, question.points if is_correct else 0.0

    def _score_form_fill(
        self, correct: dict, user_answer: dict, max_points: float
    ) -> tuple[bool, float]:
        """
        correct = {"1": "Berger", "2": "22", ...}
        user_answer = {"1": "berger", "2": "22", ...}
        Score proportionnel aux champs justes, sans tenir compte de la casse
        ni des espaces.
        """
        fields = correct.get("fields", correct)  # accepte les deux formes
        if not fields:
            return False, 0.0

        matched = 0
        for field_number, expected_value in fields.items():
            given_value = str(user_answer.get(field_number, "")).strip().lower()
            if given_value == str(expected_value).strip().lower():
                matched += 1

        ratio = matched / len(fields)
        is_correct = ratio == 1.0
        return is_correct, round(max_points * ratio, 2)

    # ── Résultat ─────────────────────────────────────────────────

    async def get_result(self, session_id: UUID, user_id: UUID) -> dict:
        session = await self.session_repo.get_with_answers(session_id)
        if not session:
            raise NotFoundException(detail="Session introuvable.")
        if session.user_id != user_id:
            raise BadRequestException(detail="Cette session ne vous appartient pas.")
        if await is_sd_assignment_session(self.db, session.id):
            raise ForbiddenException(
                detail="Le résultat de ce devoir se consulte dans votre espace Devoirs."
            )
        return await self.build_result(session)

    async def get_result_for_staff(self, session_id: UUID) -> dict:
        """Résultat complet d'une copie de devoir, pour l'enseignant (sans le Sprechen)."""
        session = await self.session_repo.get_with_answers(session_id, fresh=True)
        if not session:
            raise NotFoundException(detail="Session introuvable.")
        return await self.build_result(session, skip_sprechen=True)

    async def build_result(self, session: StartDeutschSession, skip_sprechen: bool = False) -> dict:
        """Score par module et par Teil. skip_sprechen : devoirs, où l'oral n'est pas évalué."""
        subject = await self.subject_repo.get_full_tree(session.subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet introuvable.")

        answers_by_question = {a.question_id: a for a in session.answers}
        corrections_by_teil = {c.teil_id: c for c in session.schreiben_corrections}

        module_results = []
        total_score = 0.0
        total_max_score = 0.0

        for module in sorted(subject.modules, key=lambda m: m.order):
            if skip_sprechen and module.slug == "sprechen":
                continue
            teil_results = []
            module_score = 0.0
            module_corrected = True

            for teil in sorted(module.teile, key=lambda t: t.teil_number):
                answer_results = []
                teil_score = 0.0
                teil_corrected = True

                for question in sorted(teil.questions, key=lambda q: q.question_number):
                    answer = answers_by_question.get(question.id)

                    if teil.format_type == FormatType.FREE_TEXT:
                        correction = corrections_by_teil.get(teil.id)
                        score_obtained = float(correction.overall_score) if correction else 0.0
                        is_correct = correction.passed if correction else None
                        if not correction:
                            teil_corrected = False
                    elif teil.format_type in NON_AUTO_CORRECTABLE_FORMATS:
                        # Sprechen : pas encore de correction
                        score_obtained = 0.0
                        is_correct = None
                        teil_corrected = False
                    else:
                        score_obtained = float(answer.score_obtained) if answer else 0.0
                        is_correct = answer.is_correct if answer else None
                        if answer is None:
                            teil_corrected = False

                    teil_score += score_obtained
                    answer_results.append(
                        {
                            "question_id": question.id,
                            "question_number": question.question_number,
                            "user_answer": answer.user_answer if answer else {},
                            "correct_answer": question.correct_answer,
                            "is_correct": is_correct,
                            "score_obtained": score_obtained,
                        }
                    )

                module_score += teil_score
                module_corrected = module_corrected and teil_corrected
                teil_results.append(
                    {
                        "teil_id": teil.id,
                        "teil_number": teil.teil_number,
                        "format_type": teil.format_type,
                        "max_score": teil.max_score,
                        "score_obtained": teil_score,
                        "answers": answer_results,
                    }
                )

            total_score += module_score
            total_max_score += module.max_score
            module_results.append(
                {
                    "module_id": module.id,
                    "slug": module.slug,
                    "max_score": module.max_score,
                    "score_obtained": module_score,
                    "is_corrected": module_corrected,
                    "teile": teil_results,
                }
            )

        # Recalculé ici : session.score date de la soumission et ignore les
        # corrections Schreiben arrivées ensuite
        total_pass_score = round(total_max_score * 0.6, 2)
        all_corrected = all(m["is_corrected"] for m in module_results)
        passed = (total_score / total_max_score) >= 0.6 if all_corrected and total_max_score > 0 else None

        return {
            "session_id": session.id,
            "subject_id": subject.id,
            "subject_title": subject.title,
            "level": subject.level,
            "status": session.status if all_corrected else SessionStatus.PENDING_REVIEW,
            "score": total_score,
            "total_pass_score": total_pass_score,
            "passed": passed,
            "started_at": session.started_at,
            "submitted_at": session.submitted_at,
            "modules": module_results,
        }

    async def list_user_sessions(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[dict]:
        """Historique d'entraînement (les devoirs ont leur propre espace).
        Statut et score recalculés comme sur la page de résultat : le Sprechen,
        non noté, ne laisse pas une tentative « en attente » pour toujours."""
        sessions = await self.session_repo.list_by_user(user_id, skip, limit)
        subjects: dict[UUID, StartDeutschSubject] = {}
        out: list[dict] = []

        for s in sessions:
            if await is_sd_assignment_session(self.db, s.id):
                continue
            subject = subjects.get(s.subject_id) or await self.subject_repo.get_by_id(s.subject_id)
            if subject:
                subjects[s.subject_id] = subject

            item = {
                "id": s.id,
                "subject_id": s.subject_id,
                "subject_title": subject.title if subject else "",
                "subject_number": subject.subject_number if subject else 0,
                "level": subject.level if subject else "",
                "status": s.status,
                "score": s.score,
                "score_percent": None,
                "passed": s.passed,
                "started_at": s.started_at,
                "submitted_at": s.submitted_at,
            }

            if s.status != SessionStatus.IN_PROGRESS:
                full = await self.session_repo.get_with_answers(s.id)
                result = await self.build_result(full, skip_sprechen=True)
                total_max = sum(float(m["max_score"]) for m in result["modules"])
                all_corrected = bool(result["modules"]) and all(m["is_corrected"] for m in result["modules"])
                item["score"] = float(result["score"])
                item["status"] = SessionStatus.COMPLETED if all_corrected else SessionStatus.PENDING_REVIEW
                item["passed"] = result["passed"] if all_corrected else None
                if all_corrected and total_max:
                    item["score_percent"] = round(float(result["score"]) * 100 / total_max, 1)
            out.append(item)
        return out


class StartDeutschSchreibenCorrectionService:
    """Correction IA d'une production Schreiben sur la grille officielle A à E
    (Aufgabenerfüllung, Sprache)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.teil_repo = TeilRepository(db)
        self.correction_repo = SchreibenCorrectionRepository(db)

    async def correct(
        self, session_id: UUID, user_id: UUID, data: StartDeutschSchreibenCorrectionRequest
    ):
        session = await self.session_repo.get_by_id_or_404(session_id)
        if session.user_id != user_id:
            raise BadRequestException(detail="Cette session ne vous appartient pas.")
        # Les devoirs sont corrigés par l'enseignant, jamais par l'IA
        if await is_sd_assignment_session(self.db, session.id):
            raise BadRequestException(detail="Ce devoir est corrigé par votre enseignant.")

        teil = await self.teil_repo.get_with_module_and_subject(data.teil_id)
        if not teil:
            raise NotFoundException(detail="Teil introuvable.")
        if teil.format_type != FormatType.FREE_TEXT:
            raise BadRequestException(detail="Ce Teil n'attend pas de correction Schreiben.")

        criteria_scores = await self._call_ai_correction(teil, data.submitted_text)

        overall_score = sum(c["points"] for c in criteria_scores.values())
        max_score = float(teil.max_score)

        correction = await self.correction_repo.create(
            session_id=session_id,
            teil_id=data.teil_id,
            submitted_text=data.submitted_text,
            criteria_scores=criteria_scores,
            overall_score=overall_score,
            max_score=max_score,
        )
        await self.db.commit()
        await self.db.refresh(correction)
        return correction

    async def _call_ai_correction(self, teil: StartDeutschTeil, text: str) -> dict:
        """Claude ou Gemini selon AI_PROVIDER, avec un prompt et une lecture
        propres au barème A1 et A2 (indépendant du module corrections)."""
        from app.config import get_settings
        from app.modules.corrections.ai_providers.claude import ClaudeProvider
        from app.modules.corrections.ai_providers.gemini import GeminiProvider

        settings = get_settings()
        content = teil.questions[0].content if teil.questions else {}
        instruction = content.get("prompt") or teil.instructions or ""
        content_points = content.get("content_points", [])

        subject_level = teil.module.subject.level if teil.module and teil.module.subject else None

        if subject_level == "A1":
            prompt = get_start_deutsch_a1_prompt(
                text=text, task_instruction=instruction, content_points=content_points
            )
        elif subject_level == "A2":
            task_type = "sms" if teil.teil_number == 1 else "email"
            prompt = get_start_deutsch_a2_prompt(
                text=text, task_instruction=instruction, content_points=content_points, task_type=task_type
            )
        else:
            raise BadRequestException(detail=f"Niveau non supporté pour la correction Schreiben : {subject_level}")

        provider = ClaudeProvider() if settings.AI_PROVIDER == "claude" else GeminiProvider()
        ai_result = await provider.correct(prompt)

        if subject_level == "A1":
            return self._build_a1_criteria_scores(ai_result, content_points)
        return self._build_a2_criteria_scores(ai_result, teil.max_score)

    def _build_a1_criteria_scores(self, ai_result: dict, content_points: list[str]) -> dict:
        scores = ai_result.get("content_point_scores", [])
        feedback = ai_result.get("content_point_feedback", [])
        if len(scores) != len(content_points):
            raise BadRequestException(detail="Réponse IA incohérente : nombre de points de contenu inattendu.")

        content_total = sum(float(s) for s in scores)
        communicative_score = float(ai_result.get("communicative_score", 0))

        return {
            "aufgabenerfuellung": {
                "grade": self._points_to_grade(content_total, len(content_points) * 3),
                "points": content_total,
                "label": "Erfüllung der Aufgabenstellung",
                "feedback": " · ".join(feedback) if feedback else None,
            },
            "kommunikative_gestaltung": {
                "grade": self._points_to_grade(communicative_score, 1),
                "points": communicative_score,
                "label": "Kommunikative Gestaltung",
                "feedback": ai_result.get("communicative_feedback"),
            },
        }

    def _build_a2_criteria_scores(self, ai_result: dict, teil_max_score: int) -> dict:
        # Deux critères de même poids : chacun vaut la moitié du Teil
        axis_max = teil_max_score / 2
        grade_to_ratio = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "E": 0.0}

        aufgabenerfuellung_grade = ai_result.get("aufgabenerfuellung_grade", "E")
        sprache_grade = ai_result.get("sprache_grade", "E")

        # Règle officielle : E en Aufgabenerfüllung met toute la tâche à 0
        if aufgabenerfuellung_grade == "E":
            sprache_grade = "E"

        return {
            "aufgabenerfuellung": {
                "grade": aufgabenerfuellung_grade,
                "points": round(grade_to_ratio.get(aufgabenerfuellung_grade, 0) * axis_max, 2),
                "label": "Aufgabenerfüllung",
                "feedback": ai_result.get("aufgabenerfuellung_feedback"),
            },
            "sprache": {
                "grade": sprache_grade,
                "points": round(grade_to_ratio.get(sprache_grade, 0) * axis_max, 2),
                "label": "Sprache",
                "feedback": ai_result.get("sprache_feedback"),
            },
        }

    @staticmethod
    def _points_to_grade(points: float, max_points: float) -> str:
        """Note A1 convertie en lettre A à E, pour un affichage comme en A2."""
        if max_points <= 0:
            return "E"
        ratio = points / max_points
        if ratio >= 0.9:
            return "A"
        if ratio >= 0.7:
            return "B"
        if ratio >= 0.5:
            return "C"
        if ratio >= 0.25:
            return "D"
        return "E"