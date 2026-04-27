"""
app/modules/users/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.database.base import Base, UUIDMixin, TimestampMixin


if TYPE_CHECKING:
    from app.modules.exam_access.models import ExamAccess
    from app.modules.exam_sessions.models import ExamSession
    from app.modules.payments.models import Payment


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Token de vérification email (nullable une fois vérifié)
    verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Reset password
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relations
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="user", lazy="noload"
    )
    exam_accesses: Mapped[list["ExamAccess"]] = relationship(
        "ExamAccess", back_populates="user", lazy="noload"
    )
    exam_sessions: Mapped[list["ExamSession"]] = relationship(
        "ExamSession", back_populates="user", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"