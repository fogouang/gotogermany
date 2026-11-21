"""add teacher to user_role enum

Revision ID: 0ff0e6d65f3b
Revises: b86a641a154e
Create Date: 2026-08-14 06:21:35.538038
"corrections.passed + simulator_results.passed nullable : pas de verdict isolé pour le Schreiben telc

telc B1/B2 : le Schreiben n'a pas de réussite propre, seule la partie écrite
entière (Lesen + Sprachbausteine + Hören + Schreiben >= 135/225) en a une.
Goethe et ÖSD gardent leur `passed` (Goethe et ÖSD B1 sont modulaires : 60 %
par module est la vraie règle).

Revision ID: corrections_passed_nullable
Revises: <REMPLACER_PAR_LA_DERNIERE_REVISION>
"""
from alembic import op
import sqlalchemy as sa

revision = '0ff0e6d65f3b'
down_revision = 'b86a641a154e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("corrections", "passed", existing_type=sa.Boolean(), nullable=True)
    op.alter_column("simulator_results", "passed", existing_type=sa.Boolean(), nullable=True)

    # Les anciens résultats telc portaient un verdict à 27/45 qui n'existe pas à l'examen
    op.execute("UPDATE corrections SET passed = NULL WHERE lower(provider) = 'telc'")
    op.execute(
        "UPDATE simulator_results "
        "SET passed = NULL, result_data = result_data || '{\"passed\": null}'::jsonb "
        "WHERE lower(provider) = 'telc'"
    )


def downgrade() -> None:
    for table in ("corrections", "simulator_results"):
        op.execute(
            f"UPDATE {table} SET passed = (overall_score * 100 >= max_score * 60) "
            "WHERE passed IS NULL"
        )
    op.alter_column("simulator_results", "passed", existing_type=sa.Boolean(), nullable=False)
    op.alter_column("corrections", "passed", existing_type=sa.Boolean(), nullable=False)