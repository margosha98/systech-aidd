"""Тесты для BotHandlers класса."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, User
from aiogram.types import Message as TelegramMessage

from src.bot.handlers import BotHandlers
from src.storage.models import Message


@pytest.fixture
def mock_llm_client():
    """Фикстура для мокового LLMClient."""
    client = AsyncMock()
    client.get_response = AsyncMock(return_value="LLM response")
    return client


@pytest.fixture
def mock_database():
    """Фикстура для моковой Database."""
    db = AsyncMock()
    db.save_message = AsyncMock()
    db.get_history = AsyncMock(return_value=[])
    db.clear_history = AsyncMock()
    return db


@pytest.fixture
def mock_config():
    """Фикстура для мокового Config."""
    config = MagicMock()
    config.system_prompt = "Test system prompt"
    config.max_history_messages = 10
    return config


@pytest.fixture
def handlers(mock_llm_client, mock_database, mock_config):
    """Фикстура для BotHandlers."""
    return BotHandlers(mock_llm_client, mock_database, mock_config)


def create_mock_message(text: str, user_id: int = 123, chat_id: int = 123):
    """Хелпер для создания мокового Telegram сообщения."""
    msg = MagicMock(spec=TelegramMessage)
    msg.text = text
    msg.from_user = MagicMock(spec=User)
    msg.from_user.id = user_id
    msg.chat = MagicMock(spec=Chat)
    msg.chat.id = chat_id
    msg.answer = AsyncMock()
    msg.bot = MagicMock()
    msg.bot.send_chat_action = AsyncMock()
    return msg


@pytest.mark.asyncio
async def test_cmd_start(handlers):
    """Тест команды /start."""
    msg = create_mock_message("/start")

    await handlers.cmd_start(msg)

    # Проверяем что отправлено приветствие
    msg.answer.assert_called_once()
    call_text = msg.answer.call_args[0][0]
    assert "прив" in call_text.lower()  # "Привееет"
    assert "ребенок" in call_text.lower() or "7 лет" in call_text
    assert "/role" in call_text


@pytest.mark.asyncio
async def test_handle_message_saves_user_message(handlers, mock_database):
    """Тест что пользовательское сообщение сохраняется в БД."""
    msg = create_mock_message("Hello bot", user_id=100, chat_id=100)

    await handlers.handle_message(msg)

    # Проверяем что save_message вызван для user сообщения
    assert mock_database.save_message.call_count == 2  # user + assistant
    first_call = mock_database.save_message.call_args_list[0][0][0]
    assert first_call.role == "user"
    assert first_call.content == "Hello bot"
    assert first_call.user_id == 100
    assert first_call.chat_id == 100


@pytest.mark.asyncio
async def test_handle_message_loads_history(handlers, mock_database, mock_config):
    """Тест что история загружается из БД."""
    msg = create_mock_message("Test message")

    await handlers.handle_message(msg)

    # Проверяем что get_history вызван с правильными параметрами
    mock_database.get_history.assert_called_once_with(
        chat_id=123, user_id=123, limit=mock_config.max_history_messages
    )


@pytest.mark.asyncio
async def test_handle_message_calls_llm(handlers, mock_llm_client, mock_database, mock_config):
    """Тест что LLM вызывается с историей."""
    msg = create_mock_message("What is AI?")

    # Мокаем историю
    history = [
        Message(
            user_id=123,
            chat_id=123,
            role="user",
            content="What is AI?",
            content_length=11,
        )
    ]
    mock_database.get_history.return_value = history

    await handlers.handle_message(msg)

    # Проверяем что LLM вызван
    mock_llm_client.get_response.assert_called_once_with(
        messages=history, system_prompt=mock_config.system_prompt
    )


@pytest.mark.asyncio
async def test_handle_message_saves_assistant_response(handlers, mock_database, mock_llm_client):
    """Тест что ответ ассистента сохраняется в БД."""
    msg = create_mock_message("Question")
    mock_llm_client.get_response.return_value = "Answer from LLM"

    await handlers.handle_message(msg)

    # Проверяем что save_message вызван для assistant сообщения
    assert mock_database.save_message.call_count == 2
    second_call = mock_database.save_message.call_args_list[1][0][0]
    assert second_call.role == "assistant"
    assert second_call.content == "Answer from LLM"


@pytest.mark.asyncio
async def test_handle_message_sends_response_to_user(handlers, mock_llm_client):
    """Тест что ответ отправляется пользователю."""
    msg = create_mock_message("Test")
    mock_llm_client.get_response.return_value = "Bot response"

    await handlers.handle_message(msg)

    # Проверяем что answer вызван с ответом LLM
    msg.answer.assert_called_once_with("Bot response")


@pytest.mark.asyncio
async def test_handle_message_shows_typing_action(handlers):
    """Тест что показывается индикатор 'печатает'."""
    msg = create_mock_message("Test")

    await handlers.handle_message(msg)

    # Проверяем что send_chat_action вызван
    msg.bot.send_chat_action.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_without_text_ignores(handlers, mock_database):
    """Тест что сообщения без текста игнорируются."""
    msg = create_mock_message("Test")
    msg.text = None

    await handlers.handle_message(msg)

    # Проверяем что ничего не вызвано
    mock_database.save_message.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_error_sends_error_message(handlers, mock_llm_client):
    """Тест обработки ошибки при работе с LLM."""
    msg = create_mock_message("Test")
    mock_llm_client.get_response.side_effect = Exception("LLM Error")

    await handlers.handle_message(msg)

    # Проверяем что отправлено сообщение об ошибке
    msg.answer.assert_called()
    error_msg = msg.answer.call_args[0][0]
    assert "ошибка" in error_msg.lower()


@pytest.mark.asyncio
async def test_cmd_reset(handlers, mock_database):
    """Тест команды /reset."""
    msg = create_mock_message("/reset", user_id=100, chat_id=100)

    await handlers.cmd_reset(msg)

    # Проверяем что clear_history вызван с правильными параметрами
    mock_database.clear_history.assert_called_once_with(chat_id=100, user_id=100)

    # Проверяем что отправлено подтверждение
    msg.answer.assert_called_once()
    call_text = msg.answer.call_args[0][0]
    assert "очищена" in call_text.lower() or "сброшена" in call_text.lower()


@pytest.mark.asyncio
async def test_cmd_role_responds(handlers):
    """Тест что команда /role отправляет ответ."""
    msg = create_mock_message("/role")

    await handlers.cmd_role(msg)

    # Проверяем что answer был вызван
    msg.answer.assert_called_once()


@pytest.mark.asyncio
async def test_cmd_role_shows_capabilities(handlers):
    """Тест что /role показывает информацию о ребенке."""
    msg = create_mock_message("/role")

    await handlers.cmd_role(msg)

    call_text = msg.answer.call_args[0][0]
    # Проверяем что есть информация о возрасте и интересах
    assert "7 лет" in call_text or "ребенок" in call_text.lower()
    assert "знаю" in call_text.lower()


@pytest.mark.asyncio
async def test_cmd_role_shows_limitations(handlers):
    """Тест что /role показывает ограничения знаний ребенка."""
    msg = create_mock_message("/role")

    await handlers.cmd_role(msg)

    call_text = msg.answer.call_args[0][0]
    # Проверяем что есть информация об ограничениях
    assert "не знаю" in call_text.lower() or "чего я не" in call_text.lower()
