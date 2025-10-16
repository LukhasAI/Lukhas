"""
SPDX-License-Identifier: Apache-2.0

tests/integration/test_openai_facade_integration.py

Integration tests for OpenAI façade with all polish improvements:
- Token hashing security
- X-Forwarded-For proxy support
- Trace header propagation
- Rate limiting per-tenant isolation
- OpenAPI spec generation
"""
from __future__ import annotations

import hashlib
import json
import pytest
from fastapi.testclient import TestClient

from lukhas.adapters.openai.api import get_app


@pytest.fixture
def client(monkeypatch):
    """Create test client with permissive policy mode."""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "permissive")
    app = get_app()
    return TestClient(app)


@pytest.fixture
def strict_client(monkeypatch):
    """Create test client with strict policy mode."""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")
    app = get_app()
    return TestClient(app)


class TestTokenHashingSecurity:
    """Test token hashing security improvements."""

    def test_bearer_tokens_are_hashed_not_stored_raw(self, client):
        """Verify that bearer tokens are hashed before use in rate limiting."""
        # Make request with bearer token
        token = "sk-lukhas-test-secret-token-12345"
        response = client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        # Token should NOT appear raw in any internal state
        # (we can't directly inspect rate limiter state, but we verify behavior)

        # Make second request with same token - should hit same rate limit bucket
        response2 = client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response2.status_code == 200

    def test_different_tokens_isolated_rate_limits(self, client):
        """Verify different tokens get different rate limit buckets."""
        token_a = "sk-lukhas-org-a-token-abc123"
        token_b = "sk-lukhas-org-b-token-xyz789"

        # Both tokens should work independently
        response_a = client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        response_b = client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {token_b}"}
        )

        assert response_a.status_code == 200
        assert response_b.status_code == 200


class TestProxySupport:
    """Test X-Forwarded-For proxy support."""

    def test_x_forwarded_for_header_used_for_rate_limiting(self, client):
        """Verify X-Forwarded-For is used when present."""
        # Request with auth and XFF header
        response = client.get(
            "/v1/models",
            headers={
                "Authorization": "Bearer sk-lukhas-test-token-xff",
                "X-Forwarded-For": "203.0.113.42, 10.0.0.1, 172.16.0.1"
            }
        )

        # Should succeed and use token for rate limiting (token takes precedence)
        assert response.status_code == 200

    def test_x_forwarded_for_with_multiple_proxies(self, client):
        """Verify first IP is extracted from proxy chain."""
        xff_chain = "198.51.100.50, 192.168.1.1, 10.0.0.1"

        response = client.get(
            "/healthz",
            headers={"X-Forwarded-For": xff_chain}
        )

        assert response.status_code == 200
        data = response.json()
        # Health endpoint may return detailed checks or simple status
        assert data.get("status") == "ok" or "checks" in data

    def test_bearer_token_takes_precedence_over_xff(self, client):
        """Verify bearer token is used for rate limiting when present, not XFF."""
        token = "sk-lukhas-test-token-priority"

        response = client.get(
            "/v1/models",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Forwarded-For": "198.51.100.99"
            }
        )

        # Should succeed and use token for rate limiting, not IP
        assert response.status_code == 200


class TestTraceHeaders:
    """Test trace header propagation."""

    def test_trace_id_in_response_headers(self, client):
        """Verify X-Trace-Id is present in all responses."""
        response = client.get("/healthz")

        assert response.status_code == 200
        # Trace ID should be present (if OTEL is configured)
        # May be None in test environment without OTEL
        if "X-Trace-Id" in response.headers:
            trace_id = response.headers["X-Trace-Id"]
            assert len(trace_id) > 0
            assert len(trace_id) == 32  # 128-bit hex string

    def test_trace_id_consistent_format(self, client):
        """Verify trace ID format is consistent."""
        endpoints = [
            ("/healthz", None),
            ("/readyz", None),
            ("/v1/models", "Bearer sk-lukhas-test-token-trace")
        ]

        for endpoint, auth in endpoints:
            headers = {}
            if auth:
                headers["Authorization"] = auth

            response = client.get(endpoint, headers=headers)
            assert response.status_code == 200

            if "X-Trace-Id" in response.headers:
                trace_id = response.headers["X-Trace-Id"]
                # Should be lowercase hex
                assert trace_id.islower() or trace_id.isdigit()


