"""
app/modules/schreiben_simulator/service.py

Logique du simulateur :
- Pas de ExamSession — correction directe depuis sujet + textes
- Réutilise exactement les mêmes prompts et provider que le module corrections
- Réutilise aussi la même extraction du contexte de tâche (_build_task_fields) :
  e-mail reçu, forum, annonce, promesses/problèmes, thèmes, variantes,
  texte source/graphique arrivent à l'IA comme pour une session d'examen.
- Sujets à tâches au choix (telc B2 : Aufgabe A ou B) : seule la tâche rédigée
  par l'élève est corrigée (_select_tasks), et le résultat affiche le vrai
  Teil traité (ex. "Teil 2").
"""
from __future__ import annotations
from types import SimpleNamespace
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
from app.modules.corrections.ai_providers.claude import ClaudeProvider
from app.modules.corrections.prompts import build_correction_prompt, TaskData, EXPECTED_TASK_COUNT
from app.modules.corrections.response_normalizer import normalize_correction_result, rebuild_corrected_text
from app.modules.corrections.service import _build_task_fields
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Le simulateur n'a pas d'objet Teil : consigne de repli vide pour _build_task_fields
_NO_TEIL = SimpleNamespace(instructions="")


def _exam_key(provider: str, level: str) -> tuple[str, str]:
    return (provider.lower().strip().replace("ö", "o"), level.lower().strip())


