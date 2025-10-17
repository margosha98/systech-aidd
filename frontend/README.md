# Frontend - Дашборд статистики Telegram-бота

Frontend приложение для визуализации статистики telegram-бота "Знайкин" на Next.js 14+ с TypeScript и shadcn/ui.

## Технологический стек

- **Framework**: Next.js 15 (App Router)
- **Язык**: TypeScript
- **UI библиотека**: shadcn/ui
- **Стилизация**: Tailwind CSS 4
- **Пакетный менеджер**: pnpm
- **Линтинг**: ESLint + Prettier

## Быстрый старт

### Установка зависимостей

```bash
pnpm install
```

### Переменные окружения

Скопируйте `.env.example` в `.env.local` и настройте переменные:

```bash
cp .env.example .env.local
```

Переменные окружения:

- `NEXT_PUBLIC_API_URL` - URL backend API (по умолчанию: `http://localhost:8000`)

### Запуск dev сервера

```bash
pnpm dev
```

Приложение будет доступно на http://localhost:3000

### Сборка production версии

```bash
pnpm build
pnpm start
```

## Команды

```bash
# Разработка
pnpm dev          # Запуск в режиме разработки
pnpm build        # Сборка production версии
pnpm start        # Запуск production версии

# Качество кода
pnpm lint         # Проверка линтером
pnpm format       # Форматирование кода
pnpm type-check   # Проверка типов TypeScript
```

## Структура проекта

```
frontend/
├── app/                    # App Router (Next.js 15)
│   ├── layout.tsx         # Корневой layout
│   ├── page.tsx           # Главная страница (дашборд)
│   └── globals.css        # Глобальные стили + Tailwind
├── components/
│   ├── ui/                # shadcn/ui компоненты
│   ├── dashboard/         # Компоненты дашборда
│   └── layout/            # Компоненты раскладки
├── lib/
│   ├── utils.ts           # Утилиты (cn helper от shadcn)
│   ├── api.ts             # API клиент для backend
│   └── constants.ts       # Константы приложения
├── types/
│   ├── api.ts             # TypeScript типы для API
│   └── index.ts           # Общие типы
├── public/                # Статические файлы
└── doc/                   # Документация
```

## Темная тема

Приложение поддерживает светлую и темную темы:

- **Библиотека**: `next-themes`
- **Автоопределение**: использует системную тему по умолчанию
- **Сохранение**: выбор темы сохраняется в `localStorage`
- **Переключение**: кнопка с иконкой солнца/луны в Header
- **CSS переменные**: настроены для обеих тем в `globals.css`

### Компоненты темы

- `components/theme-provider.tsx` - провайдер темы для приложения
- `components/theme-toggle.tsx` - переключатель темы
- CSS переменные в `app/globals.css` (`.dark` класс)

### Использование

Переключение темы через UI:
- Нажмите иконку солнца (для светлой темы) или луны (для темной)
- Тема автоматически сохранится и применится ко всем страницам

## Интеграция с Backend

Frontend интегрируется с FastAPI backend через REST API:

- **Endpoint**: `GET /api/stats?period={period}`
- **Параметры**: `period` = `7d` | `30d` | `3m`
- **Backend URL**: настраивается через `NEXT_PUBLIC_API_URL`

API клиент находится в `lib/api.ts`.

## Документация

- [Техническое видение](./doc/front-vision.md) - архитектура и принципы
- [ADR: Выбор стека](./doc/adr-stack-choice.md) - обоснование технологий
- [Frontend Roadmap](./doc/frontend-roadmap.md) - план развития

## Разработка

### Добавление компонентов shadcn/ui

```bash
npx shadcn@latest add button
npx shadcn@latest add card
# и т.д.
```

### Линтинг и форматирование

Проект использует ESLint и Prettier для контроля качества кода:

- **ESLint**: проверка кода, поиск ошибок
- **Prettier**: автоматическое форматирование
- **TypeScript**: строгая типизация (strict mode)

Перед коммитом обязательно:

- ✅ `pnpm format` - форматирование кода
- ✅ `pnpm lint` - проверка линтером
- ✅ `pnpm type-check` - проверка типов

### Соглашения по коду

- TypeScript strict mode
- Server Components по умолчанию
- Client Components только при необходимости (`'use client'`)
- Именование: PascalCase для компонентов, camelCase для функций
- Один компонент = один файл

## Следующие шаги

См. [Frontend Roadmap](./doc/frontend-roadmap.md) для плана развития.

### Спринт S3: Реализация dashboard

- Компоненты метрик (MetricCard)
- График timeline (TimelineChart)
- Селектор периода (PeriodSelector)
- Responsive layout

### Спринт S4: ИИ-чат

- Компонент чата
- Интеграция с chat API
- Отображение результатов

## Технические детали

### Server Components

По умолчанию все компоненты являются Server Components (SSR). Используйте Client Components (`'use client'`) только для:

- Интерактивности (onClick, useState, useEffect)
- Браузерных API
- React Context

### API интеграция

Для загрузки данных в Server Components используйте `fetch` с `cache: 'no-store'`:

```typescript
import { getStats } from '@/lib/api';

export default async function Page() {
  const stats = await getStats('7d');
  return <div>{/* ... */}</div>;
}
```

### Стилизация

Используйте Tailwind CSS utility классы:

```tsx
<div className="flex items-center gap-4 rounded-lg bg-white p-6 shadow-md">{/* ... */}</div>
```

CSS переменные для темизации находятся в `app/globals.css`.

## Производительность

- ✅ Server Components для минимизации JavaScript на клиенте
- ✅ Автоматический code splitting по роутам
- ✅ Image optimization через `<Image />` компонент
- ✅ Font optimization через `next/font`

## License

MIT
