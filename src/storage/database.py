"""Работа с PostgreSQL базой данных."""

import logging
from pathlib import Path
from typing import Any

import asyncpg  # type: ignore[import-untyped]

from src.storage.models import Message

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с PostgreSQL базой данных.

    Использует connection pool для эффективной работы с соединениями.
    Поддерживает async context manager и автоматическое применение миграций.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ):
        """Инициализация Database.

        Args:
            host: Хост PostgreSQL сервера
            port: Порт PostgreSQL сервера
            database: Имя базы данных
            user: Имя пользователя
            password: Пароль
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._pool: asyncpg.Pool | None = None
        logger.info(f"Database initialized: {host}:{port}/{database}")

    def _ensure_connected(self) -> None:
        """Проверка что connection pool создан (fail-fast).

        Raises:
            RuntimeError: Если connection pool не создан
        """
        if not self._pool:
            raise RuntimeError(
                "Database not connected. Use 'async with Database(...)' or call connect() first"
            )

    async def connect(self) -> None:
        """Создание connection pool."""
        if self._pool is not None:
            logger.warning("Database connection pool already exists")
            return

        self._pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            min_size=2,
            max_size=10,
        )
        logger.info(f"Database connection pool created: {self.host}:{self.port}/{self.database}")

    async def close(self) -> None:
        """Закрытие connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")

    async def __aenter__(self) -> "Database":
        """Вход в async context manager."""
        await self.connect()
        await self.init_db()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Выход из async context manager."""
        await self.close()

    async def init_db(self) -> None:
        """Применение миграций из папки migrations/."""
        self._ensure_connected()
        assert self._pool is not None

        migrations_dir = Path(__file__).parent.parent.parent / "migrations"
        if not migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {migrations_dir}")
            return

        # Получаем список SQL файлов, сортируем по имени
        migration_files = sorted(migrations_dir.glob("*.sql"))
        if not migration_files:
            logger.warning("No migration files found")
            return

        async with self._pool.acquire() as conn:
            for migration_file in migration_files:
                logger.info(f"Applying migration: {migration_file.name}")
                sql = migration_file.read_text(encoding="utf-8")
                await conn.execute(sql)
                logger.info(f"Migration applied: {migration_file.name}")

        logger.info("Database initialized successfully")

    async def save_message(self, message: Message) -> None:
        """Сохранение сообщения в БД.

        Args:
            message: Сообщение для сохранения
        """
        self._ensure_connected()
        assert self._pool is not None

        try:
            # Автоматически вычисляем content_length
            content_length = len(message.content)

            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO messages (user_id, chat_id, role, content, content_length)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    message.user_id,
                    message.chat_id,
                    message.role,
                    message.content,
                    content_length,
                )

            logger.info(
                f"Message saved: user_id={message.user_id}, "
                f"chat_id={message.chat_id}, role={message.role}, "
                f"content_length={content_length}"
            )

        except Exception as e:
            logger.error(f"Database error while saving message: {e}")
            raise

    async def get_history(self, chat_id: int, user_id: int, limit: int) -> list[Message]:
        """Получение последних N активных сообщений из истории.

        Args:
            chat_id: ID чата
            user_id: ID пользователя
            limit: Максимальное количество сообщений

        Returns:
            Список сообщений (от старых к новым)
        """
        self._ensure_connected()
        assert self._pool is not None

        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, user_id, chat_id, role, content, content_length,
                           created_at, is_deleted
                    FROM messages
                    WHERE chat_id = $1 AND user_id = $2 AND is_deleted = FALSE
                    ORDER BY created_at DESC, id DESC
                    LIMIT $3
                    """,
                    chat_id,
                    user_id,
                    limit,
                )

                # Преобразуем в список Message и разворачиваем (от старых к новым)
                messages = [
                    Message(
                        id=row["id"],
                        user_id=row["user_id"],
                        chat_id=row["chat_id"],
                        role=row["role"],
                        content=row["content"],
                        content_length=row["content_length"],
                        created_at=row["created_at"],
                        is_deleted=row["is_deleted"],
                    )
                    for row in reversed(rows)
                ]

                logger.info(
                    f"Retrieved {len(messages)} messages from history: "
                    f"chat_id={chat_id}, user_id={user_id}"
                )

                return messages

        except Exception as e:
            logger.error(f"Database error while getting history: {e}")
            raise

    async def clear_history(self, chat_id: int, user_id: int) -> None:
        """Очистка истории для пользователя (soft delete).

        Args:
            chat_id: ID чата
            user_id: ID пользователя
        """
        self._ensure_connected()
        assert self._pool is not None

        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE messages
                    SET is_deleted = TRUE
                    WHERE chat_id = $1 AND user_id = $2 AND is_deleted = FALSE
                    """,
                    chat_id,
                    user_id,
                )

            logger.info(f"History cleared (soft delete): chat_id={chat_id}, user_id={user_id}")

        except Exception as e:
            logger.error(f"Database error while clearing history: {e}")
            raise
