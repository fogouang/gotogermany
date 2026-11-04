"""protection du contenu : journal d'accès, incidents, blocages

Revision ID: d3f8a1c9b742
Revises: REMPLACE_PAR_LA_TETE_ACTUELLE
Create Date: 2026-11-04
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '43cf41528310'
down_revision = '6b6b987c1b9d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_access_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("path", sa.String(255), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(400), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_content_access_events_user_created", "content_access_events", ["user_id", "created_at"]
    )

    op.create_table(
        "security_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(400), nullable=True),
        sa.Column("details", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_security_incidents_status_created", "security_incidents", ["status", "created_at"])
    op.create_index("ix_security_incidents_user", "security_incidents", ["user_id"])

    op.create_table(
        "content_blocks",
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("security_incidents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("content_blocks")
    op.drop_index("ix_security_incidents_user", table_name="security_incidents")
    op.drop_index("ix_security_incidents_status_created", table_name="security_incidents")
    op.drop_table("security_incidents")
    op.drop_index("ix_content_access_events_user_created", table_name="content_access_events")
    op.drop_table("content_access_events")