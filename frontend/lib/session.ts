/**
 * Управление сессиями чата
 */

/**
 * Генерирует новый уникальный ID сессии
 * @returns Новый session ID
 */
export function generateSessionId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 15);
  return `session_${timestamp}_${random}`;
}

/**
 * Получает существующий session ID из localStorage или создает новый
 * @returns Session ID
 */
export function getSessionId(): string {
  // На сервере всегда генерируем новый
  if (typeof window === 'undefined') {
    return generateSessionId();
  }

  // На клиенте пытаемся получить из localStorage
  let sessionId = localStorage.getItem('chat_session_id');
  
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('chat_session_id', sessionId);
  }

  return sessionId;
}

/**
 * Очищает текущую сессию и создает новую
 * @returns Новый session ID
 */
export function resetSession(): string {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('chat_session_id');
  }
  return getSessionId();
}

