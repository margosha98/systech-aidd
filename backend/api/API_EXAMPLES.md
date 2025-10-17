# Примеры запросов к API статистики

## Запуск API сервера

```bash
# Режим разработки (с hot-reload)
make run-api-dev

# Режим production
make run-api
```

API будет доступен по адресу: `http://localhost:8000`

## Документация API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI spec**: http://localhost:8000/openapi.json

## Примеры запросов

### 1. Health Check

**curl:**
```bash
curl http://localhost:8000/health
```

**httpie:**
```bash
http GET http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok"
}
```

### 2. Получить статистику за 7 дней (по умолчанию)

**curl:**
```bash
curl http://localhost:8000/api/stats
```

**httpie:**
```bash
http GET http://localhost:8000/api/stats
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats" -Method Get
```

### 3. Получить статистику за 7 дней (явно)

**curl:**
```bash
curl "http://localhost:8000/api/stats?period=7d"
```

**httpie:**
```bash
http GET http://localhost:8000/api/stats period==7d
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=7d" -Method Get
```

### 4. Получить статистику за 30 дней

**curl:**
```bash
curl "http://localhost:8000/api/stats?period=30d"
```

**httpie:**
```bash
http GET http://localhost:8000/api/stats period==30d
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=30d" -Method Get
```

### 5. Получить статистику за 3 месяца

**curl:**
```bash
curl "http://localhost:8000/api/stats?period=3m"
```

**httpie:**
```bash
http GET http://localhost:8000/api/stats period==3m
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=3m" -Method Get
```

### 6. Получить статистику с красивым форматированием (curl)

**curl:**
```bash
curl "http://localhost:8000/api/stats?period=7d" | python -m json.tool
```

**httpie (автоматически форматирует):**
```bash
http GET http://localhost:8000/api/stats period==7d
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=7d" -Method Get | ConvertTo-Json -Depth 10
```

## Пример ответа

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
    { "date": "2025-10-12", "value": 1180 },
    { "date": "2025-10-13", "value": 1420 },
    { "date": "2025-10-14", "value": 1550 },
    { "date": "2025-10-15", "value": 1380 },
    { "date": "2025-10-16", "value": 1600 }
  ]
}
```

## Обработка ошибок

### Невалидный период

**Запрос:**
```bash
curl "http://localhost:8000/api/stats?period=invalid"
```

**Ответ (422 Validation Error):**
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["query", "period"],
      "msg": "Input should be '7d', '30d' or '3m'",
      "input": "invalid"
    }
  ]
}
```

## Интеграция с frontend

### JavaScript/TypeScript (fetch)

```typescript
async function getStats(period: '7d' | '30d' | '3m' = '7d') {
  const response = await fetch(`http://localhost:8000/api/stats?period=${period}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

// Использование
const stats = await getStats('7d');
console.log(stats.metrics.total_messages.value);
```

### JavaScript/TypeScript (axios)

```typescript
import axios from 'axios';

async function getStats(period: '7d' | '30d' | '3m' = '7d') {
  const { data } = await axios.get('http://localhost:8000/api/stats', {
    params: { period }
  });
  return data;
}
```

## Заметки

- API возвращает mock данные (случайные, но стабильные благодаря seed=42)
- CORS настроен для работы с любыми origins (в production нужно ограничить)
- Все даты в timeline в формате ISO 8601 (YYYY-MM-DD)
- Все значения метрик положительные
- `change` в метриках показывает изменение в процентах

