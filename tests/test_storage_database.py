"""Тесты для Database класса с PostgreSQL."""

import pytest

from src.storage.database import Database
from src.storage.models import Message


@pytest.fixture
async def db():
    """Фикстура для тестовой PostgreSQL БД.

    Использует БД из docker-compose.
    Перед каждым тестом очищает таблицу messages.
    """
    database = Database(
        host="localhost",
        port=5432,
        database="systech_aidd",
        user="postgres",
        password="postgres",
    )
    async with database:
        # Очищаем таблицу перед каждым тестом (hard delete для тестов)
        assert database._pool is not None
        async with database._pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE messages RESTART IDENTITY CASCADE")
        yield database


@pytest.mark.asyncio
async def test_init_db():
    """Тест подключения и применения миграций."""
    db = Database(
        host="localhost",
        port=5432,
        database="systech_aidd",
        user="postgres",
        password="postgres",
    )
    async with db:
        await db.init_db()
        # Проверяем что connection pool создан
        assert db._pool is not None


@pytest.mark.asyncio
async def test_save_message_user(db):
    """Тест сохранения user сообщения с автоматическим content_length."""
    msg = Message(
        user_id=123,
        chat_id=123,
        role="user",
        content="Hello",
        content_length=5,  # Будет перезаписан в save_message
    )
    await db.save_message(msg)

    # Проверяем что сообщение сохранено
    history = await db.get_history(chat_id=123, user_id=123, limit=10)
    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[0].content_length == 5
    assert history[0].is_deleted is False


@pytest.mark.asyncio
async def test_save_message_assistant(db):
    """Тест сохранения assistant сообщения."""
    msg = Message(
        user_id=456,
        chat_id=456,
        role="assistant",
        content="Hi there",
        content_length=8,
    )
    await db.save_message(msg)

    history = await db.get_history(chat_id=456, user_id=456, limit=10)
    assert len(history) == 1
    assert history[0].role == "assistant"
    assert history[0].content == "Hi there"
    assert history[0].content_length == 8


@pytest.mark.asyncio
async def test_content_length_calculated(db):
    """Тест что content_length вычисляется правильно."""
    long_content = "A" * 1000
    msg = Message(
        user_id=999,
        chat_id=999,
        role="user",
        content=long_content,
        content_length=0,  # Неважно, будет перезаписан
    )
    await db.save_message(msg)

    history = await db.get_history(chat_id=999, user_id=999, limit=10)
    assert len(history) == 1
    assert history[0].content_length == 1000


@pytest.mark.asyncio
async def test_get_history_empty(db):
    """Тест получения пустой истории."""
    history = await db.get_history(chat_id=999, user_id=999, limit=10)
    assert len(history) == 0


@pytest.mark.asyncio
async def test_get_history_limit(db):
    """Тест ограничения количества сообщений."""
    # Сохраняем 5 сообщений
    for i in range(5):
        msg = Message(
            user_id=100,
            chat_id=100,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            content_length=len(f"Message {i}"),
        )
        await db.save_message(msg)

    # Загружаем только 3 последних
    history = await db.get_history(chat_id=100, user_id=100, limit=3)
    assert len(history) == 3
    # Проверяем что это последние сообщения (от старых к новым)
    assert history[0].content == "Message 2"
    assert history[1].content == "Message 3"
    assert history[2].content == "Message 4"


@pytest.mark.asyncio
async def test_get_history_order(db):
    """Тест правильного порядка сообщений (от старых к новым)."""
    msg1 = Message(
        user_id=200, chat_id=200, role="user", content="First", content_length=5
    )
    msg2 = Message(
        user_id=200, chat_id=200, role="assistant", content="Second", content_length=6
    )
    msg3 = Message(
        user_id=200, chat_id=200, role="user", content="Third", content_length=5
    )

    await db.save_message(msg1)
    await db.save_message(msg2)
    await db.save_message(msg3)

    history = await db.get_history(chat_id=200, user_id=200, limit=10)
    assert len(history) == 3
    assert history[0].content == "First"
    assert history[1].content == "Second"
    assert history[2].content == "Third"


