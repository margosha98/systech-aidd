<!-- 47eff5e9-56fe-4237-b4e4-b18e9d34dfcd 634d4e18-0e28-4c40-9d8b-30db2880f33b -->
# Спринт S2: Инициализация Frontend проекта

## Цель

Создать каркас frontend приложения на Next.js + TypeScript с shadcn/ui для дашборда статистики telegram-бота с интеграцией к Mock API из S1.

## Технологический стек

- **Фреймворк**: Next.js 14+ (App Router)
- **Язык**: TypeScript
- **UI библиотека**: shadcn/ui
- **Стилизация**: Tailwind CSS
- **Пакетный менеджер**: pnpm
- **Линтинг**: ESLint + Prettier

## Документация

### 1. front-vision.md

Создать `frontend/doc/front-vision.md` с техническим видением UI:

- Архитектура frontend (маршрутизация, компоненты)
- Принципы организации кода (атомарный дизайн)
- Подход к управлению состоянием (серверные и клиентские компоненты)
- Интеграция с backend API
- Подход к стилизации (Tailwind + CSS переменные)

### 2. ADR (Архитектурное решение)

Создать `frontend/doc/adr-stack-choice.md` с обоснованием выбора стека:

- Почему Next.js 14 (маршрутизация, серверные компоненты, оптимизация)
- Почему shadcn/ui (настраиваемость, доступность, TypeScript-first)
- Почему Tailwind CSS (утилитарный подход, производительность)
- Почему pnpm (скорость, эффективность использования диска)

### 3. README.md

Создать `frontend/README.md` с инструкциями:

- Установка зависимостей (`pnpm install`)
- Запуск dev сервера (`pnpm dev`)
- Сборка (`pnpm build`)
- Переменные окружения
- Структура проекта

## Инициализация проекта

### 1. Создание Next.js проекта

```bash
cd frontend
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
```

Параметры:

- TypeScript: ✅
- ESLint: ✅
- Tailwind CSS: ✅
- App Router: ✅
- Без src/ директории (используем app/ напрямую)
- Алиас импорта: `@/*`

### 2. Инициализация shadcn/ui

```bash
npx shadcn@latest init
```

Выбрать:

- Стиль: Default
- Базовый цвет: Slate
- CSS переменные: Yes

## Структура проекта

```
frontend/
├── app/                    # Маршрутизация (Next.js 14)
│   ├── layout.tsx         # Корневой layout
│   ├── page.tsx           # Главная страница (дашборд)
│   ├── globals.css        # Глобальные стили + Tailwind
│   └── api/               # API роуты (при необходимости)
├── components/
│   ├── ui/                # Компоненты shadcn/ui
│   ├── dashboard/         # Компоненты дашборда
│   │   ├── metric-card.tsx
│   │   ├── timeline-chart.tsx
│   │   └── period-selector.tsx
│   └── layout/            # Компоненты раскладки
│       ├── header.tsx
│       └── sidebar.tsx
├── lib/
│   ├── utils.ts           # Утилиты (cn helper от shadcn)
│   ├── api.ts             # API клиент для backend
│   └── constants.ts       # Константы приложения
├── types/
│   ├── api.ts             # TypeScript типы для API (из backend моделей)
│   └── index.ts           # Общие типы
├── public/                # Статические файлы
│   └── favicon.ico
├── doc/                   # Документация (уже существует)
├── .env.local             # Переменные окружения (не в git)
├── .env.example           # Пример файла окружения
├── .gitignore             # Игнорируемые файлы
├── package.json           # Зависимости и скрипты
├── tsconfig.json          # Конфигурация TypeScript
├── next.config.js         # Конфигурация Next.js
├── tailwind.config.ts     # Конфигурация Tailwind
├── components.json        # Конфигурация shadcn/ui
├── .eslintrc.json         # Правила ESLint
├── .prettierrc            # Конфигурация Prettier
└── README.md              # Инструкции для frontend
```

## TypeScript типы

Создать `frontend/types/api.ts` на основе backend Pydantic моделей из `backend/api/models.py`:

```typescript
export type Period = '7d' | '30d' | '3m';
export type Trend = 'up' | 'down' | 'steady';

export interface MetricCard {
  value: number;
  change: number;
  trend: Trend;
  description: string;
}

export interface TimelinePoint {
  date: string;
  value: number;
}

export interface MetricsData {
  total_messages: MetricCard;
  active_users: MetricCard;
  total_dialogs: MetricCard;
  growth_rate: MetricCard;
}

export interface StatsResponse {
  period: Period;
  metrics: MetricsData;
  timeline: TimelinePoint[];
}
```

