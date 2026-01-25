"""add_agent_task_workflow

Revision ID: add_agent_task_workflow
Revises: 1554b237a1f1
Create Date: 2026-01-25 12:00:00.000000

Adds:
- New columns to worker_tasks for agent execution
- agent_task_sessions table
- agent_task_logs table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_agent_task_workflow'
down_revision: Union[str, None] = '1554b237a1f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add agent execution columns to worker_tasks
    with op.batch_alter_table('worker_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('agent_config', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('current_phase', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('implementation_plan', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('agent_progress', sa.Integer(), nullable=True, default=0))
        batch_op.add_column(sa.Column('agent_error', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('worktree_path', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('branch_name', sa.String(length=100), nullable=True))

    # Create agent_task_sessions table
    op.create_table('agent_task_sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('agent_type', sa.String(length=30), nullable=False),
        sa.Column('sdk_session_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('phase', sa.String(length=30), nullable=True),
        sa.Column('pending_approval_id', sa.String(length=64), nullable=True),
        sa.Column('pending_approval_tool', sa.String(length=100), nullable=True),
        sa.Column('pending_approval_input', sa.Text(), nullable=True),
        sa.Column('tokens_input', sa.Integer(), nullable=True, default=0),
        sa.Column('tokens_output', sa.Integer(), nullable=True, default=0),
        sa.Column('output_json', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_task_sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_agent_task_sessions_task_id'), ['task_id'], unique=False)
        batch_op.create_index('ix_agent_session_task_status', ['task_id', 'status'], unique=False)

    # Create agent_task_logs table
    op.create_table('agent_task_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('log_type', sa.String(length=30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['agent_task_sessions.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_task_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_agent_task_logs_task_id'), ['task_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_agent_task_logs_created_at'), ['created_at'], unique=False)
        batch_op.create_index('ix_agent_log_session_seq', ['session_id', 'seq'], unique=False)
        batch_op.create_index('ix_agent_log_task_created', ['task_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop agent_task_logs table
    with op.batch_alter_table('agent_task_logs', schema=None) as batch_op:
        batch_op.drop_index('ix_agent_log_task_created')
        batch_op.drop_index('ix_agent_log_session_seq')
        batch_op.drop_index(batch_op.f('ix_agent_task_logs_created_at'))
        batch_op.drop_index(batch_op.f('ix_agent_task_logs_task_id'))
    op.drop_table('agent_task_logs')

    # Drop agent_task_sessions table
    with op.batch_alter_table('agent_task_sessions', schema=None) as batch_op:
        batch_op.drop_index('ix_agent_session_task_status')
        batch_op.drop_index(batch_op.f('ix_agent_task_sessions_task_id'))
    op.drop_table('agent_task_sessions')

    # Remove agent execution columns from worker_tasks
    with op.batch_alter_table('worker_tasks', schema=None) as batch_op:
        batch_op.drop_column('branch_name')
        batch_op.drop_column('worktree_path')
        batch_op.drop_column('agent_error')
        batch_op.drop_column('agent_progress')
        batch_op.drop_column('implementation_plan')
        batch_op.drop_column('current_phase')
        batch_op.drop_column('agent_config')
