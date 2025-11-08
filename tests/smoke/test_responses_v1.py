"""
Smoke test: /v1/responses endpoint for streaming and non-streaming responses.

Validates:
- Streaming and non-streaming responses
- SSE protocol compliance
- Authentication
- Error handling
"""
import pytest
from fastapi.testclient import TestClient
from serve.main import app

AUTH_HEADERS = {"Authorization": "Bearer sk-lukhas-test-1234567890abcdef"}

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

def test_non_streaming_response_happy_path(client: TestClient):
    """Verify basic non-streaming response generation works."""
    payload = {"model": "lukhas-response", "input": "hello world", "stream": False}
    response = client.post("/v1/responses", headers=AUTH_HEADERS, json=payload)

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")

    data = response.json()
    assert "id" in data
    assert "model" in data
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "message" in data["choices"][0]
    assert "content" in data["choices"][0]["message"]
    assert "hello world" in data["choices"][0]["message"]["content"]

def test_streaming_response_happy_path(client: TestClient):
    """Verify basic streaming response generation works."""
    payload = {"model": "lukhas-response", "input": "hello world", "stream": True}

    with client.stream("POST", "/v1/responses", headers=AUTH_HEADERS, json=payload) as r:
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("text/event-stream")

        done_received = False
        full_content = []
        for line in r.iter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    done_received = True
                    break

                import json
                chunk = json.loads(data)
                full_content.append(chunk["choices"][0]["delta"].get("content", ""))

        assert done_received, "Stream did not complete with [DONE] marker"
        assert "hello" in "".join(full_content)
        assert "world" in "".join(full_content)

def test_authentication_required(client: TestClient):
    """Verify that the endpoint requires authentication."""
    response = client.post("/v1/responses", json={"input": "test"})
    assert response.status_code == 401

def test_missing_input_field(client: TestClient):
    """Verify that a 400 error is returned when the input field is missing."""
    response = client.post("/v1/responses", headers=AUTH_HEADERS, json={})
    assert response.status_code == 400

def test_empty_input_field(client: TestClient):
    """Verify that a 400 error is returned when the input field is empty."""
    response = client.post("/v1/responses", headers=AUTH_HEADERS, json={"input": ""})
    assert response.status_code == 400
