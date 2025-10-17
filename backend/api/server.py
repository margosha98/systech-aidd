"""FastAPI приложение для API статистики."""

from typing import Annotated

import asyncpg  # type: ignore[import-untyped]
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.collectors import RealStatCollector
from backend.api.config import APIConfig
from backend.api.models import PeriodEnum, StatsResponse

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
    
    Создает connection pool для PostgreSQL.
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
