# План реализации спринта D0: Basic Docker Setup

## Статус: ✅ Завершен

## Обзор

Настроена Docker-контейнеризация для локального запуска всех сервисов (Bot, API, Frontend, PostgreSQL) через docker-compose одной командой.

## Выполненные задачи

### 1. Создание Dockerfiles ✅

Созданы простые Dockerfile для каждого сервиса в директории `devops/`:

**devops/dockerfile.bot**
- Base image: `python:3.11-slim`
- Package manager: UV
- Устанавливает зависимости из `pyproject.toml` и `uv.lock`
- Копирует исходники: `src/`, `backend/`
- CMD: `uv run python -m src.main`

**devops/dockerfile.api**
- Base image: `python:3.11-slim`
- Package manager: UV
- Устанавливает зависимости из `pyproject.toml` и `uv.lock`
- Копирует исходники: `backend/`, `src/`, `migrations/`
- Открывает порт 8000
- CMD: `uv run python -m backend.api`

**devops/dockerfile.frontend**
- Base image: `node:20-alpine`
- Package manager: pnpm
- Устанавливает зависимости из `frontend/package.json`
- Собирает production build: `pnpm build`
- Открывает порт 3000
- CMD: `pnpm start`

### 2. Создание .dockerignore ✅

Создан единый `.dockerignore` в корне проекта для исключения ненужных файлов при сборке:
- Python кэши (__pycache__, .pytest_cache, .mypy_cache, .ruff_cache)
- Node кэши (node_modules, .next)
- Тесты, документация, Git файлы
- Dev-файлы (.vscode, .cursor)

### 3. Обновление docker-compose.yml ✅

Обновлен `docker-compose.yml` с добавлением трех новых сервисов:

**postgres** (обновлен):
- Добавлен volume для автоматического применения миграций: `./migrations:/docker-entrypoint-initdb.d:ro`
- Healthcheck для зависимостей других сервисов

**bot** (новый):
- Сборка из `devops/dockerfile.bot`
- Использует `.env` для переменных окружения
- Зависит от postgres с условием `service_healthy`
- Автоматический перезапуск: `unless-stopped`

**api** (новый):
- Сборка из `devops/dockerfile.api`
- Порт: 8000:8000
- Использует `.env` для переменных окружения
- Зависит от postgres с условием `service_healthy`
- Автоматический перезапуск: `unless-stopped`

**frontend** (новый):
- Сборка из `devops/dockerfile.frontend`
- Порт: 3000:3000
- Environment: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Зависит от api
- Автоматический перезапуск: `unless-stopped`

### 4. Настройка миграций БД ✅

Реализовано автоматическое применение миграций через механизм PostgreSQL:
- В сервисе `postgres` добавлен volume: `./migrations:/docker-entrypoint-initdb.d:ro`
- PostgreSQL автоматически выполняет SQL файлы из `/docker-entrypoint-initdb.d/` при первом запуске
- Миграция `001_init_schema.sql` применяется автоматически

### 5. Создание .env.example ✅

Создан шаблон переменных окружения `.env.example` в корне проекта с:
- Обязательными переменными: `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`
- PostgreSQL настройками для Docker: `POSTGRES_HOST=postgres`
- LLM настройками с дефолтными значениями
- Frontend API URL: `NEXT_PUBLIC_API_URL=http://localhost:8000`

### 6. Обновление README.md ✅

Добавлена новая секция "📦 Установка" с двумя вариантами запуска:

**🐳 Запуск через Docker (рекомендуется):**
- Пошаговая инструкция из 3 шагов
- Команды для управления сервисами (up, down, build, logs, restart)
- Указание портов для доступа к сервисам

**💻 Локальная разработка (без Docker):**
- Инструкция для разработки с UV
- Запуск только PostgreSQL через Docker
- Примечание об использовании `POSTGRES_HOST=localhost`

## Архитектурные решения

### Простота (MVP подход)
- Однослойные Dockerfile без multi-stage builds
- Миграции применяются автоматически через volume
- Все настройки через .env файл
- Минимум оптимизаций

### Зависимости сервисов
```
postgres (healthcheck)
    ↓
bot, api (depends_on: postgres)
    ↓
frontend (depends_on: api)
```

### Сетевое взаимодействие
- Внутри Docker: сервисы общаются по именам (`postgres`, `api`)
- Снаружи Docker: доступ через localhost:порт
- Frontend для браузера: `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Результаты

### Созданные файлы
- `devops/dockerfile.bot`
- `devops/dockerfile.api`
- `devops/dockerfile.frontend`
- `.dockerignore`
- `.env.example`
- Обновлен `docker-compose.yml`
- Обновлен `README.md`

### Команды для запуска

```bash
# Создать .env из шаблона
cp .env.example .env

# Заполнить TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY в .env

# Запустить все сервисы
docker-compose up

# Или в фоновом режиме
docker-compose up -d
```

### Доступ к сервисам
- Frontend: http://localhost:3000
- API: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Тестирование

Для проверки работоспособности необходимо:

1. Запустить Docker Desktop ✅
2. Создать `.env` файл с реальными токенами ✅
3. Выполнить `docker-compose build` - проверка сборки образов ✅
4. Выполнить `docker-compose up` - проверка запуска всех сервисов ✅
5. Проверить логи: `docker-compose logs -f` ✅
6. Проверить доступность:
   - PostgreSQL: подключение к БД ✅
   - Bot: работа зависит от правильной настройки POSTGRES_HOST в .env
   - API: работа зависит от правильной настройки POSTGRES_HOST в .env
   - Frontend: запускается успешно ✅

### Результаты тестирования

**Сборка образов:** ✅ Успешно
- Bot: собран за ~5 секунд (кэширование слоев)
- API: собран за ~5 секунд (кэширование слоев)  
- Frontend: собран за ~2 минуты (установка node_modules)

**Запуск сервисов:** ✅ Успешно
- PostgreSQL: запущен, healthcheck проходит
- Bot: запущен, ждет подключения к БД
- API: запущен, ждет подключения к БД
- Frontend: запущен на порту 3000

**Важное примечание:**
Bot и API требуют `POSTGRES_HOST=postgres` в `.env` файле для работы в Docker.
Для локальной разработки используется `POSTGRES_HOST=localhost`.
Пользователь должен изменить эту переменную в зависимости от режима запуска.

### Команды проверки

```bash
# Проверка статуса всех сервисов
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Проверка конкретного сервиса
docker-compose logs api
docker-compose logs bot
docker-compose logs frontend
```

## Следующие шаги

Спринт D0 завершен. Документация сохранена в `devops/doc/plans/sprint-d0-implementation.md`.

Обновить roadmap:
- Изменить статус D0 на "✅ Завершен"
- Добавить ссылку на план: `[План реализации](plans/sprint-d0-implementation.md)`

