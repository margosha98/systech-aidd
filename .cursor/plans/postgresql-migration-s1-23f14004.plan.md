<!-- 23f14004-a754-401f-8446-2f8887f63eae 07e49dc8-03cd-4865-8c00-97bd88aee142 -->
# Миграция на PostgreSQL (Спринт S1)

## Цель

Мигрировать с SQLite на PostgreSQL, добавить soft delete и метаданные сообщений (дата создания, длина контента).

## Технические решения

✅ **СУБД** — PostgreSQL (в Docker контейнере)  
✅ **Python драйвер** — asyncpg (замена aiosqlite)  
✅ **Подход к доступу к данным** — raw SQL без ORM (dataclass модели + SQL запросы)  
✅ **Инструмент миграций** — ручной запуск SQL скриптов через asyncpg при старте приложения

## Изменения в схеме данных

### Новая таблица messages

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    content_length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_chat_user_active (chat_id, user_id, is_deleted, created_at DESC)
);
```

Изменения:

- `is_deleted` - для soft delete (FALSE = активное, TRUE = удалённое)
- `content_length` - длина контента в символах (автоматически вычисляется)
- `created_at` - уже был, остаётся
- Индекс включает `is_deleted` для быстрой фильтрации (boolean эффективнее)

## Реализация по TDD

### 1. Инфраструктура

- `docker-compose.yml` - PostgreSQL контейнер (порт 5432)
- `migrations/001_init_schema.sql` - SQL скрипт создания схемы
- Обновить `pyproject.toml` - заменить `aiosqlite` на `asyncpg`
- Миграции применяются автоматически при старте приложения (Database.init() читает и выполняет SQL файлы)

### 2. Конфигурация

Обновить `src/config.py`:

```python
# Заменить
database_path: str = "./data/messages.db"

# На
postgres_host: str = "localhost"
postgres_port: int = 5432
postgres_db: str = "systech_aidd"
postgres_user: str = "postgres"
postgres_password: str
```

### 3. Модели

Обновить `src/storage/models.py`:

```python
@dataclass
class Message:
    user_id: int
    chat_id: int
    role: Literal["user", "assistant"]
    content: str
    content_length: int  # NEW - вычисляется автоматически
    id: int | None = None
    created_at: datetime | None = None
    is_deleted: bool = False  # NEW - для soft delete
```

### 4. Database класс

Рефакторинг `src/storage/database.py`:

- Заменить `aiosqlite` на `asyncpg`
- Обновить connection string: `postgresql://user:pass@host:port/db`
- `init()` - применять миграции из `migrations/*.sql` (читать файлы и выполнять через connection.execute())
- `save_message()` - автоматически вычислять `content_length = len(content)`
- `get_history()` - фильтровать `WHERE is_deleted = FALSE`
- `clear_history()` - soft delete: `UPDATE messages SET is_deleted = TRUE WHERE ...`

### 5. Тесты

Обновить `tests/test_storage_database.py`:

- Использовать реальный PostgreSQL из docker-compose (testcontainers не нужен - KISS)
- Фикстура `db` - подключение к тестовой БД
- Новые тесты для soft delete:
  - `test_clear_history_soft_delete` - проверить что `is_deleted = TRUE`
  - `test_get_history_excludes_deleted` - удалённые не возвращаются
- Проверять `content_length` во всех тестах

### 6. Интеграция

- Обновить `src/main.py` - использовать новую конфигурацию БД
- Обновить README с инструкциями по запуску PostgreSQL

## Ключевые файлы

Создать:

- `docker-compose.yml`
- `migrations/001_init_schema.sql`
- `.env.example` (с примером postgres настроек)

Изменить:

- `pyproject.toml` (aiosqlite → asyncpg)
- `src/config.py` (новые поля postgres)
- `src/storage/models.py` (добавить поля)
- `src/storage/database.py` (полный рефакторинг на asyncpg)
- `tests/test_storage_database.py` (адаптация под PostgreSQL)
- `src/main.py` (обновить инициализацию)
- `README.md` (добавить инструкции)

### To-dos

- [ ] Настроить инфраструктуру: docker-compose.yml, миграции, обновить зависимости
- [ ] Обновить Config с настройками PostgreSQL
- [ ] Добавить поля content_length и is_deleted в Message модель
- [ ] Рефакторинг Database класса на asyncpg с поддержкой soft delete
- [ ] Обновить и дополнить тесты для PostgreSQL и новых полей
- [ ] Интегрировать изменения в main.py и обновить документацию