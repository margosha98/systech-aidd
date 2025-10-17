"""Тесты для Mock API статистики."""

import pytest
from fastapi.testclient import TestClient

from backend.api.collectors import MockStatCollector
from backend.api.models import PeriodEnum
from backend.api.server import app


@pytest.fixture
def client() -> TestClient:
    """Фикстура для тестового клиента FastAPI.

    Returns:
        TestClient для выполнения запросов к API
    """
    return TestClient(app)


class TestMockStatCollector:
    """Тесты для MockStatCollector."""

    @pytest.mark.asyncio
    async def test_generate_stats_7d(self) -> None:
        """Тест генерации статистики за 7 дней."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)

        assert stats.period == PeriodEnum.SEVEN_DAYS
        assert len(stats.timeline) == 7
        assert stats.metrics.total_messages.value > 0
        assert stats.metrics.active_users.value > 0
        assert stats.metrics.total_dialogs.value > 0
        assert stats.metrics.growth_rate.value > 0

    @pytest.mark.asyncio
    async def test_generate_stats_30d(self) -> None:
        """Тест генерации статистики за 30 дней."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats(PeriodEnum.THIRTY_DAYS)

        assert stats.period == PeriodEnum.THIRTY_DAYS
        assert len(stats.timeline) == 30

    @pytest.mark.asyncio
    async def test_generate_stats_3m(self) -> None:
        """Тест генерации статистики за 3 месяца."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats(PeriodEnum.THREE_MONTHS)

        assert stats.period == PeriodEnum.THREE_MONTHS
        assert len(stats.timeline) == 90

    @pytest.mark.asyncio
    async def test_repeatability(self) -> None:
        """Тест повторяемости генерации (одинаковый seed = одинаковые данные)."""
        collector1 = MockStatCollector(seed=42)
        collector2 = MockStatCollector(seed=42)

        stats1 = await collector1.get_stats(PeriodEnum.SEVEN_DAYS)
        stats2 = await collector2.get_stats(PeriodEnum.SEVEN_DAYS)

        assert stats1.metrics.total_messages.value == stats2.metrics.total_messages.value
        assert stats1.timeline[0].total_messages == stats2.timeline[0].total_messages
        assert stats1.timeline[0].active_users == stats2.timeline[0].active_users

    @pytest.mark.asyncio
    async def test_timeline_dates_format(self) -> None:
        """Тест формата дат в timeline."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)

        for point in stats.timeline:
            # Проверяем формат даты YYYY-MM-DD
            assert len(point.date) == 10
            assert point.date[4] == "-"
            assert point.date[7] == "-"

    @pytest.mark.asyncio
    async def test_timeline_values_positive(self) -> None:
        """Тест что все значения timeline положительные."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats(PeriodEnum.SEVEN_DAYS)

        for point in stats.timeline:
            assert point.total_messages >= 0
            assert point.active_users >= 0


class TestAPIEndpoints:
    """Тесты для API эндпоинтов."""

    def test_health_check(self, client: TestClient) -> None:
        """Тест health check эндпоинта."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_get_stats_default_period(self, client: TestClient) -> None:
        """Тест получения статистики с дефолтным периодом."""
        response = client.get("/api/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["period"] == "7d"
        assert "metrics" in data
        assert "timeline" in data

    def test_get_stats_7d(self, client: TestClient) -> None:
        """Тест получения статистики за 7 дней."""
        response = client.get("/api/stats?period=7d")
        assert response.status_code == 200

        data = response.json()
        assert data["period"] == "7d"
        assert len(data["timeline"]) == 7

    def test_get_stats_30d(self, client: TestClient) -> None:
        """Тест получения статистики за 30 дней."""
        response = client.get("/api/stats?period=30d")
        assert response.status_code == 200

        data = response.json()
        assert data["period"] == "30d"
        assert len(data["timeline"]) == 30

    def test_get_stats_3m(self, client: TestClient) -> None:
        """Тест получения статистики за 3 месяца."""
        response = client.get("/api/stats?period=3m")
        assert response.status_code == 200

        data = response.json()
        assert data["period"] == "3m"
        assert len(data["timeline"]) == 90

    def test_get_stats_invalid_period(self, client: TestClient) -> None:
        """Тест валидации некорректного периода."""
        response = client.get("/api/stats?period=invalid")
        assert response.status_code == 422  # Validation error

    def test_get_stats_response_schema(self, client: TestClient) -> None:
        """Тест схемы ответа API."""
        response = client.get("/api/stats?period=7d")
        assert response.status_code == 200

        data = response.json()

        # Проверяем верхний уровень
        assert "period" in data
        assert "metrics" in data
        assert "timeline" in data

        # Проверяем metrics
        metrics = data["metrics"]
        assert "total_messages" in metrics
        assert "active_users" in metrics
        assert "total_dialogs" in metrics
        assert "growth_rate" in metrics

        # Проверяем структуру одной метрики
        total_messages = metrics["total_messages"]
        assert "value" in total_messages
        assert "change" in total_messages
        assert "trend" in total_messages
        assert "description" in total_messages

        # Проверяем timeline
        assert isinstance(data["timeline"], list)
        assert len(data["timeline"]) > 0
        first_point = data["timeline"][0]
        assert "date" in first_point
        assert "total_messages" in first_point
        assert "active_users" in first_point

    def test_cors_middleware_configured(self, client: TestClient) -> None:
        """Тест что CORS middleware настроен в приложении."""
        # Проверяем OPTIONS запрос (preflight)
        response = client.options(
            "/api/stats",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        # CORS middleware должен обработать OPTIONS запрос
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_openapi_docs_available(self, client: TestClient) -> None:
        """Тест доступности OpenAPI документации."""
        response = client.get("/docs")
        assert response.status_code == 200

        response = client.get("/openapi.json")
        assert response.status_code == 200
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec

