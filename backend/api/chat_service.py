"""Сервис обработки чат сообщений."""

import logging
from datetime import datetime

import asyncpg  # type: ignore[import-untyped]

from backend.api.models import ChatMode, ChatRequest, ChatResponse
from backend.api.prompts import CHAT_SYSTEM_PROMPT
from backend.api.sql_generator import SQLGenerator
from src.llm.client import LLMClient
from src.storage.models import Message

logger = logging.getLogger(__name__)


class ChatService:
    """Сервис для обработки сообщений чата в разных режимах."""

    def __init__(self, llm_client: LLMClient, db_pool: asyncpg.Pool):
        """Инициализация сервиса чата.

        Args:
            llm_client: Клиент для работы с LLM
            db_pool: Connection pool к базе данных
        """
        self.llm_client = llm_client
        self.db_pool = db_pool
        self.sql_generator = SQLGenerator(llm_client)

    async def process_message(
        self, request: ChatRequest, history: list[Message]
    ) -> ChatResponse:
        """Обрабатывает сообщение в зависимости от режима.

        Args:
            request: Запрос с сообщением и режимом
            history: История предыдущих сообщений

        Returns:
            Ответ от чата

        Raises:
            Exception: При ошибке обработки
        """
        logger.info(
            f"Processing message in {request.mode} mode, "
            f"session={request.session_id}, history_len={len(history)}"
        )

        if request.mode == ChatMode.NORMAL:
            return await self._process_normal(request, history)
        else:
            return await self._process_admin(request, history)

    async def _process_normal(
        self, request: ChatRequest, history: list[Message]
    ) -> ChatResponse:
        """Обрабатывает сообщение в обычном режиме (прямое общение с LLM).

        Args:
            request: Запрос с сообщением
            history: История диалога

        Returns:
            Ответ от LLM
        """
        logger.info("Processing in NORMAL mode")

        try:
            # Добавляем текущее сообщение пользователя в историю
            current_message = Message(
                user_id=0,  # Для веб-чата используем 0
                chat_id=0,
                role="user",
                content=request.message,
                content_length=len(request.message),
                username="web_user",
            )

            # Объединяем историю с текущим сообщением
            full_history = history + [current_message]

            # Получаем ответ от LLM
            response = await self.llm_client.get_response(
                messages=full_history, system_prompt=CHAT_SYSTEM_PROMPT
            )

            logger.info(f"NORMAL mode response length: {len(response)}")

            return ChatResponse(message=response, mode=ChatMode.NORMAL)

        except Exception as e:
            logger.error(f"Error in NORMAL mode: {e}")
            raise

    async def _process_admin(
        self, request: ChatRequest, history: list[Message]
    ) -> ChatResponse:
        """Обрабатывает сообщение в режиме администратора (text-to-SQL pipeline).

        Args:
            request: Запрос с вопросом по статистике
            history: История диалога (не используется для SQL)

        Returns:
            Ответ с интерпретацией данных и SQL запросом
        """
        logger.info("Processing in ADMIN mode (text-to-SQL pipeline)")

        try:
            # 1. Генерация SQL через LLM
            sql = await self.sql_generator.generate_sql(request.message)

            # 2. Выполнение SQL запроса
            results = await self.sql_generator.execute_sql(sql, self.db_pool)

            # 3. Интерпретация результатов через LLM
            answer = await self.sql_generator.interpret_results(request.message, sql, results)

            logger.info(f"ADMIN mode: generated answer with SQL query")

            return ChatResponse(
                message=answer,
                sql_query=sql,  # Для debug/отображения в UI
                mode=ChatMode.ADMIN,
            )

        except Exception as e:
            logger.error(f"Error in ADMIN mode: {e}")
            # Возвращаем пользователю понятное сообщение об ошибке
            error_message = (
                f"Произошла ошибка при обработке запроса: {str(e)}\n\n"
                "Попробуйте переформулировать вопрос или обратитесь к администратору."
            )
            return ChatResponse(message=error_message, mode=ChatMode.ADMIN)

