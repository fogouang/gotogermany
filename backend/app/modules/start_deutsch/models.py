"""
app/modules/start_deutsch/models.py

Module Start Deutsch (A1, A2).
- Base, UUIDMixin et TimestampMixin partagés (app.shared.database.base).
- Niveau, slug de module, format_type et statut en String simple, comme
  question_type sur le modèle Question : pas d'Enum Postgres à migrer.
- Tables préfixées "start_deutsch_" : les noms questions, teile, sessions
  sont déjà pris par les autres modules.
- Audio au niveau du Teil : un fichier par Teil, jamais par question.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, false, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.users.models import User


# ── Constantes ────────────────────────────────────────────────────

class Level:
    A1 = "A1"
    A2 = "A2"


class ModuleSlug:
    LESEN = "lesen"
    HOEREN = "hoeren"
    SCHREIBEN = "schreiben"
    SPRECHEN = "sprechen"


class FormatType:
    MC_TEXT = "mc_text"
    MC_IMAGE = "mc_image"
    TRUE_FALSE = "true_false"
    MATCHING_2OPTIONS = "matching_2options"
    MATCHING_WITH_DISTRACTOR = "matching_with_distractor"
    IMAGE_DAY_MATCHING = "image_day_matching"
    JA_NEIN = "ja_nein"
    FORM_FILL = "form_fill"
    FREE_TEXT = "free_text"
    SPRECHEN_GROUP_INTRO = "sprechen_group_intro"
    SPRECHEN_GROUP_WORD_CARD = "sprechen_group_word_card"
    SPRECHEN_GROUP_IMAGE_CARD = "sprechen_group_image_card"
    SPRECHEN_DUO_QUESTION_CARD = "sprechen_duo_question_card"
    SPRECHEN_DUO_MONOLOGUE_CARD = "sprechen_duo_monologue_card"
    SPRECHEN_DUO_NEGOTIATION = "sprechen_duo_negotiation"


class SessionStatus:
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PENDING_REVIEW = "PENDING_REVIEW"


# ── Contenu ───────────────────────────────────────────────────────

class StartDeutschSubject(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "start_deutsch_subjects"
    __table_args__ = (UniqueConstraint("level", "subject_number", name="uq_sd_subject_level_number"),)

    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    # Plusieurs sujets par niveau : Sujet 1, Sujet 2...
    subject_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Privé : absent du catalogue élève, réservé aux devoirs des enseignants
    is_private: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default=false()
    )

    modules: Mapped[list["StartDeutschModule"]] = relationship(
        "StartDeutschModule", back_populates="subject", cascade="all, delete-orphan", lazy="noload",
        order_by="StartDeutschModule.order",
    )


class StartDeutschModule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "start_deutsch_modules"
    __table_args__ = (UniqueConstraint("subject_id", "slug", name="uq_sd_module_subject_slug"),)

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_subjects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    slug: Mapped[str] = mapped_column(String(20), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=25, nullable=False)

    subject: Mapped["StartDeutschSubject"] = relationship(
        "StartDeutschSubject", back_populates="modules", lazy="noload"
    )
    teile: Mapped[list["StartDeutschTeil"]] = relationship(
        "StartDeutschTeil", back_populates="module", cascade="all, delete-orphan", lazy="noload",
        order_by="StartDeutschTeil.teil_number",
    )


class StartDeutschTeil(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "start_deutsch_teile"
    __table_args__ = (UniqueConstraint("module_id", "teil_number", name="uq_sd_teil_module_number"),)

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_modules.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    teil_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # mc_image, form_fill, sprechen_duo_negotiation... (cf. FormatType)
    format_type: Mapped[str] = mapped_column(String(40), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Chemin relatif de l'audio du Teil, ex. "a1/subject1/hoeren/hoeren_teil1.mp3"
    audio_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    module: Mapped["StartDeutschModule"] = relationship(
        "StartDeutschModule", back_populates="teile", lazy="noload"
    )
    questions: Mapped[list["StartDeutschQuestion"]] = relationship(
        "StartDeutschQuestion", back_populates="teil", cascade="all, delete-orphan", lazy="noload",
        order_by="StartDeutschQuestion.question_number",
    )
    # Texte, annonces ou images communs au Teil ; transcription en Hören
    shared_content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class StartDeutschQuestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "start_deutsch_questions"
    __table_args__ = (UniqueConstraint("teil_id", "question_number", name="uq_sd_question_teil_number"),)

    teil_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_teile.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Selon le format_type du Teil, par exemple :
    # mc_image  {"question": "...", "options": [{"label": "a", "image_file": "..."}, ...]}
    # form_fill {"prompt_text": "...", "fields": [{"number": 1, "label": "Alter"}, ...]}
    # free_text {"prompt": "...", "content_points": [...], "min_words": 20, "max_words": 30}
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # QCM {"answer": "b"} ; form_fill {"fields": {"1": "Berger", ...}} ;
    # free_text : aucune, corrigé par l'IA sur la grille officielle
    correct_answer: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    points: Mapped[float] = mapped_column(Float, nullable=False, default=1)

    # Image propre à la question si besoin (distincte de l'audio, qui reste au Teil)
    image_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

    teil: Mapped["StartDeutschTeil"] = relationship(
        "StartDeutschTeil", back_populates="questions", lazy="noload"
    )
    answers: Mapped[list["StartDeutschAnswer"]] = relationship(
        "StartDeutschAnswer", back_populates="question", lazy="noload"
    )

    @property
    def is_auto_correctable(self) -> bool:
        """Faux pour free_text et les formats sprechen_* (correction IA ou manuelle)."""
        return self.format_type_of_teil_is_auto_correctable()

    def format_type_of_teil_is_auto_correctable(self) -> bool:
        ft = self.teil.format_type if self.teil else None
        return ft not in (
            FormatType.FREE_TEXT,
            FormatType.SPRECHEN_GROUP_INTRO,
            FormatType.SPRECHEN_GROUP_WORD_CARD,
            FormatType.SPRECHEN_GROUP_IMAGE_CARD,
            FormatType.SPRECHEN_DUO_QUESTION_CARD,
            FormatType.SPRECHEN_DUO_MONOLOGUE_CARD,
            FormatType.SPRECHEN_DUO_NEGOTIATION,
        )

    def __repr__(self) -> str:
        return f"<StartDeutschQuestion #{self.question_number} teil={self.teil_id}>"


# ── Sessions ──────────────────────────────────────────────────────

class StartDeutschSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "start_deutsch_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("start_deutsch_subjects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    status: Mapped[str] = mapped_column(String(20), default=SessionStatus.IN_PROGRESS, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # Début et soumission de la tentative (created_at et updated_at concernent la ligne)
    started_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    submitted_at = mapped_column(DateTime(timezone=True), nullable=True)

    subject: Mapped["StartDeutschSubject"] = relationship("StartDeutschSubject", lazy="noload")
    user: Mapped["User"] = relationship("User", lazy="noload")
    answers: Mapped[list["StartDeutschAnswer"]] = relationship(
        "StartDeutschAnswer", back_populates="session", cascade="all, delete-orphan", lazy="noload"
    )
    schreiben_corrections: Mapped[list["StartDeutschSchreibenCorrection"]] = relationship(
        "StartDeutschSchreibenCorrection", back_populates="session", cascade="all, delete-orphan", lazy="noload"
    )


class StartDeutschAnswer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "start_deutsch_answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_sd_answer_session_question"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_questions.id"), nullable=False, index=True,
    )
    user_answer: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score_obtained: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    session: Mapped["StartDeutschSession"] = relationship(
        "StartDeutschSession", back_populates="answers", lazy="noload"
    )
    question: Mapped["StartDeutschQuestion"] = relationship(
        "StartDeutschQuestion", back_populates="answers", lazy="noload"
    )


class StartDeutschSchreibenCorrection(Base, UUIDMixin, TimestampMixin):
    """Correction IA d'une production Schreiben, sur la grille officielle A à E."""

    __tablename__ = "start_deutsch_schreiben_corrections"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    teil_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("start_deutsch_teile.id"), nullable=False,
    )
    submitted_text: Mapped[str] = mapped_column(Text, nullable=False)

    # {"aufgabenerfuellung": {"grade": "A", "points": 3}, "sprache": {"grade": "B", "points": 2}}
    criteria_scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped["StartDeutschSession"] = relationship(
        "StartDeutschSession", back_populates="schreiben_corrections", lazy="noload"
    )

    @property
    def passed(self) -> bool:
        """Tâche réussie à partir de 60 % des points."""
        return self.max_score > 0 and self.overall_score >= 0.6 * self.max_score