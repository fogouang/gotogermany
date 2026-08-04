"""
app/modules/corrections/repository.py

CRUD pour la table corrections.
Les corrections sont immuables — pas de update ni delete.

⚠️ create() ne fait plus d'extraction champ par champ selon le format IA
(_extract_scores/_extract_feedbacks/_extract_task_feedbacks ont disparu) :
toute la normalisation passe désormais par response_normalizer, une seule
fois, ici, à l'écriture. Les colonnes JSONB `criteria`/`tasks` stockent donc
directement la forme finale déjà consommée telle quelle par le frontend —
_to_response() dans service.py n'a plus rien à retraiter.
"""
from __future__ import annotations
import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.corrections.models import Correction
from app.modules.corrections.schemas import CorrectionPayload
from app.modules.corrections.response_normalizer import normalize_correction_result

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
            ai_result: JSON retourné par le modèle IA (déjà parsé), quel que
                       soit son format brut — normalize_correction_result()
                       absorbe les 3 formes possibles (nested/flat/osd_b2).

        Returns:
            Correction créée et persistée
        """
        normalized = normalize_correction_result(payload.provider, payload.level, ai_result)

        correction = Correction(
            session_id=payload.session_id,
            user_id=payload.user_id,
            provider=payload.provider,
            level=payload.level,
            overall_score=normalized["overall_score"],
            max_score=normalized["max_score"],
            passed=normalized["passed"],
            floor_reached=normalized.get("floor_reached"),
            criteria=normalized["criteria"],
            tasks=normalized["tasks"],
            corrections_list=normalized["corrections_list"],
            suggestions=normalized["suggestions"],
            appreciation=normalized["appreciation"],
            ai_provider="gemini",
        )

        self.db.add(correction)
        await self.db.commit()
        await self.db.refresh(correction)

        logger.info(
            f"Correction créée: session={payload.session_id} "
            f"{payload.provider.upper()} {payload.level.upper()} "
            f"{correction.overall_score}/{correction.max_score}"
        )
        return correction