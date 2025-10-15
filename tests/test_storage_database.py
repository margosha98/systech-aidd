"""Тесты для Database класса."""

import pytest

from src.storage.database import Database
from src.storage.models import Message


@pytest.fixture
async def db():
    """Фикстура для тестовой БД в памяти."""
    database = Database(":memory:")
    async with database:
        await database.init_db()
        yield database


@pytest.mark.asyncio
async def test_init_db():
    """Тест создания таблицы messages."""
    db = Database(":memory:")
    async with db:
        await db.init_db()
        # Проверяем что таблица создана (нет исключений)
        assert db._connection is not None


@pytest.mark.asyncio
async def test_save_message_user(db):
    """Тест сохранения user сообщения."""
    msg = Message(user_id=123, chat_id=123, role="user", content="Hello")
    await db.save_message(msg)

    # Проверяем что сообщение сохранено
    history = await db.get_history(chat_id=123, user_id=123, limit=10)
    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Hello"


@pytest.mark.asyncio
async def test_save_message_assistant(db):
    """Тест сохранения assistant сообщения."""
    msg = Message(user_id=456, chat_id=456, role="assistant", content="Hi there")
    await db.save_message(msg)

    history = await db.get_history(chat_id=456, user_id=456, limit=10)
    assert len(history) == 1
    assert history[0].role == "assistant"
    assert history[0].content == "Hi there"


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
    msg1 = Message(user_id=200, chat_id=200, role="user", content="First")
    msg2 = Message(user_id=200, chat_id=200, role="assistant", content="Second")
    msg3 = Message(user_id=200, chat_id=200, role="user", content="Third")

    await db.save_message(msg1)
    await db.save_message(msg2)
    await db.save_message(msg3)

    history = await db.get_history(chat_id=200, user_id=200, limit=10)
    assert len(history) == 3
    assert history[0].content == "First"
    assert history[1].content == "Second"
    assert history[2].content == "Third"


@pytest.mark.asyncio
async def test_clear_history(db):
    """Тест очистки истории."""
    # Сохраняем сообщения
    msg1 = Message(user_id=300, chat_id=300, role="user", content="Test")
    msg2 = Message(user_id=300, chat_id=300, role="assistant", content="Response")
    await db.save_message(msg1)
    await db.save_message(msg2)

    # Проверяем что сообщения есть
    history = await db.get_history(chat_id=300, user_id=300, limit=10)
    assert len(history) == 2

    # Очищаем
    await db.clear_history(chat_id=300, user_id=300)

    # Проверяем что история пуста
    history = await db.get_history(chat_id=300, user_id=300, limit=10)
    assert len(history) == 0


@pytest.mark.asyncio
async def test_clear_history_isolation(db):
    """Тест что очистка не затрагивает других пользователей."""
    # Сохраняем для разных пользователей
    msg1 = Message(user_id=400, chat_id=400, role="user", content="User 1")
    msg2 = Message(user_id=500, chat_id=500, role="user", content="User 2")
    await db.save_message(msg1)
    await db.save_message(msg2)

    # Очищаем для user 400
    await db.clear_history(chat_id=400, user_id=400)

    # Проверяем что user 500 не затронут
    history = await db.get_history(chat_id=500, user_id=500, limit=10)
    assert len(history) == 1
    assert history[0].content == "User 2"


@pytest.mark.asyncio
async def test_context_manager():
    """Тест async context manager."""
    db = Database(":memory:")

    async with db:
        await db.init_db()
        assert db._connection is not None

        # Проверяем что можем работать с БД
        msg = Message(user_id=600, chat_id=600, role="user", content="Test")
        await db.save_message(msg)

    # После выхода из context manager соединение закрыто
    assert db._connection is None


@pytest.mark.asyncio
async def test_connection_not_opened_raises_error():
    """Тест что работа без открытого соединения выбрасывает ошибку."""
    db = Database(":memory:")

    msg = Message(user_id=700, chat_id=700, role="user", content="Test")

    with pytest.raises(RuntimeError, match="Database not connected"):
        await db.save_message(msg)
