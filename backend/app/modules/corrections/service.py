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
from app.modules.corrections.response_normalizer import CRITERIA_CONFIG
from app.modules.exam_sessions.models import ExamSession, ExamSessionAnswer
from app.modules.exams.models import Subject, Level

from app.config import get_settings
from app.modules.questions.models import Question

settings = get_settings()
logger = logging.getLogger(__name__)

# Champs minimaux attendus par shape de sortie IA (cf. response_normalizer.py :
# "nested" = Goethe B2 / Goethe-ÖSD B1, "flat" = telc B1/B2, "osd_b2" = ÖSD B2).
_REQUIRED_FIELDS_BY_SHAPE = {
    "nested": {"global_assessment", "criteria_scores", "task_feedbacks"},
    "flat": {"overall_score", "passed"},
    "osd_b2": {"global_assessment", "task1", "task2"},
    "ecl": {"global_assessment", "task1", "task2"},
    "testdaf": {"global_assessment", "task1", "task2"},
}

def _stimulus_text(raw) -> str:
    """Message de forum / annonce : str ou {title, text, author}."""
    if not raw:
        return ""
    if isinstance(raw, dict):
        body = "\n".join(p for p in (raw.get("title", ""), raw.get("text", "")) if p)
        author = raw.get("author")
        return f"{author}: {body}" if author else body
    return str(raw)


