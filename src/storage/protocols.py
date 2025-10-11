"""Протоколы (интерфейсы) для storage layer."""

from typing import Protocol

from src.storage.models import Message


class DatabaseProtocol(Protocol):
    """Протокол для работы с базой данных.

    Определяет интерфейс для хранения и получения сообщений.
    Используется для dependency injection и тестирования.
    """

    async def init_db(self) -> None:
        """Инициализация базы данных (создание таблиц и индексов)."""
        ...

    async def save_message(self, message: Message) -> None:
        """Сохранение сообщения в базу данных.

        Args:
            message: Сообщение для сохранения
        """
        ...

    async def get_history(self, chat_id: int, user_id: int, limit: int) -> list[Message]:
        """Получение истории сообщений.

        Args:
            chat_id: ID чата
            user_id: ID пользователя
            limit: Максимальное количество сообщений

        Returns:
            Список сообщений (от старых к новым)
        """
        ...

    async def clear_history(self, chat_id: int, user_id: int) -> None:
        """Очистка истории для пользователя.

        Args:
            chat_id: ID чата
            user_id: ID пользователя
        """
        ...
