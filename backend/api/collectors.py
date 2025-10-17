"""Реализации сборщиков статистики."""

import random
from datetime import UTC, datetime, timedelta
from typing import Any

import asyncpg  # type: ignore[import-untyped]

from backend.api.models import (
    MetricCard,
    MetricsData,
    PeriodEnum,
    StatsResponse,
    TimelinePoint,
    TrendEnum,
)


class MockStatCollector:
    """Mock реализация сборщика статистики.

    Генерирует случайные, но правдоподобные данные для разработки frontend.
    Использует стабильный seed для повторяемости результатов.
    """

    def __init__(self, seed: int = 42):
        """Инициализация MockStatCollector.

        Args:
            seed: Seed для генератора случайных чисел (для повторяемости)
        """
        self._seed = seed

    async def get_stats(self, period: PeriodEnum) -> StatsResponse:
        """Получить mock статистику за указанный период.

        Args:
            period: Период для сбора статистики (7d, 30d, 3m)

        Returns:
            StatsResponse с сгенерированными данными
        """
        # Устанавливаем seed для повторяемости
        random.seed(self._seed)

        # Определяем количество точек на графике в зависимости от периода
        timeline_points_count = self._get_timeline_points_count(period)

        # Генерируем метрики
        metrics = self._generate_metrics()

        # Генерируем timeline
        timeline = self._generate_timeline(timeline_points_count)

        return StatsResponse(period=period, metrics=metrics, timeline=timeline)

    def _get_timeline_points_count(self, period: PeriodEnum) -> int:
        """Определить количество точек на графике.

        Args:
            period: Период статистики

        Returns:
            Количество точек данных
        """
        if period == PeriodEnum.SEVEN_DAYS:
            return 7
        if period == PeriodEnum.THIRTY_DAYS:
            return 30
        # THREE_MONTHS
        return 90

    def _generate_metrics(self) -> MetricsData:
        """Сгенерировать mock метрики.

        Returns:
            MetricsData с четырьмя метриками
        """
        return MetricsData(
            total_messages=MetricCard(
                value=random.randint(30000, 60000),
                change=round(random.uniform(-5.0, 25.0), 1),
                trend=random.choice([TrendEnum.UP, TrendEnum.STEADY]),
                description="Trending up this month",
            ),
            active_users=MetricCard(
                value=random.randint(800, 2000),
                change=round(random.uniform(-20.0, 10.0), 1),
                trend=random.choice([TrendEnum.DOWN, TrendEnum.STEADY, TrendEnum.UP]),
                description="Acquisition needs attention"
                if random.random() < 0.3
                else "Down this period",
            ),
            total_dialogs=MetricCard(
                value=random.randint(5000, 15000),
                change=round(random.uniform(5.0, 20.0), 1),
                trend=random.choice([TrendEnum.UP, TrendEnum.STEADY]),
                description="Strong user retention",
            ),
            growth_rate=MetricCard(
                value=round(random.uniform(2.0, 8.0), 1),
                change=round(random.uniform(-2.0, 5.0), 1),
                trend=TrendEnum.STEADY,
                description="Steady performance increase",
            ),
        )

    def _generate_timeline(self, points_count: int) -> list[TimelinePoint]:
        """Сгенерировать mock данные для timeline.

        Args:
            points_count: Количество точек данных

        Returns:
            Список TimelinePoint с датами и значениями для метрик
        """
        timeline = []
        base_messages = random.randint(1000, 2000)
        base_users = random.randint(100, 300)
        current_date = datetime.now(UTC) - timedelta(days=points_count - 1)

        for _ in range(points_count):
            # Генерируем значения с небольшой волатильностью
            messages_variation = random.randint(-300, 500)
            users_variation = random.randint(-50, 80)
            
            total_messages = max(200, base_messages + messages_variation)
            active_users = max(50, base_users + users_variation)

            timeline.append(
                TimelinePoint(
                    date=current_date.strftime("%Y-%m-%d"),
                    total_messages=total_messages,
                    active_users=active_users,
                )
            )

            # Плавное изменение base значений для следующей точки
            base_messages = int(base_messages * random.uniform(0.95, 1.15))
            base_users = int(base_users * random.uniform(0.93, 1.12))
            current_date += timedelta(days=1)

        return timeline


