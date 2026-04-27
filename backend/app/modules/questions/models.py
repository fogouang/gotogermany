"""
app/modules/questions/models.py

Une Question appartient à un Teil.
Son contenu et sa correction varient selon le format_type du Teil parent.
Tout est stocké en JSONB pour rester flexible face aux formats Goethe/ÖSD/TELC.

Exemples de contenu par format_type :

richtig_falsch / ja_nein :
  content  = {"statement": "Lena arbeitet seit drei Wochen..."}
  correct_answer = {"answer": "richtig"}

qcm_abc :
  content  = {"stem": "Worum geht es...", "options": {"a": "...", "b": "...", "c": "..."}}
  correct_answer = {"answer": "b"}

matching :
  content  = {"situation": "Sie ziehen in eine neue Wohnung..."}
  correct_answer = {"answer": "d"}

zuordnung_speaker :
  content  = {"statement": "Wer ist der Meinung, dass..."}
  correct_answer = {"answer": "b"}

free_text (Schreiben) :
  content  = {"scenario": "...", "prompts": [...], "word_count_target": 80}
  correct_answer = {"musterlösung": "...", "scoring_criteria": {...}}

oral_interaction / oral_monologue / oral_feedback (Sprechen) :
  content  = {"scenario": "...", "prompts": [...]}
  correct_answer = {"scoring_criteria": {...}}

mixed_richtig_falsch_qcm (Hören Teil 1) :
  content  = {"type": "richtig_falsch", "statement": "..."}
     OU     {"type": "qcm_abc", "stem": "...", "options": {...}}
  correct_answer = {"answer": "richtig"} ou {"answer": "b"}
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
  from app.modules.exam_sessions.models import ExamSessionAnswer
  from app.modules.exams.models import Teil


class Question(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "questions"

    __table_args__ = (
        # Pas deux questions avec le même numéro dans un même Teil
        UniqueConstraint("teil_id", "question_number", name="uq_question_teil_number"),
    )

    teil_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teile.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Reflète le format_type du Teil parent pour éviter les jointures inutiles
    # ex: "richtig_falsch", "qcm_abc", "free_text", "oral_interaction"...
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Contenu de la question — structure variable selon question_type (voir docstring)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Réponse correcte + critères de correction — variable selon question_type
    # Pour free_text/oral : contient musterlösung + scoring_criteria
    # Pour auto-corrected : contient juste {"answer": "b"}
    correct_answer: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Points attribués à cette question
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Chemin relatif vers l'audio si la question nécessite un fichier audio
    # ex: "horen/teil1/audio1.mp3"  — NULL si pas d'audio
    audio_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relations
    teil: Mapped["Teil"] = relationship("Teil", back_populates="questions", lazy="noload")
    answers: Mapped[list["ExamSessionAnswer"]] = relationship(
        "ExamSessionAnswer", back_populates="question", lazy="noload"
    )

    @property
    def is_auto_correctable(self) -> bool:
        """
        True si la question peut être corrigée automatiquement.
        Les types free_text et oral_* nécessitent une correction manuelle ou IA.
        """
        return self.question_type not in (
            "free_text",
            "oral_interaction",
            "oral_monologue",
            "oral_feedback",
        )

    def __repr__(self) -> str:
        return f"<Question #{self.question_number} ({self.question_type}) — teil:{self.teil_id}>"