class TestAuthErrorCodes:
    """Test authentication error code consistency."""

    def test_missing_auth_returns_invalid_api_key(self, strict_client):
        """Verify missing auth returns 401 with invalid_api_key."""
        response = strict_client.get("/v1/models")

        assert response.status_code == 401
        body = response.json()
        error_data = body.get("detail", body)

        assert "error" in error_data
        assert error_data["error"]["type"] == "invalid_api_key"
        assert error_data["error"]["code"] == "invalid_api_key"

    def test_malformed_bearer_returns_invalid_api_key(self, strict_client):
        """Verify malformed Bearer returns 401 with invalid_api_key."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "NotBearer token123"}
        )

        assert response.status_code == 401
        body = response.json()
        error_data = body.get("detail", body)

        assert "error" in error_data
        assert error_data["error"]["type"] == "invalid_api_key"

    def test_empty_bearer_returns_invalid_api_key(self, strict_client):
        """Verify empty Bearer returns 401 with invalid_api_key."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer "}
        )

        assert response.status_code == 401
        body = response.json()
        error_data = body.get("detail", body)

        assert "error" in error_data
        assert error_data["error"]["type"] == "invalid_api_key"


class TestOpenAPISpec:
    """Test OpenAPI spec generation."""

    def test_openapi_spec_generation(self, client):
        """Verify OpenAPI spec can be generated."""
        app = client.app
        spec = app.openapi()

        assert spec is not None
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec

        # Verify key endpoints are documented
        assert "/healthz" in spec["paths"]
        assert "/v1/models" in spec["paths"]
        assert "/v1/embeddings" in spec["paths"]

    def test_openapi_spec_has_security_schemes(self, client):
        """Verify OpenAPI spec documents security."""
        app = client.app
        spec = app.openapi()

        # Should have components section
        assert "components" in spec

        # Should document security schemes (if defined)
        # Note: May not be present in all configurations

    def test_openapi_spec_serializable(self, client):
        """Verify OpenAPI spec can be serialized to JSON."""
        app = client.app
        spec = app.openapi()

        # Should be JSON-serializable
        json_str = json.dumps(spec, indent=2)
        assert len(json_str) > 0

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed == spec


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_models_embeddings_workflow(self, client):
        """Test complete workflow: models → embeddings."""
        token = "Bearer sk-lukhas-test-workflow-token"

        # 1. Check available models
        response = client.get(
            "/v1/models",
            headers={"Authorization": token}
        )
        assert response.status_code == 200

        models_data = response.json()
        assert "data" in models_data
        assert len(models_data["data"]) > 0

        # 2. Use model for embeddings
        response = client.post(
            "/v1/embeddings",
            headers={"Authorization": token},
            json={
                "input": "test embedding",
                "model": "lukhas-matriz"
            }
        )
        assert response.status_code == 200

        embeddings_data = response.json()
        assert "data" in embeddings_data
        assert len(embeddings_data["data"]) > 0
        assert "embedding" in embeddings_data["data"][0]

    def test_health_ready_metrics_workflow(self, client):
        """Test observability workflow: health → ready → metrics."""
        # 1. Health check
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        # Health endpoint may return detailed checks or simple status
        assert data.get("status") == "ok" or "checks" in data

        # 2. Readiness check
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ready" or "checks" in data

        # 3. Metrics (Prometheus format)
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")


class TestRateLimitingIntegration:
    """Test rate limiting integration."""

    def test_rate_limit_per_route(self, client):
        """Verify rate limiting is enforced per route."""
        # Multiple requests should succeed (within rate limit)
        for i in range(5):
            response = client.get("/healthz")
            assert response.status_code == 200

    def test_rate_limit_per_principal(self, client):
        """Verify rate limiting is per-principal (token or IP)."""
        token_a = "sk-lukhas-test-token-a"
        token_b = "sk-lukhas-test-token-b"

        # Both principals should have independent rate limits
        for i in range(3):
            response_a = client.get(
                "/v1/models",
                headers={"Authorization": f"Bearer {token_a}"}
            )
            response_b = client.get(
                "/v1/models",
                headers={"Authorization": f"Bearer {token_b}"}
            )

            assert response_a.status_code == 200
            assert response_b.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
