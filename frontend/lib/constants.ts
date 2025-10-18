/**
 * Константы приложения
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const PERIODS = {
  '7d': '7 дней',
  '30d': '30 дней',
  '3m': '3 месяца',
} as const;

export const METRIC_LABELS = {
  total_messages: 'Всего сообщений',
  active_users: 'Активные пользователи',
  total_dialogs: 'Всего диалогов',
  growth_rate: 'Темп роста',
} as const;
