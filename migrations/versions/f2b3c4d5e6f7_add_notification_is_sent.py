"""Add notification email sent status.

Revision ID: f2b3c4d5e6f7
Revises: f1a2b3c4d5e6
"""

import sqlalchemy as sa
from alembic import op

revision = "f2b3c4d5e6f7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("is_sent", sa.Boolean(), server_default=sa.false(), nullable=False),
        schema="notification",
    )


def downgrade() -> None:
    op.drop_column("notifications", "is_sent", schema="notification")
