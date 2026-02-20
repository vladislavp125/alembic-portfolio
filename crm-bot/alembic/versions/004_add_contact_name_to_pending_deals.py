"""Добавить поле contact_name в pending_deals.

Хранит ФИО родителя из CRM (CRM_CONTACT_NAME_FIELD)
для передачи в conversation при авторизации чата.

Revision ID: 004_contact_name
Revises: 003_pending_deals
Create Date: 2026-02-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_contact_name"
down_revision: Union[str, None] = "003_pending_deals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "pending_deals",
        sa.Column("contact_name", sa.String(255), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("pending_deals", "contact_name")
