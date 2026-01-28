"""add_agent_tasks_tables

Revision ID: 45bd47336fca
Revises: add_execution_mode_and_questions
Create Date: 2026-01-28 16:27:21.137278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45bd47336fca'
down_revision: Union[str, None] = 'add_execution_mode_and_questions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('agent_tasks',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('initial_prompt', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=True),
    sa.Column('progress', sa.Integer(), nullable=True),
    sa.Column('phase', sa.String(length=50), nullable=True),
    sa.Column('agent_config', sa.String(length=50), nullable=True),
    sa.Column('model', sa.String(length=20), nullable=True),
    sa.Column('execution_mode', sa.String(length=20), nullable=True),
    sa.Column('chat_session_id', sa.String(length=255), nullable=True),
    sa.Column('sdk_session_id', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('last_activity_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('assigned_to', sa.Integer(), nullable=True),
    sa.Column('worker_task_id', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['worker_task_id'], ['worker_tasks.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('chat_session_id')
    )
    with op.batch_alter_table('agent_tasks', schema=None) as batch_op:
        batch_op.create_index('ix_agent_task_activity', ['last_activity_at'], unique=False)
        batch_op.create_index('ix_agent_task_chat_session', ['chat_session_id'], unique=False)
        batch_op.create_index('ix_agent_task_project', ['project_id'], unique=False)
        batch_op.create_index('ix_agent_task_status', ['status'], unique=False)

    op.create_table('agent_chat_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('sequence_num', sa.Integer(), nullable=False),
    sa.Column('log_type', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('extra_metadata', sa.Text(), nullable=True),
    sa.Column('source', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['agent_tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_chat_logs', schema=None) as batch_op:
        batch_op.create_index('ix_agent_chat_log_created', ['created_at'], unique=False)
        batch_op.create_index('ix_agent_chat_log_task_seq', ['task_id', 'sequence_num'], unique=False)
        batch_op.create_index('ix_agent_chat_log_type', ['log_type'], unique=False)

    op.create_table('agent_chat_sessions',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('sdk_session_id', sa.String(length=255), nullable=True),
    sa.Column('agent_type', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('input_tokens', sa.Integer(), nullable=True),
    sa.Column('output_tokens', sa.Integer(), nullable=True),
    sa.Column('thinking_tokens', sa.Integer(), nullable=True),
    sa.Column('total_cost_usd', sa.Float(), nullable=True),
    sa.Column('messages_count', sa.Integer(), nullable=True),
    sa.Column('tools_used', sa.Integer(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['agent_tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_chat_sessions', schema=None) as batch_op:
        batch_op.create_index('ix_agent_chat_session_started', ['started_at'], unique=False)
        batch_op.create_index('ix_agent_chat_session_task', ['task_id'], unique=False)

    op.drop_table('_alembic_tmp_agent_task_logs')
    with op.batch_alter_table('agent_task_logs', schema=None) as batch_op:
        batch_op.alter_column('session_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)

    with op.batch_alter_table('ai_assistant_sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ai_assistant_sessions_chat_session_id'), ['chat_session_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_ai_assistant_sessions_task_id'), ['task_id'], unique=False)

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.TEXT(),
               type_=sa.JSON(),
               existing_nullable=True)
        batch_op.create_foreign_key('fk_notifications_project_id', 'projects', ['project_id'], ['id'])

    with op.batch_alter_table('task_attachments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_attachments_task_id'), ['task_id'], unique=False)

    with op.batch_alter_table('task_time_entries', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_time_entries_task_id'), ['task_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('task_time_entries', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_time_entries_task_id'))

    with op.batch_alter_table('task_attachments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_attachments_task_id'))

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('data',
               existing_type=sa.JSON(),
               type_=sa.TEXT(),
               existing_nullable=True)

    with op.batch_alter_table('ai_assistant_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ai_assistant_sessions_task_id'))
        batch_op.drop_index(batch_op.f('ix_ai_assistant_sessions_chat_session_id'))

    with op.batch_alter_table('agent_task_logs', schema=None) as batch_op:
        batch_op.alter_column('session_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)

    op.create_table('_alembic_tmp_agent_task_logs',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('session_id', sa.VARCHAR(length=64), nullable=True),
    sa.Column('task_id', sa.VARCHAR(length=64), nullable=False),
    sa.Column('seq', sa.INTEGER(), nullable=False),
    sa.Column('log_type', sa.VARCHAR(length=30), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['agent_task_sessions.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_chat_sessions', schema=None) as batch_op:
        batch_op.drop_index('ix_agent_chat_session_task')
        batch_op.drop_index('ix_agent_chat_session_started')

    op.drop_table('agent_chat_sessions')
    with op.batch_alter_table('agent_chat_logs', schema=None) as batch_op:
        batch_op.drop_index('ix_agent_chat_log_type')
        batch_op.drop_index('ix_agent_chat_log_task_seq')
        batch_op.drop_index('ix_agent_chat_log_created')

    op.drop_table('agent_chat_logs')
    with op.batch_alter_table('agent_tasks', schema=None) as batch_op:
        batch_op.drop_index('ix_agent_task_status')
        batch_op.drop_index('ix_agent_task_project')
        batch_op.drop_index('ix_agent_task_chat_session')
        batch_op.drop_index('ix_agent_task_activity')

    op.drop_table('agent_tasks')
