# План технического долга Systech AIDD Bot

## 📊 Отчет по прогрессу

| Итерация | Задача | Статус | Дата завершения |
|----------|--------|--------|-----------------|
| 1 | Инструменты качества | ✅ Завершено | 2025-10-11 |
| 2 | Типы и протоколы | ✅ Завершено | 2025-10-11 |
| 3 | Database connection pool | ✅ Завершено | 2025-10-11 |
| 4 | Рефакторинг handlers (DI) | ✅ Завершено | 2025-10-11 |
| 5 | Обновление main.py и graceful shutdown | ✅ Завершено | 2025-10-11 |
| 6 | Тесты для Database | ❌ Пропущено | - |
| 7 | Тесты для LLMClient | 📋 Запланировано | - |
| 8 | Финальная проверка и документация | 📋 Запланировано | - |

**Легенда статусов:**
- ✅ Завершено
- ⏳ В работе
- 📋 Запланировано
- ⏸️ На паузе
- ❌ Отменено

---

## Итерации рефакторинга

### Итерация 1: Инструменты качества
**Цель:** Настроить ruff, mypy, pytest и Makefile команды

#### Задачи
- [x] Добавить dev-зависимости в `pyproject.toml`: ruff, mypy, pytest, pytest-asyncio, pytest-cov, pytest-mock
- [x] Добавить конфигурацию `[tool.ruff]` (line-length=100, select правил)
- [x] Добавить конфигурацию `[tool.mypy]` (strict=true)
- [x] Добавить конфигурацию `[tool.pytest.ini_options]`
- [x] Обновить `Makefile`: добавить команды lint, format, typecheck, test, quality
- [x] Создать структуру `tests/` с `__init__.py`

#### Проверки
- [x] `make format` - форматирование проходит
- [x] `make lint` - линтер запускается (могут быть ошибки, исправим в следующих итерациях)
- [x] `make typecheck` - mypy запускается
- [x] Код соответствует `conventions.mdc` (KISS, type hints)
- [x] Процесс соответствует `workflow.mdc` (согласование перед реализацией)

**Тест:** `make quality` выполняет все проверки последовательно (format + lint + typecheck + test)

**Формат коммита:**
```
refactor: итерация 1 - настройка инструментов качества

- Добавлены ruff, mypy, pytest в dev-зависимости
- Настроены конфигурации линтера и type checker
- Расширен Makefile командами проверки качества

Проверки: make quality ✅
```

---

### Итерация 2: Типы и протоколы
**Цель:** Исправить типы и создать Protocol для абстракций

#### Задачи
- [x] Исправить `src/storage/models.py`: `Message.role: str` → `Literal["user", "assistant"]`
- [x] Создать `src/storage/protocols.py` с `DatabaseProtocol`
- [x] Создать `src/llm/protocols.py` с `LLMClientProtocol`
- [x] Добавить импорт Protocol в `src/storage/__init__.py`
- [x] Добавить импорт Protocol в `src/llm/__init__.py`

#### Проверки
- [x] `make format` - код отформатирован
- [x] `make lint` - нет ошибок линтера
- [x] `make typecheck` - mypy запускается (ошибки будут исправлены в итерациях 3-5)
- [x] Код соответствует `conventions.mdc` (type hints обязательны)
- [x] Процесс соответствует `workflow.mdc` (обновлен tasklist)

**Тест:** `make typecheck` показывает 0 ошибок, протоколы импортируются без проблем

**Формат коммита:**
```
refactor: итерация 2 - типы и протоколы

- Message.role теперь Literal["user", "assistant"]
- Добавлены Protocol для Database и LLMClient
- Улучшена типизация для mypy

Проверки: make quality ✅
```

---

### Итерация 3: Database connection pool
**Цель:** Переделать Database на единое соединение с context manager

#### Задачи
- [x] Добавить атрибут `self._connection: aiosqlite.Connection | None = None` в `Database.__init__`
- [x] Реализовать `async def connect(self) -> None` - открытие соединения
- [x] Реализовать `async def close(self) -> None` - закрытие соединения
- [x] Реализовать `async def __aenter__(self)` и `async def __aexit__(self, ...)` для context manager
- [x] Переделать `save_message()` на использование `self._connection`
- [x] Переделать `get_history()` на использование `self._connection`
- [x] Переделать `clear_history()` на использование `self._connection`
- [x] Добавить проверку `if not self._connection: raise RuntimeError("Database not connected")`

