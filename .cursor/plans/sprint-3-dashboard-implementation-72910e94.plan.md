<!-- 72910e94-8126-406c-b9bd-f6c56de03d58 009e0e7c-6eb3-4b84-89b4-7d7affaf3200 -->
# План Спринта 3: Реализация Dashboard статистики

## Обзор

Создание функционального dashboard для визуализации статистики диалогов telegram-бота. Интеграция с Mock API из S1, реализация компонентов на основе референса shadcn/ui dashboard-01.

## Этапы реализации

### 1. Создание спецификации Dashboard

**Файл:** `frontend/doc/dashboard-requirements.md`

Документ включает:

- Маппинг метрик API → UI (total_messages → Total Messages, active_users → Active Users, total_dialogs → Total Dialogs, growth_rate → Growth Rate)
- Описание визуальных индикаторов трендов (up/down/steady)
- Требования к компонентам (MetricCard, TimelineChart, PeriodSelector)
- Логику переключения периодов через URL params
- Responsive поведение (grid 1 колонка на mobile, 4 на desktop)
- Форматирование чисел (разделители тысяч, проценты с 1 знаком)

### 2. Импорт базовых shadcn/ui компонентов

**Команда для выполнения:**

```bash
cd frontend
npx shadcn@latest add card button tabs
```

Импортируются компоненты:

- `card` - для карточек метрик и графика
- `button` - для интерактивных элементов
- `tabs` - для переключателя периодов

Файлы будут созданы в `components/ui/`:

- `components/ui/card.tsx`
- `components/ui/button.tsx`
- `components/ui/tabs.tsx`

### 3. Установка библиотеки для графиков

**Команда:**

```bash
cd frontend
pnpm add recharts
pnpm add -D @types/recharts
```

Recharts - рекомендованная библиотека для графиков в экосистеме shadcn/ui, declarative подход, хорошая интеграция с React.

### 4. Реализация компонента MetricCard

**Файл:** `frontend/components/dashboard/metric-card.tsx`

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { MetricCard as MetricCardData, Trend } from '@/types/api';

interface MetricCardProps {
  title: string;
  data: MetricCardData;
  format?: 'number' | 'percent';
}

export function MetricCard({ title, data, format = 'number' }: MetricCardProps) {
  // Форматирование значения (разделители тысяч для number, добавление % для percent)
  // Иконка тренда: ArrowUp (green), ArrowDown (red), Minus (gray)
  // Отображение изменения в процентах с цветом по тренду
  // Описание снизу мелким текстом
}
```

Логика:

- Использует `Card` из shadcn/ui
- Форматирует значение в зависимости от типа (число/процент)
- Показывает иконку и цвет по тренду (green для up, red для down, gray для steady)
- Отображает description из API

### 5. Реализация компонента TimelineChart

**Файл:** `frontend/components/dashboard/timeline-chart.tsx`

```typescript
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { TimelinePoint } from '@/types/api';

interface TimelineChartProps {
  data: TimelinePoint[];
  title: string;
  description?: string;
}

export function TimelineChart({ data, title, description }: TimelineChartProps) {
  // ResponsiveContainer для адаптивности
  // AreaChart с 3 линиями (как на референсе)
  // Форматирование дат для оси X (сокращенный формат)
  // Tooltip с детальной информацией
}
```

Важно:

- `'use client'` директива (Recharts требует client-side)
- Используем `ResponsiveContainer` для адаптивности
- Форматирование дат: для 7d показываем день недели, для 30d - короткую дату, для 3m - месяц
- Градиентная заливка области как на референсе

### 6. Реализация компонента PeriodSelector

**Файл:** `frontend/components/dashboard/period-selector.tsx`

```typescript
'use client';

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useRouter, useSearchParams } from 'next/navigation';
import { Period } from '@/types/api';

const PERIOD_LABELS: Record<Period, string> = {
  '7d': 'Last 7 days',
  '30d': 'Last 30 days',
  '3m': 'Last 3 months',
};

export function PeriodSelector() {
  // Чтение текущего периода из URL params
  // Переключение через router.push с обновлением query param
}
```

Логика:

- Использует `Tabs` из shadcn/ui
- Читает период из URL searchParams (по умолчанию '7d')
- При смене периода обновляет URL через `router.push()`
- Триггерит rerender страницы с новыми данными

### 7. Создание компонента Header

**Файл:** `frontend/components/layout/header.tsx`

```typescript
import { Github } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="flex items-center justify-between border-b px-6 py-4">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md border">
          <span className="text-sm font-semibold">З</span>
        </div>
        <h1 className="text-xl font-semibold">Знайкин Dashboard</h1>
      </div>
      <Button variant="outline" size="sm" asChild>
        <a 
          href="https://github.com/systech-aidd/telegram-bot" 
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2"
        >
          <Github className="h-4 w-4" />
          GitHub
        </a>
      </Button>
    </header>
  );
}
```

Header с:

- Логотипом "З" (первая буква "Знайкин")
- Названием проекта
- Кнопкой GitHub с иконкой из lucide-react

### 8. Обновление главной страницы

**Файл:** `frontend/app/page.tsx`

```typescript
import { getStats } from '@/lib/api';
import { Period } from '@/types/api';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TimelineChart } from '@/components/dashboard/timeline-chart';
import { PeriodSelector } from '@/components/dashboard/period-selector';

