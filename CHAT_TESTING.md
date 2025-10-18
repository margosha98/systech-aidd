# Руководство по тестированию AI-чата

Инструкция для проверки работы веб-чата с двумя режимами (normal/admin).

## Предварительные требования

1. **PostgreSQL запущен:**
```bash
docker-compose up -d
```

2. **Переменные окружения настроены** (`.env`):
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=systech_aidd
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# OpenRouter API (для LLM)
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

3. **Зависимости установлены:**
```bash
make install
cd frontend && pnpm install
```

## Запуск системы

### 1. Запустить Backend API

В одном терминале:
```bash
make run-api-dev
```

API будет доступен на `http://localhost:8000`

Проверить работу:
```bash
curl http://localhost:8000/health
# Должно вернуть: {"status": "ok"}
```

### 2. Запустить Frontend

В другом терминале:
```bash
cd frontend
pnpm dev
```

Frontend будет доступен на `http://localhost:3000`

## Тестирование функциональности

### 1. Открыть дашборд

Открыть в браузере: `http://localhost:3000`

Должны увидеть:
- ✅ Dashboard со статистикой
- ✅ Floating button с иконкой чата в правом нижнем углу

### 2. Открыть чат

Кликнуть на floating button.

Должны увидеть:
- ✅ Окно чата с анимацией появления
- ✅ Приветственное сообщение от AI
- ✅ Badge с режимом: "💬 Обычный" (по умолчанию)
- ✅ Кнопка настроек (Settings)
- ✅ Кнопка закрытия (X)

### 3. Тестирование обычного режима (normal)

**Режим:** 💬 Обычный

**Тестовые сообщения:**
1. "Привет! Как дела?"
   - ✅ Должен ответить приветствием
   
2. "Что ты умеешь?"
   - ✅ Должен рассказать о своих возможностях
   
3. "Какая погода?"
   - ✅ Должен ответить как обычный AI-ассистент

**Проверить:**
- ✅ Сообщения добавляются в чат
- ✅ Отображается индикатор "печатает..."
- ✅ Ответы приходят от LLM
- ✅ Нет SQL запросов в ответах

### 4. Переключение на режим администратора

Кликнуть на кнопку настроек (⚙️).

Должны увидеть:
- ✅ Badge изменился на: "🔧 Админ"
- ✅ Новое приветствие: "Я помогу вам с вопросами по статистике диалогов"

### 5. Тестирование режима администратора (admin)

**Режим:** 🔧 Админ

**Тестовые вопросы по статистике:**

1. "Сколько всего сообщений в базе?"
   - ✅ Должен выполнить SQL запрос
   - ✅ Вернуть количество
   - ✅ Показать SQL запрос в details (можно раскрыть)

2. "Сколько уникальных пользователей?"
   - ✅ Должен посчитать DISTINCT user_id
   - ✅ Интерпретировать результат понятным языком

3. "Покажи последние 5 сообщений"
   - ✅ Должен выполнить SELECT с LIMIT 5
   - ✅ Отформатировать результаты

4. "Какие пользователи были активны сегодня?"
   - ✅ Должен использовать фильтр по дате
   - ✅ Показать список

**Проверить:**
- ✅ SQL запросы генерируются через LLM
- ✅ SQL выполняется на реальной БД
- ✅ Результаты интерпретируются LLM
- ✅ SQL запрос отображается в details (раскрывающаяся секция)

### 6. Тестирование истории диалога

1. Отправить несколько сообщений подряд
2. Закрыть чат (X)
3. Открыть чат снова

**Проверить:**
- ✅ История сохраняется в localStorage (session_id)
- ✅ История сохраняется в БД
- ✅ Контекст диалога сохраняется между сообщениями

### 7. Тестирование обработки ошибок

**Сценарии:**
1. Остановить Backend API
2. Отправить сообщение
   - ✅ Должно показать сообщение об ошибке
   
3. В admin режиме задать некорректный вопрос:
   "asdfghjkl"
   - ✅ LLM должен попытаться интерпретировать или вернуть ошибку

## Проверка через API (curl)

### Отправить сообщение в обычном режиме

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет!",
    "mode": "normal",
    "session_id": "test_session_123"
  }'
