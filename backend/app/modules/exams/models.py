"""
app/modules/exams/models.py

Hiérarchie : Exam → Level → Subject → Module → Teil → Question

- Exam     : TELC B1, Goethe-ÖSD B1 (l'étudiant achète l'accès ici)
- Level    : B1, B2
- Subject  : Sujet 1, Sujet 2... (chaque JSON généré = 1 sujet)
- Module   : Lesen, Hören, Schreiben, Sprechen, Sprachbausteine
- Teil     : Teil 1, Teil 2...
- Question : les questions individuelles
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.modules.exam_access.models import ExamAccess
    from app.modules.payments.models import Payment
    from app.modules.questions.models import Question


# ─────────────────────────────────────────────
# Exam
# ex: "TELC Deutsch B1", "Goethe-ÖSD Zertifikat B1"
# L'étudiant achète l'accès à cet objet.
# ─────────────────────────────────────────────
class Exam(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exams"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relations
    levels: Mapped[list["Level"]] = relationship(
        "Level", back_populates="exam", lazy="noload", cascade="all, delete-orphan"
    )
    exam_accesses: Mapped[list["ExamAccess"]] = relationship(
        "ExamAccess", back_populates="exam", lazy="noload"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="exam", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Exam {self.slug}>"


# ─────────────────────────────────────────────
# Level
# ex: B1, B2 pour un même exam
# ─────────────────────────────────────────────
class Level(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "levels"

    __table_args__ = (
        UniqueConstraint("exam_id", "cefr_code", name="uq_level_exam_cefr"),
    )

    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cefr_code: Mapped[str] = mapped_column(String(10), nullable=False)
    total_pass_score: Mapped[int] = mapped_column(Integer, nullable=False)
    scoring_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exam_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relations
    exam: Mapped["Exam"] = relationship("Exam", back_populates="levels", lazy="noload")
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject", back_populates="level", lazy="noload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Level {self.cefr_code} — exam:{self.exam_id}>"


# ─────────────────────────────────────────────
# Subject
# Un sujet = un ensemble complet d'exercices
# ex: TELC B1 → Sujet 1, Sujet 2, Sujet 3...
# Chaque JSON généré par le script = 1 sujet
# ─────────────────────────────────────────────
class Subject(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subjects"

    __table_args__ = (
        UniqueConstraint("level_id", "subject_number", name="uq_subject_level_number"),
    )

    level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("levels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relations
    level: Mapped["Level"] = relationship("Level", back_populates="subjects", lazy="noload")
    modules: Mapped[list["Module"]] = relationship(
        "Module", back_populates="subject", lazy="noload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Subject {self.subject_number} — level:{self.level_id}>"


# ─────────────────────────────────────────────
# Module
# ex: Lesen, Hören, Schreiben, Sprechen
# Appartient à un Subject (plus à Level directement)
# ─────────────────────────────────────────────
class Module(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "modules"

    __table_args__ = (
        UniqueConstraint("subject_id", "slug", name="uq_module_subject_slug"),
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relations
    subject: Mapped["Subject"] = relationship("Subject", back_populates="modules", lazy="noload")
    teile: Mapped[list["Teil"]] = relationship(
        "Teil", back_populates="module", lazy="noload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Module {self.slug} — subject:{self.subject_id}>"


# ─────────────────────────────────────────────
# Teil
# ex: Lesen Teil 1, Lesen Teil 2...
# ─────────────────────────────────────────────
class Teil(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "teile"

    __table_args__ = (
        UniqueConstraint("module_id", "teil_number", name="uq_teil_module_number"),
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teil_number: Mapped[int] = mapped_column(Integer, nullable=False)
    format_type: Mapped[str] = mapped_column(String(50), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relations
    module: Mapped["Module"] = relationship("Module", back_populates="teile", lazy="noload")
    questions: Mapped[list["Question"]] = relationship(
        "Question", back_populates="teil", lazy="noload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Teil {self.teil_number} ({self.format_type}) — module:{self.module_id}>"