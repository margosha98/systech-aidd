"""Инициализация и запуск Telegram бота."""
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import Config
from src.bot.handlers import router

logger = logging.getLogger(__name__)


def create_bot(config: Config) -> tuple[Bot, Dispatcher]:
    """Создает экземпляры бота и диспетчера.
    
    Args:
        config: Объект конфигурации
        
    Returns:
        Кортеж (Bot, Dispatcher)
    """
    bot = Bot(
        token=config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)
    
    return bot, dp


async def start_polling(bot: Bot, dp: Dispatcher) -> None:
    """Запускает polling режим бота.
    
    Args:
        bot: Экземпляр бота
        dp: Экземпляр диспетчера
    """
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)

