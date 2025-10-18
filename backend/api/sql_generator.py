"""SQL генератор для text-to-SQL функциональности."""

import json
import logging
from typing import Any

import asyncpg  # type: ignore[import-untyped]

from backend.api.prompts import INTERPRET_RESULTS_PROMPT, TEXT_TO_SQL_PROMPT
from src.llm.client import LLMClient
from src.storage.models import Message

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Генератор SQL запросов через LLM и выполнение их."""

    def __init__(self, llm_client: LLMClient):
        """Инициализация SQL генератора.

        Args:
            llm_client: Клиент для работы с LLM
        """
        self.llm_client = llm_client

    async def generate_sql(self, question: str) -> str:
        """Генерирует SQL запрос на основе вопроса пользователя.

        Args:
            question: Вопрос пользователя на естественном языке

        Returns:
            SQL запрос в виде строки

        Raises:
            Exception: При ошибке генерации SQL
        """
        logger.info(f"Generating SQL for question: {question[:100]}")

        try:
            # Формируем промпт с вопросом
            prompt = TEXT_TO_SQL_PROMPT.format(question=question)

            # Создаем пустое сообщение с промптом для LLM
            messages = [
                Message(
                    user_id=0,
                    chat_id=0,
                    role="user",
                    content=prompt,
                    content_length=len(prompt),
                    username="system",
                )
            ]

            # Получаем SQL от LLM
            sql = await self.llm_client.get_response(
                messages=messages, system_prompt="Ты SQL эксперт. Генерируй только валидный SQL."
            )

            # Очищаем SQL от возможного markdown
            sql = sql.strip()
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
            sql = sql.strip()

            logger.info(f"Generated SQL: {sql}")
            return sql

        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise

    async def execute_sql(self, sql: str, db_pool: asyncpg.Pool) -> list[dict[str, Any]]:
        """Выполняет SQL запрос и возвращает результаты.

        Args:
            sql: SQL запрос для выполнения
            db_pool: Connection pool к базе данных

        Returns:
            Список словарей с результатами запроса

        Raises:
            Exception: При ошибке выполнения SQL
        """
        logger.info(f"Executing SQL: {sql[:200]}")

        try:
            async with db_pool.acquire() as conn:
                # Выполняем запрос
                rows = await conn.fetch(sql)

                # Преобразуем результаты в список словарей
                results = [dict(row) for row in rows]

                logger.info(f"SQL execution returned {len(results)} rows")
                return results

        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            raise

    async def interpret_results(
        self, question: str, sql: str, results: list[dict[str, Any]]
    ) -> str:
        """Интерпретирует результаты SQL запроса через LLM.

        Args:
            question: Исходный вопрос пользователя
            sql: Выполненный SQL запрос
            results: Результаты выполнения SQL

        Returns:
            Человекочитаемая интерпретация результатов

        Raises:
            Exception: При ошибке интерпретации
        """
        logger.info(f"Interpreting results for question: {question[:100]}")

        try:
            # Форматируем результаты для LLM (ограничиваем объем)
            results_str = json.dumps(results[:50], ensure_ascii=False, indent=2, default=str)
            if len(results) > 50:
                results_str += f"\n\n... и еще {len(results) - 50} строк"

            # Формируем промпт
            prompt = INTERPRET_RESULTS_PROMPT.format(
                question=question, sql=sql, results=results_str
            )

            # Создаем сообщение для LLM
            messages = [
                Message(
                    user_id=0,
                    chat_id=0,
                    role="user",
                    content=prompt,
                    content_length=len(prompt),
                    username="system",
                )
            ]

            # Получаем интерпретацию от LLM
            interpretation = await self.llm_client.get_response(
                messages=messages,
                system_prompt="Ты аналитик данных. Интерпретируй результаты запросов понятно.",
            )

            logger.info(f"Generated interpretation: {interpretation[:100]}")
            return interpretation

        except Exception as e:
            logger.error(f"Error interpreting results: {e}")
            raise

