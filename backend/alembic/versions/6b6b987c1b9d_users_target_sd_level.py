"""users target_sd_level

Niveau Start Deutsch de l'élève ("A1", "A2"), à côté de target_level_id.
"""
from alembic import op
import sqlalchemy as sa

revision = '6b6b987c1b9d'
down_revision = 'ae69dd07c08f'
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    if not _has_column("users", "target_sd_level"):
        op.add_column("users", sa.Column("target_sd_level", sa.String(length=5), nullable=True))


def downgrade() -> None:
    if _has_column("users", "target_sd_level"):
        op.execute(
            "UPDATE users SET learning_track = 'exam' "
            "WHERE target_sd_level IS NOT NULL AND branch_id IS NOT NULL"
        )
        op.drop_column("users", "target_sd_level")