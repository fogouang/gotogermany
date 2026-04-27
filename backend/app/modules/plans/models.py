"""
app/modules/plans/models.py

Plan d'accès à un exam pour GoToGermany.
Un plan définit une durée et un prix.
Ex: "7 jours", "1 mois", "3 mois"
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.payments.models import Payment


class Plan(Base, UUIDMixin, TimestampMixin):
    """
    Plan d'abonnement — durée + prix.
    Créé et géré par l'admin.
    S'applique à tous les examens (prix unique par plan).
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

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        doc="Description affichée sur la page tarifs"
    )

    # Ordre d'affichage sur la page tarifs
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # Relations
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="plan", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Plan {self.name!r} — {self.duration_days}j — {self.price} FCFA>"