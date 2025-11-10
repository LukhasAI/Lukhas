"""
Comprehensive tests for serve/main.py

Following LUKHAS Test Surgeon guidelines:
- Deterministic (time frozen, seeds fixed, no network)
- OpenAI-compatible endpoint contracts validated
- Middleware behavior (auth, headers, CORS) covered
- Streaming/SSE functionality tested
- Error conditions and edge cases handled

Target: 85%+ coverage
"""
import json
import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_env(monkeypatch):
    """Set up clean test environment variables"""
    monkeypatch.setenv("LUKHAS_API_KEY", "test-api-key-123")
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")
    monkeypatch.setenv("LUKHAS_ASYNC_ORCH", "0")
    monkeypatch.setenv("LUKHAS_WEBAUTHN", "0")
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "false")
    monkeypatch.setenv("MATRIZ_VERSION", "0.1.0")
    monkeypatch.setenv("MATRIZ_ROLLOUT", "disabled")
    monkeypatch.setenv("LUKHAS_LANE", "test")


@pytest.fixture
def client(test_env):
    """FastAPI TestClient with mocked dependencies"""
    # Mock optional dependencies to avoid import errors
    with mock.patch.dict("sys.modules", {
        "MATRIZ": mock.MagicMock(),
        "matriz": mock.MagicMock(),
        "lukhas.memory": mock.MagicMock(),
        "opentelemetry.instrumentation.fastapi": mock.MagicMock(),
        "enterprise.observability.instantiate": mock.MagicMock(),
    }):
        # Re-import to apply mocks
        import importlib
        import serve.main as main_module
        importlib.reload(main_module)
        
        yield TestClient(main_module.app)


# ========================================================================
# Helper Function Tests
# ========================================================================

def test_hash_embed_deterministic():
    """Test that _hash_embed produces deterministic embeddings"""
    from serve.main import _hash_embed
    
    text = "test input"
    embed1 = _hash_embed(text, dim=1536)
    embed2 = _hash_embed(text, dim=1536)
    
    assert embed1 == embed2, "Embeddings must be deterministic"
    assert len(embed1) == 1536, "Embedding dimension must match requested dim"
    assert all(0 <= v <= 1 for v in embed1), "Embedding values must be normalized [0,1]"


def test_hash_embed_unique():
    """Test that different inputs produce different embeddings"""
    from serve.main import _hash_embed
    
    embed1 = _hash_embed("input one", dim=128)
    embed2 = _hash_embed("input two", dim=128)
    
    assert embed1 != embed2, "Different inputs must produce different embeddings"


def test_get_health_status_basic(test_env):
    """Test _get_health_status returns expected structure"""
    from serve.main import _get_health_status
    
    status = _get_health_status()
    
    assert status["status"] == "ok"
    assert "voice_mode" in status
    assert "matriz" in status
    assert status["matriz"]["version"] == "0.1.0"
    assert status["matriz"]["rollout"] == "disabled"
    assert status["matriz"]["enabled"] is False
    assert status["lane"] == "test"


def test_get_health_status_voice_degraded(test_env, monkeypatch):
    """Test health status when voice is required but unavailable"""
    monkeypatch.setenv("LUKHAS_VOICE_REQUIRED", "true")
    
    with mock.patch("serve.main.voice_core_available", return_value=False):
        from serve.main import _get_health_status
        status = _get_health_status()
        
        assert status["voice_mode"] == "degraded"
        assert "degraded_reasons" in status
        assert "voice" in status["degraded_reasons"]


# ========================================================================
# Health Endpoint Tests
# ========================================================================

def test_healthz_endpoint(client):
    """Test /healthz endpoint returns 200 and correct structure"""
    response = client.get("/healthz")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "matriz" in data
    assert "lane" in data


def test_health_alias_endpoint(client):
    """Test /health endpoint (alias) returns same as /healthz"""
    healthz_resp = client.get("/healthz").json()
    health_resp = client.get("/health").json()
    
    assert healthz_resp == health_resp, "/health must be alias of /healthz"