def _build_task_fields(content: dict, user_answer: dict, teil) -> dict:
    """Contexte complet d'une tâche Schreiben, quel que soit le format du sujet.

    - TELC/ÖSD B2 « themen » : on prend le sujet choisi (user_answer.theme) ;
      sinon (anciennes réponses) on donne les deux et l'IA identifie celui traité.
    - ÖSD variantes d'opinion : variante choisie (user_answer.variant).
    - Goethe forum : le message à commenter (stimulus) -> opinion_quote.
    - TELC e-mail reçu (stimulus_email) : ajouté à la consigne.
    - ÖSD réclamation (info_comparison) : promesses / problèmes -> context_ad.
    """
    instruction = content.get("scenario") or content.get("instruction") or teil.instructions or ""
    bullet_points = list(content.get("prompts") or [])
    topic = content.get("topic", "") or ""
    opinion_quote = content.get("opinion_quote", "") or _stimulus_text(content.get("stimulus"))
    context_parts = [
        content.get("context_ad", ""),
        content.get("source_text", ""),
        content.get("graph_description", ""),
    ]

    # E-mail reçu (TELC)
    email = content.get("stimulus_email") or {}
    if email.get("body"):
        header = f"E-Mail von {email.get('sender', '')}".strip()
        if email.get("subject"):
            header += f" (Betreff: {email['subject']})"
        instruction = f"{instruction}\n\n{header}:\n{email['body']}".strip()

    # Réclamation (ÖSD)
    info = content.get("info_comparison")
    if info:
        lines = [f"Anbieter: {info.get('anbieter', '')}", f"Situation: {info.get('situation', '')}"]
        if info.get("versprechen"):
            lines.append("Versprochen: " + "; ".join(info["versprechen"]))
        if info.get("probleme"):
            lines.append("Probleme: " + "; ".join(info["probleme"]))
        if info.get("kontakt"):
            lines.append(f"Kontakt: {info['kontakt']}")
        context_parts.append("\n".join(lines))

    # Choix entre deux sujets (TELC / ÖSD B2 : themen)
    themes = content.get("themes") or {}
    if themes:
        chosen = themes.get(str(user_answer.get("theme") or ""))
        if chosen:
            topic = chosen.get("titel", "") or topic
            bullet_points = list(chosen.get("prompts") or [])
            context_parts.append(_stimulus_text(chosen.get("stimulus")))
        else:
            blocks = [
                f"Thema {key}: {th.get('titel', '')}\n{_stimulus_text(th.get('stimulus'))}\n"
                f"Leitpunkte: {'; '.join(th.get('prompts') or [])}"
                for key, th in themes.items()
            ]
            context_parts.append(
                "Der Kandidat hat eines der folgenden Themen gewählt. "
                "Erkenne am Text, welches, und bewerte nur danach:\n\n" + "\n\n".join(blocks)
            )

    # Choix entre deux variantes d'opinion (ÖSD)
    variants = content.get("opinion_variants") or {}
    if variants:
        chosen = variants.get(str(user_answer.get("variant") or ""))
        selected = [chosen] if chosen else list(variants.values())
        topic = " / ".join(v.get("thema", "") for v in selected if v.get("thema")) or topic
        opinion_quote = "\n".join(f"- {a}" for v in selected for a in (v.get("aussagen") or []))
        bullet_points = list(content.get("leitpunkte") or bullet_points)

    return {
        "instruction": instruction,
        "bullet_points": bullet_points,
        "topic": topic,
        "opinion_quote": opinion_quote,
        "context_ad": "\n\n".join(p for p in context_parts if p),
    }
    
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
        
        # Les devoirs sont corrigés par l'enseignant, jamais par l'IA
        if session.subject.is_private:
            raise ValueError("Ce devoir est corrigé par votre enseignant.")
        
        # 3. Extraire provider + level depuis la hiérarchie
        provider, level = await self._extract_exam_context(session)
        
        if (provider, level) not in CRITERIA_CONFIG:
            raise ValueError(
                f"La correction IA n'est pas encore disponible pour {provider.upper()} {level.upper()}."
            )
            
        # 4. Extraire les réponses free_text triées par teil_number
        tasks = await self._extract_tasks(session.id, provider, level)

        # 5. Construire le payload
        # NB: max_score ici sert surtout de trace/contexte sur le payload ;
        # le max_score réellement persisté vient de response_normalizer
        # (repository.create), calculé depuis CRITERIA_CONFIG — les deux
        # doivent rester synchronisés (MAX_SCORES dans prompts/__init__.py).
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
        level_obj = session.subject.level
        exam_obj = level_obj.exam

        provider = exam_obj.provider.lower().strip().replace("ö", "o")
        level = level_obj.cefr_code.lower().strip()

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
            user_answer = answer.user_answer or {}
            fields = _build_task_fields(question.content or {}, user_answer, question.teil)
            tasks.append(
                TaskPayload(
                    teil_number=question.teil.teil_number,
                    text=user_answer.get("text", ""),
                    **fields,
                )
            )

        return tasks

    async def _update_session_score(
        self,
        session: ExamSession,
        correction: Correction,
    ) -> None:
        """Reporte la note IA sur les réponses free_text puis recalcule la session.

        Chaque réponse reçoit (note / max) x ses points : la notation par Teil
        de ExamSessionService la ramène ensuite au barème officiel du module.
        La session sort ainsi de PENDING_REVIEW et son score global compte le Schreiben.
        """
        ratio = (correction.overall_score / correction.max_score) if correction.max_score else 0.0

        result = await self.db.execute(
            select(ExamSessionAnswer)
            .where(ExamSessionAnswer.session_id == session.id)
            .options(selectinload(ExamSessionAnswer.question))
        )
        for answer in result.scalars().all():
            if answer.question.question_type == "free_text":
                answer.score_obtained = round(ratio * float(answer.question.points or 0), 2)
        await self.db.flush()

        # Import local : évite un import circulaire entre corrections et exam_sessions
        from app.modules.exam_sessions.service import ExamSessionService

        await ExamSessionService(self.db).rescore_session(session.id)

    def _validate_ai_result(
        self,
        ai_result: dict,
        provider: str,
        level: str,
    ) -> None:
        """
        Vérifier que la réponse IA contient les champs minimaux attendus,
        selon le "shape" réel du prompt utilisé pour cet examen (et non plus
        une heuristique par provider, qui ne couvrait pas ÖSD B2 correctement —
        ce prompt n'a pas de criteria_scores/task_feedbacks, mais task1/task2
        directement).
        """
        config = CRITERIA_CONFIG.get((provider.lower(), level.lower()))
        if config is None:
            raise ValueError(f"Barème inconnu pour {provider} {level}.")

        shape = config["shape"]
        required = _REQUIRED_FIELDS_BY_SHAPE.get(shape)
        if required is None:
            raise ValueError(f"Shape inconnu: {shape}")

        missing = required - set(ai_result.keys())
        if missing:
            raise ValueError(
                f"Réponse IA incomplète pour {provider.upper()} {level.upper()} "
                f"(format '{shape}'). Champs manquants : {missing}"
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
        appreciation=correction.appreciation,
        floor_reached=correction.floor_reached,
        criteria=correction.criteria,
        tasks=correction.tasks,
        corrections_list=correction.corrections_list,
        suggestions=correction.suggestions,
        ai_provider=correction.ai_provider,
        created_at=correction.created_at,
    )