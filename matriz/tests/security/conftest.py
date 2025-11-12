
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from matriz.interfaces.api_server import app, get_orchestrator

@pytest.fixture(scope="module")
def mock_orchestrator():
    """Create a mock CognitiveOrchestrator."""
    mock = MagicMock()
    mock.available_nodes = {"mock_node": MagicMock()}
    mock.process_query.return_value = {"answer": "mocked_answer"}
    return mock

@pytest.fixture(scope="module")
def test_client(mock_orchestrator):
    """Create a TestClient with a mocked orchestrator."""
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