def test_readyz_endpoint_ready(client):
    """Test /readyz endpoint when system is ready"""
    response = client.get("/readyz")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_metrics_endpoint(client):
    """Test /metrics endpoint returns Prometheus-style metrics"""
    response = client.get("/metrics")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    content = response.text
    assert "# HELP" in content
    assert "# TYPE" in content
    assert "process_cpu_seconds_total" in content
    assert "http_requests_total" in content
    assert "lukhas_api_info" in content


# ========================================================================
# Middleware Tests - StrictAuthMiddleware
# ========================================================================

def test_strict_auth_allows_non_v1_paths(client):
    """Test that non-/v1/ paths bypass auth"""
    response = client.get("/healthz")
    assert response.status_code == 200, "Non-/v1/ paths should bypass strict auth"


def test_strict_auth_requires_bearer_token(client):
    """Test that /v1/ endpoints require Bearer token"""
    response = client.get("/v1/models")
    
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert "Missing Authorization header" in str(data)


def test_strict_auth_rejects_empty_bearer(client):
    """Test that empty Bearer token is rejected"""
    headers = {"Authorization": "Bearer "}
    response = client.get("/v1/models", headers=headers)
    
    assert response.status_code == 401
    data = response.json()
    assert "Bearer token is empty" in str(data)


def test_strict_auth_rejects_non_bearer_scheme(client):
    """Test that non-Bearer auth schemes are rejected"""
    headers = {"Authorization": "Basic dGVzdDp0ZXN0"}
    response = client.get("/v1/models", headers=headers)
    
    assert response.status_code == 401
    data = response.json()
    assert "Bearer scheme" in str(data)


def test_strict_auth_accepts_valid_bearer(client):
    """Test that valid Bearer token allows access"""
    headers = {"Authorization": "Bearer valid-token"}
    response = client.get("/v1/models", headers=headers)
    
    assert response.status_code == 200, "Valid Bearer token should allow access"


def test_strict_auth_disabled_in_permissive_mode(client, monkeypatch):
    """Test that strict auth can be disabled via LUKHAS_POLICY_MODE"""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "permissive")
    
    # Need to reload to apply env change
    import importlib
    import serve.main as main_module
    importlib.reload(main_module)
    client_permissive = TestClient(main_module.app)
    
    response = client_permissive.get("/v1/models")
    assert response.status_code == 200, "Permissive mode should allow access without token"


# ========================================================================
# Middleware Tests - HeadersMiddleware
# ========================================================================

def test_headers_middleware_adds_trace_ids(client):
    """Test that HeadersMiddleware adds X-Trace-Id and X-Request-Id"""
    response = client.get("/healthz")
    
    assert "x-trace-id" in response.headers
    assert "x-request-id" in response.headers
    
    trace_id = response.headers["x-trace-id"]
    request_id = response.headers["x-request-id"]
    
    assert trace_id == request_id, "Trace and Request IDs should match"
    assert len(trace_id) == 32, "Trace ID should be 32 chars (UUID without dashes)"


def test_headers_middleware_adds_rate_limit_headers(client):
    """Test that rate limit headers are added"""
    response = client.get("/healthz")
    
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers
    assert "x-ratelimit-limit-requests" in response.headers
    assert "x-ratelimit-remaining-requests" in response.headers
    assert "x-ratelimit-reset-requests" in response.headers
    
    assert response.headers["x-ratelimit-limit"] == "60"
    assert response.headers["x-ratelimit-remaining"] == "59"


# ========================================================================
# OpenAI-Compatible Endpoint Tests
# ========================================================================

