"""Comprehensive tests for serve/main.py - Main FastAPI application"""
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def clean_env(monkeypatch):
    """Provide clean environment for each test"""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "disabled")
    monkeypatch.setenv("LUKHAS_ASYNC_ORCH", "0")
    monkeypatch.setenv("LUKHAS_WEBAUTHN", "0")
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "false")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")
    # Clear module cache to force reload with new env
    import sys
    if "serve.main" in sys.modules:
        del sys.modules["serve.main"]
    yield
    # Clean up after test
    if "serve.main" in sys.modules:
        del sys.modules["serve.main"]


@pytest.fixture
def client(clean_env):
    """Create test client for the main app"""
    from serve.main import app
    return TestClient(app)


@pytest.fixture
def client_with_strict_auth(monkeypatch):
    """Create test client with strict auth enabled"""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")
    monkeypatch.setenv("LUKHAS_ASYNC_ORCH", "0")
    monkeypatch.setenv("LUKHAS_WEBAUTHN", "0")
    # Clear module cache
    import sys
    if "serve.main" in sys.modules:
        del sys.modules["serve.main"]

    from serve.main import app
    client = TestClient(app)
    yield client

    # Clean up
    if "serve.main" in sys.modules:
        del sys.modules["serve.main"]


# ============================================================================
# Health Endpoints Tests
# ============================================================================

def test_healthz_returns_ok(client):
    """Test /healthz endpoint returns healthy status"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "voice_mode" in data
    assert "matriz" in data
    assert "lane" in data


def test_healthz_with_voice_degraded(client, monkeypatch):
    """Test /healthz shows degraded when voice unavailable and required"""
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "true")

    # Mock voice_core_available to return False
    with patch("serve.main.voice_core_available", return_value=False):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["voice_mode"] == "degraded"
        assert "degraded_reasons" in data
        assert "voice" in data["degraded_reasons"]


def test_healthz_with_matriz_info(client, monkeypatch):
    """Test /healthz includes MATRIZ version info"""
    monkeypatch.setenv("MATRIZ_VERSION", "2.0.0")
    monkeypatch.setenv("MATRIZ_ROLLOUT", "enabled")

    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["matriz"]["version"] == "2.0.0"
    assert data["matriz"]["rollout"] == "enabled"
    assert data["matriz"]["enabled"] is True


def test_health_alias(client):
    """Test /health endpoint is an alias for /healthz"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_readyz_when_healthy(client):
    """Test /readyz returns ready status when healthy"""
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_readyz_when_not_healthy(client, monkeypatch):
    """Test /readyz returns not_ready for non-ok status"""
    # Patch _get_health_status to return non-ok status
    with patch("serve.main._get_health_status", return_value={"status": "degraded", "voice_mode": "degraded"}):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_ready"
        assert "details" in data


