"""
Comprehensive test suite for serve/openai_routes.py

Tests OpenAI-compatible API endpoints including:
- Model listing
- Embeddings (deterministic hash-based)
- Responses (streaming and non-streaming)
- Legacy modulated chat endpoints
- Authentication and rate limiting
- Request/trace ID handling
"""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Response
from fastapi.testclient import TestClient


@pytest.fixture
def mock_openai_service():
    """Mock OpenAI modulation service."""
    with patch("serve.openai_routes.OpenAIModulatedService") as mock_service_class:
        mock_instance = MagicMock()
        mock_instance.generate = AsyncMock(
            return_value={
                "content": "Modulated response",
                "raw": {"model": "gpt-4"},
                "modulation": {"applied": True},
                "metadata": {"tokens": 10},
            }
        )

        async def mock_stream():
            for chunk in ["Chunk1 ", "Chunk2 ", "Chunk3"]:
                yield chunk

        mock_instance.generate_stream = AsyncMock(return_value=mock_stream())
        mock_instance.metrics = {"requests": 100, "errors": 5}
        mock_service_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_bearer_auth():
    """Mock Bearer token authentication."""
    with patch("serve.openai_routes.require_bearer") as mock_auth:
        mock_auth.return_value = {
            "sub": "test_user",
            "scopes": ["api.read", "api.write"],
            "project_id": "test_project",
        }
        yield mock_auth


