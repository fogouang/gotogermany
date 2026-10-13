"""user whatsapp opt-in

Revision ID: a3f9c2d17b40
Revises: e7699e608558
Create Date: 2026-10-13 10:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "a3f9c2d17b40"
down_revision = "e7699e608558"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("whatsapp_opt_in", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("whatsapp_opt_in_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "whatsapp_opt_in_at")
    op.drop_column("users", "whatsapp_opt_in")