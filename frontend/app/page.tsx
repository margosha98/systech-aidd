import { getStats } from '@/lib/api';
import { Period } from '@/types/api';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TimelineChart } from '@/components/dashboard/timeline-chart';
import { PeriodSelector } from '@/components/dashboard/period-selector';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface PageProps {
  searchParams: Promise<{ period?: Period }>;
}

export default async function DashboardPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const period = (params.period as Period) || '7d';
  
  let stats;
  try {
    stats = await getStats(period);
  } catch (error) {
    console.error('Failed to fetch stats:', error);
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Ошибка загрузки Dashboard</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Не удалось загрузить статистику. Убедитесь, что API сервер запущен.</p>
            <p className="text-sm text-muted-foreground mt-2">
              Ошибка: {error instanceof Error ? error.message : 'Неизвестная ошибка'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Grid метрик: 4 колонки на desktop, 2 на tablet, 1 на mobile */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Всего сообщений" data={stats.metrics.total_messages} />
        <MetricCard title="Активные пользователи" data={stats.metrics.active_users} />
        <MetricCard title="Всего диалогов" data={stats.metrics.total_dialogs} />
        <MetricCard title="Темп роста" data={stats.metrics.growth_rate} format="percent" />
      </div>

      {/* График с селектором периода */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Активность пользователей</CardTitle>
            <p className="text-sm text-muted-foreground">
              Данные за {period === '7d' ? 'последние 7 дней' : period === '30d' ? 'последние 30 дней' : 'последние 3 месяца'}
            </p>
          </div>
          <PeriodSelector currentPeriod={period} />
        </CardHeader>
        <CardContent>
          <TimelineChart data={stats.timeline} period={period} />
        </CardContent>
      </Card>
    </div>
  );
}
