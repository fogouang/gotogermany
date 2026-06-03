"""
app/modules/corrections/repository.py

CRUD pour la table corrections.
Les corrections sont immuables — pas de update ni delete.
"""
from __future__ import annotations
import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.corrections.models import Correction
from app.modules.corrections.schemas import CorrectionPayload

logger = logging.getLogger(__name__)


class CorrectionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Lecture ──────────────────────────────────────────

    async def get_by_id(self, correction_id: uuid.UUID) -> Correction | None:
        """Récupérer une correction par son ID."""
        result = await self.db.execute(
            select(Correction).where(Correction.id == correction_id)
        )
        return result.scalar_one_or_none()

    async def get_by_session(self, session_id: uuid.UUID) -> Correction | None:
        """
        Récupérer la correction d'une session Schreiben.
        Retourne None si aucune correction n'existe encore.
        """
        result = await self.db.execute(
            select(Correction).where(Correction.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Correction]:
        """Récupérer toutes les corrections d'un utilisateur (paginées)."""
        result = await self.db.execute(
            select(Correction)
            .where(Correction.user_id == user_id)
            .order_by(Correction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def exists_for_session(self, session_id: uuid.UUID) -> bool:
        """Vérifier si une correction existe déjà pour cette session."""
        result = await self.db.execute(
            select(Correction.id).where(Correction.session_id == session_id)
        )
        return result.scalar_one_or_none() is not None

    # ── Écriture ─────────────────────────────────────────

    async def create(
        self,
        payload: CorrectionPayload,
        ai_result: dict,
    ) -> Correction:
        """
        Créer une nouvelle correction à partir du payload et du résultat IA.

        Args:
            payload: Données contextuelles (session, user, provider, level, max_score)
            ai_result: JSON retourné par le modèle IA (déjà parsé)

        Returns:
            Correction créée et persistée
        """
        # Extraire les scores — compatible format simple (Telc) et combiné (Goethe/ÖSD)
        scores = _extract_scores(ai_result)
        feedbacks = _extract_feedbacks(ai_result)

        correction = Correction(
            session_id=payload.session_id,
            user_id=payload.user_id,
            provider=payload.provider,
            level=payload.level,
            overall_score=scores["overall_score"],
            max_score=payload.max_score,
            passed=ai_result.get("passed", False),
            aufgabe_score=scores["aufgabe_score"],
            kohaesion_score=scores["kohaesion_score"],
            wortschatz_score=scores["wortschatz_score"],
            grammatik_score=scores["grammatik_score"],
            criteria_feedbacks=feedbacks,
            task_feedbacks=_extract_task_feedbacks(ai_result),
            corrections_list=ai_result.get("corrections", []),
            suggestions=ai_result.get("suggestions", []),
            appreciation=_extract_appreciation(ai_result),
            ai_provider="gemini",
        )

        self.db.add(correction)
        await self.db.commit()
        await self.db.refresh(correction)

        logger.info(
            f"Correction créée: session={payload.session_id} "
            f"{payload.provider.upper()} {payload.level.upper()} "
            f"{correction.overall_score}/{payload.max_score}"
        )
        return correction


# ─────────────────────────────────────────────────────────
# Helpers d'extraction — gèrent les 2 formats JSON de l'IA
# ─────────────────────────────────────────────────────────
# Format A (Telc — 1 tâche) :
#   {"overall_score": 34, "aufgabe_score": 12, "passed": true, ...}
#
# Format B (Goethe/ÖSD — combiné) :
#   {"global_assessment": {"overall_score": 72, "passed": true},
#    "criteria_scores": {"aufgabe_score": 22, ...}}
# ─────────────────────────────────────────────────────────

def _extract_scores(ai_result: dict) -> dict:
    """Extraire les scores quel que soit le format."""
    if "global_assessment" in ai_result:
        # Format combiné (Goethe/ÖSD)
        scores = ai_result.get("criteria_scores", {})
        return {
            "overall_score": ai_result["global_assessment"].get("overall_score", 0),
            "aufgabe_score": scores.get("aufgabe_score", 0),
            "kohaesion_score": scores.get("kohaesion_score", 0),
            "wortschatz_score": scores.get("wortschatz_score", 0),
            "grammatik_score": scores.get("grammatik_score", 0),
        }
    # Format simple (Telc)
    return {
        "overall_score": ai_result.get("overall_score", 0),
        "aufgabe_score": ai_result.get("aufgabe_score", 0),
        "kohaesion_score": ai_result.get("kohaesion_score", 0),
        "wortschatz_score": ai_result.get("wortschatz_score", 0),
        "grammatik_score": ai_result.get("grammatik_score", 0),
    }


def _extract_feedbacks(ai_result: dict) -> dict:
    """Extraire les feedbacks textuels par critère."""
    if "criteria_scores" in ai_result:
        s = ai_result["criteria_scores"]
        return {
            "aufgabe_feedback":   s.get("aufgabe_feedback", ""),
            "kohaesion_feedback": s.get("kohaesion_feedback", ""),
            "wortschatz_feedback": s.get("wortschatz_feedback", ""),
            "grammatik_feedback": s.get("grammatik_feedback", ""),
        }
    return {
        "aufgabe_feedback":   ai_result.get("aufgabe_feedback", ""),
        "kohaesion_feedback": ai_result.get("kohaesion_feedback", ""),
        "wortschatz_feedback": ai_result.get("wortschatz_feedback", ""),
        "grammatik_feedback": ai_result.get("grammatik_feedback", ""),
    }


def _extract_task_feedbacks(ai_result: dict) -> dict:
    """
    Extraire les feedbacks par tâche.
    Format A (Telc) : pas de task_feedbacks → on reconstruit depuis corrected_text
    Format B (Goethe/ÖSD) : champ task_feedbacks déjà présent
    """
    if "task_feedbacks" in ai_result:
        return ai_result["task_feedbacks"]
    # Format Telc — 1 seule tâche
    return {
        "task1": {
            "corrected_text": ai_result.get("corrected_text", ""),
            "main_strengths": [],
            "main_weaknesses": [],
        }
    }


def _extract_appreciation(ai_result: dict) -> str:
    """Extraire l'appréciation générale."""
    if "global_assessment" in ai_result:
        return ai_result["global_assessment"].get("appreciation", "")
    return ai_result.get("appreciation", "")