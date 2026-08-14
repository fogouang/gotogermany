"""add teacher to user_role enum

Revision ID: 0ff0e6d65f3b
Revises: b86a641a154e
Create Date: 2026-08-14 06:21:35.538038
"""
from alembic import op
import sqlalchemy as sa


revision = '0ff0e6d65f3b'
down_revision = 'b86a641a154e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'teacher'")


def downgrade() -> None:
    # Postgres ne permet pas de retirer une valeur d'un enum nativement
    # (pas de DROP VALUE) — downgrade volontairement omis.
    pass