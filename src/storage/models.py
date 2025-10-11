"""Модели данных для storage layer."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Модель сообщения в диалоге.
    
    Attributes:
        user_id: Telegram user_id
        chat_id: Telegram chat_id
        role: Роль отправителя ('user' или 'assistant')
        content: Текст сообщения
        id: ID сообщения в БД (опционально)
        created_at: Время создания (опционально)
    """
    user_id: int
    chat_id: int
    role: str  # 'user' | 'assistant'
    content: str
    id: int | None = None
    created_at: datetime | None = None