#### Проверки
- [x] `make format` и `make lint` - чисто
- [x] `make typecheck` - типы корректны
- [x] Бот запускается и работает с новой версией Database
- [x] Код соответствует `conventions.mdc` (async-first, fail fast)
- [x] Процесс соответствует `workflow.mdc` (тест пройден)

**Тест:** Бот работает, сообщения сохраняются, история загружается корректно

**Формат коммита:**
```
refactor: итерация 3 - Database connection pool

- Единое соединение вместо создания на каждый запрос
- Реализован context manager для Database
- Добавлена fail-fast проверка соединения

Проверки: make quality ✅
```

---

### Итерация 4: Рефакторинг handlers (убрать глобальные)
**Цель:** Убрать глобальные переменные, внедрить DI через класс

#### Задачи
- [x] Удалить глобальные переменные из `handlers.py` (строки 16-19: llm_client, database, config)
- [x] Удалить функцию `setup_handlers()` (строки 22-34)
- [x] Создать класс `BotHandlers` с конструктором принимающим (llm_client, database, config)
- [x] Создать `self.router = Router()` внутри класса
- [x] Переделать декоратор `@router.message(Command("start"))` на метод класса
- [x] Переделать декоратор `@router.message()` на метод класса
- [x] Добавить метод `_register_handlers()` для регистрации handlers
- [x] Обновить `src/bot/bot.py` для работы с `BotHandlers.router`

#### Проверки
- [x] `make format`, `make lint`, `make typecheck` - всё зелёное
- [x] Бот работает с новой архитектурой
- [x] Код соответствует `conventions.mdc` (1 класс = 1 файл, нет глобального state)
- [x] Процесс соответствует `workflow.mdc` (согласование, тест)

**Тест:** Бот запускается, команда /start работает, текстовые сообщения обрабатываются

**Формат коммита:**
```
refactor: итерация 4 - DI в handlers

- Убраны глобальные переменные
- Создан класс BotHandlers с внедрением зависимостей
- Улучшена тестируемость кода

Проверки: make quality ✅
```

---

### Итерация 5: Обновление main.py и graceful shutdown
**Цель:** Интегрировать новую архитектуру в main.py

#### Задачи
- [x] Обновить `main.py`: использовать `async with database:` вместо `await database.connect()`
- [x] Создать экземпляр `BotHandlers` с зависимостями
- [x] Передать `bot_handlers.router` в диспетчер
- [x] Удалить вызов `setup_handlers()`
- [x] Обновить `create_bot()` для работы с внешним router
- [x] Добавить graceful shutdown для Database (автоматически через context manager)

#### Проверки
- [x] `make format`, `make lint` - чисто
- [x] Context manager автоматически закрывает соединение
- [x] Код соответствует `conventions.mdc` (async-first, context manager)
- [x] Процесс соответствует `workflow.mdc` (обновлен tasklist)

**Тест:** Запуск бота, обработка сообщений, graceful shutdown (Ctrl+C) без ошибок в логах

**Формат коммита:**
```
refactor: итерация 5 - main.py и graceful shutdown

- Интегрирована новая архитектура с DI
- Добавлен context manager для Database
- Реализован graceful shutdown

Проверки: make quality ✅
```

---

### Итерация 6: Тесты для Database
**Цель:** Написать unit-тесты для Database с fixtures

#### Задачи
- [ ] Создать `tests/conftest.py`
- [ ] Добавить fixture `test_database()` с in-memory SQLite (`:memory:`)
- [ ] Создать `tests/test_database.py`
- [ ] Тест `test_init_db()` - проверка создания таблицы messages
- [ ] Тест `test_save_message()` - сохранение сообщения в БД
- [ ] Тест `test_get_history_order()` - правильный порядок (от старых к новым)
- [ ] Тест `test_get_history_limit()` - лимит работает корректно
- [ ] Тест `test_clear_history()` - удаление всех сообщений пользователя

#### Проверки
- [ ] `make test` - все тесты проходят
- [ ] `make typecheck` - тесты типизированы
- [ ] Покрытие Database > 80% (`pytest --cov=src/storage/database`)
- [ ] Код соответствует `conventions.mdc` (тестируем критичное)
- [ ] Процесс соответствует `workflow.mdc` (тест выполнен)

**Тест:** `make test` - все тесты для Database зелёные, покрытие > 80%

