"""Initial schema for Admin Platform

Revision ID: 001
Revises:
Create Date: 2026-01-13

This migration creates the initial database schema matching the existing models.
Run this on a fresh database or use --sql to generate SQL for manual review.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_lists table
    op.create_table(
        'task_lists',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_lists_project', 'task_lists', ['project'], unique=False)
    op.create_index('ix_task_lists_session_id', 'task_lists', ['session_id'], unique=False)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_list_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True, default=0),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('priority', sa.String(length=20), nullable=True, default='medium'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_list_id'], ['task_lists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_comments table
    op.create_table(
        'task_comments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author', sa.String(length=100), nullable=True, default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create claude_jobs table
    op.create_table(
        'claude_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.String(length=64), nullable=False),
        sa.Column('project', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True, default='sonnet'),
        sa.Column('mode', sa.String(length=50), nullable=True, default='ask'),
        sa.Column('status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('output_file', sa.String(length=500), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('pid', sa.Integer(), nullable=True),
        sa.Column('lines_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )
    op.create_index('ix_claude_jobs_job_id', 'claude_jobs', ['job_id'], unique=True)
    op.create_index('ix_claude_jobs_project', 'claude_jobs', ['project'], unique=False)

    # Create ai_sdk_sessions table
    op.create_table(
        'ai_sdk_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project', sa.String(length=255), nullable=False),
        sa.Column('sdk_session_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_sdk_sessions_project', 'ai_sdk_sessions', ['project'], unique=False)
    op.create_index('ix_sdk_session_project_active', 'ai_sdk_sessions', ['project', 'is_active'], unique=False)

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('project', sa.String(length=255), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('msg_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'], unique=False)
    op.create_index('ix_chat_messages_project', 'chat_messages', ['project'], unique=False)
    op.create_index('ix_chat_messages_created_at', 'chat_messages', ['created_at'], unique=False)
    op.create_index('ix_chat_session_seq', 'chat_messages', ['session_id', 'seq'], unique=False)
    op.create_index('ix_chat_project_session', 'chat_messages', ['project', 'session_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('chat_messages')
    op.drop_table('ai_sdk_sessions')
    op.drop_table('claude_jobs')
    op.drop_table('task_comments')
    op.drop_table('tasks')
    op.drop_table('task_lists')
