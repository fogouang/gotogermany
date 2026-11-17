"""
app/modules/plans/models.py
Plan d'accès à un exam pour GoToGermany.
Un plan définit une durée et un prix.
Ex: "7 jours", "1 mois", "3 mois"
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.payments.models import Payment


class Plan(Base, UUIDMixin, TimestampMixin):
    """
    Plan d'abonnement — durée + prix.
    Créé et géré par l'admin.
    Rattaché à un parcours : "standard" (B1/B2/TestDaF) ou "start_deutsch" (A1/A2).
    """
    __tablename__ = "plans"

    # Ex: "7 jours", "15 jours", "1 mois", "3 mois"
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    # Durée en jours — calculée pour expires_at de ExamAccess
    duration_days: Mapped[int] = mapped_column(
        Integer, nullable=False,
        doc="7 | 15 | 30 | 60 | 90"
    )
    # Prix en FCFA (entier)
    price: Mapped[int] = mapped_column(
        Integer, nullable=False,
        doc="Prix en FCFA — ex: 2500, 5000, 12000"
    )
       # Prix en euros pour le paiement par carte (vide = pas payable par carte)
    price_eur: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True,
        doc="Prix en euros — ex: 15.00"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        doc="Description affichée sur la page tarifs"
    )
    # Liste des clés de features cochées par l'admin — ex: ["unlimited", "corrections"]
    # Les clés valides correspondent aux traductions pricing.features.* côté frontend.
    features: Mapped[list[str] | None] = mapped_column(
        JSONB, nullable=True,
        doc="Liste des features affichées pour ce plan sur la page tarifs"
    )
    # Ordre d'affichage sur la page tarifs
    
    ai_credits: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Credits IA ajoutes a l'eleve a chaque activation de la formule",
    )
     
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    
    # Parcours auquel s'applique le plan
    track: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="standard",
        server_default="standard",
        index=True,
        doc="standard (B1/B2/TestDaF) | start_deutsch (A1/A2)",
    )
    # Badge "Populaire" sur la page tarifs
    is_popular: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    # Relations
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="plan", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Plan {self.name!r} — {self.duration_days}j — {self.price} FCFA>"