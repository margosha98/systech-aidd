# Guides - Руководства

Полный набор гайдов для быстрого онбординга и разработки.

---

## 📋 Порядок изучения

### День 1: Онбординг

1. **[Getting Started](getting_started.md)** ⏱️ 15 минут
   - Установка и запуск проекта
   - Конфигурация
   - Проверка работы

2. **[Architecture](architecture.md)** ⏱️ 20 минут
   - Слоистая архитектура
   - Поток данных
   - Ключевые принципы
   - Модель данных

3. **[Codebase Tour](codebase_tour.md)** ⏱️ 30 минут
   - Структура проекта
   - Обзор каждого модуля
   - Точки расширения
   - Навигация по коду

4. **[Visualization](visualization.md)** ⏱️ 20 минут
   - Визуализация архитектуры
   - Диаграммы потоков данных
   - Структура компонентов
   - Процессы и состояния

### День 2-3: Разработка

5. **[Development Workflow](development_workflow.md)** ⏱️ 25 минут
   - TDD цикл (RED-GREEN-REFACTOR)
   - Git workflow
   - Инструменты качества
   - Чеклист перед коммитом

6. **[Testing Guide](testing_guide.md)** ⏱️ 30 минут
   - Структура тестов
   - Фикстуры и моки
   - Примеры для каждого слоя
   - Troubleshooting

---

## 🎯 Быстрый доступ

### Начало работы
- [Как запустить проект?](getting_started.md#установка-и-запуск)
- [Где взять токены?](getting_started.md#2-настройка-конфигурации)
- [Что делать если ошибка?](getting_started.md#troubleshooting)

### Понимание проекта
- [Как устроена архитектура?](architecture.md#слоистая-архитектура)
- [Как обрабатывается сообщение?](architecture.md#поток-данных)
- [Где находится код для X?](codebase_tour.md#навигационные-подсказки)
- [Визуальная схема проекта?](visualization.md)

### Разработка
- [Как добавить новую команду?](codebase_tour.md#добавить-новую-команду-бота)
- [Как писать тесты?](testing_guide.md#структура-теста-aaa-pattern)
- [Что проверять перед коммитом?](development_workflow.md#чеклист-перед-коммитом)

---

## 📚 Дополнительные материалы

### Техническая документация
- [vision.md](../vision.md) - Детальное техническое видение (450 строк)
- [idea.md](../idea.md) - Концепция проекта
- [tasklist.md](../tasklist.md) - История разработки MVP

### Соглашения и процессы
- [conventions.mdc](../../.cursor/rules/conventions.mdc) - Соглашения по коду
- [qa_conventions.mdc](../../.cursor/rules/qa_conventions.mdc) - Соглашения по тестам
- [workflow_tdd.mdc](../../.cursor/rules/workflow_tdd.mdc) - TDD процесс (подробный)

### Ревью
- [review_002.md](../reviews/review_002.md) - Аудит проекта (оценка 9.5/10)

---

## 💡 Полезные команды

```bash
# Запуск проекта
uv run python -m src.main

# Проверка качества
uv run ruff format src/
uv run ruff check src/
uv run mypy src/
uv run pytest

# Или все сразу (Linux/Mac)
make quality

# Тесты с покрытием
uv run pytest --cov=src --cov-report=term-missing
```

---

## 🤝 Вопросы?

Если что-то непонятно:
1. Проверьте [troubleshooting](getting_started.md#troubleshooting)
2. Изучите соответствующий гайд подробнее
3. Посмотрите примеры в тестах (`tests/`)
4. Обратитесь к команде

---

**Время на полный онбординг: ~2.5 часа**

Начните с [Getting Started](getting_started.md) →

