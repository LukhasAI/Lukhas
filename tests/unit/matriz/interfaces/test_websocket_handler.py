
import asyncio
import json
import threading
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from matriz.interfaces.api_server import app, orchestrator, websocket_connections
from starlette.websockets import WebSocketDisconnect


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_websocket_connection_and_cleanup(client):
    assert len(websocket_connections) == 0
    with client.websocket_connect("/ws") as ws:
        assert len(websocket_connections) == 1
        data = ws.receive_json()
        assert data["type"] == "connected"
        assert "client_id" in data["data"]
        assert "message" in data["data"]
        assert "available_nodes" in data["data"]
        assert isinstance(data["data"]["available_nodes"], list)
    assert len(websocket_connections) == 0


def test_websocket_ping_pong(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "type": "ping",
                "data": {"key": "value"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        data = ws.receive_json()
        assert data["type"] == "pong"
        assert data["data"]["key"] == "value"


def test_websocket_query_processing(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "type": "query",
                "data": {"query": "what is 2+2"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        data = ws.receive_json()
        assert data["type"] == "response"
        assert "answer" in data["data"]
        assert data["data"]["answer"] == "4"


def test_websocket_system_info(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(
            {"type": "system_info", "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        data = ws.receive_json()
        assert data["type"] == "system_info"
        assert "nodes" in data["data"]
        assert "matriz_graph_size" in data["data"]


def test_websocket_unknown_message_type(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(
            {"type": "unknown", "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "Unknown message type" in data["data"]["error"]


@pytest.mark.asyncio
async def test_broadcast_to_websockets():
    # This test needs to be async
    from matriz.interfaces.api_server import broadcast_to_websockets

    ws1 = AsyncMock()
    ws2 = AsyncMock()
    websocket_connections.extend([ws1, ws2])

    message = {"type": "test", "data": "test"}
    await broadcast_to_websockets(message)

    ws1.send_json.assert_called_once_with(message)
    ws2.send_json.assert_called_once_with(message)

    websocket_connections.clear()


@pytest.mark.asyncio
async def test_broadcast_with_disconnected_client():
    from matriz.interfaces.api_server import broadcast_to_websockets

    ws1 = AsyncMock()
    ws2 = AsyncMock()
    ws1.send_json.side_effect = Exception("disconnected")
    websocket_connections.extend([ws1, ws2])

    message = {"type": "test", "data": "test"}
    await broadcast_to_websockets(message)

    ws2.send_json.assert_called_once_with(message)
    assert len(websocket_connections) == 1
    assert websocket_connections[0] is ws2

    websocket_connections.clear()

def test_websocket_forceful_disconnect():
    # This test is a bit more manual to control the websocket lifecycle
    client = TestClient(app)
    assert len(websocket_connections) == 0
    with client.websocket_connect("/ws"):
        assert len(websocket_connections) == 1
        # Simulate a forceful disconnect by not calling ws.close()
    # After the with block, the disconnect should have been handled
    assert len(websocket_connections) == 0


@patch("matriz.interfaces.api_server.WebSocket.receive_json")
def test_websocket_disconnect_on_receive_error(mock_receive_json, client):
    mock_receive_json.side_effect = WebSocketDisconnect()
    assert len(websocket_connections) == 0
    with client.websocket_connect("/ws"):
        assert len(websocket_connections) == 1
    assert len(websocket_connections) == 0


def test_websocket_empty_query(client):
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "type": "query",
                "data": {"query": ""},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "No query provided" in data["data"]["error"]


@patch("matriz.interfaces.api_server.CognitiveOrchestrator.process_query")
def test_websocket_query_processing_error(mock_process_query, client):
    mock_process_query.side_effect = Exception("Orchestrator error")
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "type": "query",
                "data": {"query": "test"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "Orchestrator error" in data["data"]["error"]


def test_concurrent_websocket_connections_threaded():
    client = TestClient(app)
    num_threads = 2
    threads = []
    errors = []

    def worker():
        try:
            with client.websocket_connect("/ws") as ws:
                ws.receive_json()  # Consume connected message
                ws.send_json(
                    {
                        "type": "ping",
                        "data": {},
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
                response = ws.receive_json()
                assert response["type"] == "pong"
        except Exception as e:
            errors.append(e)

    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join(timeout=10)

    assert not any(t.is_alive() for t in threads), "Some threads timed out"
    assert not errors, f"Concurrent websocket connections failed with errors: {errors}"


def test_websocket_invalid_message(client):
    with client.websocket_connect("/ws") as ws:
        # Consume the initial "connected" message
        ws.receive_json()
        ws.send_text("not a json")
        data = ws.receive_json()
        assert data["type"] == "error"
        assert "Expecting value" in data["data"]["error"]
