"""
app/modules/corrections/models.py

Une Correction est créée pour le module Schreiben d'une ExamSession.
Elle est liée à la session (pas à une answer individuelle) car le prompt
combine toutes les réponses free_text de la session en une seule évaluation.
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
    des colonnes variables selon le nombre de tâches.
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

    # ── Scores ───────────────────────────────────────────
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)      # 45, 90 ou 100
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Scores par critère
    aufgabe_score: Mapped[int] = mapped_column(Integer, nullable=False)
    kohaesion_score: Mapped[int] = mapped_column(Integer, nullable=False)
    wortschatz_score: Mapped[int] = mapped_column(Integer, nullable=False)
    grammatik_score: Mapped[int] = mapped_column(Integer, nullable=False)

    # ── Feedbacks textuels (JSONB) ───────────────────────
    # {"aufgabe_feedback": "...", "kohaesion_feedback": "...", ...}
    criteria_feedbacks: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Feedbacks par tâche :
    # {
    #   "task1": {"corrected_text": "...", "main_strengths": [...], "main_weaknesses": [...]},
    #   "task2": {...},
    #   "task3": {...}   ← présent seulement pour Goethe/ÖSD B1
    # }
    task_feedbacks: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

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