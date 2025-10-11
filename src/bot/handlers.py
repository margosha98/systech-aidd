"""Обработчики команд и сообщений бота."""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ChatAction
from aiogram.filters import Command

from src.config import Config
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)
router = Router()

# Глобальные переменные для зависимостей
llm_client: LLMClient | None = None
config: Config | None = None


def setup_handlers(client: LLMClient, cfg: Config) -> None:
    """Настройка handlers с зависимостями.
    
    Args:
        client: LLM клиент
        cfg: Конфигурация
    """
    global llm_client, config
    llm_client = client
    config = cfg
    logger.info("Handlers configured with dependencies")


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


@router.message()
async def handle_message(message: Message) -> None:
    """Обработчик текстовых сообщений.
    
    Args:
        message: Входящее сообщение от пользователя
    """
    # Проверяем что есть текст и инициализированы зависимости
    if not message.text or not llm_client or not config:
        return
    
    logger.info(
        f"Received message from user_id={message.from_user.id}, "
        f"chat_id={message.chat.id}, length={len(message.text)}"
    )
    
    try:
        # Показываем индикатор "печатает..."
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING
        )
        
        # Получаем ответ от LLM
        response = await llm_client.get_response(
            user_message=message.text,
            system_prompt=config.system_prompt
        )
        
        # Отправляем ответ пользователю
        await message.answer(response)
        logger.info(f"Response sent to user_id={message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.answer(
            "Извините, произошла ошибка при обработке вашего сообщения. "
            "Попробуйте позже."
        )

