"""mise a jour avec referals

Revision ID: a02875690227
Revises: 12c907c04f8f
Create Date: 2026-07-17 00:32:15.123857
"""
from alembic import op
import sqlalchemy as sa


revision = 'a02875690227'
down_revision = '12c907c04f8f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('payments', sa.Column('validated_manually_by', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'payments', 'users', ['validated_manually_by'], ['id'], ondelete='SET NULL')

    op.add_column('users', sa.Column('is_ambassador', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('users', sa.Column('referred_by_user_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_users_referred_by_user_id'), 'users', ['referred_by_user_id'], unique=False)
    op.create_foreign_key(None, 'users', 'users', ['referred_by_user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_referred_by_user_id'), table_name='users')
    op.drop_column('users', 'referred_by_user_id')
    op.drop_column('users', 'is_ambassador')
    op.drop_constraint(None, 'payments', type_='foreignkey')
    op.drop_column('payments', 'validated_manually_by')