# ADR: Выбор технологического стека Frontend

**Статус**: Принято  
**Дата**: 2025-10-17  
**Контекст**: Спринт S2 - Инициализация Frontend проекта

## Контекст и проблема

Необходимо выбрать оптимальный технологический стек для создания frontend дашборда статистики telegram-бота "Знайкин". Требования:

- Быстрая разработка MVP
- Современный UX и производительность
- TypeScript для типобезопасности
- Интеграция с FastAPI backend
- Возможность масштабирования
- Хорошая документация и экосистема

## Рассмотренные варианты

### 1. Framework

**Варианты:**

- Next.js 14+ (App Router)
- React + Vite
- Remix
- SvelteKit

**Выбор: Next.js 14+ (App Router)**

### 2. UI библиотека

**Варианты:**

- shadcn/ui
- Material-UI (MUI)
- Ant Design
- Chakra UI

**Выбор: shadcn/ui**

### 3. Styling

**Варианты:**

- Tailwind CSS
- Styled Components
- CSS Modules
- Emotion

**Выбор: Tailwind CSS**

### 4. Пакетный менеджер

**Варианты:**

- pnpm
- npm
- yarn

**Выбор: pnpm**

## Решение

### Next.js 14+ (App Router)

**Почему выбрали:**

1. **Server Components**
   - Уменьшение JavaScript bundle на клиенте
   - Прямой доступ к API без дополнительных библиотек
   - Оптимальная производительность из коробки

2. **App Router**
   - Современная файловая маршрутизация
   - Встроенные loading и error states
   - Layouts для переиспользования компонентов
   - Streaming и Suspense поддержка

3. **Оптимизация производительности**
   - Автоматический code splitting
   - Image optimization (`<Image />`)
   - Font optimization (`next/font`)
   - Automatic Static Optimization

4. **TypeScript first**
   - Отличная поддержка TypeScript из коробки
   - Типизация для всех API Next.js

5. **Developer Experience**
   - Hot Module Replacement (HMR)
   - Fast Refresh
   - Отличная документация
   - Большое комьюнити

6. **Production-ready**
   - Vercel deployment в 1 клик
   - Edge Functions поддержка
   - API Routes для BFF паттерна

**Почему не другие:**

- **React + Vite**: требует больше настройки для SSR, роутинга, оптимизации
- **Remix**: меньше комьюнити, более крутая кривая обучения
- **SvelteKit**: другой фреймворк (не React), меньше библиотек в экосистеме

### shadcn/ui

**Почему выбрали:**

1. **Копирование кода в проект**
   - Полный контроль над компонентами
   - Нет зависимости от внешних библиотек
   - Возможность кастомизации под дизайн

2. **Accessibility из коробки**
   - Построены на Radix UI primitives
   - ARIA атрибуты
   - Keyboard navigation
   - Screen reader friendly

3. **TypeScript first**
   - Полная типизация компонентов
   - IntelliSense поддержка
   - Type-safe props

4. **Современный дизайн**
   - Минималистичный стиль
   - Гибкая кастомизация
   - CSS переменные для тем

5. **Tailwind CSS интеграция**
   - Использует Tailwind для стилей
   - Единая система дизайна
   - Utility-first подход

6. **Не раздувает bundle**
   - Импортируешь только то, что нужно
   - Нет большой библиотеки в node_modules

**Почему не другие:**

- **Material-UI**: тяжеловесная библиотека, сложная кастомизация, свой дизайн язык
- **Ant Design**: больше подходит для enterprise, китайский дизайн, большой bundle
- **Chakra UI**: хорошая, но меньше контроля, зависимость от библиотеки

### Tailwind CSS

**Почему выбрали:**

1. **Utility-first подход**
   - Быстрая разработка через композицию классов
   - Нет необходимости придумывать имена классов
   - Меньше переключений между файлами

2. **Производительность**
   - PurgeCSS: удаление неиспользуемых стилей
   - Маленький production bundle
   - Оптимизация build time

