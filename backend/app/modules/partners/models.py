"""
app/modules/partners/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.modules.promo_codes.models import PromoCode


class Partner(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "partners"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relations
    promo_codes: Mapped[list["PromoCode"]] = relationship(
        "PromoCode", back_populates="partner", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Partner {self.name}>"