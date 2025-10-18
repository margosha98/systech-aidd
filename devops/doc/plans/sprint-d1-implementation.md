# План реализации спринта D1: Build & Publish

## Статус: ✅ Завершен

## Обзор

Настроена автоматическая сборка и публикация Docker образов (bot, api, frontend) в GitHub Container Registry с использованием GitHub Actions. Образы доступны публично и готовы к использованию в развертывании (спринты D2, D3).

## Выполненные задачи

### 1. Введение в GitHub Actions ✅

Создан документ `devops/doc/github-actions-guide.md` с подробной инструкцией:

**Основные разделы:**
- Основы GitHub Actions: workflow, job, step, runner
- Структура workflow файлов и размещение в `.github/workflows/`
- Триггеры: push, pull_request, workflow_dispatch, schedule
- Secrets и переменные: GITHUB_TOKEN, environment variables
- Matrix strategy для параллельной сборки
- GitHub Container Registry (ghcr.io): публикация, public/private доступ
- PR workflow: создание, тестирование, merge
- Permissions: workflow и package settings
- Кэширование для ускорения сборки
- Best practices и примеры

### 2. GitHub Actions Workflow ✅

Создан файл `.github/workflows/build.yml` с полной автоматизацией сборки и публикации.

**Триггеры:**
- `push` в ветку `main` → сборка + публикация образов
- `pull_request` → только сборка для проверки (без публикации)

**Matrix strategy:**
```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    include:
      - service: bot
        dockerfile: devops/dockerfile.bot
      - service: api
        dockerfile: devops/dockerfile.api
      - service: frontend
        dockerfile: devops/dockerfile.frontend
```

**Основные шаги workflow:**
1. **Checkout кода** - `actions/checkout@v4`
2. **Настройка Docker Buildx** - `docker/setup-buildx-action@v3` для кэширования
3. **Логин в ghcr.io** - `docker/login-action@v3` (только для push в main)
4. **Генерация тегов** - `docker/metadata-action@v5`:
   - `latest` - для main ветки
   - `sha-<commit>` - привязка к коммиту
5. **Build и Push** - `docker/build-push-action@v5` с кэшированием layers

**Кэширование:**
- GitHub Actions Cache для Docker layers: `cache-from: type=gha`, `cache-to: type=gha,mode=max`
- Ускорение повторных сборок за счет переиспользования layers

**Условная публикация:**
- Push только при `github.event_name == 'push'`
- PR только собирает образы для проверки

### 3. Публикация образов ✅

**Registry:** GitHub Container Registry (`ghcr.io`)

**Именование образов:**
- `ghcr.io/${{ github.repository_owner }}/systech-aidd-bot:latest`
- `ghcr.io/${{ github.repository_owner }}/systech-aidd-api:latest`
- `ghcr.io/${{ github.repository_owner }}/systech-aidd-frontend:latest`

**Теги:**
- `latest` - последняя версия из main (автоматически)
- `sha-<commit>` - привязка к конкретному коммиту (для отката)

**Public access:**
После первой публикации образы нужно сделать публичными:
1. GitHub → Packages → Выбрать образ
2. Package settings → Change visibility → Public
3. Подтвердить изменение

Теперь образы доступны без авторизации:
```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
```

### 4. Интеграция с docker-compose ✅

Создан новый файл `docker-compose.registry.yml` для использования готовых образов из ghcr.io.

**Структура:**
- Сервисы `bot`, `api`, `frontend` используют образы из registry
- `postgres` остается локальным (стандартный образ)
- Все остальные настройки идентичны `docker-compose.yml`

**Использование переменной окружения:**
```yaml
image: ghcr.io/${GITHUB_REPOSITORY_OWNER:-yourusername}/systech-aidd-bot:latest
```

**Два режима работы:**

1. **Локальная разработка** - сборка из исходников:
```bash
docker-compose up
```

2. **Запуск из registry** - готовые образы:
```bash
docker-compose -f docker-compose.registry.yml up
```

**Преимущества для D2/D3:**
- Быстрое развертывание на сервере
- Не требуется исходный код на production
- Гарантированно работающие образы

### 5. Обновление документации ✅

#### README.md
Добавлены:
- **Badge статуса сборки:** `[![Build and Publish](https://github.com/OWNER/systech-aidd/workflows/Build%20and%20Publish/badge.svg)]`
- **Секция "🐳 Docker образы":**
  - Список доступных образов в ghcr.io
  - Команды для pull образов
  - Инструкция по запуску через `docker-compose.registry.yml`
  - Преимущества готовых образов

#### devops/doc/github-actions-guide.md
Создано полное руководство по GitHub Actions (см. пункт 1).

#### devops/doc/plans/sprint-d1-implementation.md
Текущий документ - итоговый план реализации спринта.

#### devops/doc/devops-roadmap.md
Обновлен статус D1 и добавлена ссылка на план.

### 6. Инструкции по настройке ✅

#### GitHub Permissions

**Workflow permissions** (для публикации в ghcr.io):
1. Settings → Actions → General → Workflow permissions
2. Выбрать: **"Read and write permissions"**
3. Включить: **"Allow GitHub Actions to create and approve pull requests"** (опционально)

**Package visibility** (публичный доступ):
1. После первой публикации: Packages → systech-aidd-bot/api/frontend
2. Package settings → Change visibility → **Public**
3. Подтвердить изменение

Инструкции добавлены в `devops/doc/github-actions-guide.md` в разделе "Permissions".

## Архитектурные решения

### Простота (MVP подход)

