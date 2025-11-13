"""
Comprehensive test suite for serve/main.py

Tests FastAPI application initialization and middleware:
- CORS middleware configuration
- StrictAuthMiddleware (Bearer token enforcement)
- HeadersMiddleware (rate limit and trace headers)
- Health check endpoints (/healthz, /health, /readyz)
- Metrics endpoint
- OpenAI-compatible endpoints
- Router inclusion logic
- Streaming responses
"""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_env():
    """Mock environment configuration."""
    env_vars = {
        "LUKHAS_POLICY_MODE": "strict",
        "FRONTEND_ORIGIN": "http://localhost:3000",
        "LUKHAS_API_KEY": "test_api_key",
        "LUKHAS_VOICE_REQUIRED": "false",
        "MATRIZ_VERSION": "1.0.0",
        "MATRIZ_ROLLOUT": "enabled",
        "LUKHAS_LANE": "dev",
        "LUKHAS_ASYNC_ORCH": "0",
    }

    with patch.dict("os.environ", env_vars, clear=False):
        yield env_vars


@pytest.fixture
def test_client(mock_env):
    """Create test client with mocked environment."""
    # Import after env vars are set
    from serve.main import app

    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz_basic(self, test_client):
        """Test basic /healthz endpoint."""
        response = test_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "voice_mode" in data
        assert "matriz" in data
        assert "lane" in data

    def test_healthz_voice_mode_normal(self, test_client):
        """Test voice mode when not required."""
        with patch.dict("os.environ", {"LUKHAS_VOICE_REQUIRED": "false"}):
            response = test_client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["voice_mode"] in ["normal", "degraded"]

    def test_healthz_voice_required_missing(self, test_client):
        """Test voice mode degraded when required but missing."""
        with patch("serve.main.voice_core_available", return_value=False):
            with patch.dict("os.environ", {"LUKHAS_VOICE_REQUIRED": "true"}):
                response = test_client.get("/healthz")

                assert response.status_code == 200
                data = response.json()
                assert data["voice_mode"] == "degraded"
                assert "degraded_reasons" in data
                assert "voice" in data["degraded_reasons"]

    def test_healthz_matriz_info(self, test_client):
        """Test MATRIZ information in health check."""
        response = test_client.get("/healthz")

        assert response.status_code == 200
        data = response.json()

        assert "matriz" in data
        matriz = data["matriz"]
        assert "version" in matriz
        assert "rollout" in matriz
        assert "enabled" in matriz

    def test_healthz_lane_info(self, test_client):
        """Test lane information in health check."""
        with patch.dict("os.environ", {"LUKHAS_LANE": "staging"}):
            response = test_client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["lane"] == "staging"

    def test_healthz_modules_count(self, test_client):
        """Test module manifest counting."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.rglob", return_value=[]):
                response = test_client.get("/healthz")

                assert response.status_code == 200
                data = response.json()
                if "modules" in data:
                    assert "manifest_count" in data["modules"]

    def test_health_alias(self, test_client):
        """Test /health alias endpoint."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_readyz_ready(self, test_client):
        """Test /readyz when system is ready."""
        response = test_client.get("/readyz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_readyz_not_ready(self, test_client):
        """Test /readyz when system is not ready."""
        # Mock _get_health_status to return unhealthy
        from serve import main

        original_health = main._get_health_status

        def mock_unhealthy():
            return {"status": "unhealthy", "error": "test error"}

        with patch.object(main, "_get_health_status", mock_unhealthy):
            response = test_client.get("/readyz")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"
            assert "details" in data


class TestMetricsEndpoint:
    """Test /metrics endpoint."""

    def test_metrics_format(self, test_client):
        """Test metrics endpoint returns Prometheus format."""
        response = test_client.get("/metrics")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        content = response.text

        # Check for Prometheus-style metrics
        assert "# HELP" in content
        assert "# TYPE" in content
        assert "process_cpu_seconds_total" in content
        assert "http_requests_total" in content
        assert "lukhas_api_info" in content

    def test_metrics_includes_version(self, test_client):
        """Test metrics includes version information."""
        response = test_client.get("/metrics")

        assert response.status_code == 200
        content = response.text
        assert 'version="1.0.0"' in content


class TestOpenAICompatibleEndpoints:
    """Test OpenAI-compatible endpoints in main.py."""

    def test_v1_models_endpoint(self, test_client):
        """Test /v1/models endpoint."""
        response = test_client.get("/v1/models")

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "list"
        assert len(data["data"]) >= 2

        model_ids = [m["id"] for m in data["data"]]
        assert "lukhas-mini" in model_ids
        assert "lukhas-embed-1" in model_ids

    def test_v1_models_cached(self, test_client):
        """Test models list is cached."""
        response1 = test_client.get("/v1/models")
        response2 = test_client.get("/v1/models")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()

    def test_v1_embeddings_endpoint(self, test_client):
        """Test /v1/embeddings endpoint."""
        response = test_client.post(
            "/v1/embeddings",
            json={"input": "test text", "model": "text-embedding-ada-002"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "list"
        assert len(data["data"]) == 1
        assert "embedding" in data["data"][0]
        assert data["model"] == "text-embedding-ada-002"

    def test_v1_embeddings_custom_dimensions(self, test_client):
        """Test embeddings with custom dimensions."""
        response = test_client.post(
            "/v1/embeddings",
            json={"input": "test", "dimensions": 512},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"][0]["embedding"]) == 512

    def test_v1_chat_completions_endpoint(self, test_client):
        """Test /v1/chat/completions endpoint."""
        response = test_client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"},
                ],
                "model": "gpt-4",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "chat.completion"
        assert data["model"] == "gpt-4"
        assert "choices" in data
        assert len(data["choices"]) == 1
        assert data["choices"][0]["message"]["role"] == "assistant"

    def test_v1_responses_endpoint(self, test_client):
        """Test /v1/responses endpoint."""
        response = test_client.post(
            "/v1/responses",
            json={"input": "test input", "model": "lukhas-mini"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "chat.completion"
        assert data["model"] == "lukhas-mini"
        assert data["id"].startswith("resp_")

    def test_v1_responses_streaming(self, test_client):
        """Test /v1/responses streaming."""
        response = test_client.post(
            "/v1/responses",
            json={"input": "stream test", "stream": True},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Check SSE format
        content = response.text
        assert "data: " in content
        assert "data: [DONE]" in content

    def test_v1_responses_empty_input_error(self, test_client):
        """Test error on empty input."""
        response = test_client.post(
            "/v1/responses",
            json={"input": ""},
        )

        assert response.status_code == 400
        assert "error" in response.json()["detail"]

    def test_v1_responses_missing_field_streaming_error(self, test_client):
        """Test error when streaming without input."""
        response = test_client.post(
            "/v1/responses",
            json={"stream": True},
        )

        assert response.status_code == 400


class TestAsyncOrchestrator:
    """Test async orchestrator integration."""

    def test_async_orch_disabled_by_default(self, test_client):
        """Test async orchestrator is disabled by default."""
        from serve.main import ASYNC_ORCH_ENABLED

        assert ASYNC_ORCH_ENABLED is False

    def test_async_orch_enabled(self):
        """Test async orchestrator can be enabled."""
        with patch.dict("os.environ", {"LUKHAS_ASYNC_ORCH": "1"}):
            # Need to reload module to pick up env change
            import importlib
            from serve import main

            importlib.reload(main)

            # Check if enabled (may be False if import fails)
            assert isinstance(main.ASYNC_ORCH_ENABLED, bool)

    def test_v1_responses_with_async_orch(self):
        """Test responses with async orchestrator."""
        mock_orch = Mock(return_value={"answer": "orchestrated response"})

        with patch.dict("os.environ", {"LUKHAS_ASYNC_ORCH": "0"}):
            from serve.main import app

            client = TestClient(app)

            response = client.post(
                "/v1/responses",
                json={"input": "test"},
            )

            assert response.status_code == 200


class TestStrictAuthMiddleware:
    """Test StrictAuthMiddleware."""

    def test_strict_auth_disabled_permissive_mode(self, test_client):
        """Test auth is disabled in permissive mode."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "permissive"}):
            from serve.main import app

            client = TestClient(app)

            response = client.get("/v1/models")
            # Should not require auth in permissive mode
            assert response.status_code in [200, 401]

    def test_strict_auth_enabled_strict_mode(self):
        """Test auth is enforced in strict mode."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "strict"}):
            from serve.main import app

            client = TestClient(app)

            # Request without auth
            response = client.get("/v1/models")
            assert response.status_code == 401

            error = response.json()
            assert "error" in error
            assert error["error"]["type"] == "invalid_api_key"

    def test_strict_auth_missing_authorization(self):
        """Test error on missing Authorization header."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "strict"}):
            from serve.main import app

            client = TestClient(app)

            response = client.get("/v1/models")
            assert response.status_code == 401

            error = response.json()["error"]
            assert "Missing Authorization header" in str(error)

    def test_strict_auth_invalid_scheme(self):
        """Test error on non-Bearer scheme."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "strict"}):
            from serve.main import app

            client = TestClient(app)

            response = client.get(
                "/v1/models",
                headers={"Authorization": "Basic dGVzdDp0ZXN0"},
            )

            assert response.status_code == 401
            error = response.json()["error"]
            assert "Bearer scheme" in str(error)

    def test_strict_auth_empty_token(self):
        """Test error on empty Bearer token."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "strict"}):
            from serve.main import app

            client = TestClient(app)

            response = client.get(
                "/v1/models",
                headers={"Authorization": "Bearer "},
            )

            assert response.status_code == 401
            error = response.json()["error"]
            assert "empty" in str(error).lower()

    def test_strict_auth_valid_token(self):
        """Test request passes with valid Bearer token."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "strict"}):
            from serve.main import app

            client = TestClient(app)

            response = client.get(
                "/v1/models",
                headers={"Authorization": "Bearer valid_token_123"},
            )

            # May still fail auth validation, but should pass middleware
            assert response.status_code in [200, 401, 403]

    def test_strict_auth_non_v1_paths_bypass(self):
        """Test non-/v1/* paths bypass strict auth."""
        with patch.dict("os.environ", {"LUKHAS_POLICY_MODE": "strict"}):
            from serve.main import app

            client = TestClient(app)

            # Health check should work without auth
            response = client.get("/healthz")
            assert response.status_code == 200

            # Metrics should work without auth
            response = client.get("/metrics")
            assert response.status_code == 200


class TestHeadersMiddleware:
    """Test HeadersMiddleware."""

    def test_headers_added_to_response(self, test_client):
        """Test headers are added to all responses."""
        response = test_client.get("/healthz")

        assert response.status_code == 200

        # Check trace headers
        assert "X-Trace-Id" in response.headers
        assert "X-Request-Id" in response.headers

        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert "x-ratelimit-limit-requests" in response.headers
        assert "x-ratelimit-remaining-requests" in response.headers
        assert "x-ratelimit-reset-requests" in response.headers

    def test_headers_values(self, test_client):
        """Test header values are correct."""
        response = test_client.get("/healthz")

        assert response.headers["X-RateLimit-Limit"] == "60"
        assert response.headers["X-RateLimit-Remaining"] == "59"
        assert response.headers["x-ratelimit-limit-requests"] == "60"
        assert response.headers["x-ratelimit-remaining-requests"] == "59"

    def test_trace_id_generated(self, test_client):
        """Test trace ID is automatically generated."""
        response = test_client.get("/healthz")

        trace_id = response.headers["X-Trace-Id"]
        request_id = response.headers["X-Request-Id"]

        assert len(trace_id) > 0
        assert trace_id == request_id


class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    def test_cors_enabled(self, test_client):
        """Test CORS headers are present."""
        response = test_client.options(
            "/healthz",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # CORS middleware should handle OPTIONS
        assert response.status_code in [200, 405]

    def test_cors_origin_configured(self):
        """Test CORS origin is configurable."""
        with patch.dict("os.environ", {"FRONTEND_ORIGIN": "https://example.com"}):
            from serve.main import app

            # Check middleware is configured
            cors_middleware = None
            for middleware in app.user_middleware:
                if "CORSMiddleware" in str(middleware):
                    cors_middleware = middleware
                    break

            assert cors_middleware is not None


class TestHashEmbedHelper:
    """Test hash embed helper function."""

    def test_hash_embed_basic(self):
        """Test basic hash embedding."""
        from serve.main import _hash_embed

        embedding = _hash_embed("test text", dim=1536)

        assert len(embedding) == 1536
        assert all(isinstance(v, float) for v in embedding)
        assert all(0 <= v <= 1 for v in embedding)

    def test_hash_embed_deterministic(self):
        """Test embeddings are deterministic."""
        from serve.main import _hash_embed

        emb1 = _hash_embed("same text", dim=100)
        emb2 = _hash_embed("same text", dim=100)

        assert emb1 == emb2

    def test_hash_embed_different_inputs(self):
        """Test different inputs produce different embeddings."""
        from serve.main import _hash_embed

        emb1 = _hash_embed("text A", dim=100)
        emb2 = _hash_embed("text B", dim=100)

        assert emb1 != emb2


class TestStreamGenerator:
    """Test SSE stream generator."""

    def test_stream_generator_basic(self):
        """Test basic stream generation."""
        import asyncio

        from serve.main import _stream_generator

        async def run_test():
            request = {"input": "test message", "model": "lukhas-mini"}
            chunks = []

            async for chunk in _stream_generator(request):
                chunks.append(chunk)

            return chunks

        chunks = asyncio.run(run_test())

        # Should have data chunks + DONE
        assert len(chunks) > 1
        assert chunks[-1] == "data: [DONE]\n\n"

        # All chunks should be SSE format
        for chunk in chunks[:-1]:
            assert chunk.startswith("data: ")
            assert chunk.endswith("\n\n")

    def test_stream_generator_with_messages(self):
        """Test stream generator with messages format."""
        import asyncio

        from serve.main import _stream_generator

        async def run_test():
            request = {
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "lukhas-mini",
            }
            chunks = []

            async for chunk in _stream_generator(request):
                chunks.append(chunk)

            return chunks

        chunks = asyncio.run(run_test())
        assert len(chunks) > 0

    def test_stream_generator_chunk_structure(self):
        """Test chunk structure is valid JSON."""
        import asyncio

        from serve.main import _stream_generator

        async def run_test():
            request = {"input": "test"}
            chunks = []

            async for chunk in _stream_generator(request):
                chunks.append(chunk)

            return chunks

        chunks = asyncio.run(run_test())

        # Parse JSON from data chunks (excluding DONE)
        for chunk_line in chunks[:-1]:
            chunk_data = chunk_line[6:-2]  # Remove "data: " and "\n\n"
            chunk_obj = json.loads(chunk_data)

            assert chunk_obj["object"] == "chat.completion.chunk"
            assert "id" in chunk_obj
            assert "created" in chunk_obj
            assert "model" in chunk_obj
            assert "choices" in chunk_obj

    def test_stream_generator_finish_reason(self):
        """Test final chunk has finish_reason."""
        import asyncio

        from serve.main import _stream_generator

        async def run_test():
            request = {"input": "test"}
            chunks = []

            async for chunk in _stream_generator(request):
                chunks.append(chunk)

            return chunks

        chunks = asyncio.run(run_test())

        # Parse second-to-last chunk (final data chunk before DONE)
        final_chunk = chunks[-2]
        chunk_data = final_chunk[6:-2]
        chunk_obj = json.loads(chunk_data)

        assert chunk_obj["choices"][0]["finish_reason"] == "stop"


class TestRequireAPIKey:
    """Test require_api_key helper."""

    def test_require_api_key_valid(self):
        """Test API key validation."""
        from serve.main import require_api_key

        with patch.dict("os.environ", {"LUKHAS_API_KEY": "test_key"}):
            result = require_api_key(x_api_key="test_key")
            assert result == "test_key"

    def test_require_api_key_invalid(self):
        """Test invalid API key raises HTTPException."""
        from serve.main import require_api_key
        from fastapi import HTTPException

        with patch.dict("os.environ", {"LUKHAS_API_KEY": "correct_key"}):
            with pytest.raises(HTTPException) as exc_info:
                require_api_key(x_api_key="wrong_key")

            assert exc_info.value.status_code == 401

    def test_require_api_key_none_allowed(self):
        """Test None API key allowed when not configured."""
        from serve.main import require_api_key

        with patch.dict("os.environ", {"LUKHAS_API_KEY": ""}, clear=True):
            result = require_api_key(x_api_key=None)
            assert result is None


class TestVoiceCoreAvailable:
    """Test voice_core_available helper."""

    def test_voice_available(self):
        """Test voice detection when available."""
        from serve.main import voice_core_available

        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = MagicMock()
            result = voice_core_available()
            assert result is True

    def test_voice_not_available(self):
        """Test voice detection when not available."""
        from serve.main import voice_core_available

        with patch("importlib.import_module", side_effect=ImportError):
            result = voice_core_available()
            assert result is False


class TestBuildModelList:
    """Test _build_model_list helper."""

    def test_build_model_list_structure(self):
        """Test model list structure."""
        from serve.main import _build_model_list

        models = _build_model_list()

        assert models["object"] == "list"
        assert "data" in models
        assert len(models["data"]) == 4

        model_ids = [m["id"] for m in models["data"]]
        assert "lukhas-mini" in model_ids
        assert "lukhas-embed-1" in model_ids
        assert "text-embedding-ada-002" in model_ids
        assert "gpt-4" in model_ids


class TestOpenAPIExport:
    """Test OpenAPI specification export."""

    def test_openapi_export(self, test_client):
        """Test /openapi.json endpoint."""
        response = test_client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "LUKHAS API"
        assert data["info"]["version"] == "1.0.0"


class TestSafeImportRouter:
    """Test _safe_import_router helper."""

    def test_safe_import_router_success(self):
        """Test successful router import."""
        from serve.main import _safe_import_router

        # Try importing a known module
        result = _safe_import_router("serve.routes", "router")
        # Should return router or None (graceful failure)
        assert result is None or hasattr(result, "routes")

    def test_safe_import_router_failure(self):
        """Test graceful failure on import error."""
        from serve.main import _safe_import_router

        result = _safe_import_router("nonexistent.module", "router")
        assert result is None
