"""Конфигурация приложения."""
import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Класс для загрузки и хранения конфигурации."""
    
    def __init__(self):
        """Загружает конфигурацию из переменных окружения."""
        # Загружаем .env из корня проекта
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path, encoding="utf-8")
        
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
        
        # Openrouter settings
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
        
        # LLM settings
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        self.llm_timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        
        # System prompt
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "Ты полезный AI-ассистент. Отвечай на вопросы пользователя четко и понятно."
        )

