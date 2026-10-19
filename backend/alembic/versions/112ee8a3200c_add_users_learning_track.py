"""add users learning_track

Revision ID: 112ee8a3200c
Revises: 53123a2f3924
Create Date: 2026-10-18 15:55:25.248648
"""
from alembic import op
import sqlalchemy as sa


revision = '112ee8a3200c'
down_revision = '53123a2f3924'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("learning_track", sa.String(length=20), nullable=True),
    )
    # Comptes existants : un étudiant individuel qui a déjà un niveau
    # est sur le parcours examen, il ne doit plus revoir l'accueil.
    op.execute(
        """
        UPDATE users
        SET learning_track = 'exam'
        WHERE role = 'student'
          AND branch_id IS NULL
          AND target_level_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_column("users", "learning_track")