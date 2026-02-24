"""Добавить поле telegram_username в pending_deals + сделать phone nullable.

Поддержка авторизации по Telegram username как альтернативы телефону.
Поле CRM_USERNAME_FIELD из контакта CRM.

Revision ID: 005_telegram_username
Revises: 004_contact_name
Create Date: 2026-02-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_telegram_username"
down_revision: Union[str, None] = "004_contact_name"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавить столбец telegram_username
    op.add_column(
        "pending_deals",
        sa.Column("telegram_username", sa.String(128), nullable=True),
    )
    op.create_index(
        "idx_pending_deals_username",
        "pending_deals",
        ["telegram_username"],
    )

    # Сделать phone nullable (теперь pending_deal может быть только с username)
    op.alter_column(
        "pending_deals",
        "phone",
        existing_type=sa.String(32),
        nullable=True,
    )


def downgrade() -> None:
    # Восстановить NOT NULL для phone (заполним пустые значения)
    op.execute("UPDATE pending_deals SET phone = '' WHERE phone IS NULL")
    op.alter_column(
        "pending_deals",
        "phone",
        existing_type=sa.String(32),
        nullable=False,
    )

    op.drop_index("idx_pending_deals_username", table_name="pending_deals")
    op.drop_column("pending_deals", "telegram_username")
