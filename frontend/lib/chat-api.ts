/**
 * API клиент для работы с чатом
 */

import { ChatRequest, ChatResponse, ChatMessage } from '@/types/api';

// Чат всегда работает на клиентской стороне, поэтому используем только NEXT_PUBLIC_API_URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Отправить сообщение в чат
 * @param request - Запрос с сообщением, режимом и session_id
 * @returns Promise с ответом от чата
 */
export async function sendChatMessage(
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Failed to send message: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Получить историю чата
 * @param sessionId - ID сессии
 * @param limit - Максимальное количество сообщений (по умолчанию 50)
 * @returns Promise со списком сообщений
 */
export async function getChatHistory(
  sessionId: string,
  limit: number = 50
): Promise<ChatMessage[]> {
  const response = await fetch(
    `${API_URL}/api/chat/history/${sessionId}?limit=${limit}`,
    {
      cache: 'no-store',
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }

  return response.json();
}