## API клиент

Создать `frontend/lib/api.ts` для интеграции с backend API (http://localhost:8000):

```typescript
import { StatsResponse, Period } from '@/types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getStats(period: Period = '7d'): Promise<StatsResponse> {
  const response = await fetch(`${API_URL}/api/stats?period=${period}`, {
    cache: 'no-store', // Для серверного рендеринга
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }
  
  return response.json();
}
```

## Переменные окружения

Создать `.env.example`:

```env
# URL backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Создать `.env.local` (добавить в .gitignore):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Скрипты package.json

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write .",
    "type-check": "tsc --noEmit"
  }
}
```

## Линтинг и форматирование

### Конфигурация Prettier

Создать `.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 100
}
```

Создать `.prettierignore`:

```
node_modules
.next
out
dist
build
```

### Конфигурация ESLint

Расширить `.eslintrc.json`:

```json
{
  "extends": [
    "next/core-web-vitals",
    "prettier"
  ],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "warn"
  }
}
```

Установить prettier:

```bash
pnpm add -D prettier eslint-config-prettier
```

## .gitignore

Добавить в `frontend/.gitignore`:

```
# зависимости
node_modules
.pnpm-store

# next.js
.next
out
dist
build

# переменные окружения
.env.local
.env*.local

# отладка
npm-debug.log*
pnpm-debug.log*

# typescript
*.tsbuildinfo
```

## Интеграция с корневым проектом

Обновить корневой `Makefile` добавлением команд для frontend:

```makefile
# Команды frontend
install-frontend:
	cd frontend && pnpm install

run-frontend:
	cd frontend && pnpm dev

build-frontend:
	cd frontend && pnpm build

lint-frontend:
	cd frontend && pnpm lint

format-frontend:
	cd frontend && pnpm format

# Команды полного стека
install-all: install install-frontend

run-all:
	make run-api-dev & make run-frontend
```

## Проверка готовности

После выполнения спринта проверить:

### Документация

- ✅ `frontend/doc/front-vision.md` создан
- ✅ `frontend/doc/adr-stack-choice.md` создан
- ✅ `frontend/README.md` создан с инструкциями

### Структура проекта

- ✅ Next.js проект инициализирован в `frontend/`
- ✅ shadcn/ui настроен
- ✅ Структура директорий: `app/`, `components/`, `lib/`, `types/`, `public/`
- ✅ `.gitignore` настроен

### Код и типы

- ✅ TypeScript типы созданы в `types/api.ts`
- ✅ API клиент создан в `lib/api.ts`
- ✅ Переменные окружения настроены (`.env.example`, `.env.local`)

### Команды и скрипты

- ✅ Скрипты в package.json: `dev`, `build`, `start`, `lint`, `format`, `type-check`
- ✅ Prettier и ESLint настроены
- ✅ Команды в корневом Makefile добавлены

### Проверка работоспособности

- ✅ `pnpm install` выполняется успешно
- ✅ `pnpm dev` запускается без ошибок на порту 3000
- ✅ `pnpm build` проходит успешно
- ✅ `pnpm lint` проходит без ошибок
- ✅ `pnpm format` форматирует код
- ✅ `pnpm type-check` проверяет типы без ошибок

### Интеграция

- ✅ Подключение к Mock API (http://localhost:8000/api/stats) работает
- ✅ TypeScript типы соответствуют backend моделям

### Документация проекта

- ✅ `frontend/doc/frontend-roadmap.md` обновлен (статус S2, ссылка на план)

## Следующие шаги (S3)

После завершения S2, в спринте S3 будет реализован дашборд с компонентами на основе референса (`frontend/frontend-reference.png`) и интеграцией с Mock API.

### To-dos

- [ ] Создать frontend/doc/front-vision.md с техническим видением UI
- [ ] Создать frontend/doc/adr-stack-choice.md с обоснованием выбора стека
- [ ] Инициализировать Next.js проект с TypeScript и Tailwind CSS
- [ ] Настроить shadcn/ui в проекте
- [ ] Создать структуру директорий: components/, lib/, types/, public/
- [ ] Создать TypeScript типы на основе backend Pydantic моделей
- [ ] Создать API client для интеграции с backend
- [ ] Настроить environment variables (.env.example, .env.local)
- [ ] Настроить Prettier и ESLint конфигурации
- [ ] Создать frontend/README.md с инструкциями по установке и запуску
- [ ] Обновить корневой Makefile командами для frontend
- [ ] Проверить что dev/build/lint команды работают корректно