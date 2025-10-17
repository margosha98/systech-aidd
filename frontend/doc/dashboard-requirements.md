# Спецификация Dashboard статистики

## Обзор

Dashboard отображает ключевые метрики telegram-бота "Знайкин" с возможностью переключения временных периодов и визуализацией данных через графики.

## Маппинг метрик API → UI

| API поле | UI название | Формат отображения | Описание |
|----------|-------------|-------------------|----------|
| `total_messages` | Total Messages | Число с разделителями (1,234,567) | Общее количество сообщений |
| `active_users` | Active Users | Число с разделителями (1,234) | Количество активных пользователей |
| `total_dialogs` | Total Dialogs | Число с разделителями (8,920) | Общее количество диалогов |
| `growth_rate` | Growth Rate | Процент (4.5%) | Темп роста сообщений |

## Визуальные индикаторы трендов

### Типы трендов

- **up** (рост): зеленая стрелка вверх, цвет текста green-600
- **down** (падение): красная стрелка вниз, цвет текста red-600
- **steady** (стабильно): серая горизонтальная линия, цвет текста gray-600

### Отображение изменений

Формат: `+X.X%` или `-X.X%` в зависимости от значения `change`
- Положительные значения: зеленый цвет
- Отрицательные значения: красный цвет
- Нулевые значения: серый цвет

## Компоненты Dashboard

### 1. MetricCard

**Расположение:** `components/dashboard/metric-card.tsx`

**Структура:**
- Заголовок (название метрики)
- Основное значение (крупный шрифт, форматированное число)
- Индикатор тренда (иконка + процент изменения)
- Описание (description из API, мелкий текст)

**Props:**
```typescript
interface MetricCardProps {
  title: string;           // Название метрики
  data: MetricCardData;    // Данные из API
  format?: 'number' | 'percent'; // Формат отображения
}
```

### 2. TimelineChart

**Расположение:** `components/dashboard/timeline-chart.tsx`

**Структура:**
- Area chart с градиентной заливкой
- Ось X: даты (формат зависит от периода)
- Ось Y: значения метрик
- Tooltip при наведении

**Форматирование дат:**
- `7d`: День недели + число (Mon 12)
- `30d`: Месяц + число (Oct 17)
- `3m`: Месяц (Oct)

**Props:**
```typescript
interface TimelineChartProps {
  data: TimelinePoint[];
  title: string;
  description?: string;
}
```

### 3. PeriodSelector

**Расположение:** `components/dashboard/period-selector.tsx`

**Функциональность:**
- Три варианта периодов: 7d, 30d, 3m
- Переключение через URL query параметры
- Активный период подсвечивается

**Лейблы:**
- `7d`: "Last 7 days"
- `30d`: "Last 30 days"
- `3m`: "Last 3 months"

### 4. Header

**Расположение:** `components/layout/header.tsx`

**Структура:**
- Логотип "З" в рамке
- Название проекта "Знайкин Dashboard"
- Кнопка GitHub с иконкой

**Примечания:**
- Sidebar скрыт (не реализуется в текущем спринте)
- Фиксируется сверху с border-bottom

## Логика переключения периодов

### Механизм

1. Период хранится в URL query параметре: `/?period=7d`
2. По умолчанию: `7d`
3. При клике на период в `PeriodSelector`:
   - Обновляется URL через `router.push()`
   - Server Component перезагружает данные с новым периодом
   - UI обновляется с новыми данными

### Реализация

```typescript
// Чтение периода
const searchParams = useSearchParams();
const period = searchParams.get('period') || '7d';

// Обновление периода
const router = useRouter();
router.push(`/?period=${newPeriod}`);
```

## Responsive layout

### Breakpoints

- **Mobile** (< 768px): 1 колонка для метрик
- **Tablet** (768px - 1024px): 2 колонки для метрик
- **Desktop** (> 1024px): 4 колонки для метрик

### Grid структура

```typescript
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
  {/* Метрики */}
</div>
```

## Форматирование данных

### Числа

Использование `Intl.NumberFormat` для разделителей тысяч:
```typescript
// 1234567 -> "1,234,567"
new Intl.NumberFormat('en-US').format(value)
```

### Проценты

Формат с 1 знаком после запятой:
```typescript
// 4.5 -> "4.5%"
value.toFixed(1) + '%'
```

### Даты

Формат зависит от периода (см. TimelineChart выше).

## Состояния UI

### Загрузка

- Server Component загружает данные до рендера
- Loading state не требуется (SSR)

### Ошибки

- Try-catch в Server Component
- Отображение ошибки через Next.js error boundary (будущая итерация)

### Пустые данные

- Проверка `timeline.length > 0`
- Сообщение "No data available" при отсутствии данных

## Интеграция с API

### Endpoint

```
GET http://localhost:8000/api/stats?period={period}
```

### Переменные окружения

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Типы данных

Все типы синхронизированы с backend через `types/api.ts`:
- `Period`: '7d' | '30d' | '3m'
- `Trend`: 'up' | 'down' | 'steady'
- `MetricCard`: value, change, trend, description
- `StatsResponse`: period, metrics, timeline

## Цветовая схема

### Tailwind классы

**Тренды:**
- Up: `text-green-600`, `stroke-green-600`
- Down: `text-red-600`, `stroke-red-600`
- Steady: `text-gray-600`, `stroke-gray-600`

**Фон карточек:**
- Card: `bg-card`, `border`

**Текст:**
- Заголовок: `text-xl font-semibold`
- Значение: `text-3xl font-bold`
- Описание: `text-sm text-muted-foreground`

## Accessibility

### Требования

- Семантический HTML (использование `<header>`, `<main>`)
- ARIA атрибуты через shadcn/ui компоненты
- Keyboard navigation для кнопок и табов
- Контрастность цветов (WCAG AA)

### Screen readers

- Описательные aria-labels для иконок
- Альтернативный текст для визуальных элементов

## Будущие улучшения

### Не входят в S3

- Таблица с детальными данными (скрыта по умолчанию)
- Sidebar навигация (скрыт по умолчанию)
- Фильтрация и сортировка данных
- Экспорт данных
- Real-time обновления

### Планируется в S4-S5

- ИИ-чат для запросов к статистике
- Переход на Real API с PostgreSQL
- Кеширование и оптимизация запросов