@pytest.fixture
def app_client(mock_bearer_auth):
    """Create FastAPI test client with mocked dependencies."""
    from serve.openai_routes import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestLegacyModulatedChat:
    """Test legacy /openai/chat endpoints."""

    def test_modulated_chat_success(self, app_client, mock_openai_service):
        """Test successful modulated chat request."""
        response = app_client.post(
            "/openai/chat",
            json={
                "prompt": "Hello world",
                "context": {"user": "test"},
                "task": "generate",
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Modulated response"
        assert "raw" in data
        assert "modulation" in data
        assert "metadata" in data

        # Verify service was called correctly
        mock_openai_service.generate.assert_called_once()
        call_kwargs = mock_openai_service.generate.call_args.kwargs
        assert call_kwargs["prompt"] == "Hello world"
        assert call_kwargs["context"] == {"user": "test"}
        assert call_kwargs["task"] == "generate"

    def test_modulated_chat_minimal_request(self, app_client, mock_openai_service):
        """Test modulated chat with minimal request."""
        response = app_client.post(
            "/openai/chat",
            json={"prompt": "Test"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        mock_openai_service.generate.assert_called_once()

    def test_modulated_chat_service_error(self, app_client, mock_openai_service):
        """Test error handling when service fails."""
        mock_openai_service.generate.side_effect = Exception("Service error")

        response = app_client.post(
            "/openai/chat",
            json={"prompt": "Test"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 500
        assert "Service error" in response.json()["detail"]

    def test_modulated_chat_stream_success(self, app_client, mock_openai_service):
        """Test successful streaming modulated chat."""
        response = app_client.post(
            "/openai/chat/stream",
            json={"prompt": "Stream test", "context": {}, "task": "stream"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

        # Check stream content
        content = response.text
        assert "Chunk1" in content or "Chunk2" in content or "Chunk3" in content

    def test_openai_metrics_endpoint(self, app_client, mock_openai_service):
        """Test OpenAI metrics endpoint."""
        response = app_client.get(
            "/openai/metrics",
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["requests"] == 100
        assert data["errors"] == 5

    def test_openai_metrics_no_metrics(self, app_client, mock_openai_service):
        """Test metrics endpoint when service has no metrics."""
        mock_openai_service.metrics = None

        response = app_client.get(
            "/openai/metrics",
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert response.json() == {}


class TestModelsEndpoint:
    """Test /v1/models endpoint."""

    def test_list_models_success(self, app_client):
        """Test successful model listing."""
        response = app_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "list"
        assert len(data["data"]) == 2

        # Check model entries
        models = {m["id"]: m for m in data["data"]}
        assert "lukhas-mini" in models
        assert "lukhas-embed-1" in models

        for model in data["data"]:
            assert model["object"] == "model"
            assert model["owned_by"] == "lukhas"
            assert model["created"] == 1730000000

    def test_list_models_rate_limit_headers(self, app_client):
        """Test rate limit headers are present."""
        response = app_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200

        # Check rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert "x-ratelimit-limit-requests" in response.headers
        assert "x-ratelimit-remaining-requests" in response.headers
        assert "x-ratelimit-reset-requests" in response.headers

        assert response.headers["X-RateLimit-Limit"] == "60"
        assert response.headers["X-RateLimit-Remaining"] == "59"

    def test_list_models_trace_headers(self, app_client):
        """Test trace ID headers."""
        response = app_client.get(
            "/v1/models",
            headers={
                "Authorization": "Bearer test_token",
                "X-Request-Id": "custom-request-id",
            },
        )

        assert response.status_code == 200
        assert response.headers["X-Request-Id"] == "custom-request-id"
        assert response.headers["X-Trace-Id"] == "custom-request-id"

    def test_list_models_auto_trace_id(self, app_client):
        """Test automatic trace ID generation."""
        response = app_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert "X-Request-Id" in response.headers
        assert "X-Trace-Id" in response.headers
        assert len(response.headers["X-Request-Id"]) > 0


class TestEmbeddingsEndpoint:
    """Test /v1/embeddings endpoint."""

    def test_create_embeddings_single_input(self, app_client):
        """Test embeddings with single string input."""
        response = app_client.post(
            "/v1/embeddings",
            json={"input": "Hello world", "model": "lukhas-embed-1"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "list"
        assert data["model"] == "lukhas-embed-1"
        assert len(data["data"]) == 1

        embedding = data["data"][0]
        assert embedding["object"] == "embedding"
        assert embedding["index"] == 0
        assert isinstance(embedding["embedding"], list)
        assert len(embedding["embedding"]) == 128  # Default dimension

        # Check all values are floats in [0, 1]
        for val in embedding["embedding"]:
            assert isinstance(val, float)
            assert 0 <= val <= 1

        # Check usage
        assert "usage" in data
        assert data["usage"]["prompt_tokens"] == 2  # "Hello world" = 2 words
        assert data["usage"]["total_tokens"] == 2

    def test_create_embeddings_list_input(self, app_client):
        """Test embeddings with list of strings."""
        response = app_client.post(
            "/v1/embeddings",
            json={"input": ["text one", "text two", "text three"]},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 3
        for idx, embedding in enumerate(data["data"]):
            assert embedding["index"] == idx
            assert len(embedding["embedding"]) == 128

        # Verify embeddings are different for different inputs
        emb1 = data["data"][0]["embedding"]
        emb2 = data["data"][1]["embedding"]
        assert emb1 != emb2

    def test_create_embeddings_deterministic(self, app_client):
        """Test embeddings are deterministic for same input."""
        input_text = "deterministic test"

        response1 = app_client.post(
            "/v1/embeddings",
            json={"input": input_text},
            headers={"Authorization": "Bearer test_token"},
        )

        response2 = app_client.post(
            "/v1/embeddings",
            json={"input": input_text},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        emb1 = response1.json()["data"][0]["embedding"]
        emb2 = response2.json()["data"][0]["embedding"]

        assert emb1 == emb2

    def test_create_embeddings_model_prefix(self, app_client):
        """Test embeddings include model in hash calculation."""
        input_text = "same text"

        response1 = app_client.post(
            "/v1/embeddings",
            json={"input": input_text, "model": "model-a"},
            headers={"Authorization": "Bearer test_token"},
        )

        response2 = app_client.post(
            "/v1/embeddings",
            json={"input": input_text, "model": "model-b"},
            headers={"Authorization": "Bearer test_token"},
        )

        emb1 = response1.json()["data"][0]["embedding"]
        emb2 = response2.json()["data"][0]["embedding"]

        # Different models should produce different embeddings
        assert emb1 != emb2

    def test_create_embeddings_empty_input_error(self, app_client):
        """Test error on empty input."""
        response = app_client.post(
            "/v1/embeddings",
            json={"input": ""},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 400
        error = response.json()["detail"]["error"]
        assert error["type"] == "invalid_request_error"
        assert "input" in error["message"]
        assert error["param"] == "input"

    def test_create_embeddings_empty_list_error(self, app_client):
        """Test error on empty list."""
        response = app_client.post(
            "/v1/embeddings",
            json={"input": []},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 400

    def test_create_embeddings_whitespace_only_error(self, app_client):
        """Test error on whitespace-only input."""
        response = app_client.post(
            "/v1/embeddings",
            json={"input": ["  ", "   \t  "]},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 400

    def test_create_embeddings_default_model(self, app_client):
        """Test default model is used when not specified."""
        response = app_client.post(
            "/v1/embeddings",
            json={"input": "test"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert response.json()["model"] == "lukhas-embed-1"


class TestResponsesEndpoint:
    """Test /v1/responses endpoint."""

    def test_create_response_success(self, app_client):
        """Test successful response creation."""
        response = app_client.post(
            "/v1/responses",
            json={"input": "Hello world", "model": "lukhas-mini"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["object"] == "response"
        assert data["model"] == "lukhas-mini"
        assert data["id"].startswith("resp_")
        assert data["created"] > 0

        # Check output
        assert len(data["output"]) == 1
        output = data["output"][0]
        assert output["type"] == "output_text"
        assert output["text"] == "echo: Hello world"

        # Check usage
        assert "usage" in data
        assert data["usage"]["input_tokens"] == 2
        assert data["usage"]["output_tokens"] == 3  # "echo: Hello world"
        assert data["usage"]["total_tokens"] == 5

    def test_create_response_with_messages(self, app_client):
        """Test response creation with messages format."""
        response = app_client.post(
            "/v1/responses",
            json={
                "messages": [
                    {
                        "content": [
                            {"type": "input_text", "text": "Test message"},
                        ]
                    }
                ]
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "echo: Test message" in data["output"][0]["text"]

    def test_create_response_empty_input_error(self, app_client):
        """Test error on empty input."""
        response = app_client.post(
            "/v1/responses",
            json={"input": ""},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 400
        error = response.json()["detail"]["error"]
        assert error["type"] == "invalid_request_error"
        assert "input" in error["message"]

    def test_create_response_missing_input_error(self, app_client):
        """Test error when input is missing."""
        response = app_client.post(
            "/v1/responses",
            json={"model": "lukhas-mini"},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 400

    def test_create_response_streaming(self, app_client):
        """Test streaming response."""
        response = app_client.post(
            "/v1/responses",
            json={"input": "Stream test", "stream": True},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Parse SSE chunks
        content = response.text
        assert "data: " in content
        assert "data: [DONE]" in content

    def test_create_response_streaming_chunks(self, app_client):
        """Test streaming response chunk structure."""
        response = app_client.post(
            "/v1/responses",
            json={"input": "Test", "stream": True, "max_tokens": 100},
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200

        # Parse chunks
        chunks = [line for line in response.text.split("\n") if line.startswith("data: ")]

        # Should have multiple chunks plus DONE
        assert len(chunks) > 1
        assert chunks[-1] == "data: [DONE]"

        # Check data chunks
        for chunk_line in chunks[:-1]:
            chunk_data = chunk_line[6:]  # Remove "data: " prefix
            assert len(chunk_data) > 0

    def test_create_response_streaming_heavy_request(self, app_client):
        """Test streaming with heavy request parameters."""
        response = app_client.post(
            "/v1/responses",
            json={
                "input": "A" * 250,  # Long input
                "stream": True,
                "max_tokens": 2000,  # High token count
            },
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200

        # Heavy requests should have more chunks
        chunks = [line for line in response.text.split("\n") if line.startswith("data: ")]
        assert len(chunks) >= 12  # Should use more chunks for heavy requests

    def test_create_response_trace_headers_streaming(self, app_client):
        """Test trace headers are set for streaming responses."""
        response = app_client.post(
            "/v1/responses",
            json={"input": "Test", "stream": True},
            headers={
                "Authorization": "Bearer test_token",
                "X-Request-Id": "test-trace-123",
            },
        )

        assert response.status_code == 200
        assert response.headers["X-Request-Id"] == "test-trace-123"
        assert response.headers["X-Trace-Id"] == "test-trace-123"


class TestAuthenticationAndHeaders:
    """Test authentication and header handling."""

    def test_require_api_key_with_bearer(self, mock_bearer_auth):
        """Test API key requirement with Bearer token."""
        from serve.openai_routes import require_api_key

        result = require_api_key(
            authorization="Bearer test_token",
            x_lukhas_project="test_project",
        )

        assert result["sub"] == "test_user"
        assert "api.read" in result["scopes"]

        # Verify require_bearer was called correctly
        mock_bearer_auth.assert_called_once()
        call_kwargs = mock_bearer_auth.call_args.kwargs
        assert call_kwargs["authorization"] == "Bearer test_token"
        assert call_kwargs["required_scopes"] == ("api.read",)
        assert call_kwargs["project_id"] == "test_project"

    def test_rate_limit_headers_generation(self):
        """Test rate limit headers generation."""
        from serve.openai_routes import _rl_headers

        headers = _rl_headers()

        assert headers["X-RateLimit-Limit"] == "60"
        assert headers["X-RateLimit-Remaining"] == "59"
        assert "X-RateLimit-Reset" in headers
        assert headers["x-ratelimit-limit-requests"] == "60"
        assert headers["x-ratelimit-remaining-requests"] == "59"
        assert "x-ratelimit-reset-requests" in headers

    def test_with_std_headers(self):
        """Test standard headers application."""
        from serve.openai_routes import _with_std_headers
        from fastapi import Response

        response = Response()
        _with_std_headers(response, "test-trace-123")

        assert response.headers["X-Request-Id"] == "test-trace-123"
        assert response.headers["X-Trace-Id"] == "test-trace-123"
        assert response.headers["X-RateLimit-Limit"] == "60"

    def test_with_std_headers_auto_trace(self):
        """Test automatic trace ID generation in headers."""
        from serve.openai_routes import _with_std_headers
        from fastapi import Response

        response = Response()
        _with_std_headers(response, None)

        assert "X-Request-Id" in response.headers
        assert "X-Trace-Id" in response.headers
        assert response.headers["X-Request-Id"] == response.headers["X-Trace-Id"]


class TestHashEmbeddings:
    """Test hash-based embedding generation."""

    def test_hash_to_vec_basic(self):
        """Test basic hash to vector conversion."""
        from serve.openai_routes import _hash_to_vec

        vec = _hash_to_vec("test", dim=128)

        assert len(vec) == 128
        assert all(isinstance(v, float) for v in vec)
        assert all(0 <= v <= 1 for v in vec)

    def test_hash_to_vec_custom_dimension(self):
        """Test custom dimension."""
        from serve.openai_routes import _hash_to_vec

        vec = _hash_to_vec("test", dim=256)
        assert len(vec) == 256

        vec = _hash_to_vec("test", dim=64)
        assert len(vec) == 64

    def test_hash_to_vec_deterministic(self):
        """Test deterministic output."""
        from serve.openai_routes import _hash_to_vec

        vec1 = _hash_to_vec("same input", dim=128)
        vec2 = _hash_to_vec("same input", dim=128)

        assert vec1 == vec2

    def test_hash_to_vec_unique(self):
        """Test different inputs produce different vectors."""
        from serve.openai_routes import _hash_to_vec

        vec1 = _hash_to_vec("input A", dim=128)
        vec2 = _hash_to_vec("input B", dim=128)

        assert vec1 != vec2


class TestStreamingHelpers:
    """Test streaming response helpers."""

    def test_resolve_stream_plan_light(self):
        """Test stream plan for light requests."""
        from serve.openai_routes import _resolve_stream_plan

        plan = _resolve_stream_plan("short text", max_tokens=100)

        assert plan["chunk_count"] == 6
        assert plan["per_chunk_bytes"] >= 64
        assert plan["heavy"] is False

    def test_resolve_stream_plan_heavy_tokens(self):
        """Test stream plan for heavy token request."""
        from serve.openai_routes import _resolve_stream_plan

        plan = _resolve_stream_plan("text", max_tokens=2000)

        assert plan["chunk_count"] == 12
        assert plan["heavy"] is True

    def test_resolve_stream_plan_heavy_text(self):
        """Test stream plan for long text."""
        from serve.openai_routes import _resolve_stream_plan

        long_text = "word " * 100  # 200+ chars
        plan = _resolve_stream_plan(long_text, max_tokens=100)

        assert plan["chunk_count"] == 12
        assert plan["heavy"] is True

    def test_stream_chunks_generation(self):
        """Test chunk generation."""
        from serve.openai_routes import _stream_chunks

        plan = {"chunk_count": 3, "per_chunk_bytes": 50}
        chunks = _stream_chunks("test content", plan)

        assert len(chunks) == 3
        for idx, chunk in enumerate(chunks):
            assert f"chunk-{idx}:" in chunk
            assert len(chunk) <= 50

    def test_stream_chunks_empty_text(self):
        """Test chunk generation with empty text."""
        from serve.openai_routes import _stream_chunks

        plan = {"chunk_count": 2, "per_chunk_bytes": 40}
        chunks = _stream_chunks("", plan)

        assert len(chunks) == 2
        # Should use "symbolic stream" as fallback
        assert all("symbolic stream" in chunk for chunk in chunks)


class TestErrorHelpers:
    """Test error response helpers."""

    def test_invalid_request_basic(self):
        """Test basic invalid request error."""
        from serve.openai_routes import _invalid_request

        error = _invalid_request("Test error message")

        assert error["error"]["type"] == "invalid_request_error"
        assert error["error"]["message"] == "Test error message"
        assert error["error"]["code"] == "invalid_request_error"
        assert "param" not in error["error"]

    def test_invalid_request_with_param(self):
        """Test invalid request error with parameter."""
        from serve.openai_routes import _invalid_request

        error = _invalid_request("Invalid value", param="input")

        assert error["error"]["param"] == "input"
        assert error["error"]["message"] == "Invalid value"


class TestServiceDependency:
    """Test service dependency injection."""

    def test_get_service(self):
        """Test get_service returns OpenAIModulatedService."""
        from serve.openai_routes import get_service

        with patch("serve.openai_routes.OpenAIModulatedService") as mock_service:
            mock_instance = MagicMock()
            mock_service.return_value = mock_instance

            service = get_service()

            assert service == mock_instance
            mock_service.assert_called_once()


class TestRouterConfiguration:
    """Test router configuration and exports."""

    def test_router_exports(self):
        """Test router is properly exported."""
        from serve import openai_routes

        assert hasattr(openai_routes, "router")
        assert "router" in openai_routes.__all__

    def test_router_includes_v1(self):
        """Test router includes v1 routes."""
        from serve.openai_routes import router

        # Check that routes are included
        route_paths = [route.path for route in router.routes]

        assert "/v1/models" in route_paths
        assert "/v1/embeddings" in route_paths
        assert "/v1/responses" in route_paths

    def test_router_includes_legacy(self):
        """Test router includes legacy routes."""
        from serve.openai_routes import router

        route_paths = [route.path for route in router.routes]

        assert "/openai/chat" in route_paths
        assert "/openai/chat/stream" in route_paths
        assert "/openai/metrics" in route_paths

    def test_router_tags(self):
        """Test router has correct tags."""
        from serve.openai_routes import router

        assert "openai" in router.tags
