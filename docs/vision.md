# Техническое видение проекта

## 1. Технологии

### Основной стек
- **Python 3.11+** - основной язык разработки
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram** - библиотека для Telegram Bot API (режим polling)
- **openai** - клиент для работы с LLM через провайдер Openrouter
- **sqlite3** - встроенная БД для хранения истории диалогов
- **Make** - автоматизация задач сборки и запуска

### Конфигурация и утилиты
- **python-dotenv** - управление переменными окружения
- **pydantic-settings** - типизированная конфигурация приложения

### Тестирование и качество кода
- **pytest** - фреймворк для тестирования
- **pytest-asyncio** - поддержка асинхронных тестов
- **pytest-cov** - измерение покрытия тестами
- **pytest-mock** - удобные моки для тестов
- **ruff** - быстрый линтер и форматтер (замена black, isort, flake8)
- **mypy** - статическая проверка типов

## 2. Принципы разработки

### Основные принципы
1. **KISS (Keep It Simple, Stupid)** - максимальная простота решений
2. **SOLID** - следование принципам объектно-ориентированного проектирования
   - SRP (Single Responsibility) - одна ответственность на класс
   - DIP (Dependency Inversion) - зависимости через абстракции (Protocol)
   - OCP (Open-Closed) - открыт для расширения, закрыт для изменения