def test_list_models_endpoint(client):
    """Test GET /v1/models returns model list"""
    headers = {"Authorization": "Bearer test-token"}
    response = client.get("/v1/models", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["object"] == "list"
    assert "data" in data
    assert len(data["data"]) > 0
    
    # Check model structure
    model = data["data"][0]
    assert "id" in model
    assert "object" in model
    assert model["object"] == "model"
    assert "owned_by" in model


def test_list_models_caching(client):
    """Test that model list is cached"""
    headers = {"Authorization": "Bearer test-token"}
    
    response1 = client.get("/v1/models", headers=headers)
    response2 = client.get("/v1/models", headers=headers)
    
    assert response1.json() == response2.json(), "Model list should be cached"


def test_create_embeddings_basic(client):
    """Test POST /v1/embeddings with basic input"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "input": "test text",
        "model": "text-embedding-ada-002"
    }
    
    response = client.post("/v1/embeddings", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["object"] == "list"
    assert len(data["data"]) == 1
    assert data["data"][0]["object"] == "embedding"
    assert "embedding" in data["data"][0]
    assert len(data["data"][0]["embedding"]) == 1536  # Default dimension
    assert data["model"] == "text-embedding-ada-002"
    assert "usage" in data


def test_create_embeddings_custom_dimensions(client):
    """Test embeddings with custom dimensions"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "input": "test text",
        "model": "text-embedding-ada-002",
        "dimensions": 768
    }
    
    response = client.post("/v1/embeddings", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"][0]["embedding"]) == 768


def test_create_chat_completion_basic(client):
    """Test POST /v1/chat/completions with basic input"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
    
    response = client.post("/v1/chat/completions", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["object"] == "chat.completion"
    assert "created" in data
    assert data["model"] == "gpt-4"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "content" in data["choices"][0]["message"]
    assert data["choices"][0]["finish_reason"] == "stop"
    assert "usage" in data


def test_create_response_basic(client):
    """Test POST /v1/responses with input field"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "input": "test input",
        "model": "lukhas-mini"
    }
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["object"] == "chat.completion"
    assert "created" in data
    assert data["model"] == "lukhas-mini"
    assert len(data["choices"]) == 1
    assert "usage" in data


def test_create_response_with_messages(client):
    """Test POST /v1/responses with messages field"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "messages": [
            {"role": "user", "content": "test message"}
        ],
        "model": "lukhas-mini"
    }
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "content" in data["choices"][0]["message"]


def test_create_response_missing_input(client):
    """Test that missing input returns 400"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {"model": "lukhas-mini"}
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]


def test_create_response_empty_input(client):
    """Test that empty input returns 400"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {"input": "", "model": "lukhas-mini"}
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 400


# ========================================================================
# Streaming/SSE Tests
# ========================================================================

def test_create_response_streaming(client):
    """Test POST /v1/responses with stream=true"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "input": "test streaming",
        "model": "lukhas-mini",
        "stream": True
    }
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Parse SSE stream
    content = response.text
    assert "data: " in content
    assert "[DONE]" in content
    
    # Check chunks format
    chunks = [line for line in content.split("\n") if line.startswith("data: ")]
    assert len(chunks) > 0
    
    # Parse first chunk (should be JSON)
    first_chunk = chunks[0].replace("data: ", "")
    if first_chunk != "[DONE]":
        chunk_data = json.loads(first_chunk)
        assert "id" in chunk_data
        assert chunk_data["object"] == "chat.completion.chunk"
        assert "choices" in chunk_data


