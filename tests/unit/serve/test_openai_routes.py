"""
Comprehensive tests for serve/openai_routes.py

Following LUKHAS Test Surgeon guidelines:
- Deterministic (time frozen, seeds fixed, no network)
- OpenAI-compatible endpoint contracts validated
- Auth dependency mocking (require_api_key)
- Both legacy and v1 endpoints covered
- Streaming and non-streaming responses tested
- Error conditions and edge cases handled

Target: 75%+ coverage
"""
import asyncio
import json
import time
from unittest import mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.fixture
def test_env(monkeypatch):
    """Set up clean test environment variables"""
    monkeypatch.setenv("LUKHAS_API_KEY", "test-api-key-123")
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")


@pytest.fixture
def mock_token_claims():
    """Mock TokenClaims for auth dependency"""
    claims = mock.MagicMock()
    claims.sub = "test-user-123"
    claims.scopes = ["api.read"]
    claims.project_id = "test-project"
    return claims


@pytest.fixture
def client(test_env, mock_token_claims):
    """FastAPI TestClient with mocked dependencies"""
    # Mock external dependencies
    mock_openai_service = mock.MagicMock()
    mock_openai_service.generate = mock.AsyncMock(
        return_value={"response": "mocked modulated response", "usage": {"tokens": 10}}
    )
    mock_openai_service.generate_stream = mock.AsyncMock(
        return_value=["chunk1", "chunk2", "chunk3"]
    )
    mock_openai_service.metrics = {"requests": 100, "errors": 5}

    with mock.patch.dict("sys.modules", {
        "docker": mock.MagicMock(),
        "labs": mock.MagicMock(),
        "labs.tools": mock.MagicMock(),
        "labs.tools.tool_executor": mock.MagicMock(),
        "tools.tool_executor": mock.MagicMock(),
        "bridge.llm_wrappers.tool_executor": mock.MagicMock(),
        "bridge.llm_wrappers.openai_modulated_service": mock.MagicMock(),
    }):
        # Mock OpenAIModulatedService constructor
        with mock.patch("serve.openai_routes.OpenAIModulatedService", return_value=mock_openai_service):
            # Mock auth dependency
            with mock.patch("serve.openai_routes.require_bearer", return_value=mock_token_claims):
                # Re-import to apply mocks
                import importlib
                import serve.openai_routes as routes_module
                importlib.reload(routes_module)

                from fastapi import FastAPI
                app = FastAPI()
                app.include_router(routes_module.router)

                yield TestClient(app)


# ========================================================================
# Helper Function Tests
# ========================================================================

@pytest.fixture
def openai_routes_module():
    """Import serve.openai_routes with mocked dependencies"""
    with mock.patch.dict("sys.modules", {
        "docker": mock.MagicMock(),
        "labs": mock.MagicMock(),
        "labs.tools": mock.MagicMock(),
        "labs.tools.tool_executor": mock.MagicMock(),
        "tools.tool_executor": mock.MagicMock(),
        "bridge.llm_wrappers.tool_executor": mock.MagicMock(),
        "bridge.llm_wrappers.openai_modulated_service": mock.MagicMock(),
    }):
        import importlib
        import serve.openai_routes as routes_module
        importlib.reload(routes_module)
        yield routes_module


def test_hash_to_vec_deterministic(openai_routes_module):
    """Test that _hash_to_vec produces deterministic embeddings"""
    text = "test input"
    vec1 = openai_routes_module._hash_to_vec(text, dim=128)
    vec2 = openai_routes_module._hash_to_vec(text, dim=128)

    assert vec1 == vec2, "Vectors must be deterministic"
    assert len(vec1) == 128, "Vector dimension must match requested dim"
    assert all(0 <= v <= 1 for v in vec1), "Vector values must be normalized [0,1]"


