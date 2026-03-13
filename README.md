# Alembic Migrations Portfolio

Real-world database migration examples from production FastAPI + PostgreSQL / SQLite projects.
Demonstrates schema evolution, best practices, and advanced PostgreSQL features.

## Projects

### 1. CRM Bot (`crm-bot/`)

**Stack:** FastAPI, PostgreSQL 15, Alembic, SQLAlchemy
**Domain:** CRM integration + messenger bot for sales funnel automation
**Migrations:** 5 (incremental schema evolution over 2 weeks)

**Highlights:**
- PL/pgSQL trigger function for auto-updating `updated_at` timestamps
- Partial indexes with `postgresql_where` for selective indexing
- CHECK constraints for enum-like validation (platform, status, direction)
- CASCADE foreign keys with `ondelete="CASCADE"`
- Data backfill in migration (`UPDATE ... SET ... WHERE`)
- `ALTER COLUMN` to change nullability with safe downgrade

**Schema overview:**
- `conversations` — chat sessions with CRM deal linkage
- `messages` — incoming/outgoing messages with deduplication index
- `client_qualification` — lead qualification data
- `contract_data` — contract information
- `knowledge_base` — AI assistant knowledge articles
- `processed_messages` — idempotency table
- `ai_logs` — AI response tracking with token metrics
- `pending_deals` — CRM deal-to-chat matching queue

---

### 2. Admin Platform (`admin-platform/`)

**Stack:** FastAPI, SQLite (WAL mode), Alembic, SQLAlchemy
**Domain:** Web-based admin panel with RBAC, task management, AI agent orchestration
**Migrations:** 18 (6 weeks of active development)

**Highlights:**
- `batch_alter_table` throughout for SQLite compatibility
- Type conversion: `TEXT` -> `JSON` via `alter_column`
- Composite unique indexes for many-to-many relationships
- Multi-table migrations (up to 10 tables in single migration)
- Named foreign key constraints via `batch_alter_table`
- Temporary table cleanup (`_alembic_tmp_*`)
- Auto-generated + hand-tuned migrations (hybrid approach)
- Session mapping with idempotency keys and TTL

**Schema overview (50+ tables across 18 migrations):**
- Task management: `task_lists`, `tasks`, `task_comments`
- Chat system: `chat_messages`, `chat_session_mappings`, `chat_checkpoints`
- User & RBAC: `users`, `project_assignments`, `notifications`
- Worker tasks: `worker_tasks`, `worker_task_comments`, `worker_task_metrics`, `task_status_history`
- AI sessions: `ai_sdk_sessions`, `ai_assistant_sessions`
- Agent system: `agent_tasks`, `agent_chat_logs`, `agent_chat_sessions`, `agent_task_groups`
- Multi-agent pipeline: `task_plans`, `task_phases`, `task_subtasks`
- Project management: `projects`, `project_mcp_servers`, `project_setup_tasks`, `project_audit_logs`
- Attachments: `attachments`, `task_attachments`, `project_files`
- Idempotency: `idempotency_keys` (with TTL-based expiry)

---

## Migration Patterns Used

### Data Definition
- `op.create_table()` with full constraint specification
- `op.add_column()` / `op.drop_column()`
- `op.alter_column()` with type conversion and nullability changes
- `op.create_index()` including unique, composite, and partial indexes

### PostgreSQL-Specific (crm-bot)
- `op.execute()` for PL/pgSQL trigger functions
- `CREATE TRIGGER ... BEFORE UPDATE ... FOR EACH ROW`
- Partial indexes: `postgresql_where=sa.text("column IS NOT NULL")`
- `sa.CheckConstraint` for enum validation

### SQLite-Compatible (admin-platform)
- `op.batch_alter_table()` for all ALTER operations
- `batch_op.create_index()` / `batch_op.alter_column()`
- `batch_op.create_foreign_key()` with explicit names

### Data Migrations
- Backfill queries: `op.execute("UPDATE ... SET ... WHERE ...")`
- Cross-table data migration with subqueries
- Safe downgrade with data restoration before constraint changes

### Best Practices
- Every migration has both `upgrade()` and `downgrade()`
- Indexes dropped before tables in downgrade
- Foreign key order respected (child tables dropped first)
- Server defaults for new non-nullable columns
- Idempotency patterns for message deduplication

---

## Running Migrations

```bash
# Each project is independent — navigate to its directory
cd crm-bot/    # or admin-platform/

# Apply all migrations
alembic upgrade head

# Check current version
alembic current

# Rollback one step
alembic downgrade -1

# View migration history
alembic history --verbose
```

## Tech Stack

| Component | crm-bot | admin-platform |
|-----------|---------|----------------|
| Python | 3.12 | 3.12 |
| Framework | FastAPI | FastAPI |
| ORM | SQLAlchemy 2.0 | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 | SQLite (WAL) |
| Migrations | Alembic | Alembic |
