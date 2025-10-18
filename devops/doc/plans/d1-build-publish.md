# План реализации спринта D1: Build & Publish

## Статус: ✅ Завершен

**Инструкция по настройке:** [d1-setup-guide.md](d1-setup-guide.md)

## Обзор

Настройка автоматической сборки и публикации Docker образов в GitHub Container Registry с использованием GitHub Actions. Образы будут доступны публично для использования в развертывании (D2, D3).

## 1. Введение в GitHub Actions

Создать документ `devops/doc/github-actions-guide.md` с краткой инструкцией:

- **Основы GitHub Actions**: что такое workflow, job, step, runner
- **Workflow файлы**: структура YAML, размещение в `.github/workflows/`
- **Триггеры**: `push`, `pull_request`, `workflow_dispatch`, фильтры по веткам
- **Secrets и переменные**: использование `${{ secrets.GITHUB_TOKEN }}`
- **Matrix strategy**: параллельная сборка нескольких образов
- **GitHub Container Registry**: публикация в ghcr.io, публичный vs приватный доступ
- **PR workflow**: как создавать Pull Request, как тестируется сборка на PR

## 2. GitHub Actions Workflow

Создать `.github/workflows/build.yml`:

**Триггеры:**
- `push` в ветку `main` - сборка и публикация с тегом `latest` + SHA
- `pull_request` - только сборка образов, без публикации

**Matrix strategy** для 3 сервисов:
```yaml
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

**Основные шаги:**
1. Checkout кода
2. Настройка Docker Buildx (для кэширования)
3. Логин в GitHub Container Registry (`ghcr.io`)
4. Генерация тегов: `latest`, `sha-$GITHUB_SHA`
5. Build образа с кэшированием layers
6. Push образа (только для main)

**Кэширование:**
- Использовать GitHub Actions Cache для Docker layers
- Ускорение повторных сборок

## 3. Публикация образов

**Registry**: `ghcr.io/OWNER/systech-aidd-SERVICE:TAG`

**Теги:**
- `latest` - последний стабильный образ из main
- `sha-COMMIT_SHA` - привязка к конкретному коммиту

**Public access:**
- После первой публикации настроить через GitHub UI: Package settings → Change visibility → Public
- Добавить инструкцию в документацию

## 4. Интеграция с docker-compose

Создать новый файл `docker-compose.registry.yml`:

```yaml
services:
  bot:
    image: ghcr.io/OWNER/systech-aidd-bot:latest
    # остальные настройки из docker-compose.yml
  
  api:
    image: ghcr.io/OWNER/systech-aidd-api:latest
    
  frontend:
    image: ghcr.io/OWNER/systech-aidd-frontend:latest
```

Оставить `docker-compose.yml` для локальной сборки (build).

**Использование:**
- Локальная разработка: `docker-compose up` (сборка из исходников)
- Запуск из registry: `docker-compose -f docker-compose.registry.yml up`
- Для D2/D3: использовать registry версию

## 5. Тестирование

**Локальная проверка pull образов:**
```bash
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
docker pull ghcr.io/OWNER/systech-aidd-api:latest
docker pull ghcr.io/OWNER/systech-aidd-frontend:latest
```

**Запуск с registry образами:**
```bash
docker-compose -f docker-compose.registry.yml up
```

**Проверка CI:**
- Создать тестовую ветку
- Открыть PR - проверить, что сборка проходит
- Merge в main - проверить, что образы публикуются

## 6. Документация

### devops/doc/github-actions-guide.md
Введение в GitHub Actions и workflow

### devops/doc/plans/sprint-d1-implementation.md
Итоговый план реализации спринта с результатами

### README.md
Добавить в начало файла:
- Badge статуса сборки: `![Build Status](https://github.com/OWNER/REPO/workflows/Build%20and%20Publish/badge.svg)`
- Секция "Docker образы" с инструкциями:
  - Список доступных образов в ghcr.io
  - Команды pull
  - Запуск через docker-compose.registry.yml

### devops/doc/devops-roadmap.md
Обновить статус D1 на "✅ Завершен" и добавить ссылку на план

## 7. Настройка permissions

**GitHub Settings:**
- Settings → Actions → General → Workflow permissions
- Выбрать "Read and write permissions"
- Включить "Allow GitHub Actions to create and approve pull requests"

**Package visibility:**
- После первой публикации: Packages → systech-aidd-* → Package settings
- Change visibility → Public
- Подтвердить изменение

Добавить инструкцию в документацию.

## Файлы для создания/изменения

1. `.github/workflows/build.yml` - новый workflow
2. `docker-compose.registry.yml` - compose файл для registry образов
3. `devops/doc/github-actions-guide.md` - введение в GitHub Actions
4. `devops/doc/plans/sprint-d1-implementation.md` - итоговый план
5. `README.md` - обновить (badge, секция про образы)
6. `devops/doc/devops-roadmap.md` - обновить статус

## MVP требования

✅ Простота настройки - один workflow файл
✅ Автоматическая сборка - на push в main
✅ Публикация в ghcr.io - через GITHUB_TOKEN
✅ Public access - инструкция по настройке
✅ Готовность к D2/D3 - registry образы доступны
✅ Документация на русском - все файлы

❌ Не включаем (пока):
- Lint checks
- Запуск тестов
- Security scanning
- Multi-platform builds (linux/amd64, linux/arm64)

## Задачи

- [ ] Создать devops/doc/github-actions-guide.md с введением в GitHub Actions
- [ ] Создать .github/workflows/build.yml с matrix strategy для 3 образов
- [ ] Создать docker-compose.registry.yml для использования образов из ghcr.io
- [ ] Обновить README.md: добавить badge и секцию про Docker образы
- [ ] Добавить инструкцию по настройке GitHub permissions в guide
- [ ] Создать devops/doc/plans/sprint-d1-implementation.md с итоговым планом
- [ ] Обновить devops/doc/devops-roadmap.md - статус D1 и ссылка на план

