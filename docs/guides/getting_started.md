# Getting Started - Быстрый старт

Гайд для запуска проекта локально за 15 минут.

---

## Требования

- **Python 3.11+** 
- **uv** - менеджер зависимостей ([установка](https://github.com/astral-sh/uv))
- **Telegram Bot Token** - получить у [@BotFather](https://t.me/botfather)
- **Openrouter API Key** - получить на [openrouter.ai](https://openrouter.ai/keys)

---

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
# Клонирование репозитория
git clone <repository-url>
cd systech-aidd

# Установка зависимостей (создаст виртуальное окружение)
uv sync
```

### 2. Настройка конфигурации

Создайте `.env` файл из примера:

```bash
cp .env.example .env
```

Откройте `.env` и заполните обязательные переменные:

```env
# Telegram Bot (обязательно)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Openrouter (обязательно)
OPENROUTER_API_KEY=your_openrouter_key_here

# Модели LLM (необязательно - есть значение по умолчанию)
OPENROUTER_MODEL=openai/gpt-oss-20b:free,deepseek/deepseek-chat-v3.1:free,qwen/qwen3-coder:free,meta-llama/llama-3.3-8b-instruct:free

# LLM настройки (необязательно - есть значения по умолчанию)
LLM_TEMPERATURE=0.8
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=60

# База данных (необязательно - по умолчанию ./data/messages.db)
DATABASE_PATH=./data/messages.db

# История (необязательно - по умолчанию 10)
MAX_HISTORY_MESSAGES=10

# Логирование (необязательно - по умолчанию INFO)
LOG_LEVEL=INFO
```

**Где получить токены:**
- **Telegram**: отправьте `/newbot` боту [@BotFather](https://t.me/botfather)
- **Openrouter**: зарегистрируйтесь на [openrouter.ai](https://openrouter.ai/keys) и создайте API key

### 3. Запуск бота

```bash
# Windows
uv run python -m src.main

# Linux/Mac (через Makefile)
make run
```

Вы увидите логи:

```
INFO - Initializing bot...
INFO - Configuration loaded successfully
INFO - Database initialized with path: ./data/messages.db
INFO - Database connected: ./data/messages.db
INFO - LLMClient initialized with model: openai/gpt-oss-20b:free,...
INFO - BotHandlers initialized with dependencies
INFO - Bot is ready. Starting polling...
```

### 4. Проверка работы

Откройте Telegram и найдите вашего бота. Отправьте команды:

1. `/start` - должно прийти приветствие
2. `/role` - описание возможностей бота
3. Любой текст - бот ответит через LLM
4. `/reset` - очистка истории диалога

**Если бот отвечает - всё работает! ✅**

---

## Запуск тестов

Проверьте что проект настроен правильно:

```bash
# Запуск всех тестов
uv run pytest

# Ожидаемый результат: 34 passed, 1 skipped
```

Проверьте качество кода:

```bash
# Windows - запускайте команды отдельно
uv run ruff format src/
uv run ruff check src/
uv run mypy src/
uv run pytest

# Linux/Mac - через Makefile
make quality
```

**Все проверки должны пройти без ошибок.**

---

## Структура проекта (краткая)

```
systech-aidd/
├── src/                  # Исходный код
│   ├── main.py          # Точка входа
│   ├── config.py        # Конфигурация
│   ├── bot/             # Telegram бот
│   ├── llm/             # LLM интеграция
│   └── storage/         # База данных
├── tests/               # Тесты
├── docs/                # Документация
├── .env                 # Конфигурация (создать вручную)
├── .env.example         # Пример конфигурации
├── pyproject.toml       # Зависимости
└── Makefile             # Команды для разработки
```

---

## Troubleshooting

### Ошибка: "TELEGRAM_BOT_TOKEN field required"

**Причина:** Не создан `.env` файл или не заполнен токен.

**Решение:**
1. Убедитесь что файл `.env` существует в корне проекта
2. Проверьте что `TELEGRAM_BOT_TOKEN=` заполнен корректным токеном

### Ошибка: "LLM API error: timeout"

**Причина:** Нет интернета или Openrouter недоступен.

**Решение:**
1. Проверьте интернет-соединение
2. Проверьте что `OPENROUTER_API_KEY` корректный
3. Увеличьте `LLM_TIMEOUT=120` в `.env`

### Ошибка: "Database locked"

**Причина:** SQLite файл используется другим процессом.

**Решение:**
1. Остановите все запущенные экземпляры бота
2. Удалите `./data/messages.db` и перезапустите

### Бот не отвечает в Telegram

**Причина:** Неверный токен или бот не запущен.

**Решение:**
1. Проверьте что бот запущен (должны быть логи "Bot is ready")
2. Проверьте токен у @BotFather командой `/mybots`
3. Убедитесь что токен скопирован полностью (без пробелов)

### Тесты падают: "import error"

**Причина:** Зависимости не установлены.

**Решение:**
```bash
uv sync
```

---

## Следующие шаги

После успешного запуска изучите:

1. **[architecture.md](architecture.md)** - как устроен проект
2. **[visualization.md](visualization.md)** - визуализация архитектуры и процессов
3. **[codebase_tour.md](codebase_tour.md)** - где что находится в коде
4. **[development_workflow.md](development_workflow.md)** - как разрабатывать фичи

---

## Полезные команды

```bash
# Запуск бота
uv run python -m src.main

# Тесты
uv run pytest                          # Все тесты
uv run pytest tests/test_database.py   # Конкретный файл
uv run pytest -v                       # С подробным выводом

# Качество кода
uv run ruff format src/    # Форматирование
uv run ruff check src/     # Линтер
uv run mypy src/           # Проверка типов

# Makefile (Linux/Mac)
make run        # Запуск бота
make test       # Тесты
make quality    # Все проверки сразу
```

