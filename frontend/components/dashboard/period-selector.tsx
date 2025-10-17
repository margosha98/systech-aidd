'use client';

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useRouter } from 'next/navigation';
import { Period } from '@/types/api';

const PERIOD_LABELS: Record<Period, string> = {
  '7d': 'Последние 7 дней',
  '30d': 'Последние 30 дней',
  '3m': 'Последние 3 месяца',
};

const PERIODS: Period[] = ['7d', '30d', '3m'];

interface PeriodSelectorProps {
  currentPeriod: Period;
}

/**
 * Компонент для переключения периодов статистики
 */
export function PeriodSelector({ currentPeriod }: PeriodSelectorProps) {
  const router = useRouter();

  const handlePeriodChange = (value: string) => {
    router.push(`/?period=${value}`);
  };

  return (
    <Tabs value={currentPeriod} onValueChange={handlePeriodChange}>
      <TabsList>
        {PERIODS.map((period) => (
          <TabsTrigger key={period} value={period}>
            {PERIOD_LABELS[period]}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}

