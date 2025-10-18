"""FastAPI приложение для API статистики."""

import logging
from datetime import datetime
from typing import Annotated

import asyncpg  # type: ignore[import-untyped]
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat_service import ChatService
from backend.api.collectors import RealStatCollector
from backend.api.config import APIConfig
from backend.api.models import ChatMessage, ChatRequest, ChatResponse, PeriodEnum, StatsResponse
from src.config import Config
from src.llm.client import LLMClient
from src.storage.models import Message

logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Systech AIDD Bot Statistics API",
    description="API для получения статистики telegram-бота 'Знайкин'",
    version="1.0.0",
)

# Настройка CORS для frontend разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем конфигурацию
config = APIConfig()


@app.on_event("startup")
async def startup() -> None:
    """Инициализация при старте приложения.
    
    Создает connection pool для PostgreSQL и инициализирует LLM клиент.
    """
    app.state.db_pool = await asyncpg.create_pool(
        host=config.postgres_host,
        port=config.postgres_port,
        database=config.postgres_db,
        user=config.postgres_user,
        password=config.postgres_password,
        min_size=2,
        max_size=10,
    )
    print(f"[OK] Database connection pool created: {config.postgres_host}:{config.postgres_port}/{config.postgres_db}")
    
    # Инициализируем LLM клиент для чата
    bot_config = Config()
    app.state.llm_client = LLMClient(bot_config)
    print("[OK] LLM client initialized for chat service")


@app.on_event("shutdown")
async def shutdown() -> None:
    """Очистка при остановке приложения.
    
    Закрывает connection pool.
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        print("[OK] Database connection pool closed")


@app.get(
    "/api/stats",
    response_model=StatsResponse,
    summary="Получить статистику дашборда",
    description="Возвращает метрики и timeline данные для дашборда статистики бота",
)
async def get_stats(
    period: Annotated[
        PeriodEnum,
        Query(description="Период для сбора статистики: 7d (7 дней), 30d (30 дней), 3m (3 месяца)"),
    ] = PeriodEnum.SEVEN_DAYS,
) -> StatsResponse:
    """Получить статистику за указанный период.

    Args:
        period: Период статистики (7d, 30d, 3m)

    Returns:
        StatsResponse с метриками и timeline
    """
    stat_collector = RealStatCollector(app.state.db_pool)
    return await stat_collector.get_stats(period)


@app.get("/health", summary="Health check", description="Проверка работоспособности API")
async def health_check() -> dict[str, str]:
    """Health check эндпоинт.

    Returns:
        Словарь со статусом
    """
    return {"status": "ok"}


def _session_to_chat_id(session_id: str) -> int:
    """Конвертирует session_id в chat_id для БД.
    
    Используем хеш от session_id как chat_id для веб-чата.
    Добавляем большое отрицательное число чтобы отличать от telegram chat_id.
    
    Args:
        session_id: ID сессии веб-чата
        
    Returns:
        chat_id для использования в БД
    """
    # Используем hash для генерации числового chat_id
    # Делаем отрицательным и большим чтобы отличать от telegram
    return -(abs(hash(session_id)) % 1_000_000_000 + 1_000_000_000)


@app.post(
    "/api/chat/message",
    response_model=ChatResponse,
    summary="Отправить сообщение в чат",
    description="Отправляет сообщение в чат и получает ответ от AI-ассистента",
)
async def chat_message(request: ChatRequest) -> ChatResponse:
    """Обработка сообщения чата.

    Args:
        request: Запрос с сообщением, режимом и session_id

    Returns:
        Ответ от чата
    """
    logger.info(f"Chat message received: mode={request.mode}, session={request.session_id}")

    try:
        # Конвертируем session_id в chat_id
        chat_id = _session_to_chat_id(request.session_id)
        user_id = 0  # Для веб-чата используем фиксированный user_id

        # Загружаем историю диалога из БД (последние 20 сообщений)
        async with app.state.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, chat_id, role, content, content_length, username,
                       created_at, is_deleted
                FROM messages
                WHERE chat_id = $1 AND user_id = $2 AND is_deleted = FALSE
                ORDER BY created_at DESC, id DESC
                LIMIT 20
                """,
                chat_id,
                user_id,
            )

            # Преобразуем в список Message (от старых к новым)
            history = [
                Message(
                    id=row["id"],
                    user_id=row["user_id"],
                    chat_id=row["chat_id"],
                    role=row["role"],
                    content=row["content"],
                    content_length=row["content_length"],
                    username=row["username"],
                    created_at=row["created_at"],
                    is_deleted=row["is_deleted"],
                )
                for row in reversed(rows)
            ]

        # Создаем ChatService и обрабатываем сообщение
        chat_service = ChatService(app.state.llm_client, app.state.db_pool)
        response = await chat_service.process_message(request, history)

        # Сохраняем сообщение пользователя и ответ ассистента в БД
        async with app.state.db_pool.acquire() as conn:
            # Сохраняем сообщение пользователя
            await conn.execute(
                """
                INSERT INTO messages (user_id, chat_id, role, content, content_length, username)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                user_id,
                chat_id,
                "user",
                request.message,
                len(request.message),
                "web_user",
            )

            # Сохраняем ответ ассистента
            await conn.execute(
                """
                INSERT INTO messages (user_id, chat_id, role, content, content_length, username)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                user_id,
                chat_id,
                "assistant",
                response.message,
                len(response.message),
                "assistant",
            )

        logger.info(f"Chat response sent: mode={response.mode}")
        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise


@app.get(
    "/api/chat/history/{session_id}",
    response_model=list[ChatMessage],
    summary="Получить историю чата",
    description="Возвращает последние сообщения из истории чата",
)
async def get_chat_history(
    session_id: str,
    limit: Annotated[int, Query(description="Максимальное количество сообщений", ge=1, le=100)] = 50,
) -> list[ChatMessage]:
    """Получение истории чата.

    Args:
        session_id: ID сессии
        limit: Максимальное количество сообщений

    Returns:
        Список сообщений
    """
    logger.info(f"Fetching chat history: session={session_id}, limit={limit}")

    try:
        # Конвертируем session_id в chat_id
        chat_id = _session_to_chat_id(session_id)
        user_id = 0

        async with app.state.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE chat_id = $1 AND user_id = $2 AND is_deleted = FALSE
                ORDER BY created_at DESC, id DESC
                LIMIT $3
                """,
                chat_id,
                user_id,
                limit,
            )

            # Преобразуем в список ChatMessage (от старых к новым)
            messages = [
                ChatMessage(
                    role=row["role"],
                    content=row["content"],
                    timestamp=row["created_at"],
                )
                for row in reversed(rows)
            ]

            logger.info(f"Retrieved {len(messages)} messages from chat history")
            return messages

    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise
