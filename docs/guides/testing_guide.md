# Testing Guide - Руководство по тестированию

Как писать и запускать тесты в проекте.

---

## Философия

**Тестируем:**
- ✅ Бизнес-логику (команды, промпты, CRUD)
- ✅ Публичные интерфейсы
- ✅ Критичные пути
- ✅ Обработку ошибок

**НЕ тестируем:**
- ❌ Тривиальный код
- ❌ Приватные методы
- ❌ Детали реализации
- ❌ Фреймворки/библиотеки

**Принцип:** Тестируем **поведение**, не **реализацию**.

---

## Структура тестов

```
tests/
├── test_bot_handlers.py      # Bot Layer (моки LLM/DB)
├── test_llm_client.py         # LLM Layer (моки API)
├── test_storage_database.py   # Storage Layer (in-memory SQLite)
└── test_config.py             # Config
```

---

## Структура теста (AAA)

```python
@pytest.mark.asyncio
async def test_save_message_user():
    """Сохранение user сообщения в БД."""
    # Arrange - подготовка
    db = Database(":memory:")
    await db.connect()
    await db.init_db()
    
    # Act - выполнение
    await db.save_message(Message(...))
    
    # Assert - проверка
    history = await db.get_history(...)
    assert len(history) == 1
```

**AAA:** Arrange (подготовка) → Act (выполнение) → Assert (проверка)

---

## Фикстуры и моки

### Фикстуры (переиспользуемые объекты)

```python
@pytest.fixture
def mock_llm_client():
    mock = AsyncMock(spec=LLMClient)
    mock.get_response = AsyncMock(return_value="Ответ")
    return mock

@pytest.fixture
def bot_handlers(mock_llm_client, mock_database, config):
    return BotHandlers(mock_llm_client, mock_database, config)
```

### Моки

```python
# AsyncMock для async методов
mock_db = AsyncMock()
await mock_db.save_message(message)
mock_db.save_message.assert_called_once()

# MagicMock для синхронных объектов
config = MagicMock(llm_temperature=0.8)

# Проверки
mock.method.assert_called_once()
mock.method.assert_called_once_with(arg1, arg2)
mock.method.assert_not_called()
```

---

## Примеры тестов

### Bot Layer - тест команды

```python
@pytest.mark.asyncio
async def test_cmd_start_responds(bot_handlers):
    message = Mock(spec=TelegramMessage)
    message.answer = AsyncMock()
    
    await bot_handlers.cmd_start(message)
    
    message.answer.assert_called_once()
    assert "Знайкин" in message.answer.call_args[0][0]
```

### LLM Layer - тест формирования промпта

```python
@pytest.mark.asyncio
async def test_get_response_formats_messages():
    llm_client = LLMClient(config)
    llm_client.client = mock_client
    messages = [Message(...), Message(...)]
    
    await llm_client.get_response(messages, "System prompt")
    
    # Проверяем что API messages содержат system + история
    call_args = mock_client.chat.completions.create.call_args
    api_messages = call_args[1]["messages"]
    assert api_messages[0]["role"] == "system"
```

### Storage Layer - тест CRUD

```python
@pytest.mark.asyncio
async def test_save_and_get_message():
    db = Database(":memory:")
    await db.connect()
    await db.init_db()
    
    await db.save_message(Message(user_id=1, chat_id=1, role="user", content="Hello"))
    
    history = await db.get_history(chat_id=1, user_id=1, limit=10)
    assert len(history) == 1
    assert history[0].content == "Hello"
```

---

## Запуск тестов

```bash
uv run pytest                          # Все тесты
uv run pytest tests/test_bot_handlers.py  # Конкретный файл
uv run pytest tests/test_bot_handlers.py::test_cmd_start_responds  # Конкретный тест
uv run pytest -v                       # Подробный вывод
uv run pytest --cov=src                # С coverage
```

**Ожидаемый результат:** `34 passed, 1 skipped`

---

## Ключевые паттерны

### Async тесты

```python
@pytest.mark.asyncio  # Обязательно для async
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

**Важно:** `AsyncMock` для async методов, `MagicMock` для синхронных.

### Мокирование Telegram Message

```python
message = Mock(spec=TelegramMessage)
message.text = "Hello"
message.answer = AsyncMock()

await handler(message)

message.answer.assert_called_once()
```

### In-memory SQLite

```python
db = Database(":memory:")  # ← in-memory БД для тестов
await db.connect()
await db.init_db()
```

---

## Troubleshooting

**"coroutine was never awaited"** → Забыли `await` перед async вызовом  
**"MagicMock can't be used in 'await'"** → Используйте `AsyncMock` вместо `MagicMock`  
**"database is locked"** → Используйте `:memory:` для тестов  
**"fixture not found"** → Определите фикстуру в том же файле или `conftest.py`

---

## Покрытие кода

**Текущее:** ~79% (критичные модули >85%)

```bash
uv run pytest --cov=src --cov-report=term-missing
```

**Целевое покрытие:**
- Handlers, LLM, Storage: >80%
- Config: >90%
- Entry points: не критично

---

## Соглашения

**Именование:**
- Файлы: `test_{module}.py`
- Функции: `test_{что}_{ожидаемый_результат}`
- Фикстуры: описательные существительные

**Структура:** Docstring → Arrange → Act → Assert

**Проверки:** `assert x == y` (конкретные), тестируем поведение (не реализацию)

---

## Дополнительные материалы

- **Визуализация проекта:** [visualization.md](visualization.md)
- **Детальные соглашения:** [qa_conventions.mdc](../../.cursor/rules/qa_conventions.mdc)
- **TDD процесс:** [workflow_tdd.mdc](../../.cursor/rules/workflow_tdd.mdc)
- **Development workflow:** [development_workflow.md](development_workflow.md)

