"""Pydantic модели для API статистики."""

from datetime import datetime
from enum import Enum
from typing import Literal

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
        total_messages: Количество сообщений на эту дату
        active_users: Количество активных пользователей на эту дату
    """

    date: str = Field(..., description="Дата в формате YYYY-MM-DD")
    total_messages: int = Field(..., description="Количество сообщений", ge=0)
    active_users: int = Field(..., description="Количество активных пользователей", ge=0)


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


class ChatMode(str, Enum):
    """Режимы работы чата.

    Attributes:
        NORMAL: Обычный режим общения с LLM
        ADMIN: Режим администратора для вопросов по статистике
    """

    NORMAL = "normal"
    ADMIN = "admin"


class ChatRequest(BaseModel):
    """Запрос для отправки сообщения в чат.

    Attributes:
        message: Текст сообщения пользователя
        mode: Режим работы чата (normal/admin)
        session_id: Идентификатор сессии для отслеживания истории
    """

    message: str = Field(..., description="Текст сообщения", min_length=1)
    mode: ChatMode = Field(ChatMode.NORMAL, description="Режим работы чата")
    session_id: str = Field(..., description="Идентификатор сессии")


class ChatMessage(BaseModel):
    """Сообщение в чате.

    Attributes:
        role: Роль отправителя (user/assistant)
        content: Содержимое сообщения
        timestamp: Временная метка создания сообщения
    """

    role: Literal["user", "assistant"] = Field(..., description="Роль отправителя")
    content: str = Field(..., description="Содержимое сообщения")
    timestamp: datetime = Field(..., description="Временная метка")


class ChatResponse(BaseModel):
    """Ответ от чата.

    Attributes:
        message: Текст ответа от ассистента
        sql_query: SQL запрос для admin режима (для отладки)
        mode: Режим, в котором был обработан запрос
    """

    message: str = Field(..., description="Текст ответа")
    sql_query: str | None = Field(None, description="SQL запрос (только для admin режима)")
    mode: ChatMode = Field(..., description="Режим обработки")