def test_hash_to_vec_unique(openai_routes_module):
    """Test that different inputs produce different vectors"""
    vec1 = openai_routes_module._hash_to_vec("input one", dim=128)
    vec2 = openai_routes_module._hash_to_vec("input two", dim=128)

    assert vec1 != vec2, "Different inputs must produce different vectors"


def test_hash_to_vec_dimension_scaling(openai_routes_module):
    """Test that _hash_to_vec handles different dimensions correctly"""
    vec_128 = openai_routes_module._hash_to_vec("test", dim=128)
    vec_256 = openai_routes_module._hash_to_vec("test", dim=256)
    vec_1536 = openai_routes_module._hash_to_vec("test", dim=1536)

    assert len(vec_128) == 128
    assert len(vec_256) == 256
    assert len(vec_1536) == 1536


def test_rl_headers(openai_routes_module):
    """Test rate limit headers generation"""
    with mock.patch("time.time", return_value=1705320000):  # Fixed timestamp
        headers = openai_routes_module._rl_headers()

        assert headers["X-RateLimit-Limit"] == "60"
        assert headers["X-RateLimit-Remaining"] == "59"
        assert "X-RateLimit-Reset" in headers
        assert headers["x-ratelimit-limit-requests"] == "60"
        assert headers["x-ratelimit-remaining-requests"] == "59"
        assert "x-ratelimit-reset-requests" in headers

        # Verify reset timestamp is in the future
        now = 1705320000
        assert int(headers["X-RateLimit-Reset"]) == now + 60
        assert int(headers["x-ratelimit-reset-requests"]) == now + 60


def test_with_std_headers_with_trace_id(openai_routes_module):
    """Test applying standard headers with explicit trace ID"""
    response = mock.MagicMock()
    response.headers = {}

    openai_routes_module._with_std_headers(response, trace_id="trace-123")

    assert response.headers["X-Request-Id"] == "trace-123"
    assert response.headers["X-Trace-Id"] == "trace-123"
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers


def test_with_std_headers_without_trace_id(openai_routes_module):
    """Test applying standard headers generates trace ID when missing"""
    response = mock.MagicMock()
    response.headers = {}

    openai_routes_module._with_std_headers(response, trace_id=None)

    assert "X-Request-Id" in response.headers
    assert "X-Trace-Id" in response.headers
    assert response.headers["X-Request-Id"] == response.headers["X-Trace-Id"]
    assert len(response.headers["X-Request-Id"]) == 32  # UUID hex length


def test_invalid_request_basic(openai_routes_module):
    """Test _invalid_request error payload structure"""
    payload = openai_routes_module._invalid_request("Missing required field")

    assert "error" in payload
    assert payload["error"]["type"] == "invalid_request_error"
    assert payload["error"]["message"] == "Missing required field"
    assert payload["error"]["code"] == "invalid_request_error"
    assert "param" not in payload["error"]


def test_invalid_request_with_param(openai_routes_module):
    """Test _invalid_request includes param when provided"""
    payload = openai_routes_module._invalid_request("Invalid value", param="model")

    assert payload["error"]["param"] == "model"


def test_resolve_stream_plan_light_request(openai_routes_module):
    """Test stream plan for light requests"""
    plan = openai_routes_module._resolve_stream_plan("short text", max_tokens=100)

    assert plan["chunk_count"] == 6
    assert plan["heavy"] is False
    assert plan["per_chunk_bytes"] >= 64


def test_resolve_stream_plan_heavy_request_by_tokens(openai_routes_module):
    """Test stream plan for heavy requests (high max_tokens)"""
    plan = openai_routes_module._resolve_stream_plan("text", max_tokens=2000)

    assert plan["chunk_count"] == 12
    assert plan["heavy"] is True


def test_resolve_stream_plan_heavy_request_by_length(openai_routes_module):
    """Test stream plan for heavy requests (long text)"""
    long_text = "x" * 500
    plan = openai_routes_module._resolve_stream_plan(long_text, max_tokens=100)

    assert plan["chunk_count"] == 12
    assert plan["heavy"] is True


