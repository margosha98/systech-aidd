"""Инициализация и запуск Telegram бота."""

import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import Config

logger = logging.getLogger(__name__)


def create_bot(config: Config, handlers_router: Router) -> tuple[Bot, Dispatcher]:
    """Создает экземпляры бота и диспетчера.

    Args:
        config: Объект конфигурации
        handlers_router: Router с зарегистрированными handlers

    Returns:
        Кортеж (Bot, Dispatcher)
    """
    bot = Bot(
        token=config.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(handlers_router)

    return bot, dp


async def start_polling(bot: Bot, dp: Dispatcher) -> None:
    """Запускает polling режим бота.

    Args:
        bot: Экземпляр бота
        dp: Экземпляр диспетчера
    """
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)
