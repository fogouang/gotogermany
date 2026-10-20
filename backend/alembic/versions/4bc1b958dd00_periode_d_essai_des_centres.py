"""periode d essai des centres

Revision ID: 4bc1b958dd00
Revises: 7d38caa5e1e7
Create Date: 2026-10-20 02:03:37.233333
"""
from alembic import op
import sqlalchemy as sa


revision = '4bc1b958dd00'
down_revision = '7d38caa5e1e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("centers", sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "centers",
        sa.Column("trial_activations_left", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "partner_sales",
        sa.Column("is_trial", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("partner_sales", "is_trial")
    op.drop_column("centers", "trial_activations_left")
    op.drop_column("centers", "trial_ends_at")