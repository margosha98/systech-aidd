# Техническое видение Frontend приложения

## Обзор

Frontend приложение для дашборда статистики telegram-бота "Знайкин" построено на современном стеке Next.js 14+ с использованием App Router, TypeScript и shadcn/ui компонентов.

## Архитектура Frontend

### Маршрутизация (App Router)

Используется новый App Router от Next.js 14+:

- **Файловая маршрутизация**: структура папок в `app/` определяет роуты
- **Server Components по умолчанию**: оптимизация производительности
- **Layouts**: переиспользуемые обертки для страниц
- **Loading и Error states**: встроенная обработка загрузки и ошибок

### Структура компонентов

```
components/
├── ui/              # Базовые UI компоненты (shadcn/ui)
├── dashboard/       # Компоненты дашборда
└── layout/          # Компоненты раскладки
```

## Принципы организации кода

### Атомарный дизайн

Компоненты организованы по принципу атомарного дизайна:

1. **Атомы** (`components/ui/`): Базовые элементы (Button, Card, Input)
2. **Молекулы** (`components/dashboard/`): Композиция атомов (MetricCard, PeriodSelector)
3. **Организмы** (`components/layout/`): Сложные компоненты (Header, Sidebar)
4. **Страницы** (`app/page.tsx`): Полные экраны приложения

### Соглашения по коду

- **TypeScript strict mode**: полная типизация
- **Именование компонентов**: PascalCase для компонентов, kebab-case для файлов
- **Один компонент = один файл**: чистая структура
- **Props интерфейсы**: явные типы для всех пропсов
- **Экспорты**: именованные экспорты для утилит, default для компонентов

## Управление состоянием

### Server Components + Client Components

Используем гибридный подход Next.js 14:

**Server Components** (по умолчанию):

- Загрузка данных на сервере
- Нет JavaScript на клиенте
- Прямой доступ к API
- Используем для: страниц, статических компонентов, data fetching

**Client Components** (`'use client'`):

- Интерактивность (onClick, useState, useEffect)
- Браузерные API
- Используем для: форм, интерактивных элементов, real-time обновлений

### Стратегия данных

- **Server-side rendering (SSR)**: загрузка данных при каждом запросе
- **Cache: 'no-store'**: для динамических данных статистики
- **Параллельные запросы**: используем Promise.all для множественных запросов
- **Error boundaries**: обработка ошибок на уровне компонентов

### Состояние приложения

Для MVP не используем глобальный state manager (Redux, Zustand):

- Простые данные передаем через props
- Server Components для загрузки данных
- URL parameters для фильтров (period)
- React Context только при необходимости

## Интеграция с Backend API

### API клиент

Централизованный API клиент в `lib/api.ts`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getStats(period: Period): Promise<StatsResponse> {
  const response = await fetch(`${API_URL}/api/stats?period=${period}`, {
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }

  return response.json();
}
```

### TypeScript типы

Типы синхронизированы с backend Pydantic моделями:

- `Period`: '7d' | '30d' | '3m'
- `Trend`: 'up' | 'down' | 'steady'
- `MetricCard`: value, change, trend, description
- `StatsResponse`: полный ответ API

### Обработка ошибок

- Try-catch в Server Components
- Error boundaries для UI
- Fallback UI при ошибках
- Логирование ошибок в консоль (dev mode)

## Стилизация (Tailwind + CSS переменные)

### Tailwind CSS

Утилитарный подход для стилизации:

- **Utility-first**: композиция классов
- **Responsive design**: `sm:`, `md:`, `lg:`, `xl:` префиксы
- **Темная тема**: через CSS переменные
- **Custom config**: расширение в `tailwind.config.ts`

### CSS переменные (shadcn/ui)

Цветовая схема через CSS переменные в `app/globals.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  /* ... */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```

Преимущества:

- Единая система цветов
- Легкая смена темы
- Типизация через Tailwind
- Доступность (контрастность)

### Компонентный подход

shadcn/ui компоненты:

- **Копируются в проект**: полный контроль
- **Настраиваются**: изменяем под дизайн
- **Доступны**: ARIA атрибуты из коробки
- **Типизированы**: TypeScript first

## Производительность

### Оптимизации Next.js

- **Server Components**: минимум JS на клиенте
- **Автоматический code splitting**: по роутам
- **Image optimization**: компонент `<Image />`
- **Font optimization**: `next/font`

### Стратегии загрузки

- **Критические данные**: SSR в Server Components
- **Некритические данные**: lazy loading
- **Статические ресурсы**: из `/public`
- **Кеширование**: через HTTP headers

## Доступность (a11y)

Базовые принципы:

- **Семантический HTML**: правильные теги
- **ARIA атрибуты**: через shadcn/ui
- **Keyboard navigation**: focus states
- **Контрастность**: через CSS переменные
- **Screen readers**: aria-labels

## Структура проекта

```
frontend/
├── app/                    # App Router (маршрутизация)
│   ├── layout.tsx         # Корневой layout с провайдерами
│   ├── page.tsx           # Главная страница (дашборд)
│   └── globals.css        # Глобальные стили + CSS переменные
├── components/
│   ├── ui/                # shadcn/ui базовые компоненты
│   ├── dashboard/         # Бизнес-компоненты дашборда
│   └── layout/            # Компоненты раскладки (Header, Sidebar)
├── lib/
│   ├── utils.ts           # Утилиты (cn helper)
│   ├── api.ts             # API клиент
│   └── constants.ts       # Константы приложения
├── types/
│   ├── api.ts             # Типы для API
│   └── index.ts           # Общие типы
├── public/                # Статические файлы
├── doc/                   # Документация
├── .env.local             # Переменные окружения
├── package.json           # Зависимости
├── tsconfig.json          # TypeScript конфигурация
├── tailwind.config.ts     # Tailwind конфигурация
└── next.config.js         # Next.js конфигурация
```

## Workflow разработки

### Локальная разработка

```bash
pnpm install      # Установка зависимостей
pnpm dev          # Запуск dev сервера (localhost:3000)
pnpm lint         # Проверка линтером
pnpm format       # Форматирование кода
pnpm type-check   # Проверка типов
pnpm build        # Сборка production версии
```

### Проверка качества

- **ESLint**: проверка кода
- **Prettier**: форматирование
- **TypeScript**: статическая типизация
- **Все проверки перед коммитом**

## Roadmap функций

### MVP (S2 - текущий спринт)

- ✅ Инициализация проекта
- ✅ Настройка инструментов
- ✅ Базовая структура
- ✅ API интеграция

### S3: Dashboard

- Компоненты метрик
- График timeline
- Селектор периода
- Responsive layout

### S4: ИИ-чат

- Компонент чата
- Интеграция с chat API
- Отображение результатов

### S5: Production

- Оптимизация производительности
- Реальные данные из БД
- Деплой конфигурация

## Принципы разработки

1. **TypeScript везде**: строгая типизация
2. **Server Components first**: минимум клиентского JS
3. **Композиция над наследованием**: переиспользование компонентов
4. **Явное лучше неявного**: читаемый код
5. **KISS**: простота решений
6. **Responsive design**: mobile-first подход
7. **Accessibility**: доступность из коробки
8. **Performance**: производительность с самого начала

## Заключение

Архитектура frontend построена на современных практиках Next.js 14+ с акцентом на производительность, типобезопасность и простоту разработки. Использование Server Components и shadcn/ui обеспечивает оптимальный баланс между функциональностью и производительностью.
