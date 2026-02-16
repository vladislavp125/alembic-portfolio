"""Добавление поля is_bot_allowed для авторизации чатов.

AI должен отвечать только тем чатам, где мы инициировали контакт первыми
(через CRM автоматизацию). Новое поле is_bot_allowed (default false)
отделено от ai_enabled (ручной тумблер менеджера).

Revision ID: 002_is_bot_allowed
Revises: 001_initial
Create Date: 2026-02-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_is_bot_allowed"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку is_bot_allowed (по умолчанию False — чат не авторизован)
    op.add_column(
        "conversations",
        sa.Column("is_bot_allowed", sa.Boolean, nullable=False, server_default="false"),
    )

    # Backfill: существующие диалоги с привязкой к сделке уже авторизованы
    op.execute(
        "UPDATE conversations SET is_bot_allowed = true WHERE crm_deal_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column("conversations", "is_bot_allowed")
