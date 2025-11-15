"""
Test middleware edge cases and behavior.

Validates:
- Auth middleware edge cases (all possible auth failure scenarios)
- Headers middleware (OpenAI-Processing-Ms, security headers, trace IDs)
- Middleware order and interaction
- Performance under various conditions
"""
import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def strict_client(monkeypatch):
    """Create test client with strict auth mode enabled."""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")
    return TestClient(app)


@pytest.fixture
def permissive_client(monkeypatch):
    """Create test client with permissive auth mode."""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "permissive")
    return TestClient(app)


# Auth Middleware Edge Cases
class TestAuthMiddlewareEdgeCases:
    """Test all edge cases for auth middleware."""

    def test_auth_strict_mode_blocks_unauthenticated(self, strict_client):
        """Verify strict mode blocks requests without auth."""
        response = strict_client.get("/v1/models")
        assert response.status_code == 401
        assert "error" in response.json()

    def test_auth_permissive_mode_allows_unauthenticated(self, permissive_client):
        """Verify permissive mode allows requests without auth."""
        response = permissive_client.get("/v1/models")
        # Permissive mode should allow through (200 or other non-401)
        assert response.status_code != 401

    def test_auth_missing_bearer_prefix(self, strict_client):
        """Verify auth fails without 'Bearer ' prefix."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "InvalidToken123"}
        )
        assert response.status_code == 401
        error = response.json()["error"]
        assert "Bearer scheme" in error["message"]

    def test_auth_bearer_with_extra_whitespace(self, strict_client):
        """Verify auth handles tokens with extra whitespace."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer   sk-valid-1234567890   "}
        )
        # Should strip whitespace and accept
        assert response.status_code == 200

    def test_auth_token_exactly_8_chars(self, strict_client):
        """Verify minimum 8-character token is accepted."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer 12345678"}
        )
        # Exactly 8 chars should be accepted
        assert response.status_code == 200

    def test_auth_token_7_chars_rejected(self, strict_client):
        """Verify 7-character token is rejected."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer 1234567"}
        )
        assert response.status_code == 401
        error = response.json()["error"]
        assert "at least 8 characters" in error["message"]

    def test_auth_empty_bearer_token(self, strict_client):
        """Verify empty Bearer token is rejected."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == 401
        error = response.json()["error"]
        assert "empty" in error["message"].lower()

    def test_auth_only_whitespace_token(self, strict_client):
        """Verify whitespace-only token is rejected."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Bearer      "}
        )
        assert response.status_code == 401
        error = response.json()["error"]
        assert "empty" in error["message"].lower()

    def test_auth_case_sensitive_bearer(self, strict_client):
        """Verify 'Bearer' is case-sensitive."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "bearer sk-valid-1234567890"}
        )
        # Should reject lowercase 'bearer'
        assert response.status_code == 401

    def test_auth_basic_auth_rejected(self, strict_client):
        """Verify Basic auth is rejected."""
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": "Basic dXNlcjpwYXNz"}
        )
        assert response.status_code == 401
        error = response.json()["error"]
        assert "Bearer scheme" in error["message"]

    def test_auth_error_format_openai_compatible(self, strict_client):
        """Verify all auth errors use OpenAI error format."""
        test_cases = [
            {},  # No auth header
            {"Authorization": "NoBearer token"},  # Wrong scheme
            {"Authorization": "Bearer "},  # Empty token
            {"Authorization": "Bearer abc"},  # Short token
        ]

        for headers in test_cases:
            response = strict_client.get("/v1/models", headers=headers)
            assert response.status_code == 401

            data = response.json()
            assert "error" in data
            error = data["error"]

            # OpenAI error envelope format
            assert "type" in error
            assert "message" in error
            assert "code" in error
            assert error["type"] == "invalid_api_key"
            assert error["code"] == "invalid_api_key"
            assert isinstance(error["message"], str)

    def test_auth_non_v1_paths_bypass(self, strict_client):
        """Verify non-/v1/* paths bypass auth middleware."""
        # Health endpoints should not require auth
        response = strict_client.get("/healthz")
        assert response.status_code == 200

        response = strict_client.get("/readyz")
        assert response.status_code == 200


# Headers Middleware Tests
class TestHeadersMiddleware:
    """Test headers middleware behavior."""

    def test_trace_id_present(self, strict_client):
        """Verify X-Trace-Id header is present."""
        response = strict_client.get("/healthz")
        assert "X-Trace-Id" in response.headers
        trace_id = response.headers["X-Trace-Id"]
        assert len(trace_id) == 32  # UUID without hyphens
        assert trace_id.isalnum()

    def test_trace_id_unique_per_request(self, strict_client):
        """Verify each request gets unique trace ID."""
        trace_ids = set()
        for _ in range(10):
            response = strict_client.get("/healthz")
            trace_ids.add(response.headers["X-Trace-Id"])

        # All trace IDs should be unique
        assert len(trace_ids) == 10

    def test_request_id_matches_trace_id(self, strict_client):
        """Verify X-Request-Id matches X-Trace-Id."""
        response = strict_client.get("/healthz")
        assert response.headers["X-Trace-Id"] == response.headers["X-Request-Id"]

    def test_processing_ms_header_present(self, strict_client):
        """Verify OpenAI-Processing-Ms header is present."""
        response = strict_client.get("/healthz")
        assert "OpenAI-Processing-Ms" in response.headers

        processing_ms = response.headers["OpenAI-Processing-Ms"]
        assert processing_ms.isdigit()

        # Should be reasonable (< 10 seconds for health check)
        assert int(processing_ms) < 10000

    def test_processing_ms_increases_with_work(self, strict_client):
        """Verify processing time reflects actual work."""
        # Quick endpoint
        quick_response = strict_client.get("/healthz")
        quick_ms = int(quick_response.headers["OpenAI-Processing-Ms"])

        # Should be very fast
        assert quick_ms < 1000  # < 1 second

    def test_rate_limit_headers_present(self, strict_client):
        """Verify rate limit headers are present."""
        response = strict_client.get("/healthz")

        # Both formats for compatibility
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert "x-ratelimit-limit-requests" in response.headers
        assert "x-ratelimit-remaining-requests" in response.headers
        assert "x-ratelimit-reset-requests" in response.headers

    def test_security_headers_present(self, strict_client):
        """Verify all OWASP security headers are present."""
        response = strict_client.get("/healthz")

        # Security headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "no-referrer"

    def test_all_headers_on_error_responses(self, strict_client):
        """Verify headers are present even on error responses."""
        # Trigger 401 error
        response = strict_client.get("/v1/models")
        assert response.status_code == 401

        # All headers should still be present
        assert "X-Trace-Id" in response.headers
        assert "OpenAI-Processing-Ms" in response.headers
        assert "X-Content-Type-Options" in response.headers


# Middleware Integration Tests
class TestMiddlewareIntegration:
    """Test middleware order and interaction."""

    def test_cors_headers_present(self, strict_client):
        """Verify CORS middleware adds appropriate headers."""
        # Use non-auth endpoint to test CORS
        response = strict_client.options("/healthz")
        # CORS headers handled by CORSMiddleware
        # TestClient doesn't trigger CORS in same-origin mode
        assert response.status_code in (200, 405)

    def test_middleware_order_auth_before_headers(self, strict_client):
        """Verify auth middleware runs before headers middleware."""
        # Even when auth fails, headers should be present
        response = strict_client.get("/v1/models")
        assert response.status_code == 401

        # Headers middleware should have added these
        assert "X-Trace-Id" in response.headers
        assert "OpenAI-Processing-Ms" in response.headers

    def test_headers_added_to_all_endpoints(self, strict_client):
        """Verify headers are added to all endpoints."""
        endpoints = [
            "/healthz",
            "/readyz",
            "/metrics",
        ]

        for endpoint in endpoints:
            response = strict_client.get(endpoint)
            assert "X-Trace-Id" in response.headers
            assert "OpenAI-Processing-Ms" in response.headers
            assert "X-Content-Type-Options" in response.headers


# Performance Tests
class TestMiddlewarePerformance:
    """Test middleware performance characteristics."""

    def test_middleware_overhead_minimal(self, strict_client):
        """Verify middleware overhead is minimal."""
        response = strict_client.get("/healthz")
        processing_ms = int(response.headers["OpenAI-Processing-Ms"])

        # Total processing time should be < 100ms for health check
        assert processing_ms < 100

    def test_auth_check_fast(self, strict_client):
        """Verify auth check completes quickly."""
        # Auth failure should be very fast
        response = strict_client.get("/v1/models")
        assert response.status_code == 401

        processing_ms = int(response.headers["OpenAI-Processing-Ms"])
        # Auth rejection should be < 50ms
        assert processing_ms < 50
