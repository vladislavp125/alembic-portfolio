"""Add project specification, questions, and changelog tables.

Revision ID: add_tz_questions_changelog
Revises: 20260120_0001_add_projects_tables
Create Date: 2026-01-20 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tz_questions_changelog'
down_revision = 'add_projects_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create project_specifications table
    op.create_table(
        'project_specifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('attachment_id', sa.String(36), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('requirements_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['attachment_id'], ['attachments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id')
    )

    # 2. Create project_questions table
    op.create_table(
        'project_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('question_hash', sa.String(64), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending', nullable=True),
        sa.Column('chat_session_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_question_project_hash', 'project_questions',
                    ['project_id', 'question_hash'], unique=True)
    op.create_index('ix_question_project_status', 'project_questions',
                    ['project_id', 'status'], unique=False)

    # 3. Create project_changelog table
    op.create_table(
        'project_changelog',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('entry_type', sa.String(30), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('source', sa.String(50), server_default='claude', nullable=True),
        sa.Column('chat_session_id', sa.String(255), nullable=True),
        sa.Column('tool_use_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_changelog_project_created', 'project_changelog',
                    ['project_id', 'created_at'], unique=False)
    op.create_index('ix_changelog_project_type', 'project_changelog',
                    ['project_id', 'entry_type'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_changelog_project_type', table_name='project_changelog')
    op.drop_index('ix_changelog_project_created', table_name='project_changelog')
    op.drop_index('ix_question_project_status', table_name='project_questions')
    op.drop_index('ix_question_project_hash', table_name='project_questions')

    # Drop tables
    op.drop_table('project_changelog')
    op.drop_table('project_questions')
    op.drop_table('project_specifications')
