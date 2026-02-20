"""add_agent_task_groups_and_group_id

Revision ID: 8d6ab9ab755f
Revises: 42b384165355
Create Date: 2026-02-20 09:13:20.200404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d6ab9ab755f'
down_revision: Union[str, None] = '42b384165355'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agent_task_groups table
    op.create_table('agent_task_groups',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=True),
    sa.Column('orchestrator_config', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_task_groups', schema=None) as batch_op:
        batch_op.create_index('ix_agent_group_project', ['project_id'], unique=False)
        batch_op.create_index('ix_agent_group_status', ['status'], unique=False)

    # Add group_id column to agent_tasks
    with op.batch_alter_table('agent_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('group_id', sa.String(length=64), nullable=True))
        batch_op.create_index('ix_agent_task_group', ['group_id'], unique=False)
        batch_op.create_foreign_key('fk_agent_task_group', 'agent_task_groups', ['group_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('agent_tasks', schema=None) as batch_op:
        batch_op.drop_constraint('fk_agent_task_group', type_='foreignkey')
        batch_op.drop_index('ix_agent_task_group')
        batch_op.drop_column('group_id')

    with op.batch_alter_table('agent_task_groups', schema=None) as batch_op:
        batch_op.drop_index('ix_agent_group_status')
        batch_op.drop_index('ix_agent_group_project')

    op.drop_table('agent_task_groups')
