"""add_multi_agent_pipeline_models

Revision ID: 400c10f07d19
Revises: add_task_tracking_tables
Create Date: 2026-01-25 14:13:48.970283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '400c10f07d19'
down_revision: Union[str, None] = 'add_task_tracking_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create task_plans table
    op.create_table('task_plans',
        sa.Column('id', sa.String(64), nullable=False),
        sa.Column('task_id', sa.String(64), nullable=False),
        sa.Column('feature', sa.String(500), nullable=True),
        sa.Column('workflow_type', sa.String(50), nullable=True),
        sa.Column('status', sa.String(30), nullable=True),
        sa.Column('agent_sequence', sa.JSON(), nullable=True),
        sa.Column('current_phase_index', sa.Integer(), nullable=True),
        sa.Column('current_agent', sa.String(50), nullable=True),
        sa.Column('require_human_review', sa.Boolean(), nullable=True),
        sa.Column('plan_json_path', sa.String(500), nullable=True),
        sa.Column('created_by_agent', sa.String(50), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], name='fk_task_plans_task_id'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='fk_task_plans_user_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_plan_task_status', 'task_plans', ['task_id', 'status'], unique=False)

    # Create task_phases table
    op.create_table('task_phases',
        sa.Column('id', sa.String(64), nullable=False),
        sa.Column('plan_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('agent', sa.String(50), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(30), nullable=True),
        sa.Column('output_summary', sa.Text(), nullable=True),
        sa.Column('output_json', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_comment', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['task_plans.id'], name='fk_task_phases_plan_id'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], name='fk_task_phases_reviewer_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_phase_plan_order', 'task_phases', ['plan_id', 'order_index'], unique=False)

    # Create task_subtasks table
    op.create_table('task_subtasks',
        sa.Column('id', sa.String(64), nullable=False),
        sa.Column('phase_id', sa.String(64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('assigned_agent', sa.String(50), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(30), nullable=True),
        sa.Column('output', sa.JSON(), nullable=True),
        sa.Column('files_modified', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['phase_id'], ['task_phases.id'], name='fk_task_subtasks_phase_id'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_subtask_phase_order', 'task_subtasks', ['phase_id', 'order_index'], unique=False)

    # Make agent_task_logs.session_id nullable
    with op.batch_alter_table('agent_task_logs', schema=None) as batch_op:
        batch_op.alter_column('session_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)


def downgrade() -> None:
    # Drop task_subtasks
    op.drop_index('ix_task_subtask_phase_order', table_name='task_subtasks')
    op.drop_table('task_subtasks')

    # Drop task_phases
    op.drop_index('ix_task_phase_plan_order', table_name='task_phases')
    op.drop_table('task_phases')

    # Drop task_plans
    op.drop_index('ix_task_plan_task_status', table_name='task_plans')
    op.drop_table('task_plans')

    # Revert agent_task_logs.session_id to non-nullable
    with op.batch_alter_table('agent_task_logs', schema=None) as batch_op:
        batch_op.alter_column('session_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