class SchreibenSimulatorService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SchreibenSubjectRepository(db)

        provider = settings.AI_PROVIDER
        if provider == "claude":
            self._ai = ClaudeProvider()
        else:
            self._ai = GeminiProvider()

    @property
    def ai(self):
        return self._ai

    # ── Lecture ──────────────────────────────────────────

    async def list_subjects(
        self,
        provider: str | None = None,
        level: str | None = None,
        active_only: bool = True,
    ) -> list[SchreibenSubjectResponse]:
        subjects = await self.repo.get_all(provider, level, active_only)
        legacy = [SchreibenSubjectResponse.model_validate(s) for s in subjects]

        unified_dicts = await self.repo.get_all_unified(provider, level)
        unified = [SchreibenSubjectResponse.model_validate(d) for d in unified_dicts]

        return legacy + unified

    async def get_subject(self, subject_id: uuid.UUID) -> SchreibenSubjectResponse:
        subject = await self.repo.get_by_id(subject_id)
        if subject:
            return SchreibenSubjectResponse.model_validate(subject)

        unified = await self.repo.get_by_id_unified(subject_id)
        if unified:
            return SchreibenSubjectResponse.model_validate(unified)

        raise ValueError(f"Sujet {subject_id} introuvable.")

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
        Correction IA depuis un sujet simulateur (sans session).
        Tout est validé AVANT de débiter le crédit.
        """
        from app.modules.users.models import User
        from app.shared.exceptions.http import ForbiddenException

        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError("Utilisateur introuvable.")

        # ── Sujet ────────────────────────────────────────────
        subject = await self.repo.get_by_id(request.subject_id)
        if subject is None:
            unified = await self.repo.get_by_id_unified(request.subject_id)
            if unified is None:
                raise ValueError(f"Sujet {request.subject_id} introuvable.")
            subject = SimpleNamespace(
                id=unified["id"],
                provider=unified["provider"],
                level=unified["level"],
                tasks=unified["tasks"],
                is_active=unified["is_active"],
                title=unified["title"],
            )
        if not subject.is_active:
            raise ValueError("Ce sujet n'est plus disponible.")

        # ── Tâches à corriger (tâche au choix : seule celle rédigée) ──
        task_defs, task_texts, task_choices, chosen_index = self._select_tasks(subject, request)

        # ── Validation + prompt (lève ValueError si texte vide, etc.) ──
        self._validate_task_count(subject.provider, subject.level, len(task_texts))
        tasks = self._build_tasks(task_defs, task_texts, task_choices)
        prompt = build_correction_prompt(
            provider=subject.provider,
            level=subject.level,
            tasks=tasks,
        )

        # ── Crédit : vérifié et débité seulement maintenant ──
        if user.ai_credits <= 0:
            raise ForbiddenException(
                detail="Vous n'avez plus de crédits IA. Achetez des crédits pour continuer."
            )
        user.ai_credits -= 1
        await self.db.flush()

        logger.info(f"Simulateur : correction {subject.provider.upper()} {subject.level.upper()} : {subject.title}")

        try:
            ai_result = await self.ai.correct(prompt)
        except Exception as e:
            user.ai_credits += 1
            await self.db.flush()
            logger.error(f"Erreur IA, crédit remboursé pour user {user_id}: {e}")
            raise e

        response = self._build_response(subject, ai_result, task_texts)

        # Tâche au choix : afficher le vrai Teil traité (ex. "Teil 2"), pas le Teil renuméroté
        if chosen_index is not None and response.tasks:
            response.tasks[0].label = f"Teil {chosen_index + 1}"

        # Texte corrigé reconstruit depuis le texte de l'élève + corrections, et
        # liste réduite aux corrections réellement appliquées : liste et texte identiques
        kept: list[dict] = []
        for i, task in enumerate(response.tasks):
            task_no = str(i + 1)
            task_corrections = [
                c for c in response.corrections_list
                if str(c.get("task", "1") or "1") == task_no
            ]
            original = task_texts[i] if i < len(task_texts) else ""
            rebuilt, applied = rebuild_corrected_text(original, task_corrections, i + 1)
            if rebuilt:
                task.corrected_text = rebuilt
                kept.extend(applied)
            else:
                kept.extend(task_corrections)
        response.corrections_list = kept

        await self.repo.save_result(user_id, response)
        await self.db.commit()
        return response
    
    async def list_my_results(self, user_id: uuid.UUID):
        return await self.repo.get_results_by_user(user_id)

    # ── Helpers privés ───────────────────────────────────

    @staticmethod
    def _select_tasks(
        subject,
        request: SimulatorCorrectRequest,
    ) -> tuple[list[dict], list[str], list[dict[str, str]], int | None]:
        """
        Tâches réellement à corriger.

        Si l'examen n'attend qu'une tâche mais que le sujet en propose plusieurs
        (telc B2 : Aufgabe A ou B au choix), on garde la seule tâche rédigée par
        l'élève, avec ses propres consignes, et on renvoie son index (pour
        afficher le vrai Teil dans le résultat). Sinon, tout est gardé tel quel
        et l'index vaut None.
        """
        task_defs = list(subject.tasks or [])
        texts = list(request.task_texts)
        choices = list(request.task_choices or [])

        expected = EXPECTED_TASK_COUNT.get(_exam_key(subject.provider, subject.level))
        if expected == 1 and len(task_defs) > 1:
            written = [i for i, t in enumerate(texts) if (t or "").strip()]
            if len(written) != 1:
                raise ValueError(
                    "Pour ce sujet, rédigez une seule des tâches proposées (au choix)."
                )
            i = written[0]
            return (
                [task_defs[i]] if i < len(task_defs) else [],
                [texts[i]],
                [choices[i]] if i < len(choices) else [],
                i,
            )

        return task_defs, texts, choices, None

    def _build_tasks(
        self,
        task_defs: list[dict],
        task_texts: list[str],
        task_choices: list[dict[str, str]] | None = None,
    ) -> list[TaskData]:
        """
        Assembler TaskData depuis les tâches retenues + textes du candidat.

        Le contexte de chaque tâche passe par _build_task_fields (module
        corrections), qui gère tous les formats de sujet : e-mail reçu (telc),
        forum (Goethe), annonce, promesses/problèmes (ÖSD), thèmes au choix,
        variantes d'opinion, texte source + graphique (TestDaF).

        task_choices[i] = choix du candidat pour la tâche i ({"theme": ...} ou
        {"variant": ...}) : seule l'option choisie est envoyée à l'IA. Sans choix,
        l'IA reçoit toutes les options et identifie celle traitée au texte.
        """
        task_choices = task_choices or []
        tasks = []
        for i, task_def in enumerate(task_defs):
            text = task_texts[i] if i < len(task_texts) else ""
            choice = task_choices[i] if i < len(task_choices) else {}
            fields = _build_task_fields(task_def or {}, choice or {}, _NO_TEIL)
            tasks.append(TaskData(text=text, **fields))
        return tasks

    def _build_response(
        self,
        subject: SchreibenSubject,
        ai_result: dict,
        task_texts: list[str] | None = None,
    ) -> SimulatorCorrectResponse:
        """
        Construire la réponse depuis le résultat IA.
        Délègue entièrement à response_normalizer — même logique que
        corrections/repository.py, une seule source de vérité sur les
        formats de sortie possibles. task_texts sert aux règles de longueur
        (telc, ECL) ; ai_usage expose le coût réel de la correction.
        """
        normalized = normalize_correction_result(
            subject.provider, subject.level, ai_result, task_texts
        )

        return SimulatorCorrectResponse(
            subject_id=subject.id,
            provider=subject.provider,
            level=subject.level,
            ai_usage=ai_result.get("_usage"),
            **normalized,
        )

    @staticmethod
    def _validate_task_count(provider: str, level: str, count: int) -> None:
        """Vérifier la cohérence nombre de tâches / examen (même table que la correction)."""
        expected = EXPECTED_TASK_COUNT.get(_exam_key(provider, level))
        if expected is None:
            raise ValueError(
                f"Le simulateur n'est pas disponible pour {provider.upper()} {level.upper()}."
            )
        if count != expected:
            raise ValueError(
                f"{provider.upper()} {level.upper()} attend {expected} tâche(s), "
                f"{count} fournie(s)."
            )