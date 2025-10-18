# Спринт D1: Build & Publish - Инструкция по настройке

## Быстрый старт

После реализации спринта D1 выполните следующие шаги для настройки автоматической публикации образов.

## 1. Настройка GitHub Permissions

### Workflow permissions

1. Перейдите в ваш репозиторий на GitHub
2. Settings → Actions → General → Workflow permissions
3. Выберите: **"Read and write permissions"**
4. (Опционально) Включите: **"Allow GitHub Actions to create and approve pull requests"**
5. Нажмите **"Save"**

**Зачем это нужно:**
Workflow должен иметь права на публикацию образов в GitHub Container Registry.

## 2. Первый запуск

### Проверка workflow

1. Убедитесь что все файлы закоммичены:
```bash
git add .
git commit -m "chore: setup GitHub Actions workflow for D1"
```

2. Создайте тестовую ветку и PR для проверки:
```bash
git checkout -b test/d1-check
git push origin test/d1-check
```

3. Откройте Pull Request через GitHub UI
4. Проверьте что workflow запустился (Actions → Build and Publish)
5. Убедитесь что все три образа собираются успешно
6. Если всё ОК - merge PR в main

### Публикация образов

После merge в main:
1. Workflow автоматически запустится
2. Образы соберутся и опубликуются в ghcr.io
3. Проверьте в GitHub: Profile → Packages

## 3. Настройка публичного доступа

После первой публикации образы приватные. Сделайте их публичными:

### Для каждого образа (bot, api, frontend):

1. GitHub → Profile → Packages
2. Выберите пакет `systech-aidd-bot` (или api/frontend)
3. Package settings (справа внизу)
4. Danger Zone → Change package visibility
5. Выберите **"Public"**
6. Введите название пакета для подтверждения
7. Нажмите **"I understand, change package visibility"**

Повторите для всех трех образов.

## 4. Проверка работы

### Локальная проверка pull

```bash
# Замените OWNER на ваше имя пользователя/организации GitHub
docker pull ghcr.io/OWNER/systech-aidd-bot:latest
docker pull ghcr.io/OWNER/systech-aidd-api:latest
docker pull ghcr.io/OWNER/systech-aidd-frontend:latest
```

Если образы публичные - команды выполнятся без авторизации.

### Запуск из registry

```bash
# Установите переменную окружения
export GITHUB_REPOSITORY_OWNER=OWNER  # ваш GitHub username

# Или в Windows PowerShell
$env:GITHUB_REPOSITORY_OWNER="OWNER"

# Создайте .env если его нет
cp .env.example .env

# Отредактируйте .env - добавьте токены
# TELEGRAM_BOT_TOKEN=...
# OPENROUTER_API_KEY=...

# Запустите с образами из registry
docker-compose -f docker-compose.registry.yml up -d

# Проверьте логи
docker-compose -f docker-compose.registry.yml logs -f
```

### Проверка доступности

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## 5. Обновление README

В README.md замените плейсхолдер `OWNER` на ваше имя пользователя:

```bash
# Найдите все вхождения OWNER и замените на ваш username
# В файлах: README.md, docker-compose.registry.yml
```

Или используйте переменную окружения `GITHUB_REPOSITORY_OWNER`.

## 6. Проверка badge

Badge в README.md должен показывать статус последней сборки:

```markdown
[![Build and Publish](https://github.com/OWNER/systech-aidd/workflows/Build%20and%20Publish/badge.svg)](https://github.com/OWNER/systech-aidd/actions)
```

Замените `OWNER` на ваше имя пользователя. После этого badge будет работать.

## Troubleshooting

### Workflow не запускается

**Проблема:** После push workflow не запустился.

**Решение:**
1. Проверьте что файл `.github/workflows/build.yml` существует
2. Проверьте что push был в ветку `main` или это был PR
3. Проверьте Actions → Build and Publish - может быть в очереди

### Ошибка прав при публикации

**Проблема:** `Error: failed to solve: failed to push ghcr.io/...`

**Решение:**
1. Проверьте Settings → Actions → Workflow permissions
2. Должен быть выбран "Read and write permissions"
3. Повторите push (или re-run workflow)

### Образы не скачиваются без авторизации

**Проблема:** `Error: pull access denied for ghcr.io/...`

**Решение:**
1. Сделайте образы публичными (см. шаг 3 выше)
2. Проверьте Package settings → Visibility = Public

### Badge не отображается

**Проблема:** Badge показывает "unknown" или не загружается.

**Решение:**
1. Замените `OWNER` в URL badge на ваше имя пользователя
2. Проверьте что workflow называется именно "Build and Publish"
3. Дождитесь первого успешного запуска workflow

## Полезные команды

### Просмотр образов в registry

```bash
# Список тегов
docker pull ghcr.io/OWNER/systech-aidd-bot --all-tags

# Информация об образе
docker image inspect ghcr.io/OWNER/systech-aidd-bot:latest
```

### Очистка локальных образов

```bash
# Удалить все образы systech-aidd
docker images | grep systech-aidd | awk '{print $3}' | xargs docker rmi

# Удалить неиспользуемые образы
docker image prune -a
```

### Переключение между режимами

```bash
# Локальная разработка (сборка из исходников)
docker-compose up -d

# Production (готовые образы из registry)
docker-compose -f docker-compose.registry.yml up -d

# Остановка любого режима
docker-compose down
# или
docker-compose -f docker-compose.registry.yml down
```

## Готово!

После выполнения всех шагов:
- ✅ Workflow автоматически собирает образы при push в main
- ✅ Образы публикуются в ghcr.io и доступны публично
- ✅ Badge в README показывает статус сборки
- ✅ Можно использовать готовые образы для быстрого запуска

Переходите к спринту D2 для развертывания на сервер!