def test_stream_chunks_count(openai_routes_module):
    """Test _stream_chunks generates correct number of chunks"""
    plan = {"chunk_count": 6, "per_chunk_bytes": 100}
    chunks = openai_routes_module._stream_chunks("test text", plan)

    assert len(chunks) == 6
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_stream_chunks_size_limits(openai_routes_module):
    """Test _stream_chunks respects byte limits"""
    plan = {"chunk_count": 4, "per_chunk_bytes": 80}
    chunks = openai_routes_module._stream_chunks("test", plan)

    assert all(len(chunk) <= 80 for chunk in chunks)


def test_stream_chunks_deterministic(openai_routes_module):
    """Test _stream_chunks produces deterministic output"""
    plan = {"chunk_count": 3, "per_chunk_bytes": 50}
    chunks1 = openai_routes_module._stream_chunks("test input", plan)
    chunks2 = openai_routes_module._stream_chunks("test input", plan)

    assert chunks1 == chunks2


def test_stream_chunks_empty_text(openai_routes_module):
    """Test _stream_chunks handles empty text gracefully"""
    plan = {"chunk_count": 2, "per_chunk_bytes": 64}
    chunks = openai_routes_module._stream_chunks("", plan)

    assert len(chunks) == 2
    assert all("symbolic stream" in chunk for chunk in chunks)


# ========================================================================
# Legacy Endpoint Tests (/openai)
# ========================================================================

