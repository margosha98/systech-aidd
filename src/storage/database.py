"""Работа с SQLite базой данных."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite

from src.storage.models import Message

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с SQLite базой данных.

    Использует единое соединение (connection pool) вместо создания
    нового соединения на каждый запрос. Поддерживает async context manager.
    """

    def __init__(self, db_path: str):
        """Инициализация Database.

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None
        logger.info(f"Database initialized with path: {db_path}")

    def _ensure_connected(self) -> None:
        """Проверка что соединение установлено (fail-fast).

        Raises:
            RuntimeError: Если соединение не установлено
        """
        if not self._connection:
            raise RuntimeError(
                "Database not connected. Use 'async with Database(path)' or call connect() first"
            )

    async def connect(self) -> None:
        """Открытие соединения с БД."""
        if self._connection is not None:
            logger.warning("Database connection already exists")
            return

        # Создаем директорию для БД если её нет
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        logger.info(f"Database connected: {self.db_path}")

    async def close(self) -> None:
        """Закрытие соединения с БД."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    async def __aenter__(self) -> "Database":
        """Вход в async context manager."""
        await self.connect()
        await self.init_db()
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Выход из async context manager."""
        await self.close()

    async def init_db(self) -> None:
        """Создание таблицы messages и индексов."""
        self._ensure_connected()
        assert self._connection is not None

        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Создаем индекс для быстрого поиска истории
        await self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_user
            ON messages(chat_id, user_id, created_at DESC)
        """)

        await self._connection.commit()
        logger.info("Database initialized successfully")

    async def save_message(self, message: Message) -> None:
        """Сохранение сообщения в БД.

        Args:
            message: Сообщение для сохранения
        """
        self._ensure_connected()
        assert self._connection is not None

        try:
            await self._connection.execute(
                """
                INSERT INTO messages (user_id, chat_id, role, content)
                VALUES (?, ?, ?, ?)
                """,
                (message.user_id, message.chat_id, message.role, message.content),
            )
            await self._connection.commit()

            logger.info(
                f"Message saved: user_id={message.user_id}, "
                f"chat_id={message.chat_id}, role={message.role}"
            )

        except Exception as e:
            logger.error(f"Database error while saving message: {e}")
            raise

    async def get_history(self, chat_id: int, user_id: int, limit: int) -> list[Message]:
        """Получение последних N сообщений из истории.

        Args:
            chat_id: ID чата
            user_id: ID пользователя
            limit: Максимальное количество сообщений

        Returns:
            Список сообщений (от старых к новым)
        """
        self._ensure_connected()
        assert self._connection is not None

        try:
            self._connection.row_factory = aiosqlite.Row

            async with self._connection.execute(
                """
                SELECT id, user_id, chat_id, role, content, created_at
                FROM messages
                WHERE chat_id = ? AND user_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (chat_id, user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()

                # Преобразуем в список Message и разворачиваем
                # (от старых к новым)
                messages_temp = []
                for row in rows:
                    messages_temp.append(
                        Message(
                            id=row["id"],
                            user_id=row["user_id"],
                            chat_id=row["chat_id"],
                            role=row["role"],
                            content=row["content"],
                            created_at=datetime.fromisoformat(row["created_at"])
                            if row["created_at"]
                            else None,
                        )
                    )
                
                # Разворачиваем список: от старых к новым
                messages = list(reversed(messages_temp))

                logger.info(
                    f"Retrieved {len(messages)} messages from history: "
                    f"chat_id={chat_id}, user_id={user_id}"
                )

                return messages

        except Exception as e:
            logger.error(f"Database error while getting history: {e}")
            raise

    async def clear_history(self, chat_id: int, user_id: int) -> None:
        """Очистка истории для пользователя.

        Args:
            chat_id: ID чата
            user_id: ID пользователя
        """
        self._ensure_connected()
        assert self._connection is not None

        try:
            await self._connection.execute(
                """
                DELETE FROM messages
                WHERE chat_id = ? AND user_id = ?
                """,
                (chat_id, user_id),
            )
            await self._connection.commit()

            logger.info(f"History cleared: chat_id={chat_id}, user_id={user_id}")

        except Exception as e:
            logger.error(f"Database error while clearing history: {e}")
            raise
