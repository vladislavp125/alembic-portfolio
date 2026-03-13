# Alembic Migrations Portfolio

Примеры реальных миграций баз данных из продакшн-проектов на FastAPI + PostgreSQL.
Демонстрирует эволюцию схемы, лучшие практики и продвинутые возможности PostgreSQL.

## Проект

### CRM Bot (`crm-bot/`)

**Стек:** Python 3.12, FastAPI, PostgreSQL 15, Alembic, SQLAlchemy 2.0
**Домен:** CRM-интеграция + мессенджер-бот для автоматизации воронки продаж
**Миграций:** 5 (инкрементальная эволюция схемы за 2 недели)

**Ключевые особенности:**
- PL/pgSQL триггерная функция для автообновления `updated_at`
- Partial indexes с `postgresql_where` для выборочной индексации
- CHECK constraints для enum-подобной валидации (platform, status, direction)
- CASCADE foreign keys с `ondelete="CASCADE"`
- Data backfill внутри миграции (`UPDATE ... SET ... WHERE`)
- `ALTER COLUMN` для изменения nullability с безопасным downgrade

**Обзор схемы (8 таблиц):**
- `conversations` — чат-сессии с привязкой к CRM-сделкам
- `messages` — входящие/исходящие сообщения с индексом дедупликации
- `client_qualification` — данные квалификации лидов
- `contract_data` — информация по договорам
- `knowledge_base` — статьи базы знаний AI-ассистента
- `processed_messages` — таблица идемпотентности
- `ai_logs` — логи AI-ответов с метриками токенов
- `pending_deals` — очередь сопоставления CRM-сделок с чатами

---

## Использованные паттерны миграций

### Определение структуры (DDL)
- `op.create_table()` с полным описанием constraints
- `op.add_column()` / `op.drop_column()`
- `op.alter_column()` с изменением типа и nullability
- `op.create_index()` — уникальные, составные и partial индексы

### PostgreSQL-специфичные возможности
- `op.execute()` для PL/pgSQL триггерных функций
- `CREATE TRIGGER ... BEFORE UPDATE ... FOR EACH ROW`
- Partial indexes: `postgresql_where=sa.text("column IS NOT NULL")`
- `sa.CheckConstraint` для валидации допустимых значений

### Миграции данных
- Backfill-запросы: `op.execute("UPDATE ... SET ... WHERE ...")`
- Безопасный downgrade с восстановлением данных перед изменением constraints

### Лучшие практики
- Каждая миграция содержит `upgrade()` и `downgrade()`
- Индексы удаляются до таблиц при откате
- Соблюдён порядок FK (дочерние таблицы удаляются первыми)
- Server defaults для новых NOT NULL колонок
- Паттерны идемпотентности для дедупликации сообщений

---

## Запуск миграций

```bash
cd crm-bot/

# Применить все миграции
alembic upgrade head

# Текущая версия
alembic current

# Откатить на шаг назад
alembic downgrade -1

# Посмотреть историю миграций
alembic history --verbose
```

## Стек технологий

| Компонент | Версия |
|-----------|--------|
| Python | 3.12 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| БД | PostgreSQL 15 |
| Миграции | Alembic |
