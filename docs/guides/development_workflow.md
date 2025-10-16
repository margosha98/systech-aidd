# Development Workflow - Процесс разработки

Как разрабатывать новую фичу от задачи до коммита.

---

## TDD Цикл (Test-Driven Development)

Проект использует **TDD подход**: тесты пишутся **ДО** реализации кода.

```mermaid
graph LR
    A[🔴 RED] -->|Implement| B[🟢 GREEN]
    B -->|Improve| C[🔵 REFACTOR]
    C -->|Next feature| A
    
    style A fill:#8b2b2b,stroke:#fff,stroke-width:2px,color:#fff
    style B fill:#2d5f3f,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#2b5278,stroke:#fff,stroke-width:2px,color:#fff
```

### 🔴 RED - Failing Test

1. Написать тест для новой функциональности
2. Тест должен **упасть** (код еще не реализован)
3. Убедиться что тест падает **по правильной причине**

```bash
uv run pytest tests/test_bot_handlers.py::test_cmd_help_responds
# Должно упасть: AttributeError ✅
```

### 🟢 GREEN - Minimal Implementation

1. Написать **минимум кода** для прохождения теста
2. Цель: **зеленый тест**, не красивый код

```bash
uv run pytest tests/test_bot_handlers.py::test_cmd_help_responds
# Должно пройти: PASSED ✅
```

### 🔵 REFACTOR - Clean Code

1. Улучшить код (убрать дублирование, упростить)
2. Следовать соглашениям ([conventions.mdc](../../.cursor/rules/conventions.mdc))
3. **Тесты остаются зелеными** (если упали - откатить)

```bash
uv run pytest
# Все тесты зеленые ✅
```

---

## Workflow разработки

### 1. Создать ветку

```bash
git checkout -b feature/add-help-command
```

**Типы веток:** `feature/`, `fix/`, `refactor/`, `docs/`

### 2. Написать failing тест (RED)

```bash
uv run pytest tests/test_bot_handlers.py::test_cmd_help_responds
# Должно упасть ❌
```

### 3. Реализовать минимум (GREEN)

```bash
uv run pytest tests/test_bot_handlers.py::test_cmd_help_responds
# Должно пройти ✅
```

### 4. Рефакторинг (REFACTOR)

```bash
uv run pytest
# Все тесты зеленые ✅
```

### 5. Проверить качество

```bash
uv run ruff format src/
uv run ruff check src/
uv run mypy src/
uv run pytest

# Или все сразу (Linux/Mac)
make quality
```

### 6. Обновить документацию

Если нужно: обновить `README.md`, `docs/guides/`, docstrings в коде.

### 7. Коммит

```bash
git add src/ tests/
git commit -m "feat: добавлена команда /help

- Реализован обработчик cmd_help
- Написан тест test_cmd_help_responds

Тесты: 35 passed ✅
Проверки: make quality ✅"
```

**Типы коммитов:** `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`

---

## Инструменты качества

### Команды

```bash
uv run ruff format src/       # Форматирование
uv run ruff check src/        # Линтер
uv run ruff check --fix src/  # Автоисправление
uv run mypy src/              # Проверка типов (strict mode)
uv run pytest                 # Все тесты
uv run pytest -v              # Подробный вывод
uv run pytest --cov=src       # С coverage

# Все сразу (Linux/Mac)
make quality
```

---

## Ключевые соглашения

### Именование

- **Классы:** `PascalCase` 
- **Функции/методы:** `snake_case`
- **Константы:** `UPPER_SNAKE_CASE`
- **Приватные:** `_leading_underscore`

### Типизация

```python
# Всегда указывать типы
def get_history(self, chat_id: int, user_id: int) -> list[Message]: ...

# Protocol для абстракций
class StorageProtocol(Protocol):
    async def save(self, data: dict) -> None: ...

# Literal для ограниченных значений
role: Literal["user", "assistant"]
```

### Async

```python
# ✅ Все IO операции асинхронны
async def save_message(self, message: Message) -> None:
    await self._connection.execute(...)
```

### Docstrings

```python
async def get_history(self, chat_id: int, user_id: int, limit: int) -> list[Message]:
    """Получение последних N сообщений из истории.
    
    Args:
        chat_id: ID чата
        user_id: ID пользователя
        limit: Максимальное количество сообщений
    
    Returns:
        Список сообщений (от старых к новым)
    """
```

---

## Чеклист перед коммитом

- [ ] TDD цикл пройден (RED → GREEN → REFACTOR)
- [ ] Все тесты проходят (`uv run pytest`)
- [ ] Код отформатирован (`uv run ruff format src/`)
- [ ] Нет ошибок линтера (`uv run ruff check src/`)
- [ ] Нет ошибок типов (`uv run mypy src/`)
- [ ] Docstrings для публичных методов
- [ ] Документация обновлена (если нужно)

**Быстрая проверка:**
```bash
make quality  # Linux/Mac
```

---

## Полезные ссылки

- **Визуализация проекта:** [visualization.md](visualization.md)
- **Детальные соглашения:** [conventions.mdc](../../.cursor/rules/conventions.mdc)
- **Соглашения по тестам:** [qa_conventions.mdc](../../.cursor/rules/qa_conventions.mdc)
- **TDD процесс (подробный):** [workflow_tdd.mdc](../../.cursor/rules/workflow_tdd.mdc)
- **Руководство по тестированию:** [testing_guide.md](testing_guide.md)

