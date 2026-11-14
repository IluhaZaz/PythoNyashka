"""Add chat storage.

Revision ID: f3c4d5e6f7a8
Revises: f2b3c4d5e6f7
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "f3c4d5e6f7a8"
down_revision = "f2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA chat")
    op.create_table(
        "chats",
        sa.Column("id", sa.String(36), primary_key=True),
        schema="chat",
    )
    op.create_table(
        "chat_members",
        sa.Column("chat_id", sa.String(36), primary_key=True),
        sa.Column("profile_id", sa.String(36), primary_key=True),
        sa.ForeignKeyConstraint(["chat_id"], ["chat.chats.id"], ondelete="CASCADE"),
        schema="chat",
    )
    op.create_index(
        "ix_chat_members_profile_id_chat_id",
        "chat_members",
        ["profile_id", "chat_id"],
        schema="chat",
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("chat_id", sa.String(36), nullable=False),
        sa.Column("sender_id", sa.String(36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("media", JSONB(), nullable=False),
        sa.Column(
            "sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chat_id", "sender_id"],
            ["chat.chat_members.chat_id", "chat.chat_members.profile_id"],
            ondelete="CASCADE",
        ),
        schema="chat",
    )
    op.create_index(
        "ix_messages_chat_id_sent_at_id",
        "messages",
        ["chat_id", "sent_at", "id"],
        schema="chat",
    )


def downgrade() -> None:
    op.drop_table("messages", schema="chat")
    op.drop_table("chat_members", schema="chat")
    op.drop_table("chats", schema="chat")
    op.execute("DROP SCHEMA chat")
