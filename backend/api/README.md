# API Статистики Telegram-бота "Знайкин"

Mock API для дашборда статистики с автоматической генерацией OpenAPI документации.

## Быстрый старт

### Установка зависимостей

```bash
make install
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
- `MockStatCollector` - mock реализация с генерацией случайных данных

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

## Mock данные

Текущая реализация использует `MockStatCollector`, который:
- Генерирует случайные, но правдоподобные данные
- Использует стабильный seed (42) для повторяемости результатов
- Подходит для разработки и тестирования frontend

В будущем (Спринт S5) будет добавлена реализация `RealStatCollector`, которая будет получать данные из PostgreSQL базы.

## CORS

API настроен с CORS middleware, разрешающим запросы от любых origins (для разработки).

⚠️ **Важно:** В production необходимо ограничить `allow_origins` конкретными доменами.

## Расширение функциональности

Для добавления реальной интеграции с БД:

1. Создайте класс `RealStatCollector` в `collectors.py`
2. Реализуйте метод `get_stats()` согласно `StatCollectorProtocol`
3. Замените `MockStatCollector` на `RealStatCollector` в `server.py`

Благодаря паттерну Protocol, интерфейс API останется неизменным.

## Дополнительные ресурсы

- [API_EXAMPLES.md](./API_EXAMPLES.md) - Подробные примеры запросов
- [Swagger UI](http://localhost:8000/docs) - Интерактивная документация
- [ReDoc](http://localhost:8000/redoc) - Альтернативная документация

