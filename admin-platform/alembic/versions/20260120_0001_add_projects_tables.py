"""Add projects tables for project creation v3

Revision ID: add_projects_tables
Revises: da6a7c81317a
Create Date: 2026-01-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_projects_tables'
down_revision: Union[str, None] = 'da6a7c81317a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_path', sa.String(length=500), nullable=False, server_default='/root'),
        sa.Column('directory', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('project_type', sa.String(length=20), nullable=True),
        sa.Column('has_git', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('has_config_md', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('has_readme', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('has_mcp_config', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('setup_chat_session_id', sa.String(length=255), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('idempotency_key', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_name', 'projects', ['name'], unique=True)
    op.create_index('ix_projects_status', 'projects', ['status'], unique=False)
    op.create_index('ix_projects_idempotency_key', 'projects', ['idempotency_key'], unique=True)
    op.create_index('ix_project_status_deleted', 'projects', ['status', 'deleted_at'], unique=False)

    # Project MCP Servers table
    op.create_table(
        'project_mcp_servers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('command', sa.String(length=500), nullable=True),
        sa.Column('args', sa.Text(), nullable=True),
        sa.Column('env_vars', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_mcp_project_name', 'project_mcp_servers', ['project_id', 'name'], unique=False)

    # Project Setup Tasks table
    op.create_table(
        'project_setup_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=30), nullable=False),
        sa.Column('task_data', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('progress', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_setup_task_project_status', 'project_setup_tasks', ['project_id', 'status'], unique=False)

    # Project Audit Logs table
    op.create_table(
        'project_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_project', 'project_audit_logs', ['project_id'], unique=False)
    op.create_index('ix_audit_action', 'project_audit_logs', ['action'], unique=False)
    op.create_index('ix_audit_created', 'project_audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_audit_created', table_name='project_audit_logs')
    op.drop_index('ix_audit_action', table_name='project_audit_logs')
    op.drop_index('ix_audit_project', table_name='project_audit_logs')
    op.drop_table('project_audit_logs')

    op.drop_index('ix_setup_task_project_status', table_name='project_setup_tasks')
    op.drop_table('project_setup_tasks')

    op.drop_index('ix_mcp_project_name', table_name='project_mcp_servers')
    op.drop_table('project_mcp_servers')

    op.drop_index('ix_project_status_deleted', table_name='projects')
    op.drop_index('ix_projects_idempotency_key', table_name='projects')
    op.drop_index('ix_projects_status', table_name='projects')
    op.drop_index('ix_projects_name', table_name='projects')
    op.drop_table('projects')
