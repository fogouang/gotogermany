"""
app/modules/centers/models.py
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import enum
from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.database.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.models import User


class LicenseStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class PaymentMethod(str, enum.Enum):
    mobile_money = "mobile_money"
    bank_transfer = "bank_transfer"


class Center(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "centers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    branches: Mapped[list["Branch"]] = relationship(
        "Branch", back_populates="center", lazy="noload"
    )
    licenses: Mapped[list["CenterLicense"]] = relationship(
        "CenterLicense", back_populates="center", lazy="noload"
    )
    director: Mapped["User | None"] = relationship(
        "User",
        primaryjoin="Center.id == User.center_id",
        viewonly=True,
        uselist=False,
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Center {self.name}>"


class Branch(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "branches"

    center_id: Mapped[UUID] = mapped_column(
        ForeignKey("centers.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    center: Mapped["Center"] = relationship(
        "Center", back_populates="branches", lazy="noload"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="branch", foreign_keys="User.branch_id", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Branch {self.name} center={self.center_id}>"


class LicenseFormula(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "license_formulas"

    label: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    max_students: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    licenses: Mapped[list["CenterLicense"]] = relationship(
        "CenterLicense", back_populates="formula", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<LicenseFormula {self.label}>"


class CenterLicense(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "center_licenses"

    center_id: Mapped[UUID] = mapped_column(
        ForeignKey("centers.id"), nullable=False, index=True
    )
    formula_id: Mapped[UUID] = mapped_column(
        ForeignKey("license_formulas.id"), nullable=False
    )

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Copié de la formule au moment de l'activation (historique préservé
    # même si la formule source est modifiée/désactivée plus tard)
    max_students: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[LicenseStatus] = mapped_column(
        Enum(LicenseStatus, name="license_status"),
        default=LicenseStatus.pending,
        nullable=False,
        server_default=LicenseStatus.pending.value,
    )
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        Enum(PaymentMethod, name="license_payment_method"), nullable=True
    )
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activated_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    center: Mapped["Center"] = relationship(
        "Center", back_populates="licenses", lazy="noload"
    )
    formula: Mapped["LicenseFormula"] = relationship(
        "LicenseFormula", back_populates="licenses", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<CenterLicense center={self.center_id} status={self.status}>"