"""add_execution_mode_and_questions

Add execution_mode, agent_questions and awaiting_questions_response
to WorkerTask for session restore and agent-developer communication.

Revision ID: add_execution_mode_and_questions
Revises: add_agent_summary_fields
Create Date: 2026-01-25 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_execution_mode_and_questions'
down_revision: Union[str, None] = 'add_agent_summary_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add execution_mode for session restore (PLAN, ASK, AUTO)
    op.add_column('worker_tasks', sa.Column('execution_mode', sa.String(10), server_default='AUTO', nullable=True))

    # Add agent_questions for agent-developer communication
    # Format: [{id: str, question: str, answered: bool, answer: str | null, asked_at: str, answered_at: str | null}]
    op.add_column('worker_tasks', sa.Column('agent_questions', sa.JSON(), nullable=True))

    # Add flag to indicate agent is waiting for developer answers
    op.add_column('worker_tasks', sa.Column('awaiting_questions_response', sa.Boolean(), server_default='false', nullable=True))


def downgrade() -> None:
    op.drop_column('worker_tasks', 'awaiting_questions_response')
    op.drop_column('worker_tasks', 'agent_questions')
    op.drop_column('worker_tasks', 'execution_mode')
