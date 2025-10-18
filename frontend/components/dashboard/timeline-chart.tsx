'use client';

import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TimelinePoint, Period } from '@/types/api';
import { formatChartDate, formatNumber } from '@/lib/format';

interface TimelineChartProps {
  data: TimelinePoint[];
  period: Period;
}

/**
 * График timeline с несколькими метриками
 */
export function TimelineChart({ data, period }: TimelineChartProps) {
  // Преобразуем данные для графика с форматированными датами
  const chartData = data.map((point) => ({
    ...point,
    formattedDate: formatChartDate(point.date, period),
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id="colorMessages" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.5} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.5} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="formattedDate"
          className="text-xs"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
        />
        <YAxis
          className="text-xs"
          tick={{ fill: 'hsl(var(--muted-foreground))' }}
          tickFormatter={(value) => formatNumber(value)}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              return (
                <div className="rounded-lg border bg-background p-3 shadow-sm">
                  <div className="grid gap-2">
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Дата
                      </span>
                      <span className="font-bold text-muted-foreground">
                        {payload[0].payload.formattedDate}
                      </span>
                    </div>
                    {payload.map((entry, index) => (
                      <div key={index} className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                          <div
                            className="h-2 w-2 rounded-full"
                            style={{ backgroundColor: entry.color }}
                          />
                          <span className="text-xs text-muted-foreground">{entry.name}</span>
                        </div>
                        <span className="font-bold">{formatNumber(entry.value as number)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            }
            return null;
          }}
        />
        <Legend
          wrapperStyle={{ paddingTop: '20px' }}
          formatter={(value) => {
            const labels: Record<string, string> = {
              total_messages: 'Всего сообщений',
              active_users: 'Активные пользователи',
            };
            return labels[value] || value;
          }}
        />
        <Area
          type="monotone"
          dataKey="total_messages"
          name="total_messages"
          stroke="#3b82f6"
          strokeWidth={3}
          fill="url(#colorMessages)"
        />
        <Area
          type="monotone"
          dataKey="active_users"
          name="active_users"
          stroke="#22c55e"
          strokeWidth={3}
          fill="url(#colorUsers)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