3. **DRY (Don't Repeat Yourself)** - нет дублирования кода
4. **ООП** - 1 класс = 1 файл (чистая структура, легкая навигация)
5. **Явное лучше неявного** - никакой магии, все очевидно
6. **Fail fast** - ранняя валидация, быстрое падение при ошибках
7. **Async-first** - используем async/await для всех IO операций (aiogram, openai, БД)
8. **Type hints** - типизация для всех функций и методов
9. **Dependency Injection** - зависимости через конструктор, без глобального state
10. **MVP-подход** - реализуем только необходимый минимум

### Что избегаем (NO оверинжиниринг)
- ❌ Глобальные переменные (кроме констант)
- ❌ Абстрактные фабрики и сложные паттерны
- ❌ Микросервисы и избыточная модульность
- ❌ Сложные системы кеширования
- ❌ Преждевременная оптимизация

## 3. Структура проекта

```
systech-aidd/
├── src/
│   ├── bot/
│   │   ├── handlers.py      # Обработчики команд и сообщений (класс BotHandlers с DI)
│   │   └── bot.py            # Инициализация и запуск бота
│   ├── llm/
│   │   ├── client.py         # Работа с OpenAI/Openrouter
│   │   └── protocols.py      # LLMClientProtocol
│   ├── storage/
│   │   ├── database.py       # Работа с SQLite (connection pool, context manager)
│   │   ├── models.py         # Модели данных (dataclasses с Literal)
│   │   └── protocols.py      # DatabaseProtocol
│   ├── config.py             # Конфигурация (pydantic-settings)
│   └── main.py               # Точка входа (DI setup)
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Fixtures
│   ├── test_database.py      # Тесты Storage Layer
│   ├── test_llm_client.py    # Тесты LLM Layer
│   └── test_handlers.py      # Тесты Bot Layer (опционально)
├── docs/
│   ├── idea.md
│   ├── vision.md
│   ├── tasklist.md
│   └── tasklist_tech_dept.md
├── .cursor/
│   └── rules/
│       ├── conventions.mdc
│       ├── workflow.mdc
│       └── workflow_tech_debt.mdc
├── .env.example              # Пример конфигурации
├── .env                      # Реальная конфигурация (в .gitignore)
├── .gitignore
├── Makefile                  # Команды: run, install, lint, format, typecheck, test, quality
├── pyproject.toml            # uv зависимости + конфигурации ruff, mypy, pytest
└── README.md
```

**Принципы организации:**
- Плоская структура, минимум вложенности
- Один класс = один файл
- Разделение по функциональности: bot, llm, storage
- Protocol для абстракций в отдельных файлах
- Конфигурация в корне src/
- Инструменты качества: ruff, mypy, pytest

## 4. Архитектура проекта

### Слоистая архитектура

```
User (Telegram) 
    ↓
Bot Layer (handlers.py, bot.py)
    ↓
LLM Layer (client.py) 
    ↓
Storage Layer (database.py, models.py)
```

### Описание слоев

**Bot Layer** - точка входа
- Получает сообщения от пользователя через aiogram
- Парсит команды (/start, /reset и т.д.)
- Передает запросы в LLM Layer через `LLMClientProtocol`
- Использует Storage Layer через `DatabaseProtocol`
- Возвращает ответы пользователю
- **DI:** Зависимости (LLMClient, Database, Config) через конструктор `BotHandlers`

**LLM Layer** - бизнес-логика
- Формирует промпты (системный промпт + история диалога)
- Отправляет запросы в Openrouter через openai client
- Возвращает ответы от LLM
- **Абстракция:** `LLMClientProtocol` для гибкости

**Storage Layer** - персистентность данных
- Сохраняет историю диалогов в SQLite
- Читает контекст для пользователя
- Управляет БД (создание таблиц)
- **Connection Pool:** Единое соединение, переиспользуется
- **Context Manager:** `async with Database(path) as db:`
- **Абстракция:** `DatabaseProtocol` для тестирования

### Поток данных (основной сценарий)

1. Пользователь отправляет сообщение → Bot Layer
2. Bot получает историю диалога из Storage Layer
3. Bot формирует запрос через LLM Layer
4. LLM отправляет запрос в Openrouter с контекстом
5. Получен ответ от LLM
6. Запрос и ответ сохраняются в Storage Layer
7. Bot отправляет ответ пользователю

**Принцип зависимостей:** 
- Bot → LLM → Storage (зависимости идут вниз, каждый слой знает только о следующем)
- Зависимости через абстракции (Protocol), а не конкретные реализации (DIP)
- Dependency Injection через конструктор, без глобального state

## 5. Модель данных

### Таблица `messages`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER PRIMARY KEY | Уникальный ID сообщения |
| `user_id` | INTEGER NOT NULL | Telegram user_id |
| `chat_id` | INTEGER NOT NULL | Telegram chat_id |
| `role` | TEXT NOT NULL | Роль: 'user' или 'assistant' |
| `content` | TEXT NOT NULL | Текст сообщения |
| `created_at` | TIMESTAMP | Время создания (DEFAULT CURRENT_TIMESTAMP) |

**Индексы:**
- `idx_chat_user` - составной индекс на (chat_id, user_id) для быстрого поиска истории

### Dataclass модель (models.py)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass
class Message:
    user_id: int
    chat_id: int
    role: Literal["user", "assistant"]  # Типобезопасность вместо str
    content: str
    id: int | None = None
    created_at: datetime | None = None
```

**Логика:**
- Привязка истории к паре (chat_id, user_id) - каждый диалог изолирован
- Простая денормализованная структура
- В личном чате user_id == chat_id, в группах они различаются

**Не реализуем в MVP (для будущего):**
- Лимиты на количество сообщений в истории
- Таблица пользователей с настройками
- Таблица сессий диалогов

## 6. Работа с LLM

### Конфигурация Openrouter

- **Base URL**: `https://openrouter.ai/api/v1`
- **API Key**: из переменной окружения `OPENROUTER_API_KEY`
- **Модель по умолчанию**: `openai/gpt-3.5-turbo` (быстрая и дешевая для MVP)
- Возможность переопределить модель через конфиг

### Класс LLMClient (llm/client.py)

**Основной метод:**
```python
async def get_response(messages: list[Message], system_prompt: str) -> str
```
- Принимает историю сообщений и системный промпт
- Формирует запрос для OpenAI API
- Возвращает ответ от LLM

**Формат запроса к API:**
```python
[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
]
```

**Параметры генерации (по умолчанию):**
- `temperature`: 0.7 - баланс между креативностью и последовательностью
- `max_tokens`: 1000 - ограничение длины ответа
- Настраиваются через конфиг

**Обработка ошибок:**
- Timeout: 30 секунд
- Retry: нет (fail fast для MVP)
- Логирование всех запросов и ответов

## 7. Сценарии работы

### 1. Команда /start
- Приветствие пользователя
- Краткое описание возможностей бота
- Инициализация пользователя (если требуется)

### 2. Команда /reset
- Очистка истории диалога для текущего чата
- Подтверждение успешной очистки

### 3. Обработка текстового сообщения (основной сценарий)
1. Пользователь отправляет текстовое сообщение
2. Бот сохраняет сообщение в БД с `role='user'`
3. Бот загружает историю из БД (последние N сообщений)
4. Бот отправляет запрос в LLM (системный промпт + история)
5. Бот получает ответ от LLM
6. Бот сохраняет ответ в БД с `role='assistant'`
7. Бот отправляет ответ пользователю

### 4. Обработка ошибок
- **Ошибка LLM API** → "Извините, произошла ошибка. Попробуйте позже"
- **Ошибка БД** → логируем, отвечаем без истории
- **Прочие ошибки** → общее сообщение об ошибке + логирование

### Ограничения MVP
- Только текстовые сообщения (без медиа, файлов)
- Только личные чаты (без групп)
- История: последние 10 сообщений (5 пар вопрос-ответ)

## 8. Подход к конфигурированию

### Переменные окружения (.env файл)

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

### Класс Config (config.py)

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    telegram_bot_token: str
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-3.5-turbo"
    
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    llm_timeout: int = 30
    
    system_prompt: str = "Ты полезный AI-ассистент."
    database_path: str = "./data/messages.db"
    max_history_messages: int = 10
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

**Принципы:**
- Все секреты только в .env (не в коде)
- Значения по умолчанию для необязательных параметров
- Валидация через pydantic при старте приложения
- Fail fast если отсутствуют обязательные параметры

## 9. Подход к логгированию

### Уровни логирования

- **INFO** - основные события (старт бота, получение/отправка сообщений)
- **WARNING** - неожиданные ситуации (предупреждения API)
- **ERROR** - ошибки требующие внимания (БД, LLM API)
- **DEBUG** - детальная информация для разработки

### Что логируем

**INFO:**
- Старт/остановка бота
- Получение сообщения от пользователя (user_id, chat_id, длина текста)
- Отправка ответа пользователю (длина текста)

**ERROR:**
- Ошибки LLM API (статус код, текст ошибки)
- Ошибки БД (текст ошибки, query)
- Необработанные исключения

**DEBUG:**
- Полный текст запросов/ответов LLM
- SQL запросы
- Содержимое конфигурации (без секретов)

### Конфигурация логирования

**Формат логов:**
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Вывод:**
- В консоль (stdout) - для контейнеров и разработки
- Без файлов (простота для MVP)

**Настройка:**
- Уровень логирования из переменной окружения `LOG_LEVEL`
- Стандартный модуль `logging` Python

## 10. Инструменты качества кода

### Ruff - линтер и форматтер
**Что проверяет:**
- Стиль кода (PEP 8)
- Неиспользуемые импорты/переменные
- Потенциальные баги
- Best practices Python

**Команды:**
```bash
make format    # Автоформатирование кода
make lint      # Проверка линтером
```

**Конфигурация (pyproject.toml):**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "DTZ", "PIE", "RET", "SIM", "ARG"]
```

### Mypy - проверка типов
**Что проверяет:**
- Соответствие типов
- Корректность вызовов функций
- Optional/None проверки
- Protocol/Generic валидация

**Команды:**
```bash
make typecheck    # Статическая проверка типов
```

**Конфигурация (pyproject.toml):**
```toml
[tool.mypy]
strict = true
python_version = "3.11"
```

### Pytest - тестирование
**Что тестируем:**
- Database: CRUD операции, история, очистка
- LLMClient: формирование запросов, обработка ошибок
- Handlers: обработка команд (опционально)

**Команды:**
```bash
make test    # Запуск всех тестов
pytest --cov=src --cov-report=term-missing    # С покрытием
```

**Конфигурация (pyproject.toml):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"
```

**Минимальные требования:**
- Покрытие критичных модулей (Database, LLMClient): >80%
- Все тесты проходят перед коммитом

### Комплексная проверка качества
```bash
make quality    # format + lint + typecheck + test
```

**Требование:** Все проверки ✅ перед каждым коммитом

---

## Итого

Документ содержит все необходимое для разработки качественного MVP:
- Простой и понятный технический стек
- Минималистичная архитектура без оверинжиниринга с применением SOLID, DRY, DI
- Четкие сценарии работы
- Настройка через переменные окружения
- Базовое логирование
- Автоматические инструменты контроля качества (ruff, mypy, pytest)
- Protocol для абстракций и тестируемости
- Connection pool для эффективной работы с БД

Следующий шаг: начало реализации согласно этому техническому видению.


