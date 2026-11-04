"""
app/modules/security/models.py

Protection du contenu (sujets, questions, corrigés) contre l'aspiration.

  content_access_events : chaque ouverture de contenu (sujet, session, corrigé)
  security_incidents    : comportement suspect détecté, avec les preuves
  content_blocks        : élèves dont l'accès aux sujets est suspendu
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDMixin


class ContentAccessEvent(Base, UUIDMixin):
    __tablename__ = "content_access_events"
    __table_args__ = (
        Index("ix_content_access_events_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # subject_view | session_start | result_view
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    # Sujet ou session concerné
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(400), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class SecurityIncident(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "security_incidents"
    __table_args__ = (
        Index("ix_security_incidents_status_created", "status", "created_at"),
        Index("ix_security_incidents_user", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # Règle déclenchée : scripted_client, too_many_subjects, too_many_sessions, ...
    rule: Mapped[str] = mapped_column(String(50), nullable=False)
    # low | medium | high
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    # logged | throttled | blocked | banned
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(400), nullable=True)
    # Compteurs au moment de la détection + derniers accès (preuves)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # open | resolved
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class ContentBlock(Base, TimestampMixin):
    __tablename__ = "content_blocks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("security_incidents.id", ondelete="SET NULL"), nullable=True
    )