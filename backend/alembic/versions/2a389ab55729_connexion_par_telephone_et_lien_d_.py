"""connexion par telephone et lien d inscription des centres

Revision ID: 2a389ab55729
Revises: 112ee8a3200c
Create Date: 2026-10-19 03:59:47.651686
"""
from alembic import op
import sqlalchemy as sa


revision = '2a389ab55729'
down_revision = '112ee8a3200c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Les telephones vides deviennent NULL (sinon l'index unique bloque)
    op.execute(
        "UPDATE users SET phone = NULL "
        "WHERE phone IS NOT NULL AND btrim(phone) = ''"
    )

    # 2. On s'arrete proprement s'il reste des doublons
    conn = op.get_bind()
    duplicates = conn.execute(
        sa.text(
            "SELECT phone, COUNT(*) AS n FROM users "
            "WHERE phone IS NOT NULL GROUP BY phone HAVING COUNT(*) > 1"
        )
    ).fetchall()
    if duplicates:
        listing = ", ".join(f"{row.phone} ({row.n})" for row in duplicates)
        raise RuntimeError(
            f"Numeros de telephone en double, a corriger avant la migration : {listing}"
        )

    # 3. Unicite du telephone (seulement quand il est renseigne)
    op.create_index(
        "uq_users_phone",
        "users",
        ["phone"],
        unique=True,
        postgresql_where=sa.text("phone IS NOT NULL"),
    )

    # 4. Demande de rattachement a une succursale
    op.add_column(
        "users",
        sa.Column("requested_branch_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_requested_branch_id_branches",
        "users",
        "branches",
        ["requested_branch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_users_requested_branch_id", "users", ["requested_branch_id"]
    )
    op.add_column(
        "users",
        sa.Column("join_requested_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 5. Lien d'inscription du centre
    op.add_column(
        "centers",
        sa.Column("join_token", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "uq_centers_join_token", "centers", ["join_token"], unique=True
    )
    op.add_column(
        "centers",
        sa.Column(
            "join_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("centers", "join_enabled")
    op.drop_index("uq_centers_join_token", table_name="centers")
    op.drop_column("centers", "join_token")

    op.drop_column("users", "join_requested_at")
    op.drop_index("ix_users_requested_branch_id", table_name="users")
    op.drop_constraint(
        "fk_users_requested_branch_id_branches", "users", type_="foreignkey"
    )
    op.drop_column("users", "requested_branch_id")

    op.drop_index("uq_users_phone", table_name="users")