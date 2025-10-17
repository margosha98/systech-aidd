# API Статистики Telegram-бота "Знайкин"

RESTful API для дашборда статистики с поддержкой реальных данных из PostgreSQL и автоматической генерацией OpenAPI документации.

## Быстрый старт

### Установка зависимостей

```bash
make install
```

### Настройка переменных окружения

API использует те же переменные окружения, что и основной бот. Убедитесь, что файл `.env` содержит настройки PostgreSQL:

```env
# PostgreSQL Database (обязательно)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=systech_aidd
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

### Запуск PostgreSQL

Перед запуском API убедитесь, что PostgreSQL запущен:

```bash
docker-compose up -d
```

### Запуск API сервера

**Режим разработки (с hot-reload):**
```bash
make run-api-dev
```

**Режим production:**
```bash
make run-api
```

**Напрямую через uv:**
```bash
cd backend/api
uv run python -m backend.api.server
```

API будет доступен по адресу: `http://localhost:8000`

### Документация API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI spec**: http://localhost:8000/openapi.json

## Архитектура

### Структура модуля

```
backend/api/
├── __init__.py          # Инициализация модуля
├── models.py            # Pydantic модели данных
├── protocols.py         # Protocol интерфейсы
├── collectors.py        # Реализации сборщиков статистики
├── server.py            # FastAPI приложение
├── __main__.py          # Entry point для запуска
├── API_EXAMPLES.md      # Примеры запросов
└── README.md            # Эта документация
```

### Ключевые компоненты

**Models (`models.py`):**
- `PeriodEnum` - enum для периодов (7d, 30d, 3m)
- `TrendEnum` - enum для трендов (up, down, steady)
- `MetricCard` - модель карточки метрики
- `TimelinePoint` - точка данных для графика
- `MetricsData` - набор всех метрик
- `StatsResponse` - полный ответ API

**Protocols (`protocols.py`):**
- `StatCollectorProtocol` - интерфейс для сборщиков статистики

**Collectors (`collectors.py`):**
- `MockStatCollector` - mock реализация с генерацией случайных данных (для разработки frontend)
- `RealStatCollector` - реальная реализация с получением данных из PostgreSQL

**Server (`server.py`):**
- FastAPI приложение с единым эндпоинтом `/api/stats`
- CORS middleware для frontend разработки
- Автоматическая генерация OpenAPI документации

## API Endpoints

### GET /api/stats

Получить статистику дашборда за указанный период.

**Параметры:**
- `period` (query, optional) - Период статистики: `7d`, `30d`, `3m`. По умолчанию: `7d`

**Ответ:** `StatsResponse` с метриками и timeline данными

**Пример запроса:**
```bash
curl "http://localhost:8000/api/stats?period=7d"
```

**Пример ответа:**
```json
{
  "period": "7d",
  "metrics": {
    "total_messages": {
      "value": 45678,
      "change": 12.5,
      "trend": "up",
      "description": "Trending up this month"
    },
    "active_users": {
      "value": 1234,
      "change": -8.0,
      "trend": "down",
      "description": "Down this period"
    },
    "total_dialogs": {
      "value": 8920,
      "change": 15.3,
      "trend": "up",
      "description": "Strong user retention"
    },
    "growth_rate": {
      "value": 4.5,
      "change": 1.2,
      "trend": "steady",
      "description": "Steady performance increase"
    }
  },
  "timeline": [
    { "date": "2025-10-10", "value": 1200 },
    { "date": "2025-10-11", "value": 1350 },
    ...
  ]
}
```

### GET /health

Health check эндпоинт для проверки работоспособности API.

**Ответ:**
```json
{
  "status": "ok"
}
```

## Метрики дашборда

API возвращает следующие метрики:

1. **Total Messages** - Общее количество сообщений в telegram-боте
2. **Active Users** - Количество активных пользователей
3. **Total Dialogs** - Общее количество диалогов
4. **Growth Rate** - Темп роста сообщений (в процентах)

Каждая метрика включает:
- `value` - текущее значение
- `change` - изменение в процентах относительно предыдущего периода
- `trend` - направление тренда (up, down, steady)
- `description` - текстовое описание

## Timeline данные

Timeline содержит историю значений метрик по дням:
- Для периода `7d` - 7 точек данных
- Для периода `30d` - 30 точек данных
- Для периода `3m` - 90 точек данных

Формат даты: `YYYY-MM-DD` (ISO 8601)

## Тестирование

```bash
# Запустить тесты API
uv run pytest tests/test_api_mock.py -v

# Запустить все тесты проекта
make test
```

## Проверка качества кода

```bash
# Форматирование
make format

# Линтер
make lint

# Проверка типов
make typecheck

# Все проверки + тесты
make quality
```

## Источники данных

API поддерживает два источника данных:

### RealStatCollector (Production)

**Текущая реализация** - получает реальные данные из PostgreSQL:
- Подключается к таблице `messages` через connection pool
- Рассчитывает метрики на основе реальных сообщений пользователей
- Сравнивает текущий период с предыдущим для расчета изменений
- Использует UTC для работы с датами
- Автоматически конвертирует timezone-aware datetime в naive для PostgreSQL TIMESTAMP

**Метрики:**
- `total_messages` - общее количество сообщений за период
- `active_users` - уникальные user_id за период  
- `total_dialogs` - уникальные пары (chat_id, user_id) за период
- `growth_rate` - процент изменения относительно предыдущего периода

**Timeline:**
- Группировка данных по дням (DATE(created_at))
- Для каждого дня: сумма сообщений и количество уникальных пользователей

### MockStatCollector (Development)

Mock реализация для разработки frontend без реальной БД:
- Генерирует случайные, но правдоподобные данные
- Использует стабильный seed (42) для повторяемости результатов
- Подходит для разработки и тестирования frontend без зависимости от БД

## CORS

API настроен с CORS middleware, разрешающим запросы от любых origins (для разработки).

⚠️ **Важно:** В production необходимо ограничить `allow_origins` конкретными доменами.

## Архитектура и расширяемость

Проект использует паттерн Protocol для абстрагирования источника данных:

```python
# Интерфейс
class StatCollectorProtocol(Protocol):
    async def get_stats(self, period: PeriodEnum) -> StatsResponse: ...

# Реализации
class MockStatCollector: ...  # Для разработки
class RealStatCollector: ...  # Для production
```

Благодаря этому паттерну:
- Интерфейс API остается неизменным при смене источника данных
- Легко добавить новые реализации (например, кеширование, агрегация)
- Упрощается тестирование и разработка

### Connection Pool

API использует asyncpg connection pool для эффективной работы с PostgreSQL:
- Минимум 2 соединения, максимум 10
- Создается при старте приложения (`@app.on_event("startup")`)
- Закрывается при остановке (`@app.on_event("shutdown")`)
- Переиспользуется для всех запросов

## Дополнительные ресурсы

- [API_EXAMPLES.md](./API_EXAMPLES.md) - Подробные примеры запросов
- [Swagger UI](http://localhost:8000/docs) - Интерактивная документация
- [ReDoc](http://localhost:8000/redoc) - Альтернативная документация

