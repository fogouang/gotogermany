"""plans track popular

Revision ID: 34b4e8f67693
Revises: 7a1fa6502626
Create Date: 2026-11-17 02:01:28.637618
"""
from alembic import op
import sqlalchemy as sa


revision = '34b4e8f67693'
down_revision = '7a1fa6502626'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "plans",
        sa.Column("track", sa.String(20), nullable=False, server_default="standard"),
    )
    op.add_column(
        "plans",
        sa.Column("is_popular", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_plans_track", "plans", ["track"])


def downgrade() -> None:
    op.drop_index("ix_plans_track", table_name="plans")
    op.drop_column("plans", "is_popular")
    op.drop_column("plans", "track")