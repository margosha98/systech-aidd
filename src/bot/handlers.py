"""Обработчики команд и сообщений бота."""

import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message as TelegramMessage

from src.config import Config
from src.llm.protocols import LLMClientProtocol
from src.storage.models import Message
from src.storage.protocols import DatabaseProtocol

logger = logging.getLogger(__name__)


class BotHandlers:
    """Обработчики команд и сообщений бота с dependency injection.

    Использует DI через конструктор для передачи зависимостей.
    Все handlers - методы класса, зависимости доступны через self.
    """

    def __init__(
        self,
        llm_client: LLMClientProtocol,
        database: DatabaseProtocol,
        config: Config,
    ):
        """Инициализация handlers с зависимостями.

        Args:
            llm_client: Клиент для работы с LLM
            database: База данных для хранения истории
            config: Конфигурация приложения
        """
        self.llm_client = llm_client
        self.database = database
        self.config = config
        self.router = Router()
        self._register_handlers()
        logger.info("BotHandlers initialized with dependencies")

    def _register_handlers(self) -> None:
        """Регистрация handlers в router."""
        self.router.message(Command("start"))(self.cmd_start)
        self.router.message()(self.handle_message)

    async def cmd_start(self, message: TelegramMessage) -> None:
        """Обработчик команды /start.

        Args:
            message: Входящее сообщение от пользователя
        """
        if message.from_user:
            logger.info(f"Received /start command from user_id={message.from_user.id}")

        await message.answer(
            "👋 Привет! Я AI-ассистент <b>Systech AIDD</b>.\n\n"
            "Задай мне любой вопрос, и я постараюсь помочь!"
        )

    async def handle_message(self, message: TelegramMessage) -> None:
        """Обработчик текстовых сообщений.

        Args:
            message: Входящее сообщение от пользователя
        """
        # Проверяем что есть текст и необходимые данные
        if not message.text or not message.from_user:
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
                user_id=user_id, chat_id=chat_id, role="user", content=message.text
            )
            await self.database.save_message(user_message)

            # 2. Загружаем историю диалога
            history = await self.database.get_history(
                chat_id=chat_id, user_id=user_id, limit=self.config.max_history_messages
            )

            # Показываем индикатор "печатает..."
            if message.bot:
                await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

            # 3. Получаем ответ от LLM с историей
            response = await self.llm_client.get_response(
                messages=history, system_prompt=self.config.system_prompt
            )

            # 4. Сохраняем ответ ассистента
            assistant_message = Message(
                user_id=user_id, chat_id=chat_id, role="assistant", content=response
            )
            await self.database.save_message(assistant_message)

            # 5. Отправляем ответ пользователю
            await message.answer(response)
            logger.info(f"Response sent to user_id={user_id}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.answer(
                "Извините, произошла ошибка при обработке вашего сообщения. Попробуйте позже."
            )
