import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock

# Mock dependencies before importing the app
with patch("serve.main.obs_stack") as mock_obs_stack:
    mock_obs_stack.opentelemetry_enabled = False
    from serve.main import app

@pytest.mark.asyncio
async def test_concurrent_load():
    """
    Given the API is running,
    When a high volume of concurrent requests are sent to an endpoint,
    Then the API should handle all requests successfully without crashing or deadlocking.
    """
    num_requests = 50

    # We patch the auth system to bypass authentication for this test
    # and enable the async orchestrator feature flag.
    with patch('serve.main.get_auth_system') as mock_get_auth_system, \
         patch('serve.main._RUN_ASYNC_ORCH', new_callable=AsyncMock) as mock_run_async_orch, \
         patch('serve.main.ASYNC_ORCH_ENABLED', True):

        mock_auth_system = MagicMock()
        mock_auth_system.verify_jwt.return_value = {"sub": "test-user"}
        mock_get_auth_system.return_value = mock_auth_system

        # Mock the orchestrator to return a simple successful response
        mock_run_async_orch.return_value = {"answer": "concurrent test response"}

        # Use ASGITransport to test the app directly
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            tasks = []
            for i in range(num_requests):
                task = client.post(
                    "/v1/responses",
                    headers={"Authorization": "Bearer valid-token-for-test"},
                    json={"input": f"test {i}"}
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            for response in responses:
                assert response.status_code == 200
                assert "concurrent test response" in response.json()["choices"][0]["message"]["content"]
