"""add_task_tracking_tables

Add TaskAttachment, AI AssistantCodeSession, TaskTimeEntry tables
and tracking fields to WorkerTask for My Tasks / AI Code Assistant separation.

Revision ID: add_task_tracking_tables
Revises: add_agent_task_workflow
Create Date: 2026-01-25 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_task_tracking_tables'
down_revision: Union[str, None] = 'add_agent_task_workflow'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to worker_tasks for tracking separation
    with op.batch_alter_table('worker_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tracking_started_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('claude_started_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('total_tracking_time_seconds', sa.Integer(), nullable=True, default=0))
        batch_op.add_column(sa.Column('total_claude_time_seconds', sa.Integer(), nullable=True, default=0))

    # Create task_attachments table
    op.create_table('task_attachments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('attachment_id', sa.String(length=36), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=30), nullable=True, default='document'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('include_in_context', sa.Boolean(), nullable=True, default=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['attachment_id'], ['attachments.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('task_attachments', schema=None) as batch_op:
        batch_op.create_index('ix_task_attachment_task', ['task_id'], unique=False)
        batch_op.create_index('uq_task_attachment', ['task_id', 'attachment_id'], unique=True)

    # Create ai_assistant_sessions table
    op.create_table('ai_assistant_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('chat_session_id', sa.String(length=255), nullable=False),
        sa.Column('sdk_session_id', sa.String(length=255), nullable=True),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=20), nullable=True, default='sonnet'),
        sa.Column('initial_prompt', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True, default='active'),
        sa.Column('total_messages', sa.Integer(), nullable=True, default=0),
        sa.Column('total_input_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('total_output_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('total_response_time_ms', sa.Integer(), nullable=True, default=0),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('started_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
        sa.ForeignKeyConstraint(['started_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ai_assistant_sessions', schema=None) as batch_op:
        batch_op.create_index('ix_claude_session_task', ['task_id'], unique=False)
        batch_op.create_index('ix_claude_session_chat', ['chat_session_id'], unique=False)
        batch_op.create_index('ix_claude_session_status', ['status'], unique=False)

    # Create task_time_entries table
    op.create_table('task_time_entries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entry_type', sa.String(length=30), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True, default=0),
        sa.Column('claude_session_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['claude_session_id'], ['ai_assistant_sessions.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('task_time_entries', schema=None) as batch_op:
        batch_op.create_index('ix_time_entry_task', ['task_id'], unique=False)
        batch_op.create_index('ix_time_entry_task_type', ['task_id', 'entry_type'], unique=False)
        batch_op.create_index('ix_time_entry_user', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop task_time_entries table
    with op.batch_alter_table('task_time_entries', schema=None) as batch_op:
        batch_op.drop_index('ix_time_entry_user')
        batch_op.drop_index('ix_time_entry_task_type')
        batch_op.drop_index('ix_time_entry_task')
    op.drop_table('task_time_entries')

    # Drop ai_assistant_sessions table
    with op.batch_alter_table('ai_assistant_sessions', schema=None) as batch_op:
        batch_op.drop_index('ix_claude_session_status')
        batch_op.drop_index('ix_claude_session_chat')
        batch_op.drop_index('ix_claude_session_task')
    op.drop_table('ai_assistant_sessions')

    # Drop task_attachments table
    with op.batch_alter_table('task_attachments', schema=None) as batch_op:
        batch_op.drop_index('uq_task_attachment')
        batch_op.drop_index('ix_task_attachment_task')
    op.drop_table('task_attachments')

    # Remove columns from worker_tasks
    with op.batch_alter_table('worker_tasks', schema=None) as batch_op:
        batch_op.drop_column('total_claude_time_seconds')
        batch_op.drop_column('total_tracking_time_seconds')
        batch_op.drop_column('claude_started_at')
        batch_op.drop_column('tracking_started_at')
