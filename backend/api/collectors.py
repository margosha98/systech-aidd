"""Реализации сборщиков статистики."""

import random
from datetime import UTC, datetime, timedelta

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
