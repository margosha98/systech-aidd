"""Работа с SQLite базой данных."""
import logging
from pathlib import Path
import aiosqlite
from datetime import datetime

from src.storage.models import Message

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с SQLite базой данных."""
    
    def __init__(self, db_path: str):
        """Инициализация Database.
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        logger.info(f"Database initialized with path: {db_path}")
    
    async def init_db(self) -> None:
        """Создание таблицы messages и индексов."""
        # Создаем директорию для БД если её нет
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
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
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_user 
                ON messages(chat_id, user_id, created_at DESC)
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def save_message(self, message: Message) -> None:
        """Сохранение сообщения в БД.
        
        Args:
            message: Сообщение для сохранения
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO messages (user_id, chat_id, role, content)
                    VALUES (?, ?, ?, ?)
                    """,
                    (message.user_id, message.chat_id, message.role, message.content)
                )
                await db.commit()
                
            logger.info(
                f"Message saved: user_id={message.user_id}, "
                f"chat_id={message.chat_id}, role={message.role}"
            )
                
        except Exception as e:
            logger.error(f"Database error while saving message: {e}")
            raise
    
    async def get_history(
        self, 
        chat_id: int, 
        user_id: int, 
        limit: int
    ) -> list[Message]:
        """Получение последних N сообщений из истории.
        
        Args:
            chat_id: ID чата
            user_id: ID пользователя
            limit: Максимальное количество сообщений
            
        Returns:
            Список сообщений (от старых к новым)
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute(
                    """
                    SELECT id, user_id, chat_id, role, content, created_at
                    FROM messages
                    WHERE chat_id = ? AND user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (chat_id, user_id, limit)
                ) as cursor:
                    rows = await cursor.fetchall()
                    
                    # Преобразуем в список Message и разворачиваем 
                    # (от старых к новым)
                    messages = [
                        Message(
                            id=row["id"],
                            user_id=row["user_id"],
                            chat_id=row["chat_id"],
                            role=row["role"],
                            content=row["content"],
                            created_at=datetime.fromisoformat(row["created_at"]) 
                                if row["created_at"] else None
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
        """Очистка истории для пользователя.
        
        Args:
            chat_id: ID чата
            user_id: ID пользователя
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    DELETE FROM messages
                    WHERE chat_id = ? AND user_id = ?
                    """,
                    (chat_id, user_id)
                )
                await db.commit()
                
            logger.info(
                f"History cleared: chat_id={chat_id}, user_id={user_id}"
            )
                
        except Exception as e:
            logger.error(f"Database error while clearing history: {e}")
            raise

