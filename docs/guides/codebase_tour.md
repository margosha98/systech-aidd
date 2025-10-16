# Codebase Tour - Тур по кодовой базе

Детальный обзор структуры проекта и ключевых модулей.

---

## Структура директорий

```
systech-aidd/
├── src/                        # Исходный код
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── config.py               # Конфигурация
│   ├── bot/                    # Bot Layer
│   │   ├── __init__.py
│   │   ├── bot.py              # Создание бота
│   │   └── handlers.py         # Обработчики команд
│   ├── llm/                    # LLM Layer
│   │   ├── __init__.py
│   │   ├── client.py           # LLM клиент
│   │   └── protocols.py        # LLMClientProtocol
│   └── storage/                # Storage Layer
│       ├── __init__.py
│       ├── database.py         # Database класс
│       ├── models.py           # Message dataclass
│       └── protocols.py        # DatabaseProtocol
├── tests/                      # Тесты
│   ├── __init__.py
│   ├── test_bot_handlers.py    # Тесты Bot Layer
│   ├── test_llm_client.py      # Тесты LLM Layer
│   ├── test_storage_database.py # Тесты Storage Layer
│   └── test_config.py          # Тесты Config
├── docs/                       # Документация
│   ├── guides/                 # Гайды (этот файл здесь)
│   ├── vision.md               # Техническое видение
│   ├── idea.md                 # Концепция бота
│   ├── tasklist.md             # История разработки
│   └── reviews/                # Ревью проекта
├── .cursor/                    # Правила для AI
│   └── rules/
│       ├── conventions.mdc     # Соглашения по коду
│       ├── qa_conventions.mdc  # Соглашения по тестам
│       └── workflow_tdd.mdc    # TDD процесс
├── data/                       # База данных (создается автоматически)
│   └── messages.db
├── .env                        # Конфигурация (не в git)
├── .env.example                # Пример конфигурации
├── .gitignore
├── pyproject.toml              # Зависимости + настройки ruff/mypy/pytest
├── uv.lock                     # Lock-файл зависимостей
├── Makefile                    # Команды для разработки
└── README.md
```

**Принцип:** 1 класс = 1 файл (легкая навигация).

---

## main.py - Точка входа

**Ответственность:** Инициализация и запуск бота с DI setup.

```python
async def main() -> None:
    # 1. Загрузка конфигурации
    config = Config()
    
    # 2. Инициализация Database (с graceful shutdown)
    async with Database(config.database_path) as database:
        
        # 3. Создание зависимостей
        llm_client = LLMClient(config)
        bot_handlers = BotHandlers(llm_client, database, config)
        
        # 4. Создание бота
        bot, dp = create_bot(config, bot_handlers.router)
        
        # 5. Запуск polling
        await start_polling(bot, dp)
    
    # Database автоматически закрывается при выходе из context manager
```

**Ключевые моменты:**
- Dependency Injection - зависимости создаются здесь и передаются вниз
- Graceful shutdown - `async with` автоматически закрывает БД при остановке
- Fail-fast - если конфиг некорректен, приложение упадет сразу

**Когда редактировать:** Добавление новых зависимостей верхнего уровня.

---

## config.py - Конфигурация

**Ответственность:** Загрузка и валидация настроек из `.env`.

```python
class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Обязательные поля (fail-fast если отсутствуют)
    telegram_bot_token: str
    openrouter_api_key: str
    
    # Опциональные с defaults
    openrouter_model: str = "..."
    llm_temperature: float = 0.8
    database_path: str = "./data/messages.db"
    max_history_messages: int = 10
    # ...
```

**Ключевые моменты:**
- **pydantic-settings** - автоматическая загрузка из `.env`
- **Типизация** - все поля типизированы
- **Валидация** - некорректные типы приведут к ошибке при старте
- **Дефолты** - разумные значения по умолчанию

**Когда редактировать:** Добавление новой настройки (добавить поле + дефолт + обновить `.env.example`).

---

## Bot Layer

### bot/bot.py - Создание бота

**Ответственность:** Инициализация aiogram Bot и Dispatcher.

```python
def create_bot(config: Config, router: Router) -> tuple[Bot, Dispatcher]:
    bot = Bot(token=config.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)  # Подключаем router с handlers
    return bot, dp

async def start_polling(bot: Bot, dp: Dispatcher) -> None:
    await dp.start_polling(bot)
```

**Ключевые моменты:**
- `ParseMode.HTML` - для форматирования сообщений (<b>, <i>)
- Router pattern - handlers инкапсулированы в `BotHandlers`

