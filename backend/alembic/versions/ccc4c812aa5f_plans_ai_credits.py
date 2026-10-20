"""plans ai_credits

Revision ID: ccc4c812aa5f
Revises: 2a389ab55729
Create Date: 2026-10-19 21:24:16.535907
"""
from alembic import op
import sqlalchemy as sa


revision = 'ccc4c812aa5f'
down_revision = '2a389ab55729'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "plans",
        sa.Column("ai_credits", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("plans", "ai_credits")