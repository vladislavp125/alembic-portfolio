"""Начальная схема БД: 7 таблиц + индексы + триггер updated_at.

Revision ID: 001_initial
Revises: None
Create Date: 2026-02-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Триггерная функция auto-update updated_at ---
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # --- 1. conversations ---
    op.create_table(
        "conversations",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(64), nullable=False, unique=True),
        sa.Column("platform", sa.String(16), nullable=False, server_default="telegram"),
        sa.Column("sender_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("contact_phone", sa.String(32), nullable=True),
        sa.Column("contact_username", sa.String(128), nullable=True),
        sa.Column("ai_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("crm_deal_id", sa.String(64), nullable=True),
        sa.Column("crm_contact_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("platform IN ('telegram', 'vk')", name="ck_conversations_platform"),
        sa.CheckConstraint(
            "status IN ('active', 'paused', 'closed', 'transferred_to_manager')",
            name="ck_conversations_status",
        ),
    )
    op.create_index("idx_conversations_crm_deal", "conversations", ["crm_deal_id"],
                     postgresql_where=sa.text("crm_deal_id IS NOT NULL"))
    op.create_index("idx_conversations_status", "conversations", ["status"])

    op.execute("""
        CREATE TRIGGER trg_conversations_updated_at
        BEFORE UPDATE ON conversations
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # --- 2. messages ---
    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(64), sa.ForeignKey("conversations.chat_id", ondelete="CASCADE"), nullable=False),
        sa.Column("messenger_message_id", sa.String(255), nullable=True),
        sa.Column("direction", sa.String(16), nullable=False),
        sa.Column("body", sa.Text, nullable=False, server_default=""),
        sa.Column("message_type", sa.String(32), nullable=False, server_default="text"),
        sa.Column("ai_generated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("synced_to_crm", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("direction IN ('incoming', 'outgoing')", name="ck_messages_direction"),
    )
    op.create_index("idx_messages_chat_id_created", "messages", ["chat_id", "created_at"])
    op.create_index(
        "idx_messages_messenger_id", "messages", ["messenger_message_id"],
        unique=True, postgresql_where=sa.text("messenger_message_id IS NOT NULL"),
    )
    op.create_index(
        "idx_messages_not_synced", "messages", ["synced_to_crm"],
        postgresql_where=sa.text("synced_to_crm = FALSE"),
    )

    # --- 3. client_qualification ---
    op.create_table(
        "client_qualification",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(64), sa.ForeignKey("conversations.chat_id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("child_name", sa.String(255), nullable=True),
        sa.Column("child_age", sa.SmallInteger, nullable=True),
        sa.Column("child_birthdate", sa.Date, nullable=True),
        sa.Column("preferred_shift", sa.String(64), nullable=True),
        sa.Column("parent_name", sa.String(255), nullable=True),
        sa.Column("parent_phone", sa.String(32), nullable=True),
        sa.Column("qualification_complete", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.execute("""
        CREATE TRIGGER trg_client_qualification_updated_at
        BEFORE UPDATE ON client_qualification
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # --- 4. contract_data ---
    op.create_table(
        "contract_data",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(64), sa.ForeignKey("conversations.chat_id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("parent_full_name", sa.String(512), nullable=True),
        sa.Column("passport_series", sa.String(8), nullable=True),
        sa.Column("passport_number", sa.String(16), nullable=True),
        sa.Column("passport_issued_by", sa.Text, nullable=True),
        sa.Column("registration_address", sa.Text, nullable=True),
        sa.Column("parent_birthdate", sa.Date, nullable=True),
        sa.Column("child_full_name", sa.String(512), nullable=True),
        sa.Column("child_birthdate", sa.Date, nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("data_complete", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.execute("""
        CREATE TRIGGER trg_contract_data_updated_at
        BEFORE UPDATE ON contract_data
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # --- 5. knowledge_base ---
    op.create_table(
        "knowledge_base",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("section_key", sa.String(128), nullable=False, unique=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by", sa.String(255), nullable=True),
    )
    op.create_index(
        "idx_kb_active_sorted", "knowledge_base", ["sort_order"],
        postgresql_where=sa.text("is_active = TRUE"),
    )

    op.execute("""
        CREATE TRIGGER trg_knowledge_base_updated_at
        BEFORE UPDATE ON knowledge_base
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # --- 6. processed_messages ---
    op.create_table(
        "processed_messages",
        sa.Column("messenger_message_id", sa.String(255), primary_key=True),
        sa.Column("chat_id", sa.String(64), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- 7. ai_logs ---
    op.create_table(
        "ai_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("chat_id", sa.String(64), nullable=False),
        sa.Column("user_message", sa.Text, nullable=False, server_default=""),
        sa.Column("ai_response", sa.Text, nullable=False, server_default=""),
        sa.Column("model_used", sa.String(64), nullable=False, server_default=""),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("prompt_tokens", sa.Integer, nullable=True),
        sa.Column("completion_tokens", sa.Integer, nullable=True),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_ai_logs_chat_id", "ai_logs", ["chat_id"])
    op.create_index("idx_ai_logs_created", "ai_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("ai_logs")
    op.drop_table("processed_messages")
    op.drop_table("knowledge_base")
    op.drop_table("contract_data")
    op.drop_table("client_qualification")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