**Когда редактировать:** Редко (настройка middleware, изменение режима работы).

### bot/handlers.py - Обработчики команд

**Ответственность:** Обработка команд (`/start`, `/reset`, `/role`) и текстовых сообщений.

```python
class BotHandlers:
    def __init__(
        self,
        llm_client: LLMClientProtocol,
        database: DatabaseProtocol,
        config: Config,
    ):
        self.llm_client = llm_client
        self.database = database
        self.config = config
        self.router = Router()
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        self.router.message(Command("start"))(self.cmd_start)
        self.router.message(Command("reset"))(self.cmd_reset)
        self.router.message(Command("role"))(self.cmd_role)
        self.router.message()(self.handle_message)  # Все остальные
    
    async def cmd_start(self, message: TelegramMessage) -> None:
        await message.answer("Привет! Я Знайкин...")
    
    async def handle_message(self, message: TelegramMessage) -> None:
        # 1. Сохранить user message
        # 2. Загрузить историю
        # 3. Запросить LLM
        # 4. Сохранить assistant message
        # 5. Отправить ответ
```

**Ключевые моменты:**
- **DI через конструктор** - зависимости передаются извне
- **Router pattern** - handlers регистрируются в `_register_handlers()`
- **Protocol** - работа через `LLMClientProtocol` и `DatabaseProtocol`

**Когда редактировать:**
- **Добавить команду:** создать метод `cmd_xxx`, зарегистрировать в `_register_handlers()`
- **Изменить логику обработки:** редактировать `handle_message()`

---

## LLM Layer

### llm/client.py - LLM клиент

**Ответственность:** Запросы к Openrouter API.

```python
class LLMClient:
    def __init__(self, config: Config):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.openrouter_api_key,
            timeout=config.llm_timeout,
        )
        self.model = config.openrouter_model
        self.temperature = config.llm_temperature
        self.max_tokens = config.llm_max_tokens
    
    async def get_response(
        self,
        messages: list[Message],
        system_prompt: str
    ) -> str:
        # Формируем API messages
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})
        
        # Запрос к API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        
        return response.choices[0].message.content
```

**Ключевые моменты:**
- **AsyncOpenAI** - официальный клиент с async поддержкой
- **Формирование промпта** - system + история
- **Конфигурация** - все параметры из Config

**Когда редактировать:**
- **Сменить провайдера:** изменить `base_url` и формат запроса
- **Добавить параметры:** расширить Config и добавить в `create()`

### llm/protocols.py - Protocol

**Ответственность:** Определение интерфейса LLM клиента.

```python
class LLMClientProtocol(Protocol):
    async def get_response(
        self,
        messages: list[Message],
        system_prompt: str
    ) -> str: ...
```

**Ключевые моменты:**
- **Protocol** - structural subtyping (утиная типизация с типами)
- Любой класс с методом `get_response()` совместим с Protocol

**Когда редактировать:** Добавление новых методов в интерфейс.

---

## Storage Layer

### storage/database.py - Database класс

**Ответственность:** Работа с SQLite (CRUD для messages).

```python
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None
    
    async def __aenter__(self) -> "Database":
        await self.connect()
        await self.init_db()
        return self
    
    async def __aexit__(self, ...):
        await self.close()
    
    async def save_message(self, message: Message) -> None:
        await self._connection.execute(
            "INSERT INTO messages (user_id, chat_id, role, content) VALUES (?, ?, ?, ?)",
            (message.user_id, message.chat_id, message.role, message.content)
        )
        await self._connection.commit()
    
    async def get_history(self, chat_id: int, user_id: int, limit: int) -> list[Message]:
        # SELECT с ORDER BY created_at DESC, LIMIT
        # Возврат от старых к новым (reversed)
    
    async def clear_history(self, chat_id: int, user_id: int) -> None:
        # DELETE WHERE chat_id=? AND user_id=?
```

**Ключевые моменты:**
- **Connection pool** - единое соединение на lifecycle бота
- **Context manager** - `async with` для graceful shutdown
- **Fail-fast** - `_ensure_connected()` проверяет что соединение открыто
- **Индекс** - `idx_chat_user` для быстрого поиска истории

**Когда редактировать:**
- **Добавить поле:** изменить CREATE TABLE, обновить save/get методы
- **Добавить метод:** новый CRUD метод для новой фичи

### storage/models.py - Message dataclass

**Ответственность:** Модель данных для сообщения.

```python
@dataclass
class Message:
    user_id: int
    chat_id: int
    role: Literal["user", "assistant"]  # Типобезопасность
    content: str
    id: int | None = None
    created_at: datetime | None = None
```

