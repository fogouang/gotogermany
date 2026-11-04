"""paiement par carte (Stripe) : prix en euros des formules, montant débité et référence Stripe

Revision ID: e5b2c7a91f30
Revises: 43cf41528310
Create Date: 2026-11-04
"""
import sqlalchemy as sa
from alembic import op

revision = '7a1fa6502626'
down_revision = '43cf41528310'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Prix en euros d'une formule payée par carte (vide = pas payable par carte)
    op.add_column("plans", sa.Column("price_eur", sa.Numeric(10, 2), nullable=True))

    # Paiement par carte : montant réellement débité (centimes) et devise,
    # référence chez le prestataire (id de session Stripe)
    op.add_column("payments", sa.Column("charged_amount", sa.Integer(), nullable=True))
    op.add_column("payments", sa.Column("charged_currency", sa.String(3), nullable=True))
    op.add_column("payments", sa.Column("provider_ref", sa.String(255), nullable=True))
    op.create_index("ix_payments_provider_ref", "payments", ["provider_ref"])


def downgrade() -> None:
    op.drop_index("ix_payments_provider_ref", table_name="payments")
    op.drop_column("payments", "provider_ref")
    op.drop_column("payments", "charged_currency")
    op.drop_column("payments", "charged_amount")
    op.drop_column("plans", "price_eur")