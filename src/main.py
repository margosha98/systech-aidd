"""Точка входа приложения."""
import asyncio
import logging

from src.config import Config
from src.bot.bot import create_bot, start_polling


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
        
        # Создание и запуск бота
        bot, dp = create_bot(config)
        await start_polling(bot, dp)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

