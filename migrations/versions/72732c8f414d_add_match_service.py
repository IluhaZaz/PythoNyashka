"""add match service

Revision ID: 72732c8f414d
Revises: f3c4d5e6f7a8
Create Date: 2026-11-15 22:46:20.365807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '72732c8f414d'
down_revision: Union[str, Sequence[str], None] = 'f3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем схему для матчей
    op.execute("CREATE SCHEMA IF NOT EXISTS match")

    # Создаем таблицу матчей
    op.create_table(
        'matches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('initiator_profile_id', sa.String(length=36), nullable=False),
        sa.Column('target_profile_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='noResponse'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='match'
    )
    op.create_index(op.f('ix_match_matches_initiator_profile_id'), 'matches', ['initiator_profile_id'], unique=False, schema='match')
    op.create_index(op.f('ix_match_matches_target_profile_id'), 'matches', ['target_profile_id'], unique=False, schema='match')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_match_matches_target_profile_id'), table_name='matches', schema='match')
    op.drop_index(op.f('ix_match_matches_initiator_profile_id'), table_name='matches', schema='match')
    op.drop_table('matches', schema='match')
    op.execute("DROP SCHEMA IF EXISTS match CASCADE")