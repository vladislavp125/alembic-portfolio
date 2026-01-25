"""add_user_task_messages

Revision ID: 1554b237a1f1
Revises: aedf5250e588
Create Date: 2026-01-25 09:27:59.211177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1554b237a1f1'
down_revision: Union[str, None] = 'aedf5250e588'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_task_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.String(length=64), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('message_content', sa.Text(), nullable=False),
    sa.Column('message_hash', sa.String(length=64), nullable=True),
    sa.Column('chat_session_id', sa.String(length=255), nullable=True),
    sa.Column('sdk_session_id', sa.String(length=255), nullable=True),
    sa.Column('model', sa.String(length=20), nullable=True),
    sa.Column('input_tokens', sa.Integer(), nullable=True),
    sa.Column('output_tokens', sa.Integer(), nullable=True),
    sa.Column('response_time_ms', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['worker_tasks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user_task_messages', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_task_messages_chat_session_id'), ['chat_session_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_task_messages_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_task_messages_task_id'), ['task_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_task_messages_user_id'), ['user_id'], unique=False)
        batch_op.create_index('ix_user_task_msg_model', ['model'], unique=False)
        batch_op.create_index('ix_user_task_msg_task_created', ['task_id', 'created_at'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('user_task_messages', schema=None) as batch_op:
        batch_op.drop_index('ix_user_task_msg_task_created')
        batch_op.drop_index('ix_user_task_msg_model')
        batch_op.drop_index(batch_op.f('ix_user_task_messages_user_id'))
        batch_op.drop_index(batch_op.f('ix_user_task_messages_task_id'))
        batch_op.drop_index(batch_op.f('ix_user_task_messages_created_at'))
        batch_op.drop_index(batch_op.f('ix_user_task_messages_chat_session_id'))

    op.drop_table('user_task_messages')