@pytest.mark.asyncio
async def test_clear_history_soft_delete(db):
    """Тест что clear_history делает soft delete (is_deleted = TRUE)."""
    # Сохраняем сообщения
    msg1 = Message(
        user_id=300, chat_id=300, role="user", content="Test", content_length=4
    )
    msg2 = Message(
        user_id=300, chat_id=300, role="assistant", content="Response", content_length=8
    )
    await db.save_message(msg1)
    await db.save_message(msg2)

    # Очищаем (soft delete)
    await db.clear_history(chat_id=300, user_id=300)

    # Проверяем что get_history не возвращает удалённые
    history = await db.get_history(chat_id=300, user_id=300, limit=10)
    assert len(history) == 0

    # Проверяем что в БД записи остались с is_deleted = TRUE
    assert db._pool is not None
    async with db._pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, is_deleted FROM messages WHERE chat_id = $1 AND user_id = $2",
            300,
            300,
        )
        assert len(rows) == 2
        assert all(row["is_deleted"] is True for row in rows)


@pytest.mark.asyncio
async def test_get_history_excludes_deleted(db):
    """Тест что get_history не возвращает удалённые сообщения."""
    # Сохраняем 3 сообщения
    for i in range(3):
        msg = Message(
            user_id=400,
            chat_id=400,
            role="user",
            content=f"Message {i}",
            content_length=len(f"Message {i}"),
        )
        await db.save_message(msg)

    # Вручную помечаем первое сообщение как удалённое
    assert db._pool is not None
    async with db._pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE messages
            SET is_deleted = TRUE
            WHERE chat_id = $1 AND user_id = $2 AND content = $3
            """,
            400,
            400,
            "Message 0",
        )

    # get_history должен вернуть только 2 активных сообщения
    history = await db.get_history(chat_id=400, user_id=400, limit=10)
    assert len(history) == 2
    assert history[0].content == "Message 1"
    assert history[1].content == "Message 2"


@pytest.mark.asyncio
async def test_clear_history_isolation(db):
    """Тест что очистка не затрагивает других пользователей."""
    # Сохраняем для разных пользователей
    msg1 = Message(
        user_id=500, chat_id=500, role="user", content="User 1", content_length=6
    )
    msg2 = Message(
        user_id=600, chat_id=600, role="user", content="User 2", content_length=6
    )
    await db.save_message(msg1)
    await db.save_message(msg2)

    # Очищаем для user 500
    await db.clear_history(chat_id=500, user_id=500)

    # Проверяем что user 600 не затронут
    history = await db.get_history(chat_id=600, user_id=600, limit=10)
    assert len(history) == 1
    assert history[0].content == "User 2"


@pytest.mark.asyncio
async def test_context_manager():
    """Тест async context manager."""
    db = Database(
        host="localhost",
        port=5432,
        database="systech_aidd",
        user="postgres",
        password="postgres",
    )

    async with db:
        await db.init_db()
        assert db._pool is not None

        # Проверяем что можем работать с БД
        msg = Message(
            user_id=700, chat_id=700, role="user", content="Test", content_length=4
        )
        await db.save_message(msg)

    # После выхода из context manager pool закрыт
    assert db._pool is None


@pytest.mark.asyncio
async def test_connection_not_opened_raises_error():
    """Тест что работа без connection pool выбрасывает ошибку."""
    db = Database(
        host="localhost",
        port=5432,
        database="systech_aidd",
        user="postgres",
        password="postgres",
    )

    msg = Message(
        user_id=800, chat_id=800, role="user", content="Test", content_length=4
    )

    with pytest.raises(RuntimeError, match="Database not connected"):
        await db.save_message(msg)