3. **Consistency**
   - Единая система дизайна (spacing, colors, typography)
   - Нет случайных значений margin/padding
   - Легко поддерживать консистентность

4. **Responsive design**
   - Простые брейкпоинты: `sm:`, `md:`, `lg:`, `xl:`
   - Mobile-first подход
   - Легко делать адаптивные layouts

5. **Темная тема**
   - Через CSS переменные
   - `dark:` префикс для темных стилей
   - Интеграция с shadcn/ui темами

6. **Developer Experience**
   - IntelliSense в VSCode
   - Официальное расширение Tailwind CSS
   - Хорошая документация

**Почему не другие:**

- **Styled Components**: runtime overhead, сложнее с SSR, нет утилитарного подхода
- **CSS Modules**: больше boilerplate, нужно придумывать имена классов
- **Emotion**: похоже на Styled Components, runtime CSS-in-JS

### pnpm

**Почему выбрали:**

1. **Скорость установки**
   - В 2-3 раза быстрее npm
   - Параллельная установка пакетов
   - Эффективное кеширование

2. **Disk efficiency**
   - Content-addressable storage
   - Hardlinks вместо копирования
   - Экономия места на диске (50-70%)

3. **Strict node_modules**
   - Нет phantom dependencies
   - Нельзя использовать не объявленные зависимости
   - Чище dependency tree

4. **Монорепо поддержка**
   - Workspaces из коробки
   - Возможность масштабирования до монорепо

5. **Совместимость**
   - Поддержка package-lock.json
   - Аналогичные команды с npm

6. **Активное развитие**
   - Быстрые релизы
   - Поддержка от Vercel, Microsoft, ByteDance

**Почему не другие:**

- **npm**: медленнее, больше места на диске
- **yarn**: медленнее pnpm, сложнее конфигурация

## Дополнительные инструменты

### ESLint + Prettier

- **ESLint**: статический анализ кода, поиск ошибок
- **Prettier**: автоматическое форматирование
- **eslint-config-prettier**: интеграция ESLint с Prettier

### TypeScript

- **Strict mode**: полная типизация
- **Интеграция с Next.js**: типы для Server Components, API Routes
- **Type checking**: `tsc --noEmit` перед коммитом

## Последствия

### Положительные

✅ Быстрая разработка через современные инструменты  
✅ Отличная производительность (Server Components, Tailwind)  
✅ Типобезопасность на всех уровнях (TypeScript)  
✅ Accessibility из коробки (shadcn/ui)  
✅ Легкая кастомизация UI компонентов  
✅ Хорошая документация и комьюнити  
✅ Production-ready с первого дня

### Отрицательные / Компромиссы

⚠️ Next.js 14 App Router - относительно новая технология (стабильна с v13.4)  
⚠️ shadcn/ui требует ручного копирования компонентов (не npm пакет)  
⚠️ Tailwind CSS - может казаться verbose в HTML  
⚠️ pnpm - меньше распространен чем npm (но растет)

### Риски

🔴 **Миграция**: Если понадобится сменить стек - потребуется значительная работа  
🟡 **Обучение**: Команда должна изучить App Router и Server Components  
🟢 **Поддержка**: Все выбранные технологии активно поддерживаются

## Альтернативы в будущем

При необходимости можно:

- Добавить state manager (Zustand, Redux) если потребуется сложное состояние
- Перейти на Remix если понадобится больше контроля над streaming
- Использовать другие UI библиотеки параллельно с shadcn/ui
- Добавить GraphQL если API станет сложнее

## Заключение

Выбранный стек (Next.js 14 + TypeScript + shadcn/ui + Tailwind CSS + pnpm) оптимально подходит для разработки современного, производительного и типобезопасного frontend дашборда. Все технологии хорошо интегрируются друг с другом, имеют отличную документацию и активное комьюнити.

Стек позволяет быстро создать MVP в спринте S2-S3, а затем легко масштабироваться в S4-S5 без технических ограничений.

## Ссылки

- [Next.js 14 Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [pnpm Documentation](https://pnpm.io)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
