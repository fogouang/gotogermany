"""exam sessions bloc en cours

Revision ID: 7d38caa5e1e7
Revises: ccc4c812aa5f
Create Date: 2026-10-20 00:20:07.782299
"""
from alembic import op
import sqlalchemy as sa


revision = '7d38caa5e1e7'
down_revision = 'ccc4c812aa5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "exam_sessions",
        sa.Column("current_block", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "exam_sessions",
        sa.Column("block_deadline", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("exam_sessions", "block_deadline")
    op.drop_column("exam_sessions", "current_block")
