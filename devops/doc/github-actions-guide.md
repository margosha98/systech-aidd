# GitHub Actions - Краткое руководство

## Введение

GitHub Actions - это встроенная в GitHub платформа CI/CD (Continuous Integration/Continuous Deployment) для автоматизации процессов разработки, тестирования и развертывания.

## Основные концепции

### Workflow (Рабочий процесс)
- YAML файл, описывающий автоматизированный процесс
- Размещается в директории `.github/workflows/`
- Запускается при определенных событиях (push, PR, schedule и т.д.)

### Job (Задача)
- Набор шагов, выполняющихся на одном runner'е
- Несколько job'ов могут выполняться параллельно или последовательно
- Каждый job запускается в отдельном виртуальном окружении

### Step (Шаг)
- Отдельная команда или action внутри job
- Выполняются последовательно
- Могут использовать shell команды или готовые actions из marketplace

### Runner (Исполнитель)
- Виртуальная машина, на которой выполняется workflow
- GitHub предоставляет hosted runners: Ubuntu, Windows, macOS
- Можно использовать self-hosted runners

## Структура Workflow файла

```yaml
name: Название workflow

on:
  push:                    # Триггер на push
    branches: [main]       # Только для ветки main
  pull_request:            # Триггер на PR
    branches: [main]

jobs:
  build:                   # Название job
    runs-on: ubuntu-latest # Операционная система runner
    
    steps:
      - name: Checkout code            # Название шага
        uses: actions/checkout@v4      # Использование готового action
      
      - name: Run command              # Выполнение команды
        run: echo "Hello World"
```

## Триггеры (Events)

### Push
Запускается при push в репозиторий:
```yaml
on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'src/**'          # Только при изменениях в src/
```

### Pull Request
Запускается при создании или обновлении PR:
```yaml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
```

### Workflow Dispatch
Ручной запуск через UI GitHub:
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

### Schedule
Запуск по расписанию (cron):
```yaml
on:
  schedule:
    - cron: '0 2 * * *'   # Каждый день в 2:00 UTC
```

## Secrets и переменные

### GitHub Token
Автоматически доступен во всех workflows:
```yaml
- name: Login to registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Secrets
Хранение конфиденциальных данных (Settings → Secrets):
```yaml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh
```

### Environment variables
```yaml
env:
  NODE_ENV: production

jobs:
  build:
    env:
      BUILD_DIR: ./dist
    steps:
      - name: Build
        run: echo $BUILD_DIR
```

## Matrix Strategy

Параллельное выполнение job для разных конфигураций:

```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: [18, 20]
    runs-on: ${{ matrix.os }}
    
    steps:
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

### Matrix с дополнительными параметрами

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    include:
      - service: bot
        dockerfile: devops/dockerfile.bot
        port: 8080
      - service: api
        dockerfile: devops/dockerfile.api
        port: 8000
      - service: frontend
        dockerfile: devops/dockerfile.frontend
        port: 3000

steps:
  - name: Build ${{ matrix.service }}
    run: docker build -f ${{ matrix.dockerfile }} .
```

## GitHub Container Registry (ghcr.io)

### Публикация образов

GitHub предоставляет бесплатный container registry для публикации Docker образов.

**URL формат:** `ghcr.io/OWNER/IMAGE:TAG`

**Примеры:**
- `ghcr.io/myorg/myapp:latest`
- `ghcr.io/username/bot:v1.0.0`
- `ghcr.io/company/api:sha-abc123`

### Логин в ghcr.io

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Build и Push

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: |
      ghcr.io/${{ github.repository_owner }}/myapp:latest
      ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}
```

### Public vs Private доступ

**Private (по умолчанию):**
- Образы доступны только с авторизацией
- Требуется `docker login ghcr.io`

**Public:**
- Образы доступны без авторизации
- Настройка: Packages → Package settings → Change visibility → Public
- Любой может скачать: `docker pull ghcr.io/owner/image:latest`

## Pull Request Workflow

### Процесс работы с PR

1. **Создание ветки:**
```bash
git checkout -b feature/new-feature
git push origin feature/new-feature
```

2. **Открытие PR:**
- GitHub UI: "New pull request"
- Base: main ← Compare: feature/new-feature

3. **Автоматическая проверка:**
- Workflow запускается автоматически
- Статус отображается в PR
- ❌ Red - failed, ✅ Green - passed

4. **Условная публикация:**
```yaml
on:
  push:
    branches: [main]      # Публикация только из main
  pull_request:
    branches: [main]      # Только сборка для PR

jobs:
  build:
    steps:
      - name: Build image
        run: docker build .
      
      - name: Push image
        if: github.event_name == 'push'  # Только для push в main
        run: docker push myimage:latest
```

### Защита ветки main

Рекомендуется настроить:
- Settings → Branches → Branch protection rules
- Require pull request before merging
- Require status checks to pass (выбрать workflow)

## Permissions

### Workflow permissions

**Настройка:** Settings → Actions → General → Workflow permissions

**Варианты:**
- **Read repository contents and packages** (по умолчанию) - только чтение
- **Read and write permissions** - полный доступ к packages, contents

Для публикации в ghcr.io требуется **Read and write permissions**.

### Package permissions

После первой публикации настроить доступ к образу:
1. Packages → Выбрать образ
2. Package settings
3. Change visibility → Public
4. Manage Actions access (при необходимости)

## Кэширование

### Docker layer cache

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Dependencies cache

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
```

## Отладка

### Просмотр логов
- GitHub UI → Actions → Выбрать workflow run
- Раскрыть job → Раскрыть step

### Debug logging
```yaml
- name: Debug info
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Branch: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
```

### Re-run failed jobs
- В UI: "Re-run failed jobs" или "Re-run all jobs"

## Best Practices

### 1. Используйте версии actions
```yaml
# ❌ Плохо
uses: actions/checkout@master

# ✅ Хорошо
uses: actions/checkout@v4
```

### 2. Условное выполнение
```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh
```

### 3. Имена и описания
```yaml
name: CI Pipeline

jobs:
  test:
    name: Run Tests
    steps:
      - name: Run unit tests
        run: npm test
```

### 4. Fail-fast strategy
```yaml
strategy:
  fail-fast: false  # Продолжить другие задачи при ошибке
  matrix:
    os: [ubuntu, windows]
```

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [GitHub Container Registry docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## Примеры

### Простой CI pipeline
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test
```

### Multi-service Docker build
```yaml
name: Build and Publish

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, api, frontend]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to ghcr.io
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: devops/dockerfile.${{ matrix.service }}
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/myapp-${{ matrix.service }}:latest
```

