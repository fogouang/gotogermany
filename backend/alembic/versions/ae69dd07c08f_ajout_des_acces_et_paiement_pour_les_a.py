"""Start Deutsch payant : accès et paiements par niveau A1 / A2

Revision ID: c7d2a8e4f115
Revises: b4e1f6a2c903
Create Date: 2026-10-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'ae69dd07c08f'
down_revision = '85b0f4d53da9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── exam_access : un niveau d'examen OU un niveau Start Deutsch ──
    op.add_column("exam_access", sa.Column("sd_level", sa.String(length=5), nullable=True))
    op.create_index("ix_exam_access_sd_level", "exam_access", ["sd_level"])
    op.alter_column(
        "exam_access", "level_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True
    )
    op.create_unique_constraint(
        "uq_exam_access_user_sd_level", "exam_access", ["user_id", "sd_level"]
    )
    op.create_check_constraint(
        "ck_exam_access_one_level",
        "exam_access",
        "(level_id IS NOT NULL) <> (sd_level IS NOT NULL)",
    )

    # ── payments : niveau Start Deutsch acheté ──
    op.add_column("payments", sa.Column("sd_level", sa.String(length=5), nullable=True))
    op.create_index("ix_payments_sd_level", "payments", ["sd_level"])
    op.create_check_constraint(
        "ck_payment_one_level",
        "payments",
        "NOT (level_id IS NOT NULL AND sd_level IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_payment_one_level", "payments", type_="check")
    op.drop_index("ix_payments_sd_level", table_name="payments")
    op.drop_column("payments", "sd_level")

    # Les accès Start Deutsch n'ont pas de place dans l'ancien schéma
    op.execute("DELETE FROM exam_access WHERE sd_level IS NOT NULL")
    op.drop_constraint("ck_exam_access_one_level", "exam_access", type_="check")
    op.drop_constraint("uq_exam_access_user_sd_level", "exam_access", type_="unique")
    op.alter_column(
        "exam_access", "level_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False
    )
    op.drop_index("ix_exam_access_sd_level", table_name="exam_access")
    op.drop_column("exam_access", "sd_level")