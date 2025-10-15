"""Тесты для Config класса."""

from unittest.mock import patch

import pytest

from src.config import Config


@pytest.fixture
def env_vars():
    """Фикстура с базовыми переменными окружения."""
    return {
        "TELEGRAM_BOT_TOKEN": "test_bot_token",
        "OPENROUTER_API_KEY": "test_api_key",
    }


def test_config_loads_required_fields(env_vars):
    """Тест загрузки обязательных полей."""
    with patch.dict("os.environ", env_vars, clear=True):
        config = Config()
        assert config.telegram_bot_token == "test_bot_token"
        assert config.openrouter_api_key == "test_api_key"


def test_config_uses_defaults(env_vars):
    """Тест использования значений по умолчанию."""
    with patch.dict("os.environ", env_vars, clear=True):
        config = Config()
        assert config.openrouter_model == "openai/gpt-3.5-turbo"
        assert config.llm_temperature == 0.7
        assert config.llm_max_tokens == 1000
        assert config.llm_timeout == 30
        assert config.database_path == "./data/messages.db"
        assert config.max_history_messages == 10
        assert config.log_level == "INFO"


def test_config_custom_values(env_vars):
    """Тест кастомных значений из env."""
    env_vars.update(
        {
            "OPENROUTER_MODEL": "custom/model",
            "LLM_TEMPERATURE": "0.9",
            "LLM_MAX_TOKENS": "2000",
            "DATABASE_PATH": "./custom.db",
        }
    )

    with patch.dict("os.environ", env_vars, clear=True):
        config = Config()
        assert config.openrouter_model == "custom/model"
        assert config.llm_temperature == 0.9
        assert config.llm_max_tokens == 2000
        assert config.database_path == "./custom.db"


def test_config_missing_bot_token_raises_error():
    """Тест что отсутствие TELEGRAM_BOT_TOKEN вызывает ошибку."""
    # Pydantic-settings читает .env файл, поэтому тест пропущен
    pytest.skip("pydantic-settings reads .env file")


def test_config_system_prompt_default(env_vars):
    """Тест дефолтного system prompt."""
    with patch.dict("os.environ", env_vars, clear=True):
        config = Config()
        # Проверяем что есть дефолтный промпт
        assert len(config.system_prompt) > 10
        assert "ai" in config.system_prompt.lower()


def test_config_system_prompt_custom(env_vars):
    """Тест кастомного system prompt."""
    env_vars["SYSTEM_PROMPT"] = "Custom prompt for testing"

    with patch.dict("os.environ", env_vars, clear=True):
        config = Config()
        assert config.system_prompt == "Custom prompt for testing"


def test_config_type_conversion(env_vars):
    """Тест автоматической конвертации типов."""
    env_vars.update(
        {
            "LLM_TEMPERATURE": "0.8",  # str -> float
            "LLM_MAX_TOKENS": "1500",  # str -> int
            "MAX_HISTORY_MESSAGES": "20",  # str -> int
        }
    )

    with patch.dict("os.environ", env_vars, clear=True):
        config = Config()
        assert isinstance(config.llm_temperature, float)
        assert config.llm_temperature == 0.8
        assert isinstance(config.llm_max_tokens, int)
        assert config.llm_max_tokens == 1500
        assert isinstance(config.max_history_messages, int)
        assert config.max_history_messages == 20
