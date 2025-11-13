import os
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set env var for testing
os.environ['LUKHAS_LANE'] = 'test-lane'

# Mock the orchestrator before it's imported by the server
mock_orchestrator = MagicMock()

class MockCognitiveNode:
    def __init__(self, tenant, **kwargs):
        self.tenant = tenant
        self.node_name = f"mock_{tenant}"
        self.capabilities = ["mock"]
        self.processing_history = []
    def get_trace(self): return []

patch.dict('sys.modules', {
    'MATRIZ.core.orchestrator': MagicMock(CognitiveOrchestrator=lambda: mock_orchestrator),
    'MATRIZ.nodes.fact_node': MagicMock(FactNode=MockCognitiveNode),
    'MATRIZ.nodes.math_node': MagicMock(MathNode=MockCognitiveNode),
    'MATRIZ.nodes.validator_node': MagicMock(ValidatorNode=MockCognitiveNode),
}).start()

# Now import the app and its module
import matriz.interfaces.api_server as api_server
from matriz.interfaces.api_server import app, run_server, websocket_connections


@pytest.fixture
def client(mocker):
    # ... (fixture code is the same)
    mocker.patch('matriz.interfaces.api_server.initialize_orchestrator', return_value=None)
    mocker.patch('matriz.interfaces.api_server.cleanup_orchestrator', return_value=None)
    api_server.orchestrator = mock_orchestrator
    with TestClient(app) as test_client:
        yield test_client
    api_server.orchestrator = None
    websocket_connections.clear()

@pytest.fixture(autouse=True)
def reset_state():
    # ... (fixture code is the same)
    mock_orchestrator.reset_mock()
    mock_orchestrator.process_query.side_effect = None
    api_server.total_queries = 0
    mock_orchestrator.available_nodes = {'math': MagicMock(), 'facts': MagicMock(), 'validator': MagicMock()}
    mock_orchestrator.execution_trace = []
    mock_orchestrator.matriz_graph = {}
    mock_orchestrator.context_memory = {}

# ... (all previous tests are the same) ...
def test_health_check_success(client):
    mock_orchestrator.available_nodes = {'math': MagicMock(), 'facts': MagicMock()}
    response = client.get("/health")
    assert response.status_code == 200

def test_readiness_check_success(client):
    mock_orchestrator.available_nodes = {'math': MagicMock()}
    response = client.get("/health/ready")
    assert response.status_code == 200

def test_readiness_check_fails_when_critical(client):
    mock_orchestrator.available_nodes = {}
    response = client.get("/health/ready")
    assert response.status_code == 503

def test_liveness_check(client):
    response = client.get("/health/live")
    assert response.status_code == 200

def test_system_info(client):
    node1 = MagicMock(); node1.capabilities = ["math"]; node1.tenant = "test"; node1.processing_history = [1,2,3]
    mock_orchestrator.available_nodes = {"node1": node1}
    response = client.get("/system/info")
    assert response.status_code == 200

def test_list_nodes(client):
    node1 = MagicMock(); node1.node_name = "math_node"
    mock_orchestrator.available_nodes = {"math": node1}
    response = client.get("/system/nodes")
    assert response.status_code == 200

def test_get_node_details_success(client):
    node1 = MagicMock(); node1.node_name = "math_node"; node1.get_trace.return_value = ["t1"]
    mock_orchestrator.available_nodes = {"math": node1}
    response = client.get("/system/nodes/math")
    assert response.status_code == 200

def test_get_node_details_not_found(client):
    mock_orchestrator.available_nodes = {}
    response = client.get("/system/nodes/nonexistent")
    assert response.status_code == 404

def test_process_query_success(client):
    mock_orchestrator.process_query.return_value = {"answer": "42"}
    response = client.post("/query", json={"query": "test"})
    assert response.status_code == 200

def test_process_query_no_trace_or_nodes(client):
    mock_orchestrator.process_query.return_value = {"answer": "simple"}
    response = client.post("/query", json={"query": "test", "include_trace": False, "include_nodes": False})
    assert response.status_code == 200
    assert response.json().get("trace") is None

@pytest.mark.parametrize("query", [" ", "   "])
def test_process_query_validation_empty_string(client, query):
    response = client.post("/query", json={"query": query})
    assert response.status_code == 422

def test_process_query_validation_short_trace_id(client):
    response = client.post("/query", json={"query": "test", "trace_id": "123"})
    assert response.status_code == 422

def test_process_query_orchestrator_exception(client):
    mock_orchestrator.process_query.side_effect = Exception("Test Error")
    response = client.post("/query", json={"query": "test"})
    assert response.status_code == 500

def test_websocket_connection(client):
    with client.websocket_connect("/ws") as ws:
        data = ws.receive_json()
        assert data["type"] == "connected"

def test_websocket_ping_pong(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"type": "ping", "data": {}, "timestamp": "now"})
        assert ws.receive_json()["type"] == "pong"

def test_websocket_query_processing(client):
    mock_orchestrator.process_query.return_value = {"answer": "ws_answer"}
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"type": "query", "data": {"query": "ws_query"}, "timestamp": "now"})
        assert ws.receive_json()["type"] == "response"

def test_websocket_invalid_message(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"data": {}})
        assert ws.receive_json()["type"] == "error"

def test_websocket_system_info(client):
    mock_node = MagicMock(); mock_node.capabilities = ["cap"]; mock_node.processing_history = [1,2]
    mock_orchestrator.available_nodes = {"test_node": mock_node}
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json({"type": "system_info", "timestamp": "now"})
        assert ws.receive_json()["type"] == "system_info"

def test_run_server_cli(mocker):
    """Test the CLI entry point for running the server."""
    # Mock the functions that are called by the CLI
    mock_argparse = mocker.patch('argparse.ArgumentParser')
    mock_uvicorn = mocker.patch('uvicorn.run')

    # Set up the mock to return specific values
    mock_args = MagicMock()
    mock_args.host = '127.0.0.1'
    mock_args.port = 8080
    mock_args.reload = True
    mock_args.log_level = 'debug'
    mock_argparse.return_value.parse_args.return_value = mock_args

    # Use runpy to execute the __main__ block
    import runpy
    runpy.run_path('matriz/interfaces/api_server.py', run_name='__main__')

    # Assert that uvicorn.run was called with the correct arguments
    mock_uvicorn.assert_called_once_with(
        "matriz.interfaces.api_server:app",
        host='127.0.0.1',
        port=8080,
        reload=True,
        log_level='debug',
        access_log=True,
    )
