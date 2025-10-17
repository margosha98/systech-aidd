"""Протоколы для сборщиков статистики."""

from typing import Protocol

from backend.api.models import PeriodEnum, StatsResponse


class StatCollectorProtocol(Protocol):
    """Протокол для сборщиков статистики.

    Определяет интерфейс для получения статистики.
    Реализации: MockStatCollector (mock данные), RealStatCollector (из БД).
    """

    async def get_stats(self, period: PeriodEnum) -> StatsResponse:
        """Получить статистику за указанный период.

        Args:
            period: Период для сбора статистики (7d, 30d, 3m)

        Returns:
            StatsResponse с метриками и данными timeline
        """
        ...
