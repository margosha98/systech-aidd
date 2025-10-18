# План тестирования Sprint D1

## Текущий статус
✅ Все файлы созданы и закоммичены  
📋 Готовы к тестированию

---

## Шаг 1: Push в GitHub и настройка Permissions

### 1.1 Push ветки devops
```bash
git push origin devops
```

### 1.2 Настройка GitHub Permissions (ВАЖНО!)
**Без этого workflow не сможет публиковать образы!**

1. Открыть репозиторий на GitHub
2. Settings → Actions → General
3. Прокрутить вниз до "Workflow permissions"
4. Выбрать: **"Read and write permissions"**
5. Нажать **"Save"**

**Статус:** ⏳ Требует выполнения

---

## Шаг 2: Создание Pull Request для проверки

### 2.1 Создать PR через GitHub UI
1. GitHub → Pull requests → New pull request
2. Base: `main` ← Compare: `devops`
3. Заполнить название: "Sprint D1: Build & Publish - Automated Docker workflow"
4. Создать PR

### 2.2 Проверка автоматического запуска
- PR создан → workflow должен запуститься автоматически
- Проверить: PR → Checks → "Build and Publish"
- Должно быть 3 job: bot, api, frontend

### 2.3 Ожидаемый результат
✅ Все 3 образа собираются успешно  
✅ Status check = "passed" (зеленая галочка)  
❌ Образы НЕ публикуются (это PR, не main)

**Что проверяем:**
- Workflow запускается при PR
- Matrix strategy работает (3 параллельных сборки)
- Dockerfiles корректны
- Build проходит без ошибок

**Статус:** ⏳ Требует выполнения

---

## Шаг 3: Merge в main и публикация образов

### 3.1 Merge PR
После успешной проверки:
1. В PR нажать **"Merge pull request"**
2. Подтвердить merge
3. Удалить ветку devops (опционально)

### 3.2 Автоматический запуск workflow
- Merge → workflow запускается автоматически
- Проверить: Actions → "Build and Publish" → последний run
- Должен быть статус "running" или "completed"

### 3.3 Ожидаемый результат
✅ Все 3 образа собираются  
✅ Образы публикуются в GitHub Container Registry  
✅ Workflow завершается успешно (зеленая галочка)

### 3.4 Проверка публикации
1. GitHub → Profile (правый верхний угол) → Packages
2. Должны появиться 3 пакета:
   - `systech-aidd-bot`
   - `systech-aidd-api`
   - `systech-aidd-frontend`

**Статус:** ⏳ Требует выполнения

---

## Шаг 4: Настройка публичного доступа

### 4.1 Сделать образы публичными (для каждого)

**Для systech-aidd-bot:**
1. Packages → systech-aidd-bot
2. Package settings (справа внизу)
3. Danger Zone → Change package visibility
4. Выбрать **"Public"**
5. Ввести название пакета: `systech-aidd-bot`
6. "I understand, change package visibility"

**Повторить для:**
- systech-aidd-api
- systech-aidd-frontend

### 4.2 Проверка
После изменения visibility должна появиться метка "Public" на пакете.

**Статус:** ⏳ Требует выполнения

---

## Шаг 5: Обновление README.md

### 5.1 Узнать ваш GitHub username
```bash
git config user.name
# или посмотреть в GitHub UI
```

### 5.2 Заменить OWNER в README.md
Найти и заменить все вхождения `OWNER` на ваш GitHub username в:
- Badge URL (строка 3)
- Примеры команд docker pull (строки ~27-29)

Пример замены:
```bash
# До
ghcr.io/OWNER/systech-aidd-bot:latest

# После
ghcr.io/yourusername/systech-aidd-bot:latest
```

### 5.3 Коммит и push
```bash
git add README.md
git commit -m "docs: update Docker image URLs with actual GitHub username"
git push origin main
```

**Статус:** ⏳ Требует выполнения

---

## Шаг 6: Локальное тестирование образов

### 6.1 Установка переменной окружения
```bash
# В PowerShell
$env:GITHUB_REPOSITORY_OWNER="yourusername"

# Проверка
echo $env:GITHUB_REPOSITORY_OWNER
```

### 6.2 Pull образов (БЕЗ авторизации)
```bash
docker pull ghcr.io/yourusername/systech-aidd-bot:latest
docker pull ghcr.io/yourusername/systech-aidd-api:latest
docker pull ghcr.io/yourusername/systech-aidd-frontend:latest
```

**Ожидаемый результат:**
✅ Образы скачиваются без запроса логина/пароля  
✅ Нет ошибок "pull access denied"

### 6.3 Проверка размеров
```bash
docker images | grep systech-aidd
```

**Ожидаемые размеры (примерно):**
- bot: ~200-300 MB
- api: ~200-300 MB
- frontend: ~400-600 MB

**Статус:** ⏳ Требует выполнения

---

## Шаг 7: Запуск через docker-compose.registry.yml

### 7.1 Проверка .env файла
```bash
# Убедиться что .env существует
ls .env

# Проверить обязательные переменные
# TELEGRAM_BOT_TOKEN=...
# OPENROUTER_API_KEY=...
# POSTGRES_HOST=postgres  # ВАЖНО для Docker!
```

Если .env не настроен:
```bash
cp .env.example .env
# Отредактировать .env - добавить токены
```

### 7.2 Запуск сервисов
```bash
# Запуск с образами из registry
docker-compose -f docker-compose.registry.yml up -d

# Проверка статуса
docker-compose -f docker-compose.registry.yml ps
```

**Ожидаемый результат:**
```
NAME                    STATUS
systech-aidd-db         Up (healthy)
systech-aidd-bot        Up
systech-aidd-api        Up
systech-aidd-frontend   Up
```

