"""
app/modules/users/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timezone
import enum
from sqlalchemy import Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.exam_access.models import ExamAccess
    from app.modules.exam_sessions.models import ExamSession
    from app.modules.payments.models import Payment
    from app.modules.centers.models import Center, Branch
    from app.modules.exams.models import Level        


class UserRole(str, enum.Enum):
    student = "student"
    branch_secretary = "branch_secretary"
    center_director = "center_director"
    # Le staff ITIA reste géré par le booléen is_admin existant, pas dans cet enum


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

    # --- Licence de centre ---
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.student,
        nullable=False,
        server_default=UserRole.student.value,
    )

    # Renseigné uniquement pour role=center_director
    center_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("centers.id"), nullable=True, index=True
    )
    # Renseigné pour role=branch_secretary ET pour role=student rattaché à un centre
    # (reste null pour un étudiant B2C individuel classique)
    branch_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("branches.id"), nullable=True, index=True
    )

    # Ciblage examen (pertinent uniquement pour un student rattaché à un centre)
    target_level_id: Mapped[UUID | None] = mapped_column(ForeignKey("levels.id"), nullable=True)
    target_level: Mapped["Level | None"] = relationship("Level", foreign_keys=[target_level_id], lazy="noload")

    # Durée de vie du compte : 2 mois silencieux à partir de la première connexion
    first_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    access_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    access_duration_days: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False, server_default="30"
    )

    ai_credits: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,  # 2 crédits offerts à l'inscription
        server_default="2",
        doc="Crédits IA disponibles pour les corrections Schreiben"
    )

    # Relations existantes
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="user", lazy="noload"
    )
    exam_accesses: Mapped[list["ExamAccess"]] = relationship(
        "ExamAccess", back_populates="user", lazy="noload"
    )
    exam_sessions: Mapped[list["ExamSession"]] = relationship(
        "ExamSession", back_populates="user", lazy="noload"
    )

    # Relations licence de centre
    center: Mapped["Center | None"] = relationship(
        "Center", foreign_keys=[center_id], lazy="noload"
    )
    branch: Mapped["Branch | None"] = relationship(
        "Branch", back_populates="users", foreign_keys=[branch_id], lazy="noload"
    )

    # Appareils connectés (max 2, appliqué en logique métier, pas en contrainte DB)
    devices: Mapped[list["UserDevice"]] = relationship(
        "UserDevice", back_populates="user", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class UserDevice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_devices"
    __table_args__ = (
        UniqueConstraint("user_id", "device_fingerprint", name="uq_user_device_fingerprint"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="devices", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<UserDevice user={self.user_id} fp={self.device_fingerprint[:8]}>"