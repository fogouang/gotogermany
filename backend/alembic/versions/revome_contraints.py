"""add cascade delete on all FKs blocking Subject deletion

Revision ID: 3a1261c21230
Revises: 4fabcd4029ca
Create Date: 2026-08-01 00:00:00.000000

Corrige la suppression d'un Subject (ForeignKeyViolationError), bloquée par
trois contraintes sans CASCADE, repérées via une requête sur
information_schema :
  - exam_session_answers.question_id  (RESTRICT)
  - exam_sessions.subject_id          (RESTRICT)
  - sprechen_sessions.subject_id      (NO ACTION)

Toutes passent en ON DELETE CASCADE : supprimer un Subject supprime
désormais en cascade ses questions, ses exam_sessions (et leurs réponses),
et ses sprechen_sessions.
"""
from alembic import op

revision = "3a1261c21230"
down_revision = "4fabcd4029ca"
branch_labels = None
depends_on = None

# (constraint_name, referencing_table, local_column, target_table, target_column)
_FIXES = [
    (
        "exam_session_answers_question_id_fkey",
        "exam_session_answers",
        "question_id",
        "questions",
        "id",
    ),
    (
        "exam_sessions_subject_id_fkey",
        "exam_sessions",
        "subject_id",
        "subjects",
        "id",
    ),
    (
        "sprechen_sessions_subject_id_fkey",
        "sprechen_sessions",
        "subject_id",
        "subjects",
        "id",
    ),
]


def upgrade() -> None:
    for constraint, ref_table, local_col, target_table, target_col in _FIXES:
        op.drop_constraint(constraint, ref_table, type_="foreignkey")
        op.create_foreign_key(
            constraint,
            ref_table,
            target_table,
            [local_col],
            [target_col],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    # Restaure le comportement d'origine : RESTRICT pour les deux premières
    # (comportement par défaut Postgres, donc pas de ondelete explicite),
    # NO ACTION pour sprechen_sessions (idem, comportement par défaut).
    for constraint, ref_table, local_col, target_table, target_col in _FIXES:
        op.drop_constraint(constraint, ref_table, type_="foreignkey")
        op.create_foreign_key(
            constraint,
            ref_table,
            target_table,
            [local_col],
            [target_col],
        )