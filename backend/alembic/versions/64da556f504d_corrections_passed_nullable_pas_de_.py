"""corrections.passed nullable : pas de verdict isolé pour le Schreiben telc

Revision ID: 64da556f504d
Revises: 34b4e8f67693
Create Date: 2026-11-21 16:50:44.177349


corrections.passed nullable : pas de verdict isolé pour le Schreiben telc

telc B1/B2 : le Schreiben n'a pas de réussite propre, seule la partie écrite
entière (Lesen + Sprachbausteine + Hören + Schreiben >= 135/225) en a une.
Goethe et ÖSD gardent leur `passed` (Goethe et ÖSD B1 sont modulaires : 60 %
par module est la vraie règle).

Revision ID: corrections_passed_nullable
Revises: <REMPLACER_PAR_LA_DERNIERE_REVISION>
"""
from alembic import op
import sqlalchemy as sa

revision = '64da556f504d'
down_revision = '34b4e8f67693'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("corrections", "passed", existing_type=sa.Boolean(), nullable=True)
    # Les anciennes corrections telc portaient un verdict à 27/45 qui n'existe pas à l'examen
    op.execute("UPDATE corrections SET passed = NULL WHERE provider = 'telc'")


def downgrade() -> None:
    op.execute(
        "UPDATE corrections SET passed = (overall_score * 100 >= max_score * 60) "
        "WHERE passed IS NULL"
    )
    op.alter_column("corrections", "passed", existing_type=sa.Boolean(), nullable=False)