### 7.3 Проверка логов
```bash
# Все сервисы
docker-compose -f docker-compose.registry.yml logs

# Конкретный сервис
docker-compose -f docker-compose.registry.yml logs bot
docker-compose -f docker-compose.registry.yml logs api
docker-compose -f docker-compose.registry.yml logs frontend
```

**Ожидаемый результат:**
- ✅ PostgreSQL: "database system is ready to accept connections"
- ✅ Bot: подключение к БД успешно, бот запущен
- ✅ API: "Uvicorn running on http://0.0.0.0:8000"
- ✅ Frontend: "ready started server on 0.0.0.0:3000"

**Статус:** ⏳ Требует выполнения

---

## Шаг 8: Проверка доступности сервисов

### 8.1 Frontend
Открыть в браузере: http://localhost:3000

**Ожидаемый результат:**
✅ Страница загружается  
✅ UI отображается корректно  
✅ Нет ошибок в консоли браузера (F12)

### 8.2 API
Открыть в браузере: http://localhost:8000/docs

**Ожидаемый результат:**
✅ Swagger UI открывается  
✅ Все эндпоинты видны  
✅ Можно протестировать API через UI

### 8.3 PostgreSQL
```bash
# Подключение через docker exec
docker exec -it systech-aidd-db psql -U postgres -d systech_aidd

# Проверка таблиц
\dt

# Выход
\q
```

**Ожидаемый результат:**
✅ Таблицы созданы (messages, users, etc.)  
✅ База работает

**Статус:** ⏳ Требует выполнения

---

## Шаг 9: Проверка Badge в README

### 9.1 Обновить страницу README на GitHub
GitHub → Code → README.md

### 9.2 Проверка badge
В начале README должен быть badge:
```
[![Build and Publish](https://github.com/yourusername/systech-aidd/workflows/Build%20and%20Publish/badge.svg)](...)
```

**Ожидаемый результат:**
✅ Badge отображается  
✅ Статус: "passing" (зеленый)  
✅ При клике → переход на Actions

Если badge показывает "unknown" или не загружается:
- Проверить что URL содержит правильный username
- Дождаться окончания workflow (может занять 1-2 минуты)

**Статус:** ⏳ Требует выполнения

---

## Шаг 10: Финальная проверка workflow

### 10.1 Внести минимальное изменение
```bash
# Добавить комментарий в README
echo "" >> README.md
echo "<!-- Test workflow -->" >> README.md

git add README.md
git commit -m "test: verify workflow trigger"
git push origin main
```

### 10.2 Проверка автоматического запуска
1. GitHub → Actions
2. Должен запуститься новый workflow run
3. Дождаться завершения (~3-5 минут)

**Ожидаемый результат:**
✅ Workflow запустился автоматически  
✅ Все 3 образа пересобрались  
✅ Новые образы опубликованы с тегом latest  
✅ Также создан тег sha-<commit>

### 10.3 Проверка тегов образов
```bash
# Pull образ с конкретным SHA
docker pull ghcr.io/yourusername/systech-aidd-bot:sha-abc1234

# Где abc1234 - первые 7 символов последнего commit SHA
```

**Статус:** ⏳ Требует выполнения

---

## Очистка после тестирования

Если нужно освободить место:

```bash
# Остановить сервисы из registry
docker-compose -f docker-compose.registry.yml down

# Удалить скачанные образы
docker rmi ghcr.io/yourusername/systech-aidd-bot:latest
docker rmi ghcr.io/yourusername/systech-aidd-api:latest
docker rmi ghcr.io/yourusername/systech-aidd-frontend:latest

# Удалить неиспользуемые образы
docker image prune -a
```

---

## Чек-лист выполнения

### Обязательные шаги
- [ ] 1. Push ветки devops
- [ ] 2. Настроить GitHub Permissions (Read and write)
- [ ] 3. Создать PR и проверить сборку
- [ ] 4. Merge PR в main
- [ ] 5. Проверить публикацию образов в Packages
- [ ] 6. Сделать образы публичными (все 3)
- [ ] 7. Обновить README с вашим username
- [ ] 8. Pull образов локально
- [ ] 9. Запустить через docker-compose.registry.yml
- [ ] 10. Проверить доступность Frontend и API
- [ ] 11. Проверить Badge в README

### Опциональные шаги
- [ ] Протестировать тригер на новый коммит
- [ ] Проверить теги образов (latest и sha-)
- [ ] Проверить работу кэширования (повторная сборка быстрее)

---

## Возможные проблемы и решения

### ❌ Workflow не запускается
**Решение:** Проверить что файл `.github/workflows/build.yml` в ветке main

### ❌ Permission denied при публикации
**Решение:** Settings → Actions → Workflow permissions → "Read and write"

### ❌ Pull access denied
**Решение:** Сделать образы публичными (Packages → Package settings → Public)

### ❌ Badge не отображается
**Решение:** 
1. Заменить OWNER на ваш username
2. Дождаться первого успешного workflow run

### ❌ Сервисы не запускаются
**Решение:**
1. Проверить .env файл (токены заполнены)
2. Проверить POSTGRES_HOST=postgres в .env
3. Проверить логи: `docker-compose -f docker-compose.registry.yml logs`

---

## Успех! 🎉

Если все шаги выполнены успешно:
- ✅ Workflow собирает образы автоматически
- ✅ Образы публикуются в ghcr.io
- ✅ Образы доступны публично
- ✅ Можно запустить приложение из готовых образов
- ✅ Badge показывает статус сборки

**Спринт D1 полностью протестирован и работает!**

Можно переходить к планированию Спринта D2: Развертывание на сервер.

