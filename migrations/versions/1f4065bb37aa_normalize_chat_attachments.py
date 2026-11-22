"""Normalize chat attachments and index current avatars."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "1f4065bb37aa"
down_revision: str = "72732c8f414d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Prevent writes to the old column between the backfill and its removal.
    op.execute("LOCK TABLE chat.messages IN ACCESS EXCLUSIVE MODE")
    op.create_table(
        "message_attachments",
        sa.Column("message_id", sa.String(36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("media_id", sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["chat.messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("message_id", "position"),
        schema="chat",
    )
    op.execute("""
        INSERT INTO chat.message_attachments (message_id, position, media_id)
        SELECT message.id, attachment.ordinality - 1, attachment.media_id
        FROM chat.messages AS message
        CROSS JOIN LATERAL jsonb_array_elements_text(message.media)
            WITH ORDINALITY AS attachment(media_id, ordinality)
    """)
    op.create_index(
        "ix_message_attachments_media_id", "message_attachments", ["media_id"], schema="chat",
    )
    op.create_index("ix_profile_profiles_avatar_id", "profiles", ["avatar_id"], schema="profile")
    op.drop_column("messages", "media", schema="chat")


def downgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("media", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        schema="chat",
    )
    op.execute("""
        UPDATE chat.messages AS message
        SET media = attachments.media
        FROM (
            SELECT message_id, jsonb_agg(media_id ORDER BY position) AS media
            FROM chat.message_attachments
            GROUP BY message_id
        ) AS attachments
        WHERE message.id = attachments.message_id
    """)
    op.alter_column("messages", "media", server_default=None, schema="chat")
    op.drop_index("ix_profile_profiles_avatar_id", table_name="profiles", schema="profile")
    op.drop_table("message_attachments", schema="chat")
