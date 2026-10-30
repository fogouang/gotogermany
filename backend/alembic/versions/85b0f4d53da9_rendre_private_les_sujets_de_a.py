"""Classes Start Deutsch : niveau A1 / A2 sur training_sessions

Revision ID: b4e1f6a2c903
Revises: a7c3d91e5f20
Create Date: 2026-10-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '85b0f4d53da9'
down_revision = '852fd275f70d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("training_sessions", sa.Column("sd_level", sa.String(length=5), nullable=True))
    op.create_index("ix_training_sessions_sd_level", "training_sessions", ["sd_level"])
    op.alter_column(
        "training_sessions", "level_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True
    )
    op.create_check_constraint(
        "ck_training_session_one_level",
        "training_sessions",
        "(level_id IS NOT NULL) <> (sd_level IS NOT NULL)",
    )


def downgrade() -> None:
    # Les classes Start Deutsch n'ont pas de place dans l'ancien schéma
    op.execute(
        "DELETE FROM training_session_students WHERE training_session_id IN "
        "(SELECT id FROM training_sessions WHERE sd_level IS NOT NULL)"
    )
    op.execute(
        "DELETE FROM training_session_teachers WHERE training_session_id IN "
        "(SELECT id FROM training_sessions WHERE sd_level IS NOT NULL)"
    )
    op.execute(
        "DELETE FROM assignment_targets WHERE training_session_id IN "
        "(SELECT id FROM training_sessions WHERE sd_level IS NOT NULL)"
    )
    op.execute("DELETE FROM training_sessions WHERE sd_level IS NOT NULL")
    op.drop_constraint("ck_training_session_one_level", "training_sessions", type_="check")
    op.alter_column(
        "training_sessions", "level_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False
    )
    op.drop_index("ix_training_sessions_sd_level", table_name="training_sessions")
    op.drop_column("training_sessions", "sd_level")