- **Один workflow файл** - все три образа в одном workflow
- **Matrix strategy** - параллельная сборка трех образов
- **GitHub-hosted runners** - используем бесплатные Ubuntu runners
- **Минимум шагов** - только необходимые действия
- **Кэширование** - встроенное через GitHub Actions Cache

### Два режима работы

1. **Локальная разработка:**
   - `docker-compose.yml` - сборка из исходников
   - Быстрая итерация, изменения видны сразу

2. **Production/Testing:**
   - `docker-compose.registry.yml` - готовые образы
   - Быстрый старт, надежность

### Условная публикация

- **PR:** только сборка → проверка что образы собираются
- **Main:** сборка + публикация → образы попадают в registry

Защита от случайной публикации "сырых" образов.

### Тегирование

- `latest` - всегда последняя версия, удобно для development
- `sha-<commit>` - версионирование, возможность отката

## Результаты

### Созданные файлы

1. `.github/workflows/build.yml` - GitHub Actions workflow
2. `docker-compose.registry.yml` - compose файл для registry образов
3. `devops/doc/github-actions-guide.md` - руководство по GitHub Actions
4. `devops/doc/plans/sprint-d1-implementation.md` - итоговый план (этот файл)

### Обновленные файлы

1. `README.md` - badge и секция про Docker образы
2. `devops/doc/devops-roadmap.md` - статус D1

### Команды для использования

#### Локальная разработка (сборка из исходников)
```bash
docker-compose up -d
docker-compose logs -f
```

#### Использование готовых образов из registry
```bash
# Установить переменную окружения с именем владельца
export GITHUB_REPOSITORY_OWNER=yourusername

# Или в Windows PowerShell
$env:GITHUB_REPOSITORY_OWNER="yourusername"

# Запустить с образами из registry
docker-compose -f docker-compose.registry.yml up -d
```

#### Ручное скачивание образов
```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
docker pull ghcr.io/OWNER/systech-aidd-api:latest
docker pull ghcr.io/OWNER/systech-aidd-frontend:latest
```

#### Использование конкретной версии (по commit SHA)
```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:sha-abc1234
```

## Тестирование

### Проверка CI

1. **Создать тестовую ветку:**
```bash
git checkout -b test/d1-workflow
git push origin test/d1-workflow
```

2. **Открыть Pull Request:**
- GitHub UI: "New pull request"
- Base: main ← Compare: test/d1-workflow
- Workflow автоматически запустится

3. **Проверить сборку:**
- Actions → Выбрать workflow run
- Проверить что все 3 образа собираются успешно
- Образы НЕ публикуются (это PR)

4. **Merge в main:**
- После успешной проверки: "Merge pull request"
- Workflow запустится снова
- Образы соберутся И опубликуются в ghcr.io

### Локальная проверка образов

После первой публикации:

```bash
# Сделать образы публичными (см. инструкцию выше)

# Скачать образы
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
docker pull ghcr.io/OWNER/systech-aidd-api:latest
docker pull ghcr.io/OWNER/systech-aidd-frontend:latest

# Запустить через docker-compose.registry.yml
export GITHUB_REPOSITORY_OWNER=OWNER
docker-compose -f docker-compose.registry.yml up -d

# Проверить логи
docker-compose -f docker-compose.registry.yml logs -f

# Проверить доступность
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

## Готовность к следующим спринтам

### D2: Развертывание на сервер (ручное)

✅ Образы публикуются автоматически в ghcr.io
✅ Образы публичные - не требуется авторизация на сервере
✅ `docker-compose.registry.yml` готов к использованию
✅ Тегирование `latest` и `sha-<commit>` для версионирования

**Что нужно для D2:**
- Инструкция по ручному деплою на сервер
- Скопировать `docker-compose.registry.yml` и `.env` на сервер
- Выполнить `docker-compose -f docker-compose.registry.yml up -d`

### D3: Auto Deploy

✅ CI уже настроен и работает
✅ Образы публикуются автоматически
✅ Есть опыт работы с GitHub Actions

**Что нужно для D3:**
- Добавить workflow для деплоя с `workflow_dispatch`
- SSH подключение к серверу
- Pull образов и restart сервисов
- Настроить GitHub secrets (SSH_KEY, HOST, USER)

## MVP требования - выполнено

✅ **Простота настройки** - один workflow файл, matrix strategy
✅ **Автоматическая сборка** - при push в main
✅ **Публикация в ghcr.io** - через GITHUB_TOKEN
✅ **Public access** - инструкция по настройке visibility
✅ **Готовность к D2/D3** - образы доступны, compose файл готов
✅ **Документация на русском** - все файлы с подробными инструкциями

❌ **Не включено (как и планировалось):**
- Lint checks (добавим позже)
- Запуск тестов (добавим позже)
- Security scanning (добавим позже)
- Multi-platform builds (добавим позже)

## Следующие шаги

Спринт D1 завершен. Документация сохранена в `devops/doc/plans/sprint-d1-implementation.md`.

**Обновить roadmap:**
- ✅ Изменить статус D1 на "✅ Завершен"
- ✅ Добавить ссылку на план: `[План реализации](plans/sprint-d1-implementation.md)`

**Перед началом D2:**
1. Протестировать первую публикацию образов (push в main)
2. Сделать образы публичными через GitHub UI
3. Проверить локальный pull и запуск через `docker-compose.registry.yml`
4. Убедиться что badge в README отображается корректно

**Подготовка к D2:**
- Подготовить доступ к серверу (SSH ключи, IP адрес)
- Определить требования к серверу (ОС, Docker, ресурсы)
- Спланировать структуру директорий на сервере
- Подготовить шаблон `.env.production`

