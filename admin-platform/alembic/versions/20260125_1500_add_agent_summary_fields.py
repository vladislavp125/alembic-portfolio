"""add_agent_summary_fields

Add agent_summary, agent_recommendations, agent_findings, summary_extracted_at
to WorkerTask and context_for_next_agent to AgentTaskSession.

Revision ID: add_agent_summary_fields
Revises: 400c10f07d19
Create Date: 2026-01-25 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_agent_summary_fields'
down_revision: Union[str, None] = '400c10f07d19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add agent summary fields to worker_tasks
    op.add_column('worker_tasks', sa.Column('agent_summary', sa.Text(), nullable=True))
    op.add_column('worker_tasks', sa.Column('agent_recommendations', sa.JSON(), nullable=True))
    op.add_column('worker_tasks', sa.Column('agent_findings', sa.JSON(), nullable=True))
    op.add_column('worker_tasks', sa.Column('summary_extracted_at', sa.DateTime(), nullable=True))

    # Add context_for_next_agent to agent_task_sessions
    op.add_column('agent_task_sessions', sa.Column('context_for_next_agent', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove context_for_next_agent from agent_task_sessions
    op.drop_column('agent_task_sessions', 'context_for_next_agent')

    # Remove agent summary fields from worker_tasks
    op.drop_column('worker_tasks', 'summary_extracted_at')
    op.drop_column('worker_tasks', 'agent_findings')
    op.drop_column('worker_tasks', 'agent_recommendations')
    op.drop_column('worker_tasks', 'agent_summary')
