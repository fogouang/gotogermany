"""
app/modules/schreiben_simulator/models.py

Sujets dédiés au simulateur Schreiben.
Indépendants des examens réels — gérés par l'admin.
"""
from __future__ import annotations
import uuid
from sqlalchemy import UUID, Float, ForeignKey, String, Boolean, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


class SchreibenSubject(Base, UUIDMixin, TimestampMixin):
    """
    Un sujet simulateur = un exercice Schreiben complet avec 1, 2 ou 3 tâches.

    Structure de `tasks` (JSONB) :
    [
      {
        "teil": 1,
        "scenario": "Sie haben an einer Fahrradtour teilgenommen...",
        "prompts": ["Warum Sie unzufrieden waren", "Was Sie erwarten"],
        "topic": "",           ← Goethe/ÖSD B2 Teil 1 : thème du texte argumentatif
        "context_ad": "",      ← Telc B2 / ÖSD B2 : texte de l'annonce
        "opinion_quote": "",   ← Goethe B1 Teil 2 : citation du forum
        "word_count_min": 150,
        "word_count_max": 200
      },
      { "teil": 2, ... },
      { "teil": 3, ... }       ← Goethe/ÖSD B1 uniquement
    ]
    """
    __tablename__ = "schreiben_subjects"

    __table_args__ = (
        UniqueConstraint("provider", "level", "title", name="uq_subject_provider_level_title"),
    )

    # Examen et niveau
    provider: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # telc|goethe|osd
    level: Mapped[str] = mapped_column(String(5), nullable=False, index=True)       # b1|b2

    # Titre affiché à l'utilisateur (ex: "Fahrradtour mit Trainer")
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Description courte optionnelle pour l'admin
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tâches du sujet — structure variable selon provider/level
    tasks: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Ordre d'affichage dans la liste
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<SchreibenSubject {self.provider.upper()} {self.level.upper()} "
            f"— {self.title} ({'✓' if self.is_active else '✗'})>"
        )
        
class SimulatorResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "simulator_results"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    # Plus de ForeignKey — peut pointer vers schreiben_subjects.id (legacy)
    # OU subjects.id (hiérarchie unifiée), selon la source du sujet corrigé.
    # L'intégrité référentielle n'est plus garantie par la DB ici — elle
    # est de la responsabilité du service au moment de save_result().
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    provider:         Mapped[str]   = mapped_column(String(20), nullable=False)
    level:            Mapped[str]   = mapped_column(String(5),  nullable=False)
    overall_score:    Mapped[int]   = mapped_column(Integer,    default=0)
    max_score:        Mapped[int]   = mapped_column(Integer,    default=0)
    passed:           Mapped[bool]  = mapped_column(Boolean,    default=False)
    score_percentage: Mapped[float] = mapped_column(Float,      default=0.0)
    result_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<SimulatorResult {self.provider.upper()} {self.level.upper()} — {self.score_percentage}%>"