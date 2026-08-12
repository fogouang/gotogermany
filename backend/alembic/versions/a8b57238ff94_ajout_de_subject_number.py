"""Ajout de subject_number

Revision ID: a8b57238ff94
Revises: cda9bc853c66
Create Date: 2026-08-11

subject_number ajouté nullable d'abord, backfill à 1 pour les lignes
existantes, puis contrainte NOT NULL + unique(level, subject_number).
"""
from alembic import op
import sqlalchemy as sa

revision = 'a8b57238ff94'
down_revision = 'cda9bc853c66'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('start_deutsch_subjects', sa.Column('subject_number', sa.Integer(), nullable=True))
    op.execute("UPDATE start_deutsch_subjects SET subject_number = 1 WHERE subject_number IS NULL")
    op.alter_column('start_deutsch_subjects', 'subject_number', nullable=False)
    op.create_unique_constraint('uq_sd_subject_level_number', 'start_deutsch_subjects', ['level', 'subject_number'])


def downgrade() -> None:
    op.drop_constraint('uq_sd_subject_level_number', 'start_deutsch_subjects', type_='unique')
    op.drop_column('start_deutsch_subjects', 'subject_number')