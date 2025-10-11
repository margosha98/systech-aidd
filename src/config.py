"""Конфигурация приложения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Конфигурация приложения на основе pydantic-settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram Bot
    telegram_bot_token: str

    # Openrouter
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-3.5-turbo"

    # LLM settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    llm_timeout: int = 30

    # System prompt
    system_prompt: str = (
        "Ты полезный AI-ассистент. Отвечай на вопросы пользователя четко и понятно."
    )

    # Database
    database_path: str = "./data/messages.db"

    # History
    max_history_messages: int = 10

    # Logging
    log_level: str = "INFO"
