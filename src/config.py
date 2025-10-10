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

