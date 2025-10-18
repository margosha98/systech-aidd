# Systech AIDD Bot - Знайкин

[![Build and Publish](https://github.com/OWNER/systech-aidd/workflows/Build%20and%20Publish/badge.svg)](https://github.com/OWNER/systech-aidd/actions)

AI-powered Telegram бот-помощник для детей 7-10 лет с контекстным диалогом.

## 🚀 Возможности

- 🌟 **Помощник для детей** - объясняет сложное простым языком
- 💡 Отвечает на детские вопросы о мире и науке
- 🎬 Советует фильмы, книги и игры (для возраста 5-10 лет)
- 💪 Эмпатичный и поддерживающий тон общения
- 😄 Дружелюбный стиль с детскими шутками
- 💬 Контекстный диалог с AI (история последних 10 сообщений)
- 🤖 Интеграция с LLM через Openrouter API
- 💾 Хранение истории диалогов в PostgreSQL с soft delete
- ⚡ Асинхронная архитектура (aiogram 3.x)
- 🏗️ Чистая архитектура с Dependency Injection
- ✅ Автоматический контроль качества кода

## 🐳 Docker образы

Проект автоматически собирается и публикуется в GitHub Container Registry при каждом push в `main`.

### Доступные образы

- **Bot:** `ghcr.io/OWNER/systech-aidd-bot:latest`
- **API:** `ghcr.io/OWNER/systech-aidd-api:latest`
- **Frontend:** `ghcr.io/OWNER/systech-aidd-frontend:latest`

### Использование готовых образов

```bash
# Скачать образы
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
docker pull ghcr.io/OWNER/systech-aidd-api:latest
docker pull ghcr.io/OWNER/systech-aidd-frontend:latest

# Запустить из готовых образов
docker-compose -f docker-compose.registry.yml up -d
```

**Преимущества:**
- ✅ Не нужно собирать образы локально
- ✅ Быстрый старт - скачивание вместо сборки
- ✅ Гарантированно работающая версия из main

## 📦 Установка

### 🐳 Запуск через Docker (рекомендуется)

Самый простой способ запустить проект - использовать Docker Compose. Все сервисы запускаются одной командой.

```bash
# 1. Создать .env файл из шаблона
cp .env.example .env

# 2. Заполнить обязательные переменные в .env
# TELEGRAM_BOT_TOKEN=your_bot_token_here
# OPENROUTER_API_KEY=your_openrouter_key_here

# 3. Запустить все сервисы (PostgreSQL, Bot, API, Frontend)
docker-compose up

# Или в фоновом режиме
docker-compose up -d
```

После первого запуска проверьте доступность сервисов:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

**Управление сервисами:**
```bash
# Остановить все сервисы
docker-compose down

# Пересобрать образы после изменений
docker-compose build

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend

# Перезапустить конкретный сервис
docker-compose restart bot
```

### 💻 Локальная разработка (без Docker)

Проект использует [uv](https://github.com/astral-sh/uv) для управления зависимостями.

```bash
# Установка зависимостей
uv sync

# Запуск PostgreSQL через Docker
docker-compose up -d postgres

# Создание .env файла
cp .env.example .env
# Заполните .env вашими ключами (для локальной разработки используйте POSTGRES_HOST=localhost)
```

### Переменные окружения

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Openrouter
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=openai/gpt-oss-20b:free,deepseek/deepseek-chat-v3.1:free,qwen/qwen3-coder:free,meta-llama/llama-3.3-8b-instruct:free

# LLM Settings
LLM_TEMPERATURE=0.8
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=60

# System Prompt (определяет поведение и личность бота)
# По умолчанию настроен на роль помощника для детей 7-10 лет
# См. src/config.py для полной версии

# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=systech_aidd
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# History
MAX_HISTORY_MESSAGES=10

# Logging
LOG_LEVEL=INFO
```

## 🎯 Использование

### Запуск бота

```bash
uv run python -m src.main
```

### Команды бота

- `/start` — приветствие и описание возможностей
- `/role` — отображение личности и возможностей ребенка
- `/reset` — очистка истории диалога (новый старт)

### Поведение бота

Бот **ведет себя как ребенок 7 лет** с характерными особенностями:
- 🗣️ Короткие простые предложения (5-10 слов)
- 😊 Детская лексика: "прикольно", "классно", "ух ты", "вау", "круто"
- ❗ Много эмоций и восклицаний: !!! 😊 😄 🤩
- 🤔 Любознательность: "А почему?", "А правда?", "А ты знаешь?"
- 🎮 Интересы: животные, игры, мультики, еда, природа

**Бот НЕ знает** сложные взрослые темы (наука, работа, политика) и честно признается: "Не знаю! 😅 Я ещё маленький!"

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

### 🚀 Гайды для разработчиков

Начните здесь: **[docs/guides/](docs/guides/)** - полный набор руководств (~2 часа на онбординг)

1. **[Getting Started](docs/guides/getting_started.md)** - запуск проекта (15 мин)
2. **[Architecture](docs/guides/architecture.md)** - архитектура и модель данных (20 мин)
3. **[Codebase Tour](docs/guides/codebase_tour.md)** - навигация по коду (30 мин)
4. **[Development Workflow](docs/guides/development_workflow.md)** - TDD процесс (25 мин)
5. **[Testing Guide](docs/guides/testing_guide.md)** - как писать тесты (30 мин)

### 📖 Техническая документация

- [vision.md](docs/vision.md) - Техническое видение проекта
- [idea.md](docs/idea.md) - Концепция бота
- [tasklist.md](docs/tasklist.md) - История разработки MVP

### 📋 Соглашения и процессы

- [conventions.mdc](.cursor/rules/conventions.mdc) - Соглашения по коду
- [qa_conventions.mdc](.cursor/rules/qa_conventions.mdc) - Соглашения по тестам
- [workflow_tdd.mdc](.cursor/rules/workflow_tdd.mdc) - TDD процесс (подробный)

## 🎓 Технологический стек

- **Python 3.11+** - язык программирования
- **aiogram 3.x** - фреймворк для Telegram Bot API
- **AsyncOpenAI** - клиент для работы с LLM
- **PostgreSQL + asyncpg** - асинхронная работа с базой данных
- **Docker Compose** - контейнеризация инфраструктуры
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
