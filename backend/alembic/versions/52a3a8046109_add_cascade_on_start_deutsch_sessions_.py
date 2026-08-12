"""add_cascade_on_start_deutsch_sessions_subject_fk

Revision ID: 52a3a8046109
Revises: a8b57238ff94
Create Date: 2026-08-11 18:26:58.831257
"""
from alembic import op
import sqlalchemy as sa


revision = '52a3a8046109'
down_revision = 'a8b57238ff94'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "start_deutsch_sessions_subject_id_fkey",
        "start_deutsch_sessions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "start_deutsch_sessions_subject_id_fkey",
        "start_deutsch_sessions",
        "start_deutsch_subjects",
        ["subject_id"], ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "start_deutsch_sessions_subject_id_fkey",
        "start_deutsch_sessions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "start_deutsch_sessions_subject_id_fkey",
        "start_deutsch_sessions",
        "start_deutsch_subjects",
        ["subject_id"], ["id"],
    )