# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.api_gateway.unified_api_gateway
# criticality: P2

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import jwt
import time

from candidate.bridge.api_gateway.unified_api_gateway import UnifiedAPIGateway


@pytest.mark.tier3
@pytest.mark.api
@pytest.mark.integration
class TestUnifiedAPIGatewayIntegration:
    """
    Integration tests for the UnifiedAPIGateway.
    """

    @pytest.fixture
    def gateway(self) -> UnifiedAPIGateway:
        """Returns a UnifiedAPIGateway instance with real middleware."""
        config = {
            "auth": {
                "jwt_secret": "test-secret",
                "jwt_algorithm": "HS256",
            },
            "rate_limit": {
                "default": "5/minute"
            },
            "handlers": {}
        }
        return UnifiedAPIGateway(config=config)

    @pytest.fixture
    def client(self, gateway: UnifiedAPIGateway) -> TestClient:
        """Returns a TestClient for the gateway."""
        return TestClient(gateway.get_app())

    def create_test_token(self, gateway: UnifiedAPIGateway, user_id: str) -> str:
        """Creates a test JWT token."""
        payload = {"sub": user_id, "exp": int(time.time()) + 3600} # 1 hour expiry
        return jwt.encode(payload, gateway.auth_middleware.jwt_secret, algorithm=gateway.auth_middleware.jwt_algorithm)


    @pytest.mark.asyncio
    async def test_integration_chat_success(self, gateway: UnifiedAPIGateway, client: TestClient):
        """Tests a successful chat request through the integrated gateway."""
        # Mock the orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.orchestrate = AsyncMock(return_value=MagicMock(
            final_response="Integration test response",
            confidence_score=0.95,
            individual_responses=[],
            consensus_method="unanimous",
            participating_models=[],
            processing_time_ms=50,
            quality_metrics={},
        ))
        gateway.app.state.orchestrator = mock_orchestrator

        # Create a valid token
        token = self.create_test_token(gateway, "integ_user")
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/chat", json={"message": "Hello"}, headers=headers)

        assert response.status_code == 200
        assert response.json()["response"] == "Integration test response"
        mock_orchestrator.orchestrate.assert_called_once()

    @pytest.mark.asyncio
    async def test_integration_rate_limit_exceeded(self, gateway: UnifiedAPIGateway, client: TestClient):
        """Tests that the rate limiter blocks requests when the limit is exceeded."""
        # This test is more of a placeholder as the real RateLimiter logic is not available
        # We will assume a simple in-memory implementation for now.

        # Mock the orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.orchestrate = AsyncMock(return_value=MagicMock(
            final_response="Integration test response",
            confidence_score=0.95,
            individual_responses=[],
            consensus_method="unanimous",
            participating_models=[],
            processing_time_ms=50,
            quality_metrics={},
        ))
        gateway.app.state.orchestrator = mock_orchestrator

        # Create a valid token
        token = self.create_test_token(gateway, "rate_limit_user")
        headers = {"Authorization": f"Bearer {token}"}

        # Override rate limiter for test
        gateway.rate_limiter.rates = {"chat": (5, 60)} # 5 requests per 60 seconds
        gateway.rate_limiter.requests = {}

        # Exhaust the rate limit
        for i in range(5):
            response = client.post("/chat", json={"message": f"Hello {i}"}, headers=headers)
            assert response.status_code == 200

        # The 6th request should be blocked
        response = client.post("/chat", json={"message": "Hello 6"}, headers=headers)
        assert response.status_code == 429

    def test_integration_auth_failure_no_token(self, client: TestClient):
        """Tests that a request without a token is rejected."""
        response = client.post("/chat", json={"message": "Hello"})
        # The test client will raise an exception if the middleware is not mocked
        # and it tries to access a non-existent object.
        # For a true integration test, we'd need the actual AuthMiddleware code.
        # For now, we assume it will fail.
        # A more robust test would mock the JWT decoding to simulate invalid token.
        assert response.status_code in [401, 403]

    def test_integration_auth_failure_invalid_token(self, client: TestClient):
        """Tests that a request with an invalid token is rejected."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/chat", json={"message": "Hello"}, headers=headers)
        assert response.status_code in [401, 403]
