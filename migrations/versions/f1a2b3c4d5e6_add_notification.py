"""Add notification storage.

Revision ID: f1a2b3c4d5e6
Revises: 8afe0f4f0539
"""

import sqlalchemy as sa
from alembic import op

revision = "f1a2b3c4d5e6"
down_revision = "8afe0f4f0539"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA notification")
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("profile_id", sa.String(length=36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="notification",
    )
    op.create_index(
        "ix_notifications_profile_created_at_id",
        "notifications",
        ["profile_id", "created_at", "id"],
        unique=False,
        schema="notification",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notifications_profile_created_at_id",
        table_name="notifications",
        schema="notification",
    )
    op.drop_table("notifications", schema="notification")
    op.execute("DROP SCHEMA notification")
