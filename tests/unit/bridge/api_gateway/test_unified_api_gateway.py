# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.api_gateway.unified_api_gateway
# criticality: P2

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from bridge.api_gateway.unified_api_gateway import UnifiedAPIGateway


@pytest.mark.tier3
@pytest.mark.api
@pytest.mark.unit
class TestUnifiedAPIGatewayUnit:
    """
    Unit tests for the UnifiedAPIGateway.
    """

    @pytest.fixture
    def gateway(self) -> UnifiedAPIGateway:
        """Returns a UnifiedAPIGateway instance with mocked dependencies."""
        # Mock config to avoid dependency on actual config files
        config = {
            "auth": {},
            "rate_limit": {},
            "handlers": {}
        }
        gw = UnifiedAPIGateway(config=config)
        # Mock dependencies that are initialized in the constructor
        gw.auth_middleware = MagicMock()
        gw.auth_middleware.authenticate = AsyncMock(return_value={"user_id": "test_user"})
        gw.rate_limiter = MagicMock()
        gw.rate_limiter.check_rate_limit = AsyncMock()
        return gw

    @pytest.fixture
    def client(self, gateway: UnifiedAPIGateway) -> TestClient:
        """Returns a TestClient for the gateway."""
        return TestClient(gateway.get_app())

    def test_health_check(self, client: TestClient, gateway: UnifiedAPIGateway):
        """Tests the health check endpoint."""
        # We need to mock what health_check calls
        gateway.app.state.orchestrator = MagicMock()
        gateway.app.state.orchestrator.health_check = AsyncMock(return_value={"status": "ok"})
        gateway.app.state.orchestrator.performance_monitor = MagicMock()
        gateway.app.state.orchestrator.performance_monitor.get_metrics = AsyncMock(return_value={})

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] is not None

    def test_performance_middleware(self, client: TestClient, gateway: UnifiedAPIGateway):
        """Tests that the performance monitoring middleware adds the X-Response-Time header."""
        gateway.app.state.orchestrator = MagicMock()
        gateway.app.state.orchestrator.get_status = AsyncMock(return_value={})
        response = client.get("/status") # use a different endpoint to be safe
        assert "x-response-time" in response.headers
        assert "x-gateway-version" in response.headers

    @pytest.mark.asyncio
    async def test_chat_endpoint_success(self, gateway: UnifiedAPIGateway, client: TestClient):
        """Tests the /chat endpoint on success."""
        # Mock orchestrator on the app state
        mock_orchestrator = MagicMock()
        mock_orchestrator.orchestrate = AsyncMock(return_value=MagicMock(
            final_response="Test response",
            confidence_score=0.9,
            individual_responses=[],
            consensus_method="unanimous",
            participating_models=[],
            processing_time_ms=50,
            quality_metrics={},
        ))
        gateway.app.state.orchestrator = mock_orchestrator

        response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Test response"
        assert data["confidence"] == 0.9

        gateway.auth_middleware.authenticate.assert_called_once()
        gateway.rate_limiter.check_rate_limit.assert_called_once()
        mock_orchestrator.orchestrate.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_endpoint_auth_fails(self, gateway: UnifiedAPIGateway, client: TestClient):
        """Tests that the /chat endpoint fails on authentication error."""
        from fastapi import HTTPException
        gateway.auth_middleware.authenticate.side_effect = HTTPException(status_code=401, detail="Unauthorized")

        response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    @pytest.mark.asyncio
    async def test_orchestrate_endpoint_success(self, gateway: UnifiedAPIGateway, client: TestClient):
        """Tests the /orchestrate endpoint on success."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.orchestrate = AsyncMock(return_value=MagicMock(
            final_response="Test response",
            confidence_score=0.9,
            individual_responses=[],
            consensus_method="unanimous",
            participating_models=[],
            processing_time_ms=50,
            quality_metrics={},
        ))
        mock_orchestrator.performance_monitor = MagicMock()
        mock_orchestrator.performance_monitor.get_metrics = AsyncMock(return_value={"some_metric": 1})
        gateway.app.state.orchestrator = mock_orchestrator

        response = client.post("/orchestrate", json={"message": "Hello"})

        assert response.status_code == 200
        data = response.json()
        assert data["result"]["response"] == "Test response"
        assert data["performance_metrics"] == {"some_metric": 1}

        gateway.auth_middleware.authenticate.assert_called_once()
        gateway.rate_limiter.check_rate_limit.assert_called_once()
        mock_orchestrator.orchestrate.assert_called_once()