interface PageProps {
  searchParams: Promise<{ period?: Period }>;
}

export default async function DashboardPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const period = params.period || '7d';
  const stats = await getStats(period);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Grid метрик: 4 колонки на desktop, 1 на mobile */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Messages" data={stats.metrics.total_messages} />
        <MetricCard title="Active Users" data={stats.metrics.active_users} />
        <MetricCard title="Total Dialogs" data={stats.metrics.total_dialogs} />
        <MetricCard title="Growth Rate" data={stats.metrics.growth_rate} format="percent" />
      </div>

      {/* График с селектором периода */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Total Visitors</CardTitle>
            <p className="text-sm text-muted-foreground">
              Total for the selected period
            </p>
          </div>
          <PeriodSelector />
        </CardHeader>
        <CardContent>
          <TimelineChart data={stats.timeline} />
        </CardContent>
      </Card>
    </div>
  );
}
```

Ключевые моменты:

- Server Component (загрузка данных на сервере)
- Период из URL searchParams
- Grid layout с responsive breakpoints
- Маппинг метрик API → UI компоненты

### 9. Обновление корневого Layout

**Файл:** `frontend/app/layout.tsx`

```typescript
import { Header } from '@/components/layout/header';
// ... остальные импорты

export const metadata: Metadata = {
  title: 'Знайкин Dashboard | Статистика диалогов',
  description: 'Dashboard статистики telegram-бота Знайкин',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className={/* fonts */}>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
```

Добавляем Header и обновляем metadata.

### 10. Создание утилит форматирования

**Файл:** `frontend/lib/format.ts`

```typescript
/**
 * Форматирование числа с разделителями тысяч
 * 1234567 -> "1,234,567"
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

/**
 * Форматирование процента
 * 4.5 -> "4.5%"
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

/**
 * Форматирование даты для графика
 */
export function formatChartDate(date: string, period: Period): string {
  const d = new Date(date);
  if (period === '7d') {
    return d.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' });
  } else if (period === '30d') {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } else {
    return d.toLocaleDateString('en-US', { month: 'short' });
  }
}
```

Централизованные функции форматирования данных.

### 11. Переменные окружения

**Файл:** `frontend/.env.local` (создать если нет)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Для разработки API работает локально на порту 8000.

## Проверка результата

### Запуск и тестирование

1. Запустить Backend API:
```bash
make run-api-dev
```

2. Запустить Frontend:
```bash
cd frontend
pnpm dev
```

3. Открыть http://localhost:3000

### Критерии приемки

- Отображаются 4 карточки метрик с корректными данными из API
- Показываются иконки и цвета трендов (green/red/gray)
- График timeline отображает данные с правильной осью времени
- Переключение периодов (7d/30d/3m) работает и обновляет данные
- Responsive layout: 1 колонка на mobile, 4 на desktop
- Числа форматированы с разделителями тысяч
- Growth Rate отображается как процент

## Технические детали

### Архитектурные решения

1. **Server Components для данных**: страница загружает данные на сервере через `getStats()`
2. **Client Components для интерактивности**: PeriodSelector и TimelineChart с `'use client'`
3. **URL как источник истины**: период хранится в query params
4. **Композиция компонентов**: MetricCard переиспользуется для всех метрик
5. **Типобезопасность**: все данные типизированы через TypeScript

### Маппинг данных API → UI

| API поле | UI название | Формат |

|----------|-------------|--------|

| total_messages | Total Messages | число с разделителями |

| active_users | Active Users | число с разделителями |

| total_dialogs | Total Dialogs | число с разделителями |

| growth_rate | Growth Rate | процент (X.X%) |

### Цветовая схема трендов

- `up`: green (text-green-600, stroke-green-600)
- `down`: red (text-red-600, stroke-red-600)
- `steady`: gray (text-gray-600, stroke-gray-600)

## Порядок выполнения

1. Создать спецификацию
2. Импортировать shadcn/ui компоненты
3. Установить Recharts
4. Реализовать UI компоненты (MetricCard, TimelineChart, PeriodSelector)
5. Создать Layout компоненты (Header)
6. Обновить главную страницу с интеграцией данных
7. Добавить утилиты форматирования
8. Протестировать с запущенным API

## Итог

После завершения спринта будет готовый функциональный dashboard с:

- 4 карточками ключевых метрик
- Интерактивным графиком timeline
- Переключением периодов
- Адаптивным дизайном
- Интеграцией с Mock API

### To-dos

- [ ] Создать dashboard-requirements.md со спецификацией UI компонентов и требований
- [ ] Импортировать shadcn/ui компоненты (card, button, tabs)
- [ ] Установить библиотеку Recharts для графиков
- [ ] Реализовать компонент MetricCard для отображения карточек метрик
- [ ] Реализовать компонент TimelineChart с использованием Recharts
- [ ] Реализовать компонент PeriodSelector для переключения периодов
- [ ] Создать компонент Header для layout
- [ ] Создать утилиты форматирования чисел и дат в lib/format.ts
- [ ] Обновить app/page.tsx с интеграцией всех компонентов и загрузкой данных
- [ ] Обновить app/layout.tsx с добавлением Header и metadata
- [ ] Создать .env.local с переменными окружения для API URL
- [ ] Протестировать интеграцию: запустить API и Frontend, проверить работу dashboard