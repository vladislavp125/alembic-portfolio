"""Add ChatSessionMapping and IdempotencyKey tables

Revision ID: da6a7c81317a
Revises: 002
Create Date: 2026-01-20 06:52:05.995864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da6a7c81317a'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('attachments',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('session_id', sa.String(length=255), nullable=True),
    sa.Column('original_filename', sa.String(length=255), nullable=False),
    sa.Column('stored_path', sa.String(length=512), nullable=False),
    sa.Column('file_type', sa.String(length=20), nullable=False),
    sa.Column('mime_type', sa.String(length=100), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('base64_data', sa.Text(), nullable=True),
    sa.Column('extracted_text', sa.Text(), nullable=True),
    sa.Column('extraction_status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('attachments', schema=None) as batch_op:
        batch_op.create_index('ix_attachment_session', ['session_id'], unique=False)
        batch_op.create_index('ix_attachment_sha256', ['sha256'], unique=False)
        batch_op.create_index(batch_op.f('ix_attachments_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_attachments_session_id'), ['session_id'], unique=False)

    op.create_table('chat_session_mappings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('project', sa.String(length=255), nullable=False),
    sa.Column('chat_session_id', sa.String(length=255), nullable=False),
    sa.Column('sdk_session_id', sa.String(length=255), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('chat_session_mappings', schema=None) as batch_op:
        batch_op.create_index('ix_chat_mapping_project', ['project'], unique=False)
        batch_op.create_index('uq_chat_mapping', ['project', 'chat_session_id'], unique=True)

    op.create_table('idempotency_keys',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('request_id', sa.String(length=64), nullable=False),
    sa.Column('project', sa.String(length=255), nullable=False),
    sa.Column('chat_session_id', sa.String(length=255), nullable=False),
    sa.Column('message_hash', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('result_summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('idempotency_keys', schema=None) as batch_op:
        batch_op.create_index('ix_idem_expires', ['expires_at'], unique=False)
        batch_op.create_index('ix_idem_key_lookup', ['project', 'chat_session_id', 'request_id'], unique=True)

    with op.batch_alter_table('chat_messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attachment_id', sa.String(length=36), nullable=True))
        batch_op.create_index(batch_op.f('ix_chat_messages_attachment_id'), ['attachment_id'], unique=False)

    with op.batch_alter_table('ai_sdk_sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ai_sdk_sessions_chat_session_id'), ['chat_session_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('ai_sdk_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ai_sdk_sessions_chat_session_id'))

    with op.batch_alter_table('chat_messages', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chat_messages_attachment_id'))
        batch_op.drop_column('attachment_id')

    with op.batch_alter_table('idempotency_keys', schema=None) as batch_op:
        batch_op.drop_index('ix_idem_key_lookup')
        batch_op.drop_index('ix_idem_expires')

    op.drop_table('idempotency_keys')
    with op.batch_alter_table('chat_session_mappings', schema=None) as batch_op:
        batch_op.drop_index('uq_chat_mapping')
        batch_op.drop_index('ix_chat_mapping_project')

    op.drop_table('chat_session_mappings')
    with op.batch_alter_table('attachments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_attachments_session_id'))
        batch_op.drop_index(batch_op.f('ix_attachments_created_at'))
        batch_op.drop_index('ix_attachment_sha256')
        batch_op.drop_index('ix_attachment_session')

    op.drop_table('attachments')
