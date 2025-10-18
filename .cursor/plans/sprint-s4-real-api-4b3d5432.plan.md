<!-- 4b3d5432-faa1-464f-ac5c-6d7f56cb5258 b687fd0e-e719-424c-9b60-aa6cfac40566 -->
# План: Спринт S4 - Переход на реальный API

## Цели

Заменить MockStatCollector на RealStatCollector, который будет получать реальную статистику из PostgreSQL базы данных с таблицей messages.

## Бизнес-логика метрик

**Метрики:**

- total_messages: общее количество сообщений за период (все записи)
- active_users: уникальные user_id за период
- total_dialogs: уникальные пары (chat_id, user_id) за период
- growth_rate: процент изменения total_messages относительно предыдущего периода

**Timeline:**

- Группировка по дням (DATE(created_at))
- Для каждого дня: сумма сообщений и количество уникальных пользователей

**Расчет изменений (change):**

Сравнение текущего периода с предыдущим периодом той же длины.

## Архитектура

Существующая структура:

- `backend/api/models.py` - Pydantic модели (не меняем)
- `backend/api/protocols.py` - StatCollectorProtocol интерфейс (не меняем)
- `backend/api/collectors.py` - MockStatCollector (добавляем RealStatCollector)
- `backend/api/server.py` - FastAPI приложение (меняем импорт)

База данных:

- Таблица: `messages` из `migrations/001_init_schema.sql`
- Поля: id, user_id, chat_id, role, content, content_length, username, created_at, is_deleted

## Шаги реализации

### 1. Конфигурация БД для API

Добавить в `backend/api/server.py` настройки подключения к PostgreSQL через переменные окружения:

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

Использовать те же настройки, что уже используются ботом.

### 2. Реализация RealStatCollector

Создать класс `RealStatCollector` в `backend/api/collectors.py`:

**Конструктор:**

```python
def __init__(self, db_pool: asyncpg.Pool):
    self._pool = db_pool
```

**Метод get_stats:**

Реализовать согласно StatCollectorProtocol с SQL-запросами:

1. Определить временные границы для текущего и предыдущего периодов
2. Выполнить SQL-запросы для расчета метрик
3. Выполнить SQL-запрос для timeline данных
4. Сформировать StatsResponse

**SQL для метрик текущего периода:**

```sql
SELECT 
    COUNT(*) as total_messages,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT (chat_id, user_id)) as total_dialogs
FROM messages
WHERE created_at >= $1 AND created_at < $2
```

**SQL для метрик предыдущего периода (для расчета change):**

То же самое, но с другими границами дат.

**SQL для timeline:**

```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_messages,
    COUNT(DISTINCT user_id) as active_users
FROM messages
WHERE created_at >= $1 AND created_at < $2
GROUP BY DATE(created_at)
ORDER BY date
```

**Расчет трендов:**

- change > 5%: trend = "up"
- change < -5%: trend = "down"
- иначе: trend = "steady"

**Генерация описаний:**

Простые шаблоны на основе значений change и trend.

### 3. Интеграция в server.py

Изменить `backend/api/server.py`:

1. Добавить создание connection pool при старте приложения:
```python
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(...)
```

2. Добавить закрытие pool при остановке:
```python
@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()
```

3. Заменить MockStatCollector на RealStatCollector:
```python
stat_collector = RealStatCollector(app.state.db_pool)
```


### 4. Тестирование

Создать `tests/test_api_real.py`:

- Тесты с использованием реальной тестовой БД
- Заполнение тестовыми данными
- Проверка корректности расчета метрик
- Проверка timeline данных
- Проверка расчета изменений (change)

### 5. Документация

Обновить `backend/api/README.md`:

- Убрать упоминание о "только mock данных"
- Добавить раздел о RealStatCollector
- Документировать переменные окружения для БД
- Обновить примеры запуска

## Зависимости

Добавить в проект (если еще нет):

- asyncpg - уже используется в src/storage/database.py

## Риски и ограничения

1. **Производительность**: При большом объеме данных запросы могут быть медленными

   - Решение: индексы уже есть (idx_chat_user_active), возможно понадобятся дополнительные

2. **Пустая БД**: При отсутствии данных метрики будут нулевыми

   - Решение: graceful handling, возврат нулевых значений

3. **Timezone**: created_at хранится как TIMESTAMP, нужно учитывать часовой пояс

   - Решение: использовать UTC для всех расчетов

## Проверка готовности

После реализации:

1. API возвращает реальные данные из БД
2. Метрики корректно рассчитываются
3. Timeline отображает исторические данные
4. Frontend продолжает работать без изменений (контракт API не изменился)
5. Все тесты проходят

### To-dos

- [ ] Добавить конфигурацию подключения к PostgreSQL в backend/api
- [ ] Реализовать класс RealStatCollector с SQL-запросами для метрик
- [ ] Реализовать SQL-запрос для timeline данных с группировкой по дням
- [ ] Интегрировать RealStatCollector в server.py с connection pool
- [ ] Написать тесты для RealStatCollector с реальной БД
- [ ] Обновить документацию API после перехода на реальные данные