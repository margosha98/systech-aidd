"""Обработчики команд и сообщений бота."""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start.
    
    Args:
        message: Входящее сообщение от пользователя
    """
    logger.info(f"Received /start command from user_id={message.from_user.id}")
    
    await message.answer(
        "👋 Привет! Я AI-ассистент <b>Systech AIDD</b>.\n\n"
        "Задай мне любой вопрос, и я постараюсь помочь!"
    )

