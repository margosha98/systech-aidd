/**
 * TypeScript типы для API, синхронизированные с backend Pydantic моделями
 * Источник: backend/api/models.py
 */

export type Period = '7d' | '30d' | '3m';
export type Trend = 'up' | 'down' | 'steady';

export interface MetricCard {
  value: number;
  change: number;
  trend: Trend;
  description: string;
}

export interface TimelinePoint {
  date: string; // Формат: YYYY-MM-DD
  total_messages: number;
  active_users: number;
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

// Типы для Chat API
export type ChatMode = 'normal' | 'admin';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  mode: ChatMode;
  session_id: string;
}

export interface ChatResponse {
  message: string;
  sql_query?: string;
  mode: ChatMode;
}
