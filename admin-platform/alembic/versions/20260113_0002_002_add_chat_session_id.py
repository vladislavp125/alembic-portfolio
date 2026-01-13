"""Add chat_session_id to ai_sdk_sessions

Revision ID: 002
Revises: 001
Create Date: 2026-01-13

This migration adds chat_session_id column to ai_sdk_sessions table
for linking SDK sessions to internal chat sessions, enabling resume functionality.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add chat_session_id column to ai_sdk_sessions
    op.add_column(
        'ai_sdk_sessions',
        sa.Column('chat_session_id', sa.String(length=255), nullable=True)
    )
    # Create index for faster lookups by chat_session_id
    op.create_index(
        'ix_sdk_session_chat',
        'ai_sdk_sessions',
        ['chat_session_id'],
        unique=False
    )


def downgrade() -> None:
    # Remove index first
    op.drop_index('ix_sdk_session_chat', table_name='ai_sdk_sessions')
    # Remove column
    op.drop_column('ai_sdk_sessions', 'chat_session_id')