**Формат коммита:**
```
test: итерация 6 - тесты для Database

- Добавлены unit-тесты для всех методов Database
- Покрытие > 80%
- Используется in-memory SQLite для тестов

Проверки: make quality ✅
```

---

### Итерация 7: Тесты для LLMClient
**Цель:** Написать unit-тесты для LLMClient с моками

#### Задачи
- [ ] Добавить fixture `mock_config()` в `tests/conftest.py`
- [ ] Создать `tests/test_llm_client.py`
- [ ] Тест `test_get_response_success()` - успешный ответ (мок AsyncOpenAI)
- [ ] Тест `test_get_response_error()` - обработка ошибки API
- [ ] Тест `test_get_response_formats_messages()` - проверка формирования messages (system + history)
- [ ] Тест `test_get_response_uses_config()` - проверка использования параметров из Config

#### Проверки
- [ ] `make test` - все тесты проходят
- [ ] Покрытие LLMClient > 80% (`pytest --cov=src/llm/client`)
- [ ] `make typecheck` - чисто
- [ ] Код соответствует `conventions.mdc`
- [ ] Процесс соответствует `workflow.mdc`

**Тест:** `make test` - все тесты Database и LLMClient проходят, общее покрытие > 80%

**Формат коммита:**
```
test: итерация 7 - тесты для LLMClient

- Добавлены unit-тесты с моками AsyncOpenAI
- Покрытие > 80%
- Проверена обработка ошибок API

Проверки: make quality ✅
```

---

### Итерация 8: Финальная проверка и документация
**Цель:** Комплексная проверка всех улучшений

#### Задачи
- [ ] Запустить `make quality` - все проверки должны пройти
- [ ] Проверить покрытие тестами: `pytest --cov=src --cov-report=term-missing`
- [ ] Обновить `README.md` - добавить секцию "Quality Tools"
- [ ] Документировать команды Makefile (lint, format, typecheck, test, quality)
- [ ] Проверить весь код на соответствие `conventions.mdc` (KISS, async-first, type hints)
- [ ] Проверить workflow на соответствие `workflow.mdc`
- [ ] Финальное end-to-end тестирование: запуск → диалог → /reset → graceful shutdown

#### Проверки
- [ ] `make quality` - всё зелёное (format + lint + typecheck + test)
- [ ] Покрытие тестами > 80% для критичных модулей (Database, LLMClient)
- [ ] Все соглашения `conventions.mdc` соблюдены
- [ ] Все пункты `workflow.mdc` выполнены
- [ ] Бот работает стабильно в production режиме

**Тест:** Полный цикл - запуск бота, диалог из нескольких сообщений, /reset, graceful shutdown (Ctrl+C)

**Формат коммита:**
```
docs: итерация 8 - финальная проверка и документация

- Обновлен README.md с описанием Quality Tools
- Все проверки качества пройдены
- Покрытие тестами > 80%

Проверки: make quality ✅
```

---

## 📝 Примечания

### Порядок работы
1. Выполнять итерации строго последовательно
2. После каждой итерации обязательно тестировать
3. Обновлять таблицу прогресса
4. Коммитить после успешного прохождения всех проверок

### Критерии завершения итерации
- ✅ Все чекбоксы задач отмечены
- ✅ Тест пройден успешно
- ✅ `make format && make lint && make typecheck` - чисто
- ✅ Код соответствует правилам `conventions.mdc`
- ✅ Workflow соответствует `workflow.mdc`

### Команды для проверки качества

```bash
# Форматирование кода
make format

# Проверка линтером
make lint

# Проверка типов
make typecheck

# Запуск тестов
make test

# Запуск всех проверок
make quality
```

### Отклонения от плана
- Если итерация блокируется - отметить статусом ⏸️
- Если требуются изменения - добавить в примечания
- Если итерация отменяется - отметить статусом ❌
- Если возникают проблемы с линтером/тестами - исправить перед переходом к следующей итерации

### Технический долг устранен
После завершения всех 8 итераций:
- ✅ Настроены автоматические инструменты контроля качества
- ✅ Убраны глобальные переменные, внедрен DI
- ✅ Database использует connection pool
- ✅ Протоколы для абстракций созданы
- ✅ Типизация улучшена (Literal, Protocol)
- ✅ Покрытие тестами > 80% для критичных модулей
- ✅ Graceful shutdown реализован
- ✅ Код соответствует SOLID, DRY, conventions.mdc


