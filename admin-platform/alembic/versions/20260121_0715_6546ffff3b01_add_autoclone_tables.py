"""add_autoclone_tables

Revision ID: 6546ffff3b01
Revises: add_chat_session_id_messages
Create Date: 2026-01-21 07:15:01.040252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6546ffff3b01'
down_revision: Union[str, None] = 'add_chat_session_id_messages'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('auto_clone_analysis_cache',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('project_name', sa.String(length=255), nullable=False),
    sa.Column('project_path', sa.String(length=500), nullable=False),
    sa.Column('framework', sa.Text(), nullable=True),
    sa.Column('database', sa.Text(), nullable=True),
    sa.Column('routes', sa.Text(), nullable=True),
    sa.Column('tests', sa.Text(), nullable=True),
    sa.Column('security', sa.Text(), nullable=True),
    sa.Column('ci', sa.Text(), nullable=True),
    sa.Column('analyzed_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('auto_clone_analysis_cache', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_auto_clone_analysis_cache_project_name'), ['project_name'], unique=True)

    op.create_table('auto_clone_tasks',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('project_name', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=True),
    sa.Column('phase', sa.String(length=30), nullable=True),
    sa.Column('progress', sa.Integer(), nullable=True),
    sa.Column('implementation_plan', sa.Text(), nullable=True),
    sa.Column('qa_report', sa.Text(), nullable=True),
    sa.Column('worktree_path', sa.String(length=500), nullable=True),
    sa.Column('branch_name', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('auto_clone_tasks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_auto_clone_tasks_project_name'), ['project_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_auto_clone_tasks_status'), ['status'], unique=False)
        batch_op.create_index('ix_autoclone_task_project_status', ['project_name', 'status'], unique=False)

    op.create_table('auto_clone_sessions',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('subtask_id', sa.String(length=64), nullable=True),
    sa.Column('agent_type', sa.String(length=30), nullable=False),
    sa.Column('sdk_session_id', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('logs', sa.Text(), nullable=True),
    sa.Column('insights', sa.Text(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('commits_made', sa.Integer(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['auto_clone_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('auto_clone_sessions', schema=None) as batch_op:
        batch_op.create_index('ix_autoclone_session_task', ['task_id'], unique=False)

    op.create_table('auto_clone_subtasks',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('phase_number', sa.Integer(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('attempt_count', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('commit_before', sa.String(length=64), nullable=True),
    sa.Column('commit_after', sa.String(length=64), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['auto_clone_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('auto_clone_subtasks', schema=None) as batch_op:
        batch_op.create_index('ix_autoclone_subtask_task_status', ['task_id', 'status'], unique=False)

    with op.batch_alter_table('project_changelog', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_changelog_created_at'), ['created_at'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('project_changelog', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_changelog_created_at'))

    with op.batch_alter_table('auto_clone_subtasks', schema=None) as batch_op:
        batch_op.drop_index('ix_autoclone_subtask_task_status')

    op.drop_table('auto_clone_subtasks')
    with op.batch_alter_table('auto_clone_sessions', schema=None) as batch_op:
        batch_op.drop_index('ix_autoclone_session_task')

    op.drop_table('auto_clone_sessions')
    with op.batch_alter_table('auto_clone_tasks', schema=None) as batch_op:
        batch_op.drop_index('ix_autoclone_task_project_status')
        batch_op.drop_index(batch_op.f('ix_auto_clone_tasks_status'))
        batch_op.drop_index(batch_op.f('ix_auto_clone_tasks_project_name'))

    op.drop_table('auto_clone_tasks')
    with op.batch_alter_table('auto_clone_analysis_cache', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_auto_clone_analysis_cache_project_name'))

    op.drop_table('auto_clone_analysis_cache')
