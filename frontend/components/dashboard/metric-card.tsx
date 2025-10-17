import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { MetricCard as MetricCardData, Trend } from '@/types/api';
import { formatNumber, formatPercent, formatChange } from '@/lib/format';

interface MetricCardProps {
  title: string;
  data: MetricCardData;
  format?: 'number' | 'percent';
}

/**
 * Получить иконку тренда в зависимости от типа
 */
function getTrendIcon(trend: Trend) {
  switch (trend) {
    case 'up':
      return <ArrowUp className="h-4 w-4" />;
    case 'down':
      return <ArrowDown className="h-4 w-4" />;
    case 'steady':
      return <Minus className="h-4 w-4" />;
  }
}

/**
 * Получить цвет для тренда
 */
function getTrendColor(trend: Trend) {
  switch (trend) {
    case 'up':
      return 'text-green-600';
    case 'down':
      return 'text-red-600';
    case 'steady':
      return 'text-gray-600';
  }
}

/**
 * Карточка метрики с трендом и описанием
 */
export function MetricCard({ title, data, format = 'number' }: MetricCardProps) {
  const formattedValue =
    format === 'percent' ? formatPercent(data.value) : formatNumber(data.value);

  const trendColor = getTrendColor(data.trend);
  const changeColor = data.change > 0 ? 'text-green-600' : data.change < 0 ? 'text-red-600' : 'text-gray-600';

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={trendColor}>{getTrendIcon(data.trend)}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formattedValue}</div>
        <div className="flex items-center gap-1 pt-1">
          <span className={`text-xs font-medium ${changeColor}`}>
            {formatChange(data.change)}
          </span>
          <p className="text-xs text-muted-foreground">{data.description}</p>
        </div>
      </CardContent>
    </Card>
  );
}

