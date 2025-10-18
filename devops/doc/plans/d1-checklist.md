# Спринт D1: Чек-лист для проверки

Используйте этот чек-лист для проверки корректности реализации спринта D1.

## ✅ Созданные файлы

- [ ] `.github/workflows/build.yml` - GitHub Actions workflow
- [ ] `docker-compose.registry.yml` - compose для registry образов
- [ ] `devops/doc/github-actions-guide.md` - руководство по GitHub Actions
- [ ] `devops/doc/plans/sprint-d1-implementation.md` - итоговый план
- [ ] `devops/doc/plans/d1-setup-guide.md` - инструкция по настройке
- [ ] `devops/doc/plans/d1-summary.md` - сводка изменений

## ✅ Обновленные файлы

- [ ] `README.md` - добавлен badge и секция Docker образы
- [ ] `devops/doc/devops-roadmap.md` - статус D1 → Завершен
- [ ] `devops/doc/plans/d1-build-publish.md` - статус → Завершен

## ✅ Содержимое workflow (.github/workflows/build.yml)

- [ ] Имя: "Build and Publish"
- [ ] Триггеры: push (main) и pull_request (main)
- [ ] Matrix strategy для 3 сервисов: bot, api, frontend
- [ ] Steps: checkout, buildx, login, metadata, build-push
- [ ] Кэширование: cache-from/cache-to type=gha
- [ ] Условная публикация: push только для main

## ✅ Содержимое docker-compose.registry.yml

- [ ] Сервис postgres: стандартный образ PostgreSQL
- [ ] Сервисы bot, api, frontend: образы из ghcr.io
- [ ] Переменная окружения: GITHUB_REPOSITORY_OWNER
- [ ] Все настройки идентичны docker-compose.yml (кроме образов)

## ✅ Документация

### README.md
- [ ] Badge в начале файла
- [ ] Секция "🐳 Docker образы"
- [ ] Список доступных образов
- [ ] Команды docker pull
- [ ] Команда запуска через registry compose

### github-actions-guide.md
- [ ] Основы GitHub Actions
- [ ] Структура workflow
- [ ] Триггеры и примеры
- [ ] Matrix strategy
- [ ] GitHub Container Registry
- [ ] PR workflow
- [ ] Permissions
- [ ] Кэширование
- [ ] Best practices

### sprint-d1-implementation.md
- [ ] Статус: ✅ Завершен
- [ ] Описание всех выполненных задач
- [ ] Архитектурные решения
- [ ] Команды для использования
- [ ] Готовность к D2/D3

### d1-setup-guide.md
- [ ] Инструкция по настройке GitHub permissions
- [ ] Первый запуск и проверка workflow
- [ ] Настройка публичного доступа к образам
- [ ] Локальная проверка pull и запуск
- [ ] Troubleshooting

## ✅ После merge в main

### Настройка GitHub (один раз)
- [ ] Settings → Actions → Workflow permissions → "Read and write"
- [ ] Commit и push в main
- [ ] Проверить Actions → Build and Publish запустился
- [ ] Проверить все 3 образа собрались успешно
- [ ] Проверить образы опубликовались в Packages

### Публичный доступ (для каждого образа)
- [ ] Packages → systech-aidd-bot → Package settings → Public
- [ ] Packages → systech-aidd-api → Package settings → Public
- [ ] Packages → systech-aidd-frontend → Package settings → Public

### Обновление README.md
- [ ] Заменить OWNER на ваш GitHub username в badge URL
- [ ] Заменить OWNER в примерах команд docker pull

### Локальная проверка
- [ ] `docker pull ghcr.io/OWNER/systech-aidd-bot:latest` - успешно
- [ ] `docker pull ghcr.io/OWNER/systech-aidd-api:latest` - успешно
- [ ] `docker pull ghcr.io/OWNER/systech-aidd-frontend:latest` - успешно
- [ ] Установить `GITHUB_REPOSITORY_OWNER=OWNER`
- [ ] `docker-compose -f docker-compose.registry.yml up -d` - успешно
- [ ] Frontend доступен: http://localhost:3000
- [ ] API доступен: http://localhost:8000/docs
- [ ] Логи без критических ошибок

### Проверка badge
- [ ] Badge в README отображается
- [ ] Badge показывает "passing" (зеленый)
- [ ] При клике переходит на Actions

## ✅ Тестирование PR workflow

- [ ] Создать тестовую ветку: `git checkout -b test/d1-check`
- [ ] Push ветки: `git push origin test/d1-check`
- [ ] Открыть PR через GitHub UI
- [ ] Workflow запустился автоматически
- [ ] Все 3 образа собираются
- [ ] Образы НЕ публикуются (это PR)
- [ ] Status check проходит
- [ ] Merge PR в main
- [ ] После merge workflow запустился снова
- [ ] Образы собрались И опубликовались

## ❌ Что НЕ включено (по плану)

- [ ] Lint checks - добавим позже
- [ ] Запуск тестов - добавим позже
- [ ] Security scanning - добавим позже
- [ ] Multi-platform builds - добавим позже

## 📋 Готовность к D2

- [ ] Образы публикуются автоматически при push в main
- [ ] Образы доступны публично без авторизации
- [ ] docker-compose.registry.yml готов к использованию на сервере
- [ ] Тегирование latest и sha-commit для версионирования
- [ ] Документация полная и на русском языке

---

## Сводка

**Всего пунктов:** ~50
**Критических для работы:** ~25
**Опциональных:** ~25

После выполнения всех критических пунктов спринт D1 считается **успешно завершенным** и можно переходить к D2.

## Быстрая проверка (минимум)

Если времени мало, проверьте хотя бы это:

1. ✅ Workflow файл создан и синтаксически корректен
2. ✅ Push в main запускает workflow
3. ✅ Все 3 образа собираются успешно
4. ✅ Образы публикуются в ghcr.io
5. ✅ Образы доступны публично
6. ✅ Можно скачать образы без авторизации
7. ✅ docker-compose.registry.yml запускает сервисы
8. ✅ Документация создана

**8 из 8 = можно двигаться дальше! 🚀**