class RealStatCollector:
    """Реальная реализация сборщика статистики.
    
    Получает данные из PostgreSQL базы данных (таблица messages).
    """

    def __init__(self, db_pool: asyncpg.Pool):
        """Инициализация RealStatCollector.
        
        Args:
            db_pool: Connection pool для работы с PostgreSQL
        """
        self._pool = db_pool

    async def get_stats(self, period: PeriodEnum) -> StatsResponse:
        """Получить статистику за указанный период из БД.
        
        Args:
            period: Период для сбора статистики (7d, 30d, 3m)
            
        Returns:
            StatsResponse с реальными данными из БД
        """
        # Определяем временные границы
        current_end = datetime.now(UTC)
        current_start = self._get_period_start(current_end, period)
        previous_start = self._get_period_start(current_start, period)
        
        # Получаем метрики для текущего периода
        current_metrics = await self._fetch_metrics(current_start, current_end)
        
        # Получаем метрики для предыдущего периода (для расчета change)
        previous_metrics = await self._fetch_metrics(previous_start, current_start)
        
        # Получаем timeline данные
        timeline = await self._fetch_timeline(current_start, current_end)
        
        # Формируем MetricsData с расчетом change и trend
        metrics = self._build_metrics_data(current_metrics, previous_metrics)
        
        return StatsResponse(period=period, metrics=metrics, timeline=timeline)

    def _get_period_start(self, end_date: datetime, period: PeriodEnum) -> datetime:
        """Определить начало периода.
        
        Args:
            end_date: Конечная дата
            period: Период статистики
            
        Returns:
            Дата начала периода
        """
        if period == PeriodEnum.SEVEN_DAYS:
            return end_date - timedelta(days=7)
        if period == PeriodEnum.THIRTY_DAYS:
            return end_date - timedelta(days=30)
        # THREE_MONTHS
        return end_date - timedelta(days=90)

    async def _fetch_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Получить метрики из БД за указанный период.
        
        Args:
            start_date: Начало периода
            end_date: Конец периода
            
        Returns:
            Словарь с метриками: total_messages, active_users, total_dialogs
        """
        # Конвертируем в naive datetime для PostgreSQL TIMESTAMP (без timezone)
        start_naive = start_date.replace(tzinfo=None)
        end_naive = end_date.replace(tzinfo=None)
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(DISTINCT (chat_id, user_id)) as total_dialogs
                FROM messages
                WHERE created_at >= $1 AND created_at < $2
                """,
                start_naive,
                end_naive,
            )
            
            return {
                "total_messages": int(row["total_messages"]) if row else 0,
                "active_users": int(row["active_users"]) if row else 0,
                "total_dialogs": int(row["total_dialogs"]) if row else 0,
            }

    async def _fetch_timeline(
        self, start_date: datetime, end_date: datetime
    ) -> list[TimelinePoint]:
        """Получить timeline данные из БД.
        
        Args:
            start_date: Начало периода
            end_date: Конец периода
            
        Returns:
            Список TimelinePoint с данными по дням
        """
        # Конвертируем в naive datetime для PostgreSQL TIMESTAMP (без timezone)
        start_naive = start_date.replace(tzinfo=None)
        end_naive = end_date.replace(tzinfo=None)
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT user_id) as active_users
                FROM messages
                WHERE created_at >= $1 AND created_at < $2
                GROUP BY DATE(created_at)
                ORDER BY date
                """,
                start_naive,
                end_naive,
            )
            
            timeline = [
                TimelinePoint(
                    date=row["date"].strftime("%Y-%m-%d"),
                    total_messages=int(row["total_messages"]),
                    active_users=int(row["active_users"]),
                )
                for row in rows
            ]
            
            # Если данных нет, возвращаем хотя бы одну точку с нулями
            if not timeline:
                timeline = [
                    TimelinePoint(
                        date=start_date.strftime("%Y-%m-%d"),
                        total_messages=0,
                        active_users=0,
                    )
                ]
            
            return timeline

    def _build_metrics_data(
        self, current: dict[str, Any], previous: dict[str, Any]
    ) -> MetricsData:
        """Сформировать MetricsData с расчетом change и trend.
        
        Args:
            current: Метрики текущего периода
            previous: Метрики предыдущего периода
            
        Returns:
            MetricsData с заполненными карточками метрик
        """
        # Расчет growth_rate (темп роста сообщений)
        growth_rate_value = self._calculate_growth_rate(
            current["total_messages"], previous["total_messages"]
        )
        
        return MetricsData(
            total_messages=MetricCard(
                value=float(current["total_messages"]),
                change=self._calculate_change(
                    current["total_messages"], previous["total_messages"]
                ),
                trend=self._calculate_trend(
                    current["total_messages"], previous["total_messages"]
                ),
                description=self._generate_description(
                    "messages", current["total_messages"], previous["total_messages"]
                ),
            ),
            active_users=MetricCard(
                value=float(current["active_users"]),
                change=self._calculate_change(
                    current["active_users"], previous["active_users"]
                ),
                trend=self._calculate_trend(
                    current["active_users"], previous["active_users"]
                ),
                description=self._generate_description(
                    "users", current["active_users"], previous["active_users"]
                ),
            ),
            total_dialogs=MetricCard(
                value=float(current["total_dialogs"]),
                change=self._calculate_change(
                    current["total_dialogs"], previous["total_dialogs"]
                ),
                trend=self._calculate_trend(
                    current["total_dialogs"], previous["total_dialogs"]
                ),
                description=self._generate_description(
                    "dialogs", current["total_dialogs"], previous["total_dialogs"]
                ),
            ),
            growth_rate=MetricCard(
                value=growth_rate_value,
                change=self._calculate_change(
                    current["total_messages"], previous["total_messages"]
                ),
                trend=TrendEnum.STEADY,
                description="Growth rate based on message volume",
            ),
        )

    def _calculate_change(self, current: int, previous: int) -> float:
        """Рассчитать изменение в процентах.
        
        Args:
            current: Текущее значение
            previous: Предыдущее значение
            
        Returns:
            Изменение в процентах (округлено до 1 знака)
        """
        if previous == 0:
            return 0.0 if current == 0 else 100.0
        
        change = ((current - previous) / previous) * 100
        return round(change, 1)

    def _calculate_trend(self, current: int, previous: int) -> TrendEnum:
        """Определить тренд на основе изменения.
        
        Args:
            current: Текущее значение
            previous: Предыдущее значение
            
        Returns:
            Направление тренда (up, down, steady)
        """
        change = self._calculate_change(current, previous)
        
        if change > 5.0:
            return TrendEnum.UP
        if change < -5.0:
            return TrendEnum.DOWN
        return TrendEnum.STEADY

    def _calculate_growth_rate(self, current: int, previous: int) -> float:
        """Рассчитать темп роста.
        
        Args:
            current: Текущее количество сообщений
            previous: Предыдущее количество сообщений
            
        Returns:
            Темп роста в процентах (округлено до 1 знака)
        """
        if previous == 0:
            return 0.0 if current == 0 else 100.0
        
        growth = ((current - previous) / previous) * 100
        return round(abs(growth), 1)

    def _generate_description(
        self, metric_type: str, current: int, previous: int
    ) -> str:
        """Сгенерировать описание для метрики.
        
        Args:
            metric_type: Тип метрики ('messages', 'users', 'dialogs')
            current: Текущее значение
            previous: Предыдущее значение
            
        Returns:
            Текстовое описание
        """
        trend = self._calculate_trend(current, previous)
        change = self._calculate_change(current, previous)
        
        if trend == TrendEnum.UP:
            return f"Trending up by {abs(change):.1f}%"
        if trend == TrendEnum.DOWN:
            return f"Down by {abs(change):.1f}%"
        return "Stable performance"