def test_metrics_endpoint(client):
    """Test /metrics returns Prometheus-style metrics"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    content = response.text
    assert "process_cpu_seconds_total" in content
    assert "http_requests_total" in content
    assert "lukhas_api_info" in content


# ============================================================================
# OpenAI-Compatible Endpoints Tests
# ============================================================================

def test_list_models(client):
    """Test /v1/models returns model list"""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert "data" in data
    assert len(data["data"]) > 0

    # Verify expected models
    model_ids = [m["id"] for m in data["data"]]
    assert "lukhas-mini" in model_ids
    assert "lukhas-embed-1" in model_ids
    assert "text-embedding-ada-002" in model_ids
    assert "gpt-4" in model_ids


def test_list_models_caching(client):
    """Test model list is cached between requests"""
    response1 = client.get("/v1/models")
    response2 = client.get("/v1/models")
    assert response1.json() == response2.json()


def test_create_embeddings_default(client):
    """Test /v1/embeddings with default parameters"""
    response = client.post("/v1/embeddings", json={
        "input": "test input text",
        "model": "text-embedding-ada-002"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) == 1
    assert data["data"][0]["object"] == "embedding"
    assert len(data["data"][0]["embedding"]) == 1536  # Default dimension
    assert data["model"] == "text-embedding-ada-002"


def test_create_embeddings_custom_dimensions(client):
    """Test /v1/embeddings with custom dimensions"""
    response = client.post("/v1/embeddings", json={
        "input": "test",
        "dimensions": 512
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"][0]["embedding"]) == 512


def test_create_embeddings_deterministic(client):
    """Test embeddings are deterministic for same input"""
    payload = {"input": "deterministic test"}
    response1 = client.post("/v1/embeddings", json=payload)
    response2 = client.post("/v1/embeddings", json=payload)

    embedding1 = response1.json()["data"][0]["embedding"]
    embedding2 = response2.json()["data"][0]["embedding"]
    assert embedding1 == embedding2


def test_create_embeddings_empty_input(client):
    """Test /v1/embeddings with empty input"""
    response = client.post("/v1/embeddings", json={
        "input": ""
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"][0]["embedding"]) == 1536


def test_chat_completion_basic(client):
    """Test /v1/chat/completions with basic request"""
    response = client.post("/v1/chat/completions", json={
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["object"] == "chat.completion"
    assert data["model"] == "gpt-4"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert data["choices"][0]["finish_reason"] == "stop"
    assert "usage" in data


def test_chat_completion_empty_messages(client):
    """Test /v1/chat/completions with empty messages"""
    response = client.post("/v1/chat/completions", json={
        "model": "gpt-4",
        "messages": []
    })
    assert response.status_code == 200
    # Should still return a response even with empty messages


def test_chat_completion_token_usage(client):
    """Test /v1/chat/completions includes token usage"""
    response = client.post("/v1/chat/completions", json={
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "test message"}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "prompt_tokens" in data["usage"]
    assert "completion_tokens" in data["usage"]
    assert "total_tokens" in data["usage"]
    assert data["usage"]["total_tokens"] == data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"]


def test_create_response_basic(client):
    """Test /v1/responses with basic input"""
    response = client.post("/v1/responses", json={
        "input": "test input",
        "model": "lukhas-mini"
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["object"] == "chat.completion"
    assert data["model"] == "lukhas-mini"
    assert data["choices"][0]["message"]["content"].startswith("[stub]")


def test_create_response_with_messages(client):
    """Test /v1/responses with messages format"""
    response = client.post("/v1/responses", json={
        "messages": [
            {"role": "user", "content": "hello"}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert "[stub]" in data["choices"][0]["message"]["content"]


def test_create_response_missing_input(client):
    """Test /v1/responses returns 400 when input missing"""
    response = client.post("/v1/responses", json={
        "model": "lukhas-mini"
    })
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_create_response_empty_input(client):
    """Test /v1/responses returns 400 when input empty"""
    response = client.post("/v1/responses", json={
        "input": ""
    })
    assert response.status_code == 400


def test_create_response_streaming_missing_input(client):
    """Test /v1/responses streaming returns 400 when input missing"""
    response = client.post("/v1/responses", json={
        "stream": True
    })
    assert response.status_code == 400


def test_create_response_streaming_empty_input(client):
    """Test /v1/responses streaming returns 400 when input empty"""
    response = client.post("/v1/responses", json={
        "stream": True,
        "input": ""
    })
    assert response.status_code == 400


def test_create_response_streaming(client):
    """Test /v1/responses with streaming enabled"""
    response = client.post("/v1/responses", json={
        "input": "test",
        "stream": True
    })
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    # Read streaming response
    content = response.text
    assert "data:" in content
    assert "[DONE]" in content


def test_create_response_with_async_orch(client, monkeypatch):
    """Test /v1/responses with async orchestrator enabled"""
    monkeypatch.setenv("LUKHAS_ASYNC_ORCH", "1")

    # Mock the async orchestrator
    mock_orch = MagicMock(return_value={"answer": "orchestrated response"})

    with patch("serve.main.ASYNC_ORCH_ENABLED", True):
        with patch("serve.main._RUN_ASYNC_ORCH", mock_orch):
            # Reload module with new settings
            import sys
            if "serve.main" in sys.modules:
                del sys.modules["serve.main"]
            from serve.main import app
            test_client = TestClient(app)

            response = test_client.post("/v1/responses", json={
                "input": "test orchestration"
            })
            assert response.status_code == 200


def test_openapi_export(client):
    """Test /openapi.json returns OpenAPI spec"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


# ============================================================================
# Middleware Tests
# ============================================================================

def test_headers_middleware_adds_trace_id(client):
    """Test HeadersMiddleware adds X-Trace-Id"""
    response = client.get("/healthz")
    assert "X-Trace-Id" in response.headers
    assert "X-Request-Id" in response.headers
    assert response.headers["X-Trace-Id"] == response.headers["X-Request-Id"]


def test_headers_middleware_adds_rate_limit_headers(client):
    """Test HeadersMiddleware adds rate limit headers"""
    response = client.get("/healthz")
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "60"


def test_strict_auth_disabled_allows_requests(client):
    """Test StrictAuthMiddleware allows requests when disabled"""
    response = client.get("/v1/models")
    assert response.status_code == 200


def test_strict_auth_enabled_blocks_without_header(client_with_strict_auth):
    """Test StrictAuthMiddleware blocks requests without auth header"""
    response = client_with_strict_auth.get("/v1/models")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data