```

Ожидаемый ответ:
```json
{
  "message": "Привет! Как я могу помочь?",
  "sql_query": null,
  "mode": "normal"
}
```

### Отправить вопрос в режиме администратора

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Сколько всего сообщений?",
    "mode": "admin",
    "session_id": "test_session_123"
  }'
```

Ожидаемый ответ:
```json
{
  "message": "В базе данных всего 1,234 сообщений.",
  "sql_query": "SELECT COUNT(*) FROM messages WHERE is_deleted = false",
  "mode": "admin"
}
```

### Получить историю

```bash
curl http://localhost:8000/api/chat/history/test_session_123?limit=10
```

## Проверка в БД

Проверить что сообщения сохраняются:

```sql
-- Подключиться к PostgreSQL
psql -h localhost -U postgres -d systech_aidd

-- Посмотреть последние веб-чат сообщения
SELECT 
  chat_id,
  role,
  content,
  created_at
FROM messages
WHERE user_id = 0  -- Веб-чат использует user_id = 0
ORDER BY created_at DESC
LIMIT 20;
```

Должны увидеть:
- ✅ Сообщения с `user_id = 0`
- ✅ Отрицательный `chat_id` (для отличия от telegram)
- ✅ `role` = 'user' или 'assistant'
- ✅ Корректные timestamps

## Логи и отладка

### Backend логи

При запуске API в терминале должны видеть:
```
[OK] Database connection pool created: localhost:5432/systech_aidd
[OK] LLM client initialized for chat service
INFO:     Application startup complete.
```

При отправке сообщений:
```
INFO:     Chat message received: mode=normal, session=session_xxx
INFO:     Processing message in NORMAL mode, session=session_xxx, history_len=2
INFO:     NORMAL mode response length: 156
INFO:     Chat response sent: mode=normal
```

В admin режиме:
```
INFO:     Processing message in ADMIN mode, session=session_xxx
INFO:     Generating SQL for question: Сколько всего сообщений?
INFO:     Generated SQL: SELECT COUNT(*) FROM messages WHERE is_deleted = false
INFO:     SQL execution returned 1 rows
INFO:     Generated interpretation: В базе данных...
```

### Frontend логи

В консоли браузера (F12):
- ✅ Нет ошибок при открытии чата
- ✅ При отправке сообщений видны fetch запросы
- ✅ Session ID сохраняется в localStorage

## Известные ограничения

1. **Session ID** - привязан к localStorage браузера, очистка кеша сбросит историю
2. **Rate limits** - OpenRouter API может иметь лимиты на запросы
3. **SQL безопасность** - В production нужно добавить валидацию SQL и ограничения
4. **Длина истории** - Ограничена 20 последними сообщениями

## Troubleshooting

### Чат не открывается
- Проверить что frontend запущен
- Проверить console браузера на ошибки
- Проверить что framer-motion установлен

### Ошибка "Failed to send message"
- Проверить что Backend API запущен (`curl http://localhost:8000/health`)
- Проверить CORS настройки
- Проверить переменные окружения (OPENROUTER_API_KEY)

### SQL запросы не выполняются
- Проверить что PostgreSQL запущен
- Проверить подключение к БД
- Проверить что таблица messages существует

### LLM не отвечает
- Проверить OPENROUTER_API_KEY в .env
- Проверить баланс аккаунта OpenRouter
- Проверить логи backend на ошибки API

## Успешное завершение тестирования

Все пункты должны быть отмечены ✅:

**Backend:**
- [x] API сервер запускается
- [x] Health check работает
- [x] Эндпоинт `/api/chat/message` отвечает
- [x] Эндпоинт `/api/chat/history` работает
- [x] LLM интеграция работает
- [x] SQL генерация работает (admin режим)
- [x] Сообщения сохраняются в БД

**Frontend:**
- [x] Dashboard загружается
- [x] Floating button отображается
- [x] Чат открывается/закрывается
- [x] Обычный режим работает
- [x] Режим администратора работает
- [x] Переключение между режимами работает
- [x] SQL запросы отображаются (admin)
- [x] История сохраняется
- [x] Анимации работают

**Интеграция:**
- [x] Frontend → Backend связь работает
- [x] Session management работает
- [x] История чата синхронизируется с БД
- [x] Text-to-SQL pipeline работает
- [x] Ошибки обрабатываются корректно