**Ключевые моменты:**
- **dataclass** - простота, авто `__init__` и `__repr__`
- **Literal** - mypy проверит что role только "user" или "assistant"
- **Optional поля** - id и created_at заполняются БД

**Когда редактировать:** Добавление нового поля в сообщение.

### storage/protocols.py - Protocol

**Ответственность:** Определение интерфейса Database.

```python
class DatabaseProtocol(Protocol):
    async def save_message(self, message: Message) -> None: ...
    async def get_history(self, chat_id: int, user_id: int, limit: int) -> list[Message]: ...
    async def clear_history(self, chat_id: int, user_id: int) -> None: ...
    async def connect(self) -> None: ...
    async def close(self) -> None: ...
```

**Когда редактировать:** Добавление нового метода в интерфейс.

---

## Тесты

### tests/test_bot_handlers.py

**Что тестирует:** Bot Layer (команды, обработка сообщений).

**Фикстуры:**
- `mock_llm_client` - AsyncMock для LLM
- `mock_database` - AsyncMock для Database
- `bot_handlers` - реальный BotHandlers с моками

**Примеры тестов:**
- `test_cmd_start_responds` - проверка ответа на /start
- `test_handle_message_saves_and_responds` - полный flow обработки

### tests/test_llm_client.py

**Что тестирует:** LLM Layer (формирование промптов, запросы).

**Фикстуры:**
- `mock_openai_client` - AsyncMock для openai client

**Примеры тестов:**
- `test_get_response_formats_messages_correctly` - проверка формата API messages
- `test_get_response_handles_errors` - обработка ошибок API

### tests/test_storage_database.py

**Что тестирует:** Storage Layer (CRUD операции).

**Фикстуры:**
- `db` - in-memory SQLite (`:memory:`)

**Примеры тестов:**
- `test_save_message_user` - сохранение сообщения
- `test_get_history_respects_limit` - проверка limit
- `test_clear_history` - очистка истории

---

## Точки расширения

### Добавить новую команду бота

1. Создать метод в `BotHandlers`:
```python
async def cmd_help(self, message: TelegramMessage) -> None:
    await message.answer("Помощь...")
```

2. Зарегистрировать в `_register_handlers()`:
```python
self.router.message(Command("help"))(self.cmd_help)
```

3. Написать тест в `test_bot_handlers.py`

### Добавить новое поле в Message

1. Обновить `storage/models.py`:
```python
@dataclass
class Message:
    # ... существующие поля
    metadata: dict | None = None  # новое поле
```

2. Обновить SQL в `database.py`:
```python
CREATE TABLE messages (
    ...
    metadata TEXT  -- JSON string
)
```

3. Обновить `save_message()` и `get_history()`

4. Написать миграцию (или пересоздать БД)

### Добавить новый слой (например, Cache)

1. Создать `src/cache/client.py` с классом
2. Создать `src/cache/protocols.py` с Protocol
3. Инициализировать в `main.py` и передать в DI
4. Использовать в нужных handlers
5. Написать тесты в `tests/test_cache.py`

---

## Навигационные подсказки

**Ищу где...**

| Задача | Файл |
|--------|------|
| Обрабатываются команды бота | `src/bot/handlers.py` |
| Формируются промпты для LLM | `src/llm/client.py` → `get_response()` |
| Сохраняется история | `src/storage/database.py` → `save_message()` |
| Читается история | `src/storage/database.py` → `get_history()` |
| Определена схема БД | `src/storage/database.py` → `init_db()` |
| Загружается конфигурация | `src/config.py` |
| Инициализируется бот | `src/main.py` |
| Тестируются handlers | `tests/test_bot_handlers.py` |
| Определены соглашения по коду | `.cursor/rules/conventions.mdc` |

**Хочу добавить...**

| Фича | Где начать |
|------|-----------|
| Новую команду | `bot/handlers.py` → метод + регистрация |
| Новый параметр LLM | `config.py` → добавить поле, `llm/client.py` → использовать |
| Новое поле в Message | `storage/models.py` → dataclass, `storage/database.py` → SQL |
| Новую интеграцию | `src/<integration>/` → client.py + protocols.py, `main.py` → DI |
| Middleware | `bot/bot.py` → `dp.middleware.setup()` |

---

## Дополнительные материалы

- **Визуализация проекта:** [visualization.md](visualization.md)
- **Архитектура:** [architecture.md](architecture.md)
- **Процесс разработки:** [development_workflow.md](development_workflow.md)
- **Соглашения по коду:** [../../.cursor/rules/conventions.mdc](../../.cursor/rules/conventions.mdc)