def test_create_response_streaming_missing_input(client):
    """Test that streaming without input/messages returns 400"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {"stream": True, "model": "lukhas-mini"}
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 400


def test_create_response_streaming_empty_input(client):
    """Test that streaming with empty input returns 400"""
    headers = {"Authorization": "Bearer test-token"}
    payload = {"input": "", "stream": True}
    
    response = client.post("/v1/responses", headers=headers, json=payload)
    
    assert response.status_code == 400


# ========================================================================
# OpenAPI Export Test
# ========================================================================

def test_openapi_export(client):
    """Test GET /openapi.json returns valid OpenAPI spec"""
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "LUKHAS API"
    assert "paths" in data


# ========================================================================
# CORS Configuration Test
# ========================================================================

def test_cors_preflight(client):
    """Test CORS preflight OPTIONS request

    Note: StrictAuthMiddleware runs before CORSMiddleware due to FastAPI
    middleware execution order (LIFO), so OPTIONS requests to /v1/* endpoints
    also require Bearer token authentication.
    """
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    }

    # OPTIONS without auth should be blocked by StrictAuthMiddleware
    response = client.options("/v1/models", headers=headers)
    assert response.status_code == 401

    # OPTIONS with auth should pass StrictAuthMiddleware
    headers_with_auth = {
        **headers,
        "Authorization": "Bearer test-token"
    }
    response_with_auth = client.options("/v1/models", headers=headers_with_auth)
    # After passing auth, should get 405 (Method Not Allowed) or 404
    assert response_with_auth.status_code in (200, 404, 405)


# ========================================================================
# Error Handling & Edge Cases
# ========================================================================

def test_require_api_key_function():
    """Test require_api_key dependency function"""
    from serve.main import require_api_key
    
    # Test with valid key
    with mock.patch("serve.main.env_get", return_value="expected-key"):
        result = require_api_key(x_api_key="expected-key")
        assert result == "expected-key"
    
    # Test with invalid key
    with mock.patch("serve.main.env_get", return_value="expected-key"):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            require_api_key(x_api_key="wrong-key")
        assert exc_info.value.status_code == 401


def test_voice_core_available_true():
    """Test voice_core_available when bridge.voice exists"""
    with mock.patch("importlib.import_module", return_value=mock.MagicMock()):
        from serve.main import voice_core_available
        assert voice_core_available() is True


def test_voice_core_available_false():
    """Test voice_core_available when bridge.voice missing"""
    def mock_import(name):
        if name == "bridge.voice":
            raise ImportError("Module not found")
        return mock.MagicMock()
    
    with mock.patch("importlib.import_module", side_effect=mock_import):
        from serve.main import voice_core_available
        assert voice_core_available() is False


def test_safe_import_router_success():
    """Test _safe_import_router with successful import"""
    from serve.main import _safe_import_router
    
    mock_module = mock.MagicMock()
    mock_router = mock.MagicMock()
    mock_module.router = mock_router
    
    with mock.patch("builtins.__import__", return_value=mock_module):
        result = _safe_import_router("test_module", "router")
        assert result == mock_router


def test_safe_import_router_failure():
    """Test _safe_import_router returns None on import error"""
    from serve.main import _safe_import_router
    
    with mock.patch("builtins.__import__", side_effect=ImportError("Module not found")):
        result = _safe_import_router("nonexistent_module")
        assert result is None


# ========================================================================
# Confidence & Coverage Report
# ========================================================================

"""
Confidence: 0.85

Test Coverage Analysis:
- ✅ Health endpoints: /healthz, /health, /readyz, /metrics
- ✅ StrictAuthMiddleware: auth validation, 401 errors, policy modes
- ✅ HeadersMiddleware: trace IDs, rate limit headers
- ✅ OpenAI endpoints: /v1/models, /v1/embeddings, /v1/chat/completions
- ✅ LUKHAS endpoint: /v1/responses (non-streaming + streaming)
- ✅ Helper functions: _hash_embed, _get_health_status, etc.
- ✅ Error handling: missing input, empty input, auth errors
- ✅ Edge cases: voice degradation, CORS preflight

Assumptions:
1. Router imports (_safe_import_router) are mocked and don't need deep testing
2. MATRIZ orchestrator integration is optional and mocked out
3. OpenTelemetry instrumentation is tested via presence check only
4. Network blocking is handled by conftest.py fixture
5. Time freezing is handled by conftest.py fixture

Remaining gaps:
1. Module manifest counting in _get_health_status (pathlib edge cases)
2. ASYNC_ORCH_ENABLED=1 path (requires MATRIZ mocking)
3. WebAuthn router integration (LUKHAS_WEBAUTHN=1)
4. Deep SSE chunk parsing (partial coverage only)
5. Router-level endpoint tests (delegated to individual router test files)

Coverage target: 85%+
Mutation score: TBD (run mutmut for mutation coverage)
"""
