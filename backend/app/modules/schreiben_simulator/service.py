"""
app/modules/schreiben_simulator/service.py

Logique du simulateur :
- Pas de ExamSession — correction directe depuis sujet + textes
- Réutilise exactement les mêmes prompts et provider que le module corrections
"""
from __future__ import annotations
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.schreiben_simulator.models import SchreibenSubject
from app.modules.schreiben_simulator.schemas import (
    SchreibenSubjectCreate,
    SchreibenSubjectUpdate,
    SchreibenSubjectResponse,
    SimulatorCorrectRequest,
    SimulatorCorrectResponse,
)
from app.modules.schreiben_simulator.repository import SchreibenSubjectRepository
from app.modules.corrections.ai_providers.gemini import GeminiProvider
from app.modules.corrections.prompts import build_correction_prompt, get_max_score, TaskData

logger = logging.getLogger(__name__)


class SchreibenSimulatorService:

    def __init__(self, db: AsyncSession):
        self.db   = db
        self.repo = SchreibenSubjectRepository(db)
        self._ai  = None

    @property
    def ai(self) -> GeminiProvider:
        if self._ai is None:
            self._ai = GeminiProvider()
        return self._ai
    
    # ── Lecture ──────────────────────────────────────────

    async def list_subjects(
        self,
        provider: str | None = None,
        level: str | None = None,
        active_only: bool = True,
    ) -> list[SchreibenSubjectResponse]:
        subjects = await self.repo.get_all(provider, level, active_only)
        return [SchreibenSubjectResponse.model_validate(s) for s in subjects]

    async def get_subject(self, subject_id: uuid.UUID) -> SchreibenSubjectResponse:
        subject = await self.repo.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Sujet {subject_id} introuvable.")
        return SchreibenSubjectResponse.model_validate(subject)

    # ── Admin CRUD ───────────────────────────────────────

    async def create_subject(self, data: SchreibenSubjectCreate) -> SchreibenSubjectResponse:
        self._validate_task_count(data.provider, data.level, len(data.tasks))
        subject = await self.repo.create(data)
        return SchreibenSubjectResponse.model_validate(subject)

    async def update_subject(
        self,
        subject_id: uuid.UUID,
        data: SchreibenSubjectUpdate,
    ) -> SchreibenSubjectResponse:
        if data.tasks is not None:
            subject = await self.repo.get_by_id(subject_id)
            if subject:
                self._validate_task_count(subject.provider, subject.level, len(data.tasks))

        updated = await self.repo.update(subject_id, data)
        if not updated:
            raise ValueError(f"Sujet {subject_id} introuvable.")
        return SchreibenSubjectResponse.model_validate(updated)

    async def delete_subject(self, subject_id: uuid.UUID) -> None:
        deleted = await self.repo.delete(subject_id)
        if not deleted:
            raise ValueError(f"Sujet {subject_id} introuvable.")

    # ── Correction simulateur ────────────────────────────

    async def correct(
        self,
        request: SimulatorCorrectRequest,
        user_id: uuid.UUID,
    ) -> SimulatorCorrectResponse:
        """
        Lancer la correction IA depuis un sujet simulateur.
        Pas de session — les textes sont envoyés directement.
        """
        # ── Vérifier et déduire le crédit ───────────────────
        from app.modules.users.models import User
        from app.shared.exceptions.http import ForbiddenException

        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError("Utilisateur introuvable.")

        if user.ai_credits <= 0:
            raise ForbiddenException(
                detail="Vous n'avez plus de crédits IA. Achetez des crédits pour continuer."
            )

        # Déduire 1 crédit avant l'appel IA
        user.ai_credits -= 1
        await self.db.flush()

        # ── Correction ────────────────────────────────────────
        subject = await self.repo.get_by_id(request.subject_id)
        if not subject:
            await self.db.rollback()
            raise ValueError(f"Sujet {request.subject_id} introuvable.")
        if not subject.is_active:
            await self.db.rollback()
            raise ValueError("Ce sujet n'est plus disponible.")

        self._validate_task_count(subject.provider, subject.level, len(request.task_texts))
        tasks  = self._build_tasks(subject, request.task_texts)
        prompt = build_correction_prompt(
            provider=subject.provider,
            level=subject.level,
            tasks=tasks,
        )

        logger.info(f"Simulateur — correction {subject.provider.upper()} {subject.level.upper()}: {subject.title}")

        try:
            ai_result = await self.ai.correct(prompt)
        except Exception as e:
            # ── Rembourser le crédit si l'IA échoue ─────────
            user.ai_credits += 1
            await self.db.flush()
            logger.error(f"Erreur IA — crédit remboursé pour user {user_id}: {e}")
            raise e

        response = self._build_response(subject, ai_result)

        # ── Persister le résultat ────────────────────────────
        await self.repo.save_result(user_id, response)
        await self.db.commit()

        return response

     
    async def list_my_results(self, user_id: uuid.UUID):
        return await self.repo.get_results_by_user(user_id)

    # ── Helpers privés ───────────────────────────────────

    def _build_tasks(
        self,
        subject: SchreibenSubject,
        task_texts: list[str],
    ) -> list[TaskData]:
        """Assembler TaskData depuis subject.tasks + textes du candidat."""
        tasks = []
        for i, task_def in enumerate(subject.tasks):
            text = task_texts[i] if i < len(task_texts) else ""
            tasks.append(TaskData(
                text=text,
                instruction=task_def.get("scenario", ""),
                bullet_points=task_def.get("prompts", []),
                topic=task_def.get("topic", ""),
                context_ad=task_def.get("context_ad", ""),
                opinion_quote=task_def.get("opinion_quote", ""),
            ))
        return tasks

    def _build_response(
        self,
        subject: SchreibenSubject,
        ai_result: dict,
    ) -> SimulatorCorrectResponse:
        """Construire la réponse depuis le résultat IA."""
        max_score = get_max_score(subject.provider, subject.level)

        # Extraire scores — même logique que corrections/repository.py
        if "global_assessment" in ai_result:
            overall = ai_result["global_assessment"].get("overall_score", 0)
            passed  = ai_result["global_assessment"].get("passed", False)
            scores  = ai_result.get("criteria_scores", {})
            feedbacks = {
                "aufgabe_feedback":   scores.get("aufgabe_feedback", ""),
                "kohaesion_feedback": scores.get("kohaesion_feedback", ""),
                "wortschatz_feedback": scores.get("wortschatz_feedback", ""),
                "grammatik_feedback": scores.get("grammatik_feedback", ""),
            }
            task_feedbacks = ai_result.get("task_feedbacks", {})
            appreciation   = ai_result["global_assessment"].get("appreciation", "")
        else:
            overall = ai_result.get("overall_score", 0)
            passed  = ai_result.get("passed", False)
            scores  = ai_result
            feedbacks = {
                "aufgabe_feedback":    ai_result.get("aufgabe_feedback", ""),
                "kohaesion_feedback":  ai_result.get("kohaesion_feedback", ""),
                "wortschatz_feedback": ai_result.get("wortschatz_feedback", ""),
                "grammatik_feedback":  ai_result.get("grammatik_feedback", ""),
            }
            task_feedbacks = {
                "task1": {
                    "corrected_text": ai_result.get("corrected_text", ""),
                    "main_strengths": [],
                    "main_weaknesses": [],
                }
            }
            appreciation = ai_result.get("appreciation", "")

        return SimulatorCorrectResponse(
            subject_id=subject.id,
            provider=subject.provider,
            level=subject.level,
            overall_score=overall,
            max_score=max_score,
            passed=passed,
            score_percentage=round(overall / max_score * 100, 1) if max_score else 0,
            aufgabe_score=scores.get("aufgabe_score", 0),
            kohaesion_score=scores.get("kohaesion_score", 0),
            wortschatz_score=scores.get("wortschatz_score", 0),
            grammatik_score=scores.get("grammatik_score", 0),
            criteria_feedbacks=feedbacks,
            task_feedbacks=task_feedbacks,
            corrections_list=ai_result.get("corrections", []),
            suggestions=ai_result.get("suggestions", []),
            appreciation=appreciation,
        )

    @staticmethod
    def _validate_task_count(provider: str, level: str, count: int) -> None:
        """Vérifier la cohérence nombre de tâches ↔ examen."""
        expected = {
            ("telc",   "b1"): 1, ("telc",   "b2"): 1,
            ("goethe", "b1"): 3, ("goethe", "b2"): 2,
            ("osd",    "b1"): 3, ("osd",    "b2"): 2,
        }.get((provider.lower(), level.lower()))

        if expected and count != expected:
            raise ValueError(
                f"{provider.upper()} {level.upper()} attend {expected} tâche(s), "
                f"{count} fournie(s)."
            )