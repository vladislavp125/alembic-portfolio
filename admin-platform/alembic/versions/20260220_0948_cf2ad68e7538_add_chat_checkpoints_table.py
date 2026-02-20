"""add chat_checkpoints table

Revision ID: cf2ad68e7538
Revises: 8d6ab9ab755f
Create Date: 2026-02-20 09:48:20.426752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf2ad68e7538'
down_revision: Union[str, None] = '8d6ab9ab755f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('chat_checkpoints',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('chat_session_id', sa.String(length=255), nullable=False),
    sa.Column('project_name', sa.String(length=255), nullable=False),
    sa.Column('turn_number', sa.Integer(), nullable=False),
    sa.Column('git_commit_hash', sa.String(length=40), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('files_changed', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('chat_checkpoints', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_chat_checkpoints_chat_session_id'), ['chat_session_id'], unique=False)
        batch_op.create_index('ix_checkpoint_session', ['chat_session_id', 'turn_number'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('chat_checkpoints', schema=None) as batch_op:
        batch_op.drop_index('ix_checkpoint_session')
        batch_op.drop_index(batch_op.f('ix_chat_checkpoints_chat_session_id'))
    op.drop_table('chat_checkpoints')
