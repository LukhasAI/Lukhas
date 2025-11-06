import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# The TestClient needs to be initialized before we try to import the app,
# but the app itself has dependencies that might not be installed in the test environment.
# We can mock these dependencies before importing the app.
with patch("serve.main.obs_stack") as mock_obs_stack:
    mock_obs_stack.opentelemetry_enabled = False
    from serve.main import app

client = TestClient(app)

class SimulatedServiceError(Exception):
    """A custom exception to simulate a downstream service failure."""
    pass

@patch('serve.main._RUN_ASYNC_ORCH')
@patch('serve.main.get_auth_system')
@patch('serve.main.ASYNC_ORCH_ENABLED', True)
def test_downstream_service_failure_returns_500(
    mock_get_auth_system, mock_run_async_orch
):
    """
    Given a simulated failure in the downstream orchestration service,
    When the API receives a request that triggers that service,
    Then the API should return a 500 Internal Server Error.
    """
    # 1. Bypass authentication by mocking the auth system
    mock_auth_system = MagicMock()
    mock_auth_system.verify_jwt.return_value = {"sub": "test-user"}
    mock_get_auth_system.return_value = mock_auth_system

    # 2. Simulate a critical failure in the orchestrator service
    mock_run_async_orch.side_effect = SimulatedServiceError("Orchestrator is unavailable")

    # 3. Make a request to the endpoint that uses the orchestrator
    response = client.post(
        "/v1/responses",
        headers={"Authorization": "Bearer valid-token-for-test"},
        json={"input": "What is the meaning of life?"}
    )

    # 4. Assert that the API correctly returns a 500 error
    assert response.status_code == 500
