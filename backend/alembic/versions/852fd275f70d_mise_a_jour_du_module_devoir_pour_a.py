"""Start Deutsch : sujets privés et devoirs A1/A2

Revision ID: a7c3d91e5f20
Revises: <REMPLACER par la sortie de `alembic heads`>
Create Date: 2026-10-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '852fd275f70d'
down_revision = '4bc1b958dd00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sujets Start Deutsch : public par défaut
    op.add_column(
        "start_deutsch_subjects",
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # Devoir : soit un sujet B1/B2, soit un sujet Start Deutsch
    op.add_column(
        "assignments",
        sa.Column("sd_subject_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_assignments_sd_subject_id",
        "assignments", "start_deutsch_subjects",
        ["sd_subject_id"], ["id"], ondelete="RESTRICT",
    )
    op.create_index("ix_assignments_sd_subject_id", "assignments", ["sd_subject_id"])
    op.alter_column("assignments", "subject_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.create_check_constraint(
        "ck_assignment_one_subject",
        "assignments",
        "(subject_id IS NOT NULL) <> (sd_subject_id IS NOT NULL)",
    )

    # Copie d'un devoir Start Deutsch
    op.add_column(
        "assignment_submissions",
        sa.Column("sd_session_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_assignment_submissions_sd_session_id",
        "assignment_submissions", "start_deutsch_sessions",
        ["sd_session_id"], ["id"], ondelete="SET NULL",
    )
    op.create_index("ix_assignment_submissions_sd_session_id", "assignment_submissions", ["sd_session_id"])


def downgrade() -> None:
    op.drop_index("ix_assignment_submissions_sd_session_id", table_name="assignment_submissions")
    op.drop_constraint("fk_assignment_submissions_sd_session_id", "assignment_submissions", type_="foreignkey")
    op.drop_column("assignment_submissions", "sd_session_id")

    # Les devoirs Start Deutsch n'ont pas de place dans l'ancien schéma
    op.execute("DELETE FROM assignments WHERE sd_subject_id IS NOT NULL")
    op.drop_constraint("ck_assignment_one_subject", "assignments", type_="check")
    op.alter_column("assignments", "subject_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    op.drop_index("ix_assignments_sd_subject_id", table_name="assignments")
    op.drop_constraint("fk_assignments_sd_subject_id", "assignments", type_="foreignkey")
    op.drop_column("assignments", "sd_subject_id")

    op.drop_column("start_deutsch_subjects", "is_private")