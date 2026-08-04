"""
app/modules/corrections/models.py

Une Correction est créée pour le module Schreiben d'une ExamSession.
Elle est liée à la session (pas à une answer individuelle) car le prompt
combine toutes les réponses free_text de la session en une seule évaluation.

⚠️ Changement structurel : les 4 colonnes fixes aufgabe_score/kohaesion_score/
wortschatz_score/grammatik_score (+ criteria_feedbacks séparé) sont remplacées
par une colonne JSONB générique `criteria` (liste de critères, nombre et noms
variables selon l'examen). `task_feedbacks` devient `tasks` (même idée, liste
au lieu de dict clé→objet). Nécessite une migration Alembic — voir
alembic_migration_criteria_tasks.py. La normalisation vers ce format se fait
une seule fois à l'écriture (repository.create), donc ces colonnes JSONB
stockent déjà la forme finale consommée telle quelle par le frontend.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, Float, Boolean,
    DateTime, ForeignKey, UniqueConstraint, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.exam_sessions.models import ExamSession


class Correction(Base, UUIDMixin, TimestampMixin):
    """
    Résultat de la correction IA du module Schreiben.

    Une seule correction par session (UniqueConstraint).
    Tous les feedbacks et scores sont stockés en JSONB pour éviter
    des colonnes variables selon le nombre de tâches ET selon le nombre/nom
    des critères (qui diffère par examen : 3 pour telc, 4 pour Goethe,
    structure imbriquée pour ÖSD B2).
    """
    __tablename__ = "corrections"

    __table_args__ = (
        # Une session ne peut avoir qu'une seule correction Schreiben
        UniqueConstraint("session_id", name="uq_correction_session"),
    )

    # ── Relations ───────────────────────────────────────
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Dénormalisé pour éviter les jointures dans les requêtes fréquentes
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Contexte examen ──────────────────────────────────
    # Dénormalisé depuis Exam.provider + Level.cefr_code
    # Évite de reconstruire la chaîne session→subject→level→exam à chaque lecture
    provider: Mapped[str] = mapped_column(String(20), nullable=False)   # telc | goethe | osd
    level: Mapped[str] = mapped_column(String(5), nullable=False)        # b1 | b2

    # ── Scores globaux ───────────────────────────────────
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)      # 30, 45 ou 100
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # ÖSD B2 uniquement : vrai plancher officiel (>=10/30), distinct de `passed`
    # (qui reste un repère interne à 60% pour tous les examens, cf. osd_b2_prompt.py).
    # Nullable — non renseigné pour les autres examens.
    floor_reached: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)

    # ── Critères de notation (JSONB) ─────────────────────
    # [{"key": "erfullung", "label": "Erfüllung", "score": 18, "max_score": 25,
    #   "feedback": "..."}, ...]
    # Nombre et clés variables selon l'examen — voir response_normalizer.CRITERIA_CONFIG.
    criteria: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # ── Feedbacks par tâche (JSONB) ───────────────────────
    # [{"key": "task1", "label": "Teil 1", "corrected_text": "...",
    #   "main_strengths": [...], "main_weaknesses": [...],
    #   "score": 12, "max_score": 15, "sub_criteria": [...]}, ...]  (score/max_score/
    # sub_criteria optionnels, remplis seulement pour ÖSD B2)
    tasks: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Liste des erreurs corrigées :
    # [{"error": "...", "correction": "...", "task": "1", "explanation": "..."}]
    corrections_list: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Conseils d'amélioration
    suggestions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Appréciation générale (texte libre)
    appreciation: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # ── Meta IA ──────────────────────────────────────────
    ai_provider: Mapped[str] = mapped_column(String(30), nullable=False, default="gemini")

    # ── Relation ─────────────────────────────────────────
    session: Mapped["ExamSession"] = relationship(
        "ExamSession", lazy="noload"
    )

    # ── Propriétés calculées ─────────────────────────────
    @property
    def score_percentage(self) -> float:
        """Pourcentage du score obtenu."""
        if self.max_score == 0:
            return 0.0
        return round(self.overall_score / self.max_score * 100, 1)

    def __repr__(self) -> str:
        return (
            f"<Correction session:{self.session_id} "
            f"{self.provider.upper()} {self.level.upper()} "
            f"{self.overall_score}/{self.max_score} "
            f"({'✓' if self.passed else '✗'})>"
        )