"""FastAPI приложение для API статистики."""

from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.collectors import MockStatCollector
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

# Создаем единственный экземпляр MockStatCollector
stat_collector = MockStatCollector(seed=42)


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
    return await stat_collector.get_stats(period)


@app.get("/health", summary="Health check", description="Проверка работоспособности API")
async def health_check() -> dict[str, str]:
    """Health check эндпоинт.

    Returns:
        Словарь со статусом
    """
    return {"status": "ok"}
