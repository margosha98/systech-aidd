<!-- f9bf07e0-10f9-4e51-9f69-32e9ae542fe0 5c5b4e3d-2c79-495b-96ad-064785f0f9d0 -->
# Спринт 1: Mock API для дашборда статистики

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
    └── __main__.py        # Entry point для запуска
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

**pyproject.toml:** добавить `fastapi>=0.104.0`, `uvicorn>=0.24.0`

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

### 6. Тестирование

**tests/test_api_mock.py:**

- Тест MockStatCollector (генерация данных)
- Тест эндпоинта /api/stats (status codes, схема ответа)
- Тест валидации параметра period (7d, 30d, 3m)
- Тест CORS headers

### To-dos

- [ ] Реализовать Pydantic модели в models.py (MetricCard, TimelinePoint, MetricsResponse, TimelineResponse)
- [ ] Создать StatCollectorProtocol в protocols.py
- [ ] Реализовать MockStatCollector в collectors.py с генерацией mock-данных
- [ ] Создать FastAPI приложение в server.py с двумя эндпоинтами (/api/stats/metrics, /api/stats/timeline)
- [ ] Создать __main__.py для запуска API сервера
- [ ] Добавить fastapi и uvicorn в pyproject.toml и установить зависимости
- [ ] Добавить команды run-api и run-api-dev в Makefile
- [ ] Создать tests/test_api_mock.py с тестами для MockStatCollector и эндпоинтов
- [ ] Запустить make quality для проверки линтеров и тестов