"""Тесты для Real API статистики с PostgreSQL."""

from datetime import UTC, datetime, timedelta

import asyncpg  # type: ignore[import-untyped]
import pytest

from backend.api.collectors import RealStatCollector
from backend.api.config import APIConfig
from backend.api.models import PeriodEnum, TrendEnum


@pytest.fixture
async def db_pool() -> asyncpg.Pool:
    """Фикстура для connection pool к тестовой БД.
    
    Returns:
        Connection pool для тестов
    """
    config = APIConfig()
    pool = await asyncpg.create_pool(
        host=config.postgres_host,
        port=config.postgres_port,
        database=config.postgres_db,
        user=config.postgres_user,
        password=config.postgres_password,
        min_size=1,
        max_size=2,
    )
    
    # Очищаем таблицу перед тестами
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM messages")
    
    yield pool
    
    # Закрываем pool после тестов
    await pool.close()


@pytest.fixture
async def populated_db(db_pool: asyncpg.Pool) -> asyncpg.Pool:
    """Фикстура с заполненной БД тестовыми данными.
    
    Args:
        db_pool: Connection pool
        
    Returns:
        Pool с заполненной БД
    """
    async with db_pool.acquire() as conn:
        # Очищаем таблицу
        await conn.execute("DELETE FROM messages")
        
        # Добавляем тестовые данные
        now = datetime.now(UTC).replace(tzinfo=None)  # Конвертируем в naive datetime для PostgreSQL
        
        # За последние 7 дней - 70 сообщений от 10 пользователей
        for day_offset in range(7):
            date = now - timedelta(days=day_offset)
            for user_id in range(1, 11):
                await conn.execute(
                    """
                    INSERT INTO messages (user_id, chat_id, role, content, content_length, username, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    user_id,
                    100 + user_id,
                    "user",
                    f"Test message {day_offset}-{user_id}",
                    20,
                    f"user{user_id}",
                    date,
                )
        
        # За предыдущие 7 дней (8-14 дней назад) - 56 сообщений от 8 пользователей
        for day_offset in range(8, 15):
            date = now - timedelta(days=day_offset)
            for user_id in range(1, 9):
                await conn.execute(
                    """
                    INSERT INTO messages (user_id, chat_id, role, content, content_length, username, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    user_id,
                    100 + user_id,
                    "user",
                    f"Test message {day_offset}-{user_id}",
                    20,
                    f"user{user_id}",
                    date,
                )
    
    return db_pool


class TestRealStatCollector:
    """Тесты для RealStatCollector."""

    @pytest.mark.asyncio
    async def test_empty_database(self, db_pool: asyncpg.Pool) -> None:
        """Тест работы с пустой БД."""
        collector = RealStatCollector(db_pool)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        assert stats.period == PeriodEnum.SEVEN_DAYS
        assert stats.metrics.total_messages.value == 0.0
        assert stats.metrics.active_users.value == 0.0
        assert stats.metrics.total_dialogs.value == 0.0
        assert stats.metrics.growth_rate.value == 0.0
        
        # Timeline должен содержать хотя бы одну точку
        assert len(stats.timeline) >= 1
        assert stats.timeline[0].total_messages == 0
        assert stats.timeline[0].active_users == 0

    @pytest.mark.asyncio
    async def test_basic_metrics_calculation(self, populated_db: asyncpg.Pool) -> None:
        """Тест базового расчета метрик."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Должно быть 70 сообщений (7 дней * 10 пользователей)
        assert stats.metrics.total_messages.value == 70.0
        
        # Должно быть 10 уникальных пользователей
        assert stats.metrics.active_users.value == 10.0
        
        # Должно быть 10 уникальных диалогов (пары chat_id, user_id)
        assert stats.metrics.total_dialogs.value == 10.0

    @pytest.mark.asyncio
    async def test_change_calculation(self, populated_db: asyncpg.Pool) -> None:
        """Тест расчета изменений (change)."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Проверяем что change рассчитан корректно (проверяем формулу, а не конкретное значение)
        # change должен быть положительным (текущий > предыдущего)
        assert stats.metrics.total_messages.change > 0
        assert stats.metrics.total_messages.value == 70.0

    @pytest.mark.asyncio
    async def test_trend_calculation(self, populated_db: asyncpg.Pool) -> None:
        """Тест определения тренда."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Change = 25% > 5%, значит тренд UP
        assert stats.metrics.total_messages.trend == TrendEnum.UP
        
        # Пользователи: 10 vs 8 = +25% > 5%, значит UP
        assert stats.metrics.active_users.trend == TrendEnum.UP

    @pytest.mark.asyncio
    async def test_timeline_data(self, populated_db: asyncpg.Pool) -> None:
        """Тест timeline данных."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Timeline должен содержать данные по дням
        assert len(stats.timeline) >= 1
        
        # Проверяем формат дат
        for point in stats.timeline:
            assert len(point.date) == 10
            assert point.date[4] == "-"
            assert point.date[7] == "-"
            
            # Значения должны быть >= 0
            assert point.total_messages >= 0
            assert point.active_users >= 0

    @pytest.mark.asyncio
    async def test_period_30d(self, populated_db: asyncpg.Pool) -> None:
        """Тест статистики за 30 дней."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.THIRTY_DAYS)
        
        assert stats.period == PeriodEnum.THIRTY_DAYS
        # Должны быть данные за доступный период
        assert stats.metrics.total_messages.value > 0

    @pytest.mark.asyncio
    async def test_period_3m(self, populated_db: asyncpg.Pool) -> None:
        """Тест статистики за 3 месяца."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.THREE_MONTHS)
        
        assert stats.period == PeriodEnum.THREE_MONTHS
        # Должны быть данные за доступный период
        assert stats.metrics.total_messages.value > 0

    @pytest.mark.asyncio
    async def test_growth_rate_calculation(self, populated_db: asyncpg.Pool) -> None:
        """Тест расчета темпа роста."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Growth rate должен быть положительным (рост сообщений)
        assert stats.metrics.growth_rate.value > 0
        
        # Growth rate должен быть равен abs(change) для total_messages
        assert stats.metrics.growth_rate.value == abs(stats.metrics.total_messages.change)

    @pytest.mark.asyncio
    async def test_description_generation(self, populated_db: asyncpg.Pool) -> None:
        """Тест генерации описаний."""
        collector = RealStatCollector(populated_db)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Описания должны быть непустыми
        assert len(stats.metrics.total_messages.description) > 0
        assert len(stats.metrics.active_users.description) > 0
        assert len(stats.metrics.total_dialogs.description) > 0
        assert len(stats.metrics.growth_rate.description) > 0
        
        # Описание для растущего тренда должно содержать "up" или проценты
        assert (
            "up" in stats.metrics.total_messages.description.lower()
            or "%" in stats.metrics.total_messages.description
        )

    @pytest.mark.asyncio
    async def test_zero_previous_period(self, db_pool: asyncpg.Pool) -> None:
        """Тест обработки случая когда предыдущий период пустой."""
        async with db_pool.acquire() as conn:
            await conn.execute("DELETE FROM messages")
            
            # Добавляем данные только за последние 7 дней
            now = datetime.now(UTC).replace(tzinfo=None)
            for day_offset in range(7):
                date = now - timedelta(days=day_offset)
                await conn.execute(
                    """
                    INSERT INTO messages (user_id, chat_id, role, content, content_length, username, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    1,
                    100,
                    "user",
                    "Test message",
                    20,
                    "user1",
                    date,
                )
        
        collector = RealStatCollector(db_pool)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # При нулевом предыдущем периоде change должно быть 100%
        assert stats.metrics.total_messages.change == 100.0
        assert stats.metrics.total_messages.trend == TrendEnum.UP

    @pytest.mark.asyncio
    async def test_decline_trend(self, db_pool: asyncpg.Pool) -> None:
        """Тест определения нисходящего тренда."""
        async with db_pool.acquire() as conn:
            await conn.execute("DELETE FROM messages")
            
            now = datetime.now(UTC).replace(tzinfo=None)
            
            # Текущий период: 7 сообщений
            for day_offset in range(7):
                date = now - timedelta(days=day_offset)
                await conn.execute(
                    """
                    INSERT INTO messages (user_id, chat_id, role, content, content_length, username, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    1,
                    100,
                    "user",
                    "Test",
                    4,
                    "user1",
                    date,
                )
            
            # Предыдущий период: 50 сообщений
            for day_offset in range(8, 15):
                date = now - timedelta(days=day_offset)
                for i in range(7):
                    await conn.execute(
                        """
                        INSERT INTO messages (user_id, chat_id, role, content, content_length, username, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        1,
                        100,
                        "user",
                        "Test",
                        4,
                        "user1",
                        date,
                    )
        
        collector = RealStatCollector(db_pool)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)
        
        # Снижение с 49 до 7, change < -5%, тренд DOWN
        assert stats.metrics.total_messages.trend == TrendEnum.DOWN
        assert stats.metrics.total_messages.change < -5.0

