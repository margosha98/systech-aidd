"""Точка входа приложения."""

import asyncio
import logging

from src.bot.bot import create_bot, start_polling
from src.bot.handlers import BotHandlers
from src.config import Config
from src.llm.client import LLMClient
from src.storage.database import Database


async def main() -> None:
    """Главная функция запуска бота."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info("Initializing bot...")

    try:
        # Загрузка конфигурации
        config = Config()  # type: ignore[call-arg]
        logger.info("Configuration loaded successfully")

        # Инициализация Database с context manager (graceful shutdown)
        async with Database(config.database_path) as database:
            # Создание LLM клиента
            llm_client = LLMClient(config)

            # Создание handlers с зависимостями (DI)
            bot_handlers = BotHandlers(llm_client, database, config)

            # Создание бота с router от handlers
            bot, dp = create_bot(config, bot_handlers.router)

            # Запуск polling
            logger.info("Bot is ready. Starting polling...")
            await start_polling(bot, dp)

        # Database connection автоматически закрывается при выходе из context manager
        logger.info("Bot stopped. Database connection closed.")

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
