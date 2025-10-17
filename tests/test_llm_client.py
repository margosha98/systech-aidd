"""Тесты для LLMClient класса."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import Config
from src.llm.client import LLMClient
from src.storage.models import Message


@pytest.fixture
def mock_config():
    """Фикстура для мокового Config."""
    config = MagicMock(spec=Config)
    config.openrouter_api_key = "test_key"
    config.openrouter_model = "test/model"
    config.llm_temperature = 0.7
    config.llm_max_tokens = 1000
    config.llm_timeout = 30
    return config


@pytest.fixture
def llm_client(mock_config):
    """Фикстура для LLMClient."""
    return LLMClient(mock_config)


@pytest.mark.asyncio
async def test_get_response_simple(llm_client):
    """Тест простого запроса к LLM."""
    messages = [Message(user_id=1, chat_id=1, role="user", content="Hello", content_length=5, username="test_user")]
    system_prompt = "You are helpful assistant"

    # Мокаем ответ от API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hi there!"

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await llm_client.get_response(messages, system_prompt)

    assert result == "Hi there!"


@pytest.mark.asyncio
async def test_get_response_with_history(llm_client):
    """Тест запроса с историей диалога."""
    messages = [
        Message(user_id=1, chat_id=1, role="user", content="What is 2+2?", content_length=13, username="test_user"),
        Message(user_id=1, chat_id=1, role="assistant", content="4", content_length=1, username="test_user"),
        Message(user_id=1, chat_id=1, role="user", content="And 3+3?", content_length=8, username="test_user"),
    ]
    system_prompt = "You are a math teacher"

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "6"

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        result = await llm_client.get_response(messages, system_prompt)

        # Проверяем что API вызван с правильными параметрами
        call_args = mock_create.call_args
        api_messages = call_args.kwargs["messages"]

        # Должен быть system prompt + 3 сообщения из истории
        assert len(api_messages) == 4
        assert api_messages[0]["role"] == "system"
        assert api_messages[0]["content"] == system_prompt
        assert api_messages[1]["content"] == "What is 2+2?"
        assert api_messages[2]["content"] == "4"
        assert api_messages[3]["content"] == "And 3+3?"

    assert result == "6"


@pytest.mark.asyncio
async def test_get_response_api_error(llm_client):
    """Тест обработки ошибки API."""
    messages = [Message(user_id=1, chat_id=1, role="user", content="Test", content_length=4, username="test_user")]
    system_prompt = "Test prompt"

    with (
        patch.object(
            llm_client.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=Exception("API Error"),
        ),
        pytest.raises(Exception, match="API Error"),
    ):
        await llm_client.get_response(messages, system_prompt)


@pytest.mark.asyncio
async def test_get_response_uses_config_params(llm_client):
    """Тест что используются параметры из конфига."""
    messages = [Message(user_id=1, chat_id=1, role="user", content="Test", content_length=4, username="test_user")]
    system_prompt = "Test"

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        await llm_client.get_response(messages, system_prompt)

        # Проверяем параметры вызова
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["model"] == "test/model"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 1000


@pytest.mark.asyncio
async def test_get_response_empty_history(llm_client):
    """Тест запроса без истории (пустой список)."""
    messages = []
    system_prompt = "Test prompt"

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello"

    with patch.object(
        llm_client.client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_create:
        result = await llm_client.get_response(messages, system_prompt)

        # Проверяем что отправлен только system prompt
        api_messages = mock_create.call_args.kwargs["messages"]
        assert len(api_messages) == 1
        assert api_messages[0]["role"] == "system"

    assert result == "Hello"
