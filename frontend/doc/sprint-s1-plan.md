# План Спринта S1: Mock API для дашборда статистики

**Статус:** ✅ Завершен  
**Дата:** 2025-10-17

## Цель

Создать Mock API с контрактом данных для дашборда статистики telegram-бота "Знайкин", адаптированным под метрики работы бота.

## Архитектурные решения

**Технологический стек:**

- FastAPI (async, автодокументация OpenAPI/Swagger)
- Pydantic v2 (валидация и сериализация)
- Protocol pattern (MockStatCollector / RealStatCollector)

**Структура:** `backend/api/` (отдельно от основного кода бота в `src/`)

**Адаптация метрик под telegram-бота:**

- Total Messages (общее количество сообщений) → было Total Revenue
- Active Users (активные пользователи) → было New Customers
- Total Dialogs (всего диалогов) → было Active Accounts
- Messages Growth Rate (темп роста сообщений) → было Growth Rate
- Messages Over Time (график сообщений по времени) → было Total Visitors

## Реализация

### 1. Структура backend/api/

```
backend/
└── api/
    ├── __init__.py
    ├── models.py          # Pydantic модели (MetricCard, TimelinePoint, MetricsData, StatsResponse)
    ├── protocols.py       # StatCollectorProtocol
    ├── collectors.py      # MockStatCollector с рандомными данными
    ├── server.py          # FastAPI приложение, единый эндпоинт /api/stats, CORS
    ├── __main__.py        # Entry point для запуска
    └── API_EXAMPLES.md    # Примеры запросов к API
```

### 2. API endpoint

**GET /api/stats?period=7d**

Единый эндпоинт, возвращающий все данные для дашборда.

**Параметры:** `period` = `7d` | `30d` | `3m` (enum validation)

**Ответ (StatsResponse):**

```json
{
  "period": "7d",
  "metrics": {
    "total_messages": { "value": 45678, "change": 12.5, "trend": "up", "description": "Trending up this month" },
    "active_users": { "value": 1234, "change": -8.0, "trend": "down", "description": "Down 8% this period" },
    "total_dialogs": { "value": 8920, "change": 15.3, "trend": "up", "description": "Strong user retention" },
    "growth_rate": { "value": 4.5, "change": 1.2, "trend": "steady", "description": "Steady performance increase" }
  },
  "timeline": [
    { "date": "2025-10-10", "value": 1200 },
    { "date": "2025-10-11", "value": 1350 },
    ...
  ]
}
```

### 3. Реализация Mock данных

**MockStatCollector:**

- Генерирует случайные, но правдоподобные данные
- Стабильные seed для повторяемости
- Реализует StatCollectorProtocol

### 4. Конфигурация

**pyproject.toml:** добавлены `fastapi>=0.104.0`, `uvicorn>=0.24.0`, `httpx>=0.25.0`

**Makefile:** новые команды

```makefile
run-api:
    uv run python -m backend.api

run-api-dev:
    uv run uvicorn backend.api.server:app --reload --port 8000
```

### 5. Документация

- Автогенерация через FastAPI: `/docs` (Swagger UI), `/redoc`
- CORS настройки для frontend разработки
- Примеры запросов в `backend/api/API_EXAMPLES.md`

### 6. Тестирование

**tests/test_api_mock.py:**

- Тест MockStatCollector (генерация данных)
- Тест эндпоинта /api/stats (status codes, схема ответа)
- Тест валидации параметра period (7d, 30d, 3m)
- Тест CORS middleware

**Результаты:** ✅ 15/15 тестов прошли успешно

## Выполненные задачи

✅ Создана структура backend/api/ с **init**.py файлами  
✅ Реализованы Pydantic модели (MetricCard, TimelinePoint, MetricsData, StatsResponse)  
✅ Создан StatCollectorProtocol  
✅ Реализован MockStatCollector с генерацией mock-данных  
✅ Создано FastAPI приложение с единым эндпоинтом /api/stats  
✅ Создан **main**.py для запуска API сервера  
✅ Добавлены зависимости fastapi, uvicorn, httpx  
✅ Добавлены команды run-api и run-api-dev в Makefile  
✅ Созданы тесты tests/test_api_mock.py  
✅ Созданы примеры запросов к API  
✅ Проверка качества кода (ruff, mypy) - пройдена  
✅ Обновлена документация frontend-roadmap.md

## Как использовать

```bash
# Установить зависимости
make install

# Запустить API сервер (dev режим)
make run-api-dev

# API доступен на http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc

# Пример запроса
curl "http://localhost:8000/api/stats?period=7d"

# Запустить тесты
uv run pytest tests/test_api_mock.py -v
```

## Следующие шаги (S2)

После завершения S1, в следующем спринте S2 будет создан каркас frontend проекта для интеграции с API.