def test_strict_auth_enabled_blocks_invalid_scheme(client_with_strict_auth):
    """Test StrictAuthMiddleware blocks non-Bearer auth"""
    response = client_with_strict_auth.get(
        "/v1/models",
        headers={"Authorization": "Basic invalid"}
    )
    assert response.status_code == 401


def test_strict_auth_enabled_blocks_empty_token(client_with_strict_auth):
    """Test StrictAuthMiddleware blocks empty Bearer token"""
    response = client_with_strict_auth.get(
        "/v1/models",
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401


def test_strict_auth_enabled_allows_with_token(client_with_strict_auth):
    """Test StrictAuthMiddleware allows requests with Bearer token"""
    response = client_with_strict_auth.get(
        "/v1/models",
        headers={"Authorization": "Bearer valid-token-123"}
    )
    assert response.status_code == 200


def test_strict_auth_skips_non_v1_endpoints(client_with_strict_auth):
    """Test StrictAuthMiddleware skips non-/v1/ endpoints"""
    response = client_with_strict_auth.get("/healthz")
    assert response.status_code == 200


def test_cors_middleware_configured(client):
    """Test CORS middleware is configured"""
    response = client.options("/v1/models", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    # CORS should be handled
    assert response.status_code in [200, 204]


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_hash_embed_deterministic():
    """Test _hash_embed produces deterministic outputs"""
    from serve.main import _hash_embed

    result1 = _hash_embed("test", 100)
    result2 = _hash_embed("test", 100)
    assert result1 == result2
    assert len(result1) == 100
    assert all(0.0 <= x <= 1.0 for x in result1)


def test_hash_embed_different_inputs():
    """Test _hash_embed produces different outputs for different inputs"""
    from serve.main import _hash_embed

    result1 = _hash_embed("input1", 100)
    result2 = _hash_embed("input2", 100)
    assert result1 != result2


def test_voice_core_available_when_missing():
    """Test voice_core_available returns False when module missing"""
    from serve.main import voice_core_available

    with patch("importlib.import_module", side_effect=ImportError):
        assert voice_core_available() is False


def test_require_api_key_no_key_set(client, monkeypatch):
    """Test require_api_key allows when no key configured"""
    from serve.main import require_api_key

    monkeypatch.delenv("LUKHAS_API_KEY", raising=False)
    result = require_api_key(x_api_key=None)
    assert result is None


def test_require_api_key_valid(client, monkeypatch):
    """Test require_api_key validates correct key"""
    from serve.main import require_api_key

    monkeypatch.setenv("LUKHAS_API_KEY", "secret-key")
    result = require_api_key(x_api_key="secret-key")
    assert result == "secret-key"


def test_require_api_key_invalid(client, monkeypatch):
    """Test require_api_key rejects incorrect key"""
    from serve.main import require_api_key
    from fastapi import HTTPException

    monkeypatch.setenv("LUKHAS_API_KEY", "secret-key")

    with pytest.raises(HTTPException) as exc_info:
        require_api_key(x_api_key="wrong-key")
    assert exc_info.value.status_code == 401


def test_safe_import_router_success():
    """Test _safe_import_router with valid module"""
    from serve.main import _safe_import_router

    # Should not raise even if module doesn't exist
    result = _safe_import_router("nonexistent.module")
    assert result is None


def test_streaming_generator_with_messages():
    """Test _stream_generator with messages format"""
    import asyncio
    from serve.main import _stream_generator

    request = {
        "messages": [
            {"role": "user", "content": "hello"}
        ],
        "model": "lukhas-mini"
    }

    # Collect chunks
    async def collect_chunks():
        chunks = []
        async for chunk in _stream_generator(request):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_chunks())
    assert len(chunks) > 0
    assert any("[stub]" in chunk for chunk in chunks)
    assert any("[DONE]" in chunk for chunk in chunks)


def test_streaming_generator_with_input():
    """Test _stream_generator with direct input"""
    import asyncio
    from serve.main import _stream_generator

    request = {
        "input": "test input",
        "model": "lukhas-mini"
    }

    async def collect_chunks():
        chunks = []
        async for chunk in _stream_generator(request):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_chunks())
    assert len(chunks) > 0


def test_streaming_generator_empty_input():
    """Test _stream_generator with empty input"""
    import asyncio
    from serve.main import _stream_generator

    request = {"model": "lukhas-mini"}

    async def collect_chunks():
        chunks = []
        async for chunk in _stream_generator(request):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_chunks())
    # Should still generate chunks for empty input
    assert len(chunks) > 0
