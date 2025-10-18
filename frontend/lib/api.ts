/**
 * API клиент для интеграции с backend
 */

import { StatsResponse, Period } from '@/types/api';

// Для клиентской части (браузер) используем localhost
// Для серверной части (SSR) используем внутренний адрес Docker
const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Серверная сторона (SSR) - используем внутренний Docker адрес
    return process.env.API_URL_SERVER || 'http://api:8000';
  }
  // Клиентская сторона (браузер) - используем localhost
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

/**
 * Получить статистику дашборда за указанный период
 * @param period - Период статистики ('7d', '30d', '3m')
 * @returns Promise с данными статистики
 */
export async function getStats(period: Period = '7d'): Promise<StatsResponse> {
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/stats?period=${period}`, {
    cache: 'no-store', // Для серверного рендеринга без кеширования
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }

  return response.json();
}