def test_modulated_chat_success(client):
    """Test POST /openai/chat returns modulated response"""
    payload = {
        "prompt": "Hello, world",
        "context": "test context",
        "task": "conversation"
    }

    response = client.post("/openai/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "mocked modulated response"
    assert data["usage"]["tokens"] == 10


def test_modulated_chat_minimal_payload(client):
    """Test POST /openai/chat with minimal required fields"""
    payload = {"prompt": "test"}

    response = client.post("/openai/chat", json=payload)

    assert response.status_code == 200
    assert "response" in response.json()


def test_modulated_chat_stream_success(client):
    """Test POST /openai/chat/stream returns streaming response"""
    payload = {
        "prompt": "Stream test",
        "context": "streaming context",
        "task": "generation"
    }

    response = client.post("/openai/chat/stream", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    # Verify streaming content
    content = response.text
    assert "chunk1" in content or "chunk2" in content or "chunk3" in content


def test_openai_metrics_success(client):
    """Test GET /openai/metrics returns service metrics"""
    response = client.get("/openai/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["requests"] == 100
    assert data["errors"] == 5


def test_openai_metrics_empty_when_unavailable(client):
    """Test GET /openai/metrics handles missing metrics gracefully"""
    with mock.patch("serve.openai_routes.get_service") as mock_get_service:
        mock_service = mock.MagicMock()
        mock_service.metrics = None
        mock_get_service.return_value = mock_service

        response = client.get("/openai/metrics")

        assert response.status_code == 200
        assert response.json() == {}


# ========================================================================
# v1 OpenAI-Compatible Endpoint Tests
# ========================================================================

def test_list_models_success(client):
    """Test GET /v1/models returns model catalog"""
    response = client.get("/v1/models")

    assert response.status_code == 200
    data = response.json()

    assert data["object"] == "list"
    assert len(data["data"]) == 2

    # Verify lukhas-mini model
    mini = next((m for m in data["data"] if m["id"] == "lukhas-mini"), None)
    assert mini is not None
    assert mini["object"] == "model"
    assert mini["owned_by"] == "lukhas"
    assert mini["created"] == 1730000000

    # Verify lukhas-embed-1 model
    embed = next((m for m in data["data"] if m["id"] == "lukhas-embed-1"), None)
    assert embed is not None
    assert embed["object"] == "model"

    # Verify rate limit headers
    assert response.headers["X-RateLimit-Limit"] == "60"
    assert response.headers["X-RateLimit-Remaining"] == "59"
    assert "X-Request-Id" in response.headers
    assert "X-Trace-Id" in response.headers


def test_list_models_trace_id_passthrough(client):
    """Test GET /v1/models passes through trace ID headers"""
    headers = {"X-Request-Id": "custom-trace-123"}
    response = client.get("/v1/models", headers=headers)

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "custom-trace-123"
    assert response.headers["X-Trace-Id"] == "custom-trace-123"


def test_create_embeddings_single_string(client):
    """Test POST /v1/embeddings with single string input"""
    payload = {
        "model": "lukhas-embed-1",
        "input": "test embedding"
    }

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["object"] == "list"
    assert data["model"] == "lukhas-embed-1"
    assert len(data["data"]) == 1

    # Verify embedding structure
    embedding = data["data"][0]
    assert embedding["object"] == "embedding"
    assert embedding["index"] == 0
    assert len(embedding["embedding"]) == 128
    assert all(0 <= v <= 1 for v in embedding["embedding"])

    # Verify usage tokens
    assert data["usage"]["prompt_tokens"] == 2  # "test" + "embedding"
    assert data["usage"]["total_tokens"] == 2


def test_create_embeddings_list_of_strings(client):
    """Test POST /v1/embeddings with multiple inputs"""
    payload = {
        "model": "lukhas-embed-1",
        "input": ["first text", "second text", "third text"]
    }

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]) == 3
    assert data["data"][0]["index"] == 0
    assert data["data"][1]["index"] == 1
    assert data["data"][2]["index"] == 2

    # Verify embeddings are different
    emb1 = data["data"][0]["embedding"]
    emb2 = data["data"][1]["embedding"]
    assert emb1 != emb2


def test_create_embeddings_default_model(client):
    """Test POST /v1/embeddings uses default model when not specified"""
    payload = {"input": "test"}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "lukhas-embed-1"


def test_create_embeddings_invalid_input_empty(client):
    """Test POST /v1/embeddings rejects empty input"""
    payload = {"input": ""}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 400
    error = response.json()
    assert "error" in error
    assert error["error"]["param"] == "input"


def test_create_embeddings_invalid_input_empty_list(client):
    """Test POST /v1/embeddings rejects empty list"""
    payload = {"input": []}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 400


def test_create_embeddings_invalid_input_whitespace(client):
    """Test POST /v1/embeddings rejects whitespace-only input"""
    payload = {"input": ["   ", "  "]}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 400


def test_create_embeddings_token_counting(client):
    """Test POST /v1/embeddings counts tokens correctly"""
    payload = {
        "input": [
            "one two three",  # 3 tokens
            "four five"       # 2 tokens
        ]
    }

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["usage"]["prompt_tokens"] == 5
    assert data["usage"]["total_tokens"] == 5


def test_create_response_non_stream_success(client):
    """Test POST /v1/responses returns non-streaming response"""
    payload = {
        "model": "lukhas-mini",
        "input": "test prompt",
        "stream": False
    }

    with mock.patch("time.time", return_value=1705320000):
        response = client.post("/v1/responses", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "response"
        assert data["model"] == "lukhas-mini"
        assert data["id"].startswith("resp_")
        assert data["created"] == 1705320000

        # Verify output structure
        assert len(data["output"]) == 1
        output = data["output"][0]
        assert output["type"] == "output_text"
        assert output["text"] == "echo: test prompt"

        # Verify usage tokens
        assert data["usage"]["input_tokens"] == 2  # "test" + "prompt"
        assert data["usage"]["output_tokens"] == 3  # "echo:" + "test" + "prompt"
        assert data["usage"]["total_tokens"] == 5


def test_create_response_default_model(client):
    """Test POST /v1/responses uses default model"""
    payload = {"input": "test"}

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "lukhas-mini"


def test_create_response_messages_format(client):
    """Test POST /v1/responses handles messages format"""
    payload = {
        "messages": [
            {
                "content": [
                    {"type": "input_text", "text": "Hello from messages"}
                ]
            }
        ]
    }

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "echo: Hello from messages" in data["output"][0]["text"]


def test_create_response_contents_format(client):
    """Test POST /v1/responses handles contents format"""
    payload = {
        "contents": [
            {
                "content": [
                    {"type": "input_text", "text": "Hello from contents"}
                ]
            }
        ]
    }

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "echo: Hello from contents" in data["output"][0]["text"]


def test_create_response_invalid_input_missing(client):
    """Test POST /v1/responses rejects missing input"""
    payload = {"model": "lukhas-mini"}

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 400
    error = response.json()
    assert "error" in error
    assert error["error"]["param"] == "input"


def test_create_response_invalid_input_empty(client):
    """Test POST /v1/responses rejects empty input"""
    payload = {"input": ""}

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 400


def test_create_response_invalid_input_whitespace(client):
    """Test POST /v1/responses rejects whitespace-only input"""
    payload = {"input": "   "}

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 400


def test_create_response_stream_success(client):
    """Test POST /v1/responses returns streaming response"""
    payload = {
        "input": "streaming test",
        "stream": True
    }

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Verify SSE format
    content = response.text
    assert "data: " in content
    assert "data: [DONE]" in content


def test_create_response_stream_with_max_tokens(client):
    """Test POST /v1/responses streaming with max_tokens influences chunking"""
    payload = {
        "input": "test" * 100,
        "stream": True,
        "max_tokens": 2000  # Should trigger heavy request
    }

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    content = response.text

    # Count chunks (should be more for heavy request)
    chunk_count = content.count("data: chunk-")
    assert chunk_count > 0


def test_create_response_stream_light_request(client):
    """Test POST /v1/responses streaming light request"""
    payload = {
        "input": "short",
        "stream": True,
        "max_tokens": 100
    }

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    content = response.text

    # Light requests should have fewer chunks
    chunk_count = content.count("data: chunk-")
    assert chunk_count <= 6


def test_create_response_trace_id_in_stream(client):
    """Test POST /v1/responses streaming preserves trace ID"""
    headers = {"X-Trace-Id": "stream-trace-456"}
    payload = {"input": "test", "stream": True}

    response = client.post("/v1/responses", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == "stream-trace-456"
    assert response.headers.get("x-trace-id") == "stream-trace-456"


# ========================================================================
# Edge Cases and Error Handling
# ========================================================================

def test_get_service_returns_instance():
    """Test get_service returns OpenAIModulatedService instance"""
    from serve.openai_routes import get_service

    service = get_service()
    assert service is not None


def test_require_api_key_calls_require_bearer():
    """Test require_api_key delegates to require_bearer with correct params"""
    from serve.openai_routes import require_api_key

    with mock.patch("serve.openai_routes.require_bearer") as mock_bearer:
        mock_claims = mock.MagicMock()
        mock_bearer.return_value = mock_claims

        result = require_api_key(
            authorization="Bearer test-token",
            x_lukhas_project="project-123"
        )

        mock_bearer.assert_called_once_with(
            authorization="Bearer test-token",
            required_scopes=("api.read",),
            project_id="project-123"
        )
        assert result == mock_claims


def test_create_embeddings_rate_limit_headers(client):
    """Test POST /v1/embeddings includes rate limit headers"""
    payload = {"input": "test"}

    response = client.post("/v1/embeddings", json=payload)

    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert "X-Request-Id" in response.headers


def test_create_response_rate_limit_headers(client):
    """Test POST /v1/responses includes rate limit headers"""
    payload = {"input": "test"}

    response = client.post("/v1/responses", json=payload)

    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers


def test_router_exports():
    """Test serve/openai_routes exports router correctly"""
    from serve.openai_routes import router

    assert router is not None
    assert hasattr(router, "routes")


def test_all_exports():
    """Test __all__ exports match expected public API"""
    from serve import openai_routes

    assert hasattr(openai_routes, "__all__")
    assert "router" in openai_routes.__all__
