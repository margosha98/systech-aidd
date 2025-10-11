"""Протоколы (интерфейсы) для LLM layer."""

from typing import Protocol

from src.storage.models import Message


class LLMClientProtocol(Protocol):
    """Протокол для работы с LLM клиентом.

    Определяет интерфейс для получения ответов от языковой модели.
    Используется для dependency injection и тестирования.
    """

    async def get_response(self, messages: list[Message], system_prompt: str) -> str:
        """Получает ответ от LLM с учетом истории.

        Args:
            messages: История сообщений диалога
            system_prompt: Системный промпт для LLM

        Returns:
            Ответ от LLM
        """
        ...
