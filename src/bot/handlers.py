"""Обработчики команд и сообщений бота."""
import logging
from aiogram import Router
from aiogram.types import Message as TelegramMessage
from aiogram.enums import ChatAction
from aiogram.filters import Command

from src.config import Config
from src.llm.client import LLMClient
from src.storage.database import Database
from src.storage.models import Message

logger = logging.getLogger(__name__)
router = Router()

# Глобальные переменные для зависимостей
llm_client: LLMClient | None = None
database: Database | None = None
config: Config | None = None


def setup_handlers(client: LLMClient, db: Database, cfg: Config) -> None:
    """Настройка handlers с зависимостями.
    
    Args:
        client: LLM клиент
        db: База данных
        cfg: Конфигурация
    """
    global llm_client, database, config
    llm_client = client
    database = db
    config = cfg
    logger.info("Handlers configured with dependencies")


@router.message(Command("start"))
async def cmd_start(message: TelegramMessage) -> None:
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
async def handle_message(message: TelegramMessage) -> None:
    """Обработчик текстовых сообщений.
    
    Args:
        message: Входящее сообщение от пользователя
    """
    # Проверяем что есть текст и инициализированы зависимости
    if not message.text or not llm_client or not database or not config:
        return
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    logger.info(
        f"Received message from user_id={user_id}, "
        f"chat_id={chat_id}, length={len(message.text)}"
    )
    
    try:
        # 1. Сохраняем сообщение пользователя
        user_message = Message(
            user_id=user_id,
            chat_id=chat_id,
            role="user",
            content=message.text
        )
        await database.save_message(user_message)
        
        # 2. Загружаем историю диалога
        history = await database.get_history(
            chat_id=chat_id,
            user_id=user_id,
            limit=config.max_history_messages
        )
        
        # Показываем индикатор "печатает..."
        await message.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.TYPING
        )
        
        # 3. Получаем ответ от LLM с историей
        response = await llm_client.get_response(
            messages=history,
            system_prompt=config.system_prompt
        )
        
        # 4. Сохраняем ответ ассистента
        assistant_message = Message(
            user_id=user_id,
            chat_id=chat_id,
            role="assistant",
            content=response
        )
        await database.save_message(assistant_message)
        
        # 5. Отправляем ответ пользователю
        await message.answer(response)
        logger.info(f"Response sent to user_id={user_id}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.answer(
            "Извините, произошла ошибка при обработке вашего сообщения. "
            "Попробуйте позже."
        )

