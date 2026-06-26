# app/modules/settings/models.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.database.base import Base, UUIDMixin, TimestampMixin

class AppSetting(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)