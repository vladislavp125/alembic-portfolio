"""Таблица pending_deals для связки deal → chatId.

При создании сделки (ON_CRM_DEAL_ADD) сохраняем phone → deal_id.
При получении outgoing_message_status от Messenger связываем chatId → deal.

Revision ID: 003_pending_deals
Revises: 002_is_bot_allowed
Create Date: 2026-02-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_pending_deals"
down_revision: Union[str, None] = "002_is_bot_allowed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pending_deals",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("phone", sa.String(32), nullable=False, index=True),
        sa.Column("deal_id", sa.String(64), nullable=False, unique=True),
        sa.Column(
            "preferred_messenger",
            sa.String(16),
            nullable=False,
            server_default="telegram",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("pending_deals")
