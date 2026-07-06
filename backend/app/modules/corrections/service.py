"""
app/modules/corrections/service.py

Orchestre la correction IA :
1. Charger la session + vérifier ownership
2. Vérifier qu'une correction n'existe pas déjà
3. Extraire les réponses free_text et leur contexte
4. Construire le prompt selon (provider, level)
5. Appeler l'IA
6. Valider le résultat
7. Persister + retourner
"""
from __future__ import annotations
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.modules.corrections.models import Correction
from app.modules.corrections.schemas import (
    CorrectionRequest,
    CorrectionResponse,
    CorrectionPayload,
    TaskPayload,
)
from app.modules.corrections.repository import CorrectionRepository
from app.modules.corrections.ai_providers.gemini import GeminiProvider
from app.modules.corrections.ai_providers.claude import ClaudeProvider
from app.modules.corrections.prompts import (
    build_correction_prompt,
    get_max_score,
    TaskData,
)
from app.modules.exam_sessions.models import ExamSession, ExamSessionAnswer
from app.modules.exams.models import Subject, Level

from app.config import get_settings
from app.modules.questions.models import Question
settings = get_settings()

logger = logging.getLogger(__name__)

# Champs requis dans la réponse IA selon le format
_REQUIRED_FIELDS_SIMPLE   = {"overall_score", "passed", "aufgabe_score"}
_REQUIRED_FIELDS_COMBINED = {"global_assessment", "criteria_scores", "task_feedbacks"}


class CorrectionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CorrectionRepository(db)
        
        # Choisir provider selon config (default: gemini avec fallback claude)
        provider = settings.AI_PROVIDER
        if provider == "claude":
            self.ai = ClaudeProvider()
        else:
            self.ai = GeminiProvider()  # fallback Claude automatique si 503

    # ── Point d'entrée principal ─────────────────────────

    async def correct(
        self,
        request: CorrectionRequest,
        current_user_id: uuid.UUID,
    ) -> CorrectionResponse:
        """
        Lancer ou récupérer la correction d'une session Schreiben.

        Si une correction existe déjà pour cette session, la retourner
        directement sans rappeler l'IA.
        """
        # 1. Vérifier si déjà corrigé
        existing = await self.repo.get_by_session(request.exam_session_id)
        if existing:
            logger.info(f"Correction déjà existante pour session {request.exam_session_id}")
            return _to_response(existing)

        # 2. Charger la session avec toutes ses relations
        session = await self._load_session(request.exam_session_id, current_user_id)

        # 3. Extraire provider + level depuis la hiérarchie
        provider, level = await self._extract_exam_context(session)

        # 4. Extraire les réponses free_text triées par teil_number
        tasks = await self._extract_tasks(session.id, provider, level)

        # 5. Construire le payload
        max_score = get_max_score(provider, level)
        payload = CorrectionPayload(
            session_id=session.id,
            user_id=current_user_id,
            provider=provider,
            level=level,
            max_score=max_score,
            tasks=tasks,
        )

        # 6. Builder le prompt + appeler l'IA
        prompt = build_correction_prompt(
            provider=provider,
            level=level,
            tasks=[
                TaskData(
                    text=t.text,
                    instruction=t.instruction,
                    bullet_points=t.bullet_points,
                    opinion_quote=t.opinion_quote,
                    topic=t.topic,
                    context_ad=t.context_ad,
                )
                for t in tasks
            ],
        )

        logger.info(f"Appel IA pour session {session.id} — {provider.upper()} {level.upper()}")
        ai_result = await self.ai.correct(prompt)

        # 7. Valider la réponse IA
        self._validate_ai_result(ai_result, provider, level)

        # 8. Persister
        correction = await self.repo.create(payload, ai_result)

        # 9. Mettre à jour le score_breakdown de la session
        await self._update_session_score(session, correction)

        return _to_response(correction)

    async def get_by_id(
        self,
        correction_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> CorrectionResponse:
        """Récupérer une correction par ID (vérification ownership)."""
        correction = await self.repo.get_by_id(correction_id)
        if not correction:
            raise ValueError(f"Correction {correction_id} introuvable.")
        if correction.user_id != current_user_id:
            raise PermissionError("Accès refusé.")
        return _to_response(correction)

    async def get_by_session(
        self,
        session_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> CorrectionResponse | None:
        """Récupérer la correction d'une session (None si pas encore corrigée)."""
        correction = await self.repo.get_by_session(session_id)
        if not correction:
            return None
        if correction.user_id != current_user_id:
            raise PermissionError("Accès refusé.")
        return _to_response(correction)

    # ── Helpers privés ───────────────────────────────────

    async def _load_session(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ExamSession:
        """Charger la session avec subject + level + exam."""
        result = await self.db.execute(
            select(ExamSession)
            .where(
                ExamSession.id == session_id,
                ExamSession.user_id == user_id,
            )
            .options(
                selectinload(ExamSession.subject)
                .selectinload(Subject.level)
                .selectinload(Level.exam)
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} introuvable ou accès refusé.")
        return session

    async def _extract_exam_context(self, session: ExamSession) -> tuple[str, str]:
        """
        Extraire (provider, level) depuis la hiérarchie session→subject→level→exam.

        Returns:
            ("telc", "b1"), ("goethe", "b2"), etc.
        """
        level_obj  = session.subject.level
        exam_obj   = level_obj.exam

        provider = exam_obj.provider.lower().strip()
        level    = level_obj.cefr_code.lower().strip()

        return provider, level

    async def _extract_tasks(
        self,
        session_id: uuid.UUID,
        provider: str,
        level: str,
    ) -> list[TaskPayload]:
        result = await self.db.execute(
            select(ExamSessionAnswer)
            .where(ExamSessionAnswer.session_id == session_id)
            .options(
                selectinload(ExamSessionAnswer.question)
                .selectinload(Question.teil)
            )
        )
        all_answers = result.scalars().all()

        free_text_answers = [
            a for a in all_answers
            if a.question.question_type == "free_text"
        ]

        if not free_text_answers:
            raise ValueError(
                f"Aucune réponse free_text trouvée pour la session {session_id}."
            )

        free_text_answers.sort(key=lambda a: a.question.teil.teil_number)

        tasks = []
        for answer in free_text_answers:
            question = answer.question
            teil = question.teil
            content = question.content

            # ✅ La consigne peut venir de plusieurs endroits selon le format :
            # - scenario / instruction : cas général (Goethe, TELC message unique)
            # - teil.instructions : cas "réponse à un e-mail reçu" (stimulus_email),
            #   où la vraie consigne est au niveau du Teil, pas de la question
            instruction = (
                content.get("scenario")
                or content.get("instruction")
                or teil.instructions
                or ""
            )

            task = TaskPayload(
                teil_number=teil.teil_number,
                text=answer.user_answer.get("text", ""),
                instruction=instruction,
                bullet_points=content.get("prompts", []),
                opinion_quote=content.get("opinion_quote", ""),
                topic=content.get("topic", ""),
                context_ad=content.get("context_ad", ""),
            )
            tasks.append(task)

        return tasks

    async def _update_session_score(
        self,
        session: ExamSession,
        correction: Correction,
    ) -> None:
        """
        Mettre à jour le score_breakdown de la session avec le score Schreiben.
        Ne touche pas aux autres modules (Lesen, Hören...).
        """
        breakdown = session.score_breakdown or {}
        breakdown["schreiben"] = correction.overall_score

        session.score_breakdown = breakdown
        await self.db.commit()

    def _validate_ai_result(
        self,
        ai_result: dict,
        provider: str,
        level: str,
    ) -> None:
        """
        Vérifier que la réponse IA contient les champs minimaux attendus.
        Lève ValueError si la réponse est incomplète.
        """
        # Format combiné (Goethe/ÖSD — plusieurs tâches)
        is_combined = provider in ("goethe", "osd") or (
            provider == "telc" and level == "b1" and
            "global_assessment" in ai_result
        )

        required = _REQUIRED_FIELDS_COMBINED if is_combined else _REQUIRED_FIELDS_SIMPLE
        missing  = required - set(ai_result.keys())

        if missing:
            raise ValueError(
                f"Réponse IA incomplète. Champs manquants : {missing}"
            )


# ─────────────────────────────────────────────────────────
# Conversion model → schema
# ─────────────────────────────────────────────────────────

def _to_response(correction: Correction) -> CorrectionResponse:
    return CorrectionResponse(
        id=correction.id,
        session_id=correction.session_id,
        provider=correction.provider,
        level=correction.level,
        overall_score=correction.overall_score,
        max_score=correction.max_score,
        passed=correction.passed,
        score_percentage=correction.score_percentage,
        aufgabe_score=correction.aufgabe_score,
        kohaesion_score=correction.kohaesion_score,
        wortschatz_score=correction.wortschatz_score,
        grammatik_score=correction.grammatik_score,
        criteria_feedbacks=correction.criteria_feedbacks,
        task_feedbacks=correction.task_feedbacks,
        corrections_list=correction.corrections_list,
        suggestions=correction.suggestions,
        appreciation=correction.appreciation,
        ai_provider=correction.ai_provider,
        created_at=correction.created_at,
    )