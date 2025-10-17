"""Конфигурация для API сервера."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseSettings):
    """Конфигурация API с подключением к PostgreSQL.
    
    Использует те же переменные окружения, что и основной бот.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # PostgreSQL Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "systech_aidd"
    postgres_user: str = "postgres"
    postgres_password: str

    def get_db_dsn(self) -> str:
        """Получить DSN строку для подключения к PostgreSQL.
        
        Returns:
            DSN строка в формате postgresql://user:pass@host:port/db
        """
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

