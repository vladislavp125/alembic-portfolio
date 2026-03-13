"""add_users_and_rbac_models

Revision ID: aedf5250e588
Revises: 6546ffff3b01
Create Date: 2026-01-25 08:53:57.855900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aedf5250e588'
down_revision: Union[str, None] = '6546ffff3b01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('codebase_map',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('last_analyzed', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('codebase_map', schema=None) as batch_op:
        batch_op.create_index('uq_codebase_map', ['project', 'file_path'], unique=True)

    op.create_table('project_gotchas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(length=255), nullable=False),
    sa.Column('gotcha_text', sa.Text(), nullable=False),
    sa.Column('severity', sa.String(length=20), nullable=True),
    sa.Column('source_session', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('project_gotchas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_gotchas_project'), ['project'], unique=False)

    op.create_table('project_patterns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(length=255), nullable=False),
    sa.Column('pattern_text', sa.Text(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('source_session', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('project_patterns', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_patterns_project'), ['project'], unique=False)

    op.create_table('session_insights',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(length=255), nullable=False),
    sa.Column('chat_session_id', sa.String(length=255), nullable=False),
    sa.Column('session_number', sa.Integer(), nullable=True),
    sa.Column('subtasks_completed', sa.Text(), nullable=True),
    sa.Column('discoveries', sa.Text(), nullable=True),
    sa.Column('what_worked', sa.Text(), nullable=True),
    sa.Column('what_failed', sa.Text(), nullable=True),
    sa.Column('recommendations', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('session_insights', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_session_insights_chat_session_id'), ['chat_session_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_session_insights_project'), ['project'], unique=False)
        batch_op.create_index('ix_session_insights_project_session', ['project', 'chat_session_id'], unique=False)

    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index('ix_user_role_status', ['role', 'status'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('project_assignments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('can_view_metrics', sa.Boolean(), nullable=True),
    sa.Column('can_manage_containers', sa.Boolean(), nullable=True),
    sa.Column('can_view_logs', sa.Boolean(), nullable=True),
    sa.Column('can_use_ai', sa.Boolean(), nullable=True),
    sa.Column('assigned_at', sa.DateTime(), nullable=True),
    sa.Column('assigned_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('project_assignments', schema=None) as batch_op:
        batch_op.create_index('uq_user_project', ['user_id', 'project_id'], unique=True)

    op.create_table('worker_tasks',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('project_name', sa.String(length=255), nullable=False),
    sa.Column('assignee_id', sa.Integer(), nullable=True),
    sa.Column('assignment_type', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=True),
    sa.Column('priority', sa.String(length=20), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True),
    sa.Column('time_in_progress_seconds', sa.Integer(), nullable=True),
    sa.Column('chat_session_id', sa.String(length=255), nullable=True),
    sa.Column('ai_messages_count', sa.Integer(), nullable=True),
    sa.Column('review_notes', sa.Text(), nullable=True),
    sa.Column('reviewed_by', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('worker_tasks', schema=None) as batch_op:
        batch_op.create_index('ix_worker_task_assignee', ['assignee_id'], unique=False)
        batch_op.create_index('ix_worker_task_project', ['project_name'], unique=False)
        batch_op.create_index('ix_worker_task_status_priority', ['status', 'priority'], unique=False)
        batch_op.create_index(batch_op.f('ix_worker_tasks_chat_session_id'), ['chat_session_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_worker_tasks_project_name'), ['project_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_worker_tasks_status'), ['status'], unique=False)

    op.create_table('notifications',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('recipient_id', sa.Integer(), nullable=False),
    sa.Column('notification_type', sa.String(length=30), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('task_id', sa.String(length=64), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('read_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.create_index('ix_notification_recipient_unread', ['recipient_id', 'is_read'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_is_read'), ['is_read'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_recipient_id'), ['recipient_id'], unique=False)

    op.create_table('task_status_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('from_status', sa.String(length=30), nullable=True),
    sa.Column('to_status', sa.String(length=30), nullable=False),
    sa.Column('changed_by', sa.Integer(), nullable=False),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('task_status_history', schema=None) as batch_op:
        batch_op.create_index('ix_status_history_task_created', ['task_id', 'created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_task_status_history_created_at'), ['created_at'], unique=False)

    op.create_table('worker_task_comments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('comment_type', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('worker_task_metrics',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('time_pending', sa.Integer(), nullable=True),
    sa.Column('time_in_progress', sa.Integer(), nullable=True),
    sa.Column('time_under_review', sa.Integer(), nullable=True),
    sa.Column('ai_messages_count', sa.Integer(), nullable=True),
    sa.Column('ai_tokens_input', sa.Integer(), nullable=True),
    sa.Column('ai_tokens_output', sa.Integer(), nullable=True),
    sa.Column('ai_sessions_count', sa.Integer(), nullable=True),
    sa.Column('rejection_count', sa.Integer(), nullable=True),
    sa.Column('pause_count', sa.Integer(), nullable=True),
    sa.Column('total_elapsed_time', sa.Integer(), nullable=True),
    sa.Column('efficiency_score', sa.Float(), nullable=True),
    sa.Column('last_activity_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id')
    )


def downgrade() -> None:
    op.drop_table('worker_task_metrics')
    op.drop_table('worker_task_comments')
    with op.batch_alter_table('task_status_history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_status_history_created_at'))
        batch_op.drop_index('ix_status_history_task_created')

    op.drop_table('task_status_history')
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notifications_recipient_id'))
        batch_op.drop_index(batch_op.f('ix_notifications_is_read'))
        batch_op.drop_index(batch_op.f('ix_notifications_created_at'))
        batch_op.drop_index('ix_notification_recipient_unread')

    op.drop_table('notifications')
    with op.batch_alter_table('worker_tasks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_worker_tasks_status'))
        batch_op.drop_index(batch_op.f('ix_worker_tasks_project_name'))
        batch_op.drop_index(batch_op.f('ix_worker_tasks_chat_session_id'))
        batch_op.drop_index('ix_worker_task_status_priority')
        batch_op.drop_index('ix_worker_task_project')
        batch_op.drop_index('ix_worker_task_assignee')

    op.drop_table('worker_tasks')
    with op.batch_alter_table('project_assignments', schema=None) as batch_op:
        batch_op.drop_index('uq_user_project')

    op.drop_table('project_assignments')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.drop_index('ix_user_role_status')

    op.drop_table('users')
    with op.batch_alter_table('session_insights', schema=None) as batch_op:
        batch_op.drop_index('ix_session_insights_project_session')
        batch_op.drop_index(batch_op.f('ix_session_insights_project'))
        batch_op.drop_index(batch_op.f('ix_session_insights_chat_session_id'))

    op.drop_table('session_insights')
    with op.batch_alter_table('project_patterns', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_patterns_project'))

    op.drop_table('project_patterns')
    with op.batch_alter_table('project_gotchas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_gotchas_project'))

    op.drop_table('project_gotchas')
    with op.batch_alter_table('codebase_map', schema=None) as batch_op:
        batch_op.drop_index('uq_codebase_map')

    op.drop_table('codebase_map')
