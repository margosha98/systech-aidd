"""Точка входа приложения."""
import asyncio
import logging

from src.config import Config
from src.bot.bot import create_bot, start_polling
from src.llm.client import LLMClient
from src.storage.database import Database
from src.bot.handlers import setup_handlers


async def main() -> None:
    """Главная функция запуска бота."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Initializing bot...")
    
    try:
        # Загрузка конфигурации
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Инициализация Database
        database = Database(config.database_path)
        await database.init_db()
        
        # Создание LLM клиента
        llm_client = LLMClient(config)
        
        # Создание бота
        bot, dp = create_bot(config)
        
        # Настройка handlers с зависимостями
        setup_handlers(llm_client, database, config)
        
        # Запуск polling
        await start_polling(bot, dp)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

