"""add_project_files_table

Revision ID: 42b384165355
Revises: 45bd47336fca
Create Date: 2026-02-02 08:38:59.214159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42b384165355'
down_revision: Union[str, None] = '45bd47336fca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create project_files table for multiple file uploads
    op.create_table('project_files',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('attachment_id', sa.String(length=36), nullable=False),
        sa.Column('category', sa.String(length=30), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('include_in_context', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['attachment_id'], ['attachments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('project_files', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_files_project_id'), ['project_id'], unique=False)
        batch_op.create_index('ix_project_files_project_order', ['project_id', 'display_order'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('project_files', schema=None) as batch_op:
        batch_op.drop_index('ix_project_files_project_order')
        batch_op.drop_index(batch_op.f('ix_project_files_project_id'))

    op.drop_table('project_files')
