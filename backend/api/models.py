"""Pydantic модели для API статистики."""

from enum import Enum

from pydantic import BaseModel, Field


class PeriodEnum(str, Enum):
    """Перечисление доступных периодов для статистики."""

    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    THREE_MONTHS = "3m"


class TrendEnum(str, Enum):
    """Перечисление возможных трендов для метрик."""

    UP = "up"
    DOWN = "down"
    STEADY = "steady"


class MetricCard(BaseModel):
    """Модель карточки метрики для дашборда.

    Attributes:
        value: Значение метрики (число или процент)
        change: Изменение относительно предыдущего периода в процентах
        trend: Направление тренда ('up', 'down', 'steady')
        description: Текстовое описание для отображения пользователю
    """

    value: float = Field(..., description="Значение метрики")
    change: float = Field(..., description="Изменение в процентах")
    trend: TrendEnum = Field(..., description="Направление тренда")
    description: str = Field(..., description="Описание метрики")


class TimelinePoint(BaseModel):
    """Точка данных для графика временной шкалы.

    Attributes:
        date: Дата в формате YYYY-MM-DD
        value: Значение метрики на эту дату
    """

    date: str = Field(..., description="Дата в формате YYYY-MM-DD")
    value: int = Field(..., description="Значение метрики", ge=0)


class MetricsData(BaseModel):
    """Набор всех метрик для дашборда.

    Attributes:
        total_messages: Общее количество сообщений
        active_users: Количество активных пользователей
        total_dialogs: Общее количество диалогов
        growth_rate: Темп роста сообщений в процентах
    """

    total_messages: MetricCard = Field(..., description="Общее количество сообщений")
    active_users: MetricCard = Field(..., description="Активные пользователи")
    total_dialogs: MetricCard = Field(..., description="Всего диалогов")
    growth_rate: MetricCard = Field(..., description="Темп роста")


class StatsResponse(BaseModel):
    """Ответ API с полной статистикой для дашборда.

    Attributes:
        period: Период, за который собрана статистика
        metrics: Набор метрик (карточки дашборда)
        timeline: Данные для графика изменения во времени
    """

    period: PeriodEnum = Field(..., description="Период статистики")
    metrics: MetricsData = Field(..., description="Метрики дашборда")
    timeline: list[TimelinePoint] = Field(
        ..., description="Данные для графика временной шкалы", min_length=1
    )
