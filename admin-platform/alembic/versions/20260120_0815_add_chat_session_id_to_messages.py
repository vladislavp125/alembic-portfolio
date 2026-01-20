"""Add chat_session_id to chat_messages for proper session tracking.

This migration adds chat_session_id field to link messages to UI chat sessions,
separate from sdk_session_id which is stored in session_id field.

Revision ID: add_chat_session_id_messages
Revises: add_tz_questions_changelog
Create Date: 2026-01-20 08:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_chat_session_id_messages'
down_revision = 'add_tz_questions_changelog'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add chat_session_id column to chat_messages
    with op.batch_alter_table('chat_messages', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('chat_session_id', sa.String(length=255), nullable=True)
        )
        batch_op.create_index(
            'ix_chat_messages_chat_session_id',
            ['chat_session_id'],
            unique=False
        )
        batch_op.create_index(
            'ix_chat_project_chat_session',
            ['project', 'chat_session_id'],
            unique=False
        )

    # Populate chat_session_id from chat_session_mappings where possible
    # This migrates existing data by looking up the mapping
    op.execute("""
        UPDATE chat_messages
        SET chat_session_id = (
            SELECT chat_session_mappings.chat_session_id
            FROM chat_session_mappings
            WHERE chat_session_mappings.sdk_session_id = chat_messages.session_id
              AND chat_session_mappings.project = chat_messages.project
            LIMIT 1
        )
        WHERE chat_session_id IS NULL
    """)


def downgrade() -> None:
    with op.batch_alter_table('chat_messages', schema=None) as batch_op:
        batch_op.drop_index('ix_chat_project_chat_session')
        batch_op.drop_index('ix_chat_messages_chat_session_id')
        batch_op.drop_column('chat_session_id')
