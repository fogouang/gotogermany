"""
app/modules/start_deutsch/service.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

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
)
from app.modules.start_deutsch.prompts.a1_prompt import get_start_deutsch_a1_prompt
from app.modules.start_deutsch.prompts.a2_prompt import get_start_deutsch_a2_prompt
from app.shared.exceptions.http import BadRequestException, NotFoundException

# Formats qui ne peuvent jamais être corrigés automatiquement — nécessitent
# soit la grille Schreiben IA (free_text), soit une future logique Sprechen
# (agent IA ou live_session, pas encore branchés en V1 de ce module)
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

    async def list_subjects(self, level: str | None = None) -> list[StartDeutschSubject]:
        return await self.subject_repo.list_active(level)

    async def get_subject_detail(self, subject_id: UUID) -> StartDeutschSubject:
        subject = await self.subject_repo.get_full_tree(subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet Start Deutsch introuvable.")
        return subject

    # ── Admin ────────────────────────────────────────────────────

    async def list_all_admin(self, level: str | None = None) -> list[StartDeutschSubject]:
        """Vue admin — tous les sujets, actifs ou non (contrairement à
        list_subjects qui filtre is_active pour la vue étudiant)."""
        return await self.subject_repo.list_all(level)

    async def delete_subject(self, subject_id: UUID) -> None:
        """
        Supprime un sujet et tout ce qui en dépend (modules/teile/questions,
        sessions/réponses/corrections liées) — cascade déjà posée au niveau
        DB (ondelete="CASCADE" sur toutes les FK descendantes), donc un
        simple DELETE sur le Subject suffit.
        """
        subject = await self.subject_repo.get_by_id_or_404(subject_id)
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

    async def start_session(self, user_id: UUID, subject_id: UUID) -> StartDeutschSession:
        subject = await self.subject_repo.get_by_id_or_404(subject_id)
        if not subject.is_active:
            raise BadRequestException(detail="Ce sujet n'est plus disponible.")
        return await self.session_repo.create(user_id=user_id, subject_id=subject_id)

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
                # Pas de scoring auto — reste à 0 en attendant la correction
                # IA (Schreiben) ou une future logique Sprechen dédiée
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
            # Seuil 60% — cf. barème officiel A2 (100 pts, 60 pts minimum) ;
            # à ajuster si le seuil A1 diverge une fois son barème global confirmé
            session.passed = total_max_score > 0 and (total_score / total_max_score) >= 0.6

        await self.db.commit()
        await self.db.refresh(session)
        return session

    def _score_answer(
        self, question: StartDeutschQuestion, answer: StartDeutschAnswerSubmit
    ) -> tuple[bool, float]:
        """
        Scoring pour les format_type auto-correctables. Le format de
        correct_answer/user_answer est volontairement homogène sur ces
        types : {"answer": "<valeur>"}, sauf form_fill qui a un champ par
        numéro.
        """
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
        Score proportionnel au nombre de champs corrects (comparaison
        insensible à la casse/espaces — pas de tolérance orthographique
        fine ici, à affiner si besoin plus tard).
        """
        fields = correct.get("fields", correct)  # tolère les deux formes
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

        subject = await self.subject_repo.get_full_tree(session.subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet introuvable.")

        answers_by_question = {a.question_id: a for a in session.answers}
        corrections_by_teil = {c.teil_id: c for c in session.schreiben_corrections}

        module_results = []
        total_score = 0.0
        total_max_score = 0.0

        for module in subject.modules:
            teil_results = []
            module_score = 0.0
            module_corrected = True

            for teil in module.teile:
                answer_results = []
                teil_score = 0.0
                teil_corrected = True

                for question in teil.questions:
                    answer = answers_by_question.get(question.id)

                    if teil.format_type == FormatType.FREE_TEXT:
                        correction = corrections_by_teil.get(teil.id)
                        score_obtained = float(correction.overall_score) if correction else 0.0
                        is_correct = correction.passed if correction else None
                        if not correction:
                            teil_corrected = False
                    elif teil.format_type in NON_AUTO_CORRECTABLE_FORMATS:
                        # Sprechen — pas encore de mécanisme de correction (V1)
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

        # Score recalculé à la volée plutôt que de faire confiance à
        # session.score (figé au moment du submit, donc obsolète dès qu'une
        # correction Schreiben arrive après coup)
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

    async def list_user_sessions(self, user_id: UUID, skip: int = 0, limit: int = 20):
        return await self.session_repo.list_by_user(user_id, skip, limit)


class StartDeutschSchreibenCorrectionService:
    """
    Correction IA d'une production Schreiben, sur la grille officielle A-E
    (Aufgabenerfüllung + Sprache). Réutilise le même principe que la
    correction Schreiben B1/B2 existante (Claude en primaire, Gemini en
    fallback) — le point d'intégration exact dépend de comment ce service
    est exposé chez vous (à brancher).
    """

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

        teil = await self.teil_repo.get_with_module_and_subject(data.teil_id)
        if not teil:
            raise NotFoundException(detail="Teil introuvable.")
        if teil.format_type != FormatType.FREE_TEXT:
            raise BadRequestException(detail="Ce Teil n'attend pas de correction Schreiben.")

        # TODO: appeler le service de correction IA existant (Claude
        # primaire / Gemini fallback) avec le barème A-E officiel A1/A2
        # (Aufgabenerfüllung + Sprache) plutôt que le barème B1/B2 actuel.
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
        """
        Appelle Claude (primaire) avec fallback Gemini — même provider
        infra que le module corrections existant, mais prompt et parsing
        dédiés au barème A1/A2 (pas de dépendance vers CorrectionService,
        volontairement, cf. décision de ne pas coupler start_deutsch aux
        autres modules).
        """
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
        # Deux axes à poids égal — chacun vaut la moitié du max_score du Teil
        axis_max = teil_max_score / 2
        grade_to_ratio = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "E": 0.0}

        aufgabenerfuellung_grade = ai_result.get("aufgabenerfuellung_grade", "E")
        sprache_grade = ai_result.get("sprache_grade", "E")

        # Règle officielle : E sur Aufgabenerfüllung → toute l'épreuve à 0
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
        """Convertit un score numérique A1 en équivalent A-E, pour un affichage cohérent avec le A2."""
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