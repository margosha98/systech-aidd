# Systech AIDD Bot

AI-powered Telegram bot assistant с поддержкой контекстного диалога.

## 🚀 Возможности

- 💬 Контекстный диалог с AI (история последних 10 сообщений)
- 🤖 Интеграция с LLM через Openrouter API
- 💾 Хранение истории диалогов в SQLite
- ⚡ Асинхронная архитектура (aiogram 3.x)
- 🏗️ Чистая архитектура с Dependency Injection
- ✅ Автоматический контроль качества кода

## 📦 Установка

Проект использует [uv](https://github.com/astral-sh/uv) для управления зависимостями.

```bash
# Установка зависимостей
uv sync

# Создание .env файла
cp .env.example .env
# Заполните .env вашими ключами
```

### Переменные окружения

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Openrouter
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=openai/gpt-3.5-turbo

# LLM Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=30

# System Prompt
SYSTEM_PROMPT="Ты полезный AI-ассистент. Отвечай на вопросы пользователя четко и понятно."

# Database
DATABASE_PATH=./data/messages.db

# History
MAX_HISTORY_MESSAGES=10

# Logging
LOG_LEVEL=INFO
```

## 🎯 Использование

```bash
# Запуск бота
uv run python -m src.main
```

## 🏗️ Архитектура

Проект следует **слоистой архитектуре** с применением SOLID принципов:

```
Bot Layer (handlers.py)
    ↓ использует Protocol
LLM Layer (client.py)
    ↓ использует Protocol
Storage Layer (database.py, models.py)
```

### Ключевые принципы:

- **Dependency Injection** - зависимости через конструктор
- **Protocol** - абстракции вместо конкретных реализаций
- **Connection Pool** - переиспользование соединений с БД
- **Context Manager** - автоматическое управление ресурсами
- **Fail-fast** - ранняя валидация и явные ошибки

## 🛠️ Разработка

### Quality Tools

Проект использует современные инструменты контроля качества:

#### Ruff - Линтер и Форматтер
Быстрый линтер на Rust, заменяющий black, isort, flake8.

```bash
# Автоформатирование
uv run ruff format src/

# Проверка линтером
uv run ruff check src/

# Автоисправление
uv run ruff check --fix src/
```

#### Mypy - Проверка типов
Статическая проверка типов в strict режиме.

```bash
# Проверка типов
uv run mypy src/
```

#### Pytest - Тестирование
Фреймворк для unit и интеграционных тестов.

```bash
# Запуск тестов
uv run pytest

# С покрытием
uv run pytest --cov=src --cov-report=term-missing
```

### Команды Makefile

**Примечание:** На Windows используйте команды `uv run` напрямую.

```bash
# Форматирование кода
make format

# Проверка линтером
make lint

# Проверка типов
make typecheck

# Запуск тестов
make test

# Все проверки сразу
make quality
```

### Требования к коду

Перед коммитом обязательно:
- ✅ `ruff format` - код отформатирован
- ✅ `ruff check` - 0 ошибок линтера
- ✅ Соответствие [conventions.mdc](.cursor/rules/conventions.mdc)

## 📚 Документация

- [vision.md](docs/vision.md) - Техническое видение проекта
- [conventions.mdc](.cursor/rules/conventions.mdc) - Соглашения по коду
- [workflow.mdc](.cursor/rules/workflow.mdc) - Процесс разработки
- [tasklist.md](docs/tasklist.md) - История разработки MVP
- [tasklist_tech_dept.md](docs/tasklist_tech_dept.md) - Устранение технического долга

## 🎓 Технологический стек

- **Python 3.11+** - язык программирования
- **aiogram 3.x** - фреймворк для Telegram Bot API
- **AsyncOpenAI** - клиент для работы с LLM
- **aiosqlite** - асинхронная работа с SQLite
- **pydantic-settings** - типизированная конфигурация
- **ruff** - линтер и форматтер
- **mypy** - проверка типов
- **pytest** - тестирование

## 📝 Лицензия

MIT

## 🤝 Разработка

Проект находится в активной разработке. Технический долг устранен в рамках итераций 1-5:

- ✅ Настроены инструменты качества (ruff, mypy, pytest)
- ✅ Добавлена типизация (Literal, Protocol)
- ✅ Реализован Connection Pool для Database
- ✅ Убраны глобальные переменные, внедрен DI
- ✅ Реализован Graceful Shutdown

Следующие шаги см. в [tasklist.md](docs/tasklist.md).
