"""Модели данных для storage layer."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Message:
    """Модель сообщения в диалоге.

    Attributes:
        user_id: Telegram user_id
        chat_id: Telegram chat_id
        role: Роль отправителя ('user' или 'assistant')
        content: Текст сообщения
        content_length: Длина контента в символах (вычисляется автоматически)
        username: Telegram username пользователя (или user_id как строка, если username отсутствует)
        id: ID сообщения в БД (опционально)
        created_at: Время создания (опционально)
        is_deleted: Флаг мягкого удаления (False - активное, True - удалённое)
    """

    user_id: int
    chat_id: int
    role: Literal["user", "assistant"]
    content: str
    content_length: int
    username: str
    id: int | None = None
    created_at: datetime | None = None
    is_deleted: bool = False
