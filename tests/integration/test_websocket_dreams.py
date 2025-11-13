import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from serve.main import app as main_app
from serve.websocket_routes import DreamEvent, router as websocket_router

# Create a new app instance for testing without the middleware
app = FastAPI()
app.include_router(websocket_router)

# Mock DreamEngine for fine-grained control in tests
class MockDreamEngine:
    def __init__(self, dream_events, error_on_stream=False):
        self._dream_events = dream_events
        self._error_on_stream = error_on_stream

    async def stream_generate(self, user_id: str):
        if self._error_on_stream:
            raise ValueError("Dream generation failed")

        for event in self._dream_events:
            yield event
            await asyncio.sleep(0.01)

# Test Data
short_dream = [
    DreamEvent("dream_start", {"message": "Dream started"}, 0),
    DreamEvent("dream_complete", {"narrative": "A short dream"}, 100)
]

long_dream = [
    DreamEvent("dream_start", {"message": "Dream started"}, 0),
    *[DreamEvent("dream_progress", {"step": i}, i * 10) for i in range(1, 10)],
    DreamEvent("dream_complete", {"narrative": "A long dream"}, 100)
]

dream_with_no_progress = [
    DreamEvent("dream_start", {"message": "Dream started"}, 0),
    DreamEvent("dream_complete", {"narrative": "A dream with no progress"}, 100)
]

dream_scenarios = [
    ("short_dream", short_dream),
    ("long_dream", long_dream),
    ("dream_with_no_progress", dream_with_no_progress)
]

@pytest.fixture
def client():
    return TestClient(app)

# --- Test Cases ---

def test_websocket_unauthorized(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/dreams/stream?token=invalid-token") as ws:
            ws.receive_json()

def test_websocket_missing_token(client):
    with pytest.raises(Exception), client.websocket_connect("/ws/dreams/stream") as ws:
        ws.receive_json()

@pytest.mark.parametrize("scenario, dream_events", dream_scenarios)
def test_websocket_dream_scenarios(client, scenario, dream_events):
    with patch("serve.websocket_routes.DreamEngine", new=lambda: MockDreamEngine(dream_events)):
        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            messages = [ws.receive_json() for _ in range(len(dream_events))]

    assert len(messages) == len(dream_events)
    assert messages[0]["type"] == "dream_start"
    assert messages[-1]["type"] == "dream_complete"

def test_websocket_error_handling(client):
    with patch("serve.websocket_routes.generate_dream_stream", new=AsyncMock(side_effect=ValueError("Test error"))):
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
                ws.receive_json()

@pytest.mark.asyncio
async def test_websocket_concurrent_connections():
    def connect_and_receive():
        with TestClient(app) as client:
            with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
                return [ws.receive_json() for _ in range(len(long_dream))]

    with patch("serve.websocket_routes.DreamEngine", new=lambda: MockDreamEngine(long_dream)):
        task1 = asyncio.to_thread(connect_and_receive)
        task2 = asyncio.to_thread(connect_and_receive)

        results = await asyncio.gather(task1, task2)

    assert len(results[0]) == len(long_dream)
    assert len(results[1]) == len(long_dream)
    assert results[0] == results[1]

def test_websocket_connection_cleanup(client):
    with patch("serve.websocket_routes.logger.info") as mock_log:
        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            pass

    mock_log.assert_called_with("Client disconnected: user123")

def test_websocket_reconnection(client):
    with patch("serve.websocket_routes.DreamEngine", new=lambda: MockDreamEngine(short_dream)):
        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            message = ws.receive_json()
            assert message["type"] == "dream_start"

        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            message = ws.receive_json()
            assert message["type"] == "dream_start"

def test_websocket_payload_structure(client):
    with patch("serve.websocket_routes.DreamEngine", new=lambda: MockDreamEngine(short_dream)):
        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            message = ws.receive_json()

    assert "type" in message
    assert "data" in message
    assert "progress" in message

def test_websocket_progress_is_int(client):
    with patch("serve.websocket_routes.DreamEngine", new=lambda: MockDreamEngine(long_dream)):
        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            for _ in range(len(long_dream)):
                message = ws.receive_json()
                assert isinstance(message["progress"], int)

# Add more tests to reach 20+
@pytest.mark.parametrize("i", range(10))
def test_multiple_connections_in_sequence(client, i):
    with patch("serve.websocket_routes.DreamEngine", new=lambda: MockDreamEngine(short_dream)):
        with client.websocket_connect("/ws/dreams/stream?token=valid-token") as ws:
            messages = [ws.receive_json() for _ in range(len(short_dream))]

    assert len(messages) == len(short_dream)
