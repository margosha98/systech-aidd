/**
 * Утилиты форматирования данных для dashboard
 */

import { Period } from '@/types/api';

/**
 * Форматирование числа с разделителями тысяч
 * @example formatNumber(1234567) -> "1,234,567"
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

/**
 * Форматирование процента с 1 знаком после запятой
 * @example formatPercent(4.5) -> "4.5%"
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

/**
 * Форматирование изменения в процентах со знаком
 * @example formatChange(12.5) -> "+12.5%"
 * @example formatChange(-8.0) -> "-8.0%"
 */
export function formatChange(value: number): string {
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

/**
 * Форматирование даты для графика в зависимости от периода
 * @param date - Дата в формате ISO (YYYY-MM-DD)
 * @param period - Период статистики
 */
export function formatChartDate(date: string, period: Period): string {
  const d = new Date(date);
  
  if (period === '7d') {
    // Для недели: короткий день недели + число (Пн 12)
    return d.toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric' });
  } else if (period === '30d') {
    // Для месяца: число + месяц (17 окт.)
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  } else {
    // Для 3 месяцев: только месяц (Окт.)
    return d.toLocaleDateString('ru-RU', { month: 'short' });
  }
}

