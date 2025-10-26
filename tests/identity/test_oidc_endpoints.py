#!/usr/bin/env python3
"""
LUKHAS OIDC Endpoints Test Suite
T4/0.01% Excellence Standard

Comprehensive test suite for production-ready OIDC/OAuth2 endpoints.
Tests security, performance, validation, and compliance.
"""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import modules to test
from api.oidc import get_correlation_id, router, security_check_dependency
from identity.security_hardening import SecurityAction


@pytest.fixture
def app():
    """Create test FastAPI app"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_security_dependency():
    """Mock security dependency"""
    return {
        "correlation_id": "test-correlation-123",
        "client_ip": "127.0.0.1",
        "security_report": {"action": "allow"},
        "action": SecurityAction.ALLOW
    }


@pytest.fixture
def mock_oidc_provider():
    """Mock OIDC provider"""
    provider = Mock()
    provider.get_discovery_document.return_value = {
        "issuer": "https://test.ai",
        "authorization_endpoint": "https://test.ai/oauth2/authorize",
        "token_endpoint": "https://test.ai/oauth2/token",
        "userinfo_endpoint": "https://test.ai/oauth2/userinfo",
        "jwks_uri": "https://test.ai/.well-known/jwks.json"
    }
    provider.get_jwks.return_value = {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key-1",
                "use": "sig",
                "n": "test-n-value",
                "e": "AQAB"
            }
        ]
    }
    return provider


class TestOIDCDiscoveryEndpoint:
    """Test OIDC Discovery endpoint"""

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.get_oidc_provider')
    @patch('api.oidc.rate_limiter')
    def test_discovery_success(
        self, mock_rate_limiter, mock_provider_dep, mock_security_dep, client
    ):
        """Test successful discovery document retrieval"""
        # Setup mocks
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_provider = Mock()
        mock_provider.get_discovery_document.return_value = {
            "issuer": "https://test.ai",
            "authorization_endpoint": "https://test.ai/oauth2/authorize"
        }
        mock_provider_dep.return_value = mock_provider

        mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 9})

        # Make request
        response = client.get("/.well-known/openid-configuration")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["issuer"] == "https://test.ai"
        assert "lukhas_version" in data
        assert data["tier_authentication_supported"] is True
        assert data["webauthn_supported"] is True

        # Check security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "Cache-Control" in response.headers

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.rate_limiter')
    def test_discovery_rate_limited(self, mock_rate_limiter, mock_security_dep, client):
        """Test discovery endpoint rate limiting"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_rate_limiter.check_rate_limit.return_value = (
            False, {"retry_after": 60, "error": "rate_limit_exceeded"}
        )

        response = client.get("/.well-known/openid-configuration")

        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "60"

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.get_oidc_provider')
    @patch('api.oidc.rate_limiter')
    def test_discovery_server_error(
        self, mock_rate_limiter, mock_provider_dep, mock_security_dep, client
    ):
        """Test discovery endpoint server error handling"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_provider = Mock()
        mock_provider.get_discovery_document.side_effect = Exception("Database error")
        mock_provider_dep.return_value = mock_provider

        mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 9})

        response = client.get("/.well-known/openid-configuration")

        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "server_error"
        assert "correlation_id" in data


class TestJWKSEndpoint:
    """Test JWKS endpoint"""

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.get_oidc_provider')
    @patch('api.oidc.jwks_cache')
    @patch('api.oidc.rate_limiter')
    def test_jwks_cache_hit(
        self, mock_rate_limiter, mock_cache, mock_provider_dep, mock_security_dep, client
    ):
        """Test JWKS endpoint with cache hit"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 4})

        # Mock cache hit
        cached_jwks = {
            "keys": [
                {"kty": "RSA", "kid": "cached-key", "use": "sig"}
            ]
        }
        mock_cache.get.return_value = (cached_jwks, True)  # Cache hit

        response = client.get("/.well-known/jwks.json")

        assert response.status_code == 200
        data = response.json()
        assert len(data["keys"]) == 1
        assert data["keys"][0]["kid"] == "cached-key"

        # Verify cache was checked but provider wasn't called
        mock_cache.get.assert_called_once()
        mock_provider_dep.assert_not_called()

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.get_oidc_provider')
    @patch('api.oidc.jwks_cache')
    @patch('api.oidc.rate_limiter')
    def test_jwks_cache_miss(
        self, mock_rate_limiter, mock_cache, mock_provider_dep, mock_security_dep, client
    ):
        """Test JWKS endpoint with cache miss"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 4})

        # Mock cache miss
        mock_cache.get.return_value = (None, False)

        # Mock provider response
        provider_jwks = {
            "keys": [
                {"kty": "RSA", "kid": "provider-key", "use": "sig"}
            ]
        }
        mock_provider = Mock()
        mock_provider.get_jwks.return_value = provider_jwks
        mock_provider_dep.return_value = mock_provider

        response = client.get("/.well-known/jwks.json")

        assert response.status_code == 200
        data = response.json()
        assert len(data["keys"]) == 1
        assert data["keys"][0]["kid"] == "provider-key"

        # Verify cache miss handling
        mock_cache.get.assert_called_once()
        mock_cache.put.assert_called_once()
        mock_provider.get_jwks.assert_called_once()

    def test_jwks_cors_headers(self, client):
        """Test JWKS CORS headers for cross-origin access"""
        with patch('api.oidc.security_check_dependency') as mock_security_dep, \
             patch('api.oidc.jwks_cache') as mock_cache, \
             patch('api.oidc.rate_limiter') as mock_rate_limiter:

            mock_security_dep.return_value = {
                "correlation_id": "test-123",
                "client_ip": "127.0.0.1",
                "security_report": {},
                "action": SecurityAction.ALLOW
            }

            mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 4})
            mock_cache.get.return_value = ({"keys": []}, True)

            response = client.get("/.well-known/jwks.json")

            assert response.status_code == 200
            assert response.headers["Access-Control-Allow-Origin"] == "*"
            assert "Access-Control-Allow-Methods" in response.headers


class TestAuthorizationEndpoint:
    """Test Authorization endpoint"""

    def test_authorization_request_validation(self, client):
        """Test authorization request parameter validation"""
        with patch('api.oidc.security_check_dependency') as mock_security_dep:
            mock_security_dep.return_value = {
                "correlation_id": "test-123",
                "client_ip": "127.0.0.1",
                "security_report": {},
                "action": SecurityAction.ALLOW
            }

            # Invalid request - missing required parameters
            response = client.get("/authorize")
            assert response.status_code == 400

            # Invalid redirect URI
            response = client.get("/authorize?client_id=test&response_type=code&redirect_uri=invalid_uri&scope=openid")
            assert response.status_code == 400

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.get_oidc_provider')
    @patch('api.oidc.get_current_user')
    @patch('api.oidc.rate_limiter')
    def test_authorization_success_redirect(
        self, mock_rate_limiter, mock_get_user, mock_provider_dep, mock_security_dep, client
    ):
        """Test successful authorization with redirect"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 29})

        mock_get_user.return_value = {
            "user_id": "test_user",
            "authenticated": True,
            "auth_tier": "T2"
        }

        mock_provider = Mock()
        mock_provider.handle_authorization_request.return_value = {
            "action": "redirect",
            "redirect_url": "https://client.example.com/callback?code=test_code&state=test_state"
        }
        mock_provider_dep.return_value = mock_provider

        # Valid authorization request
        params = {
            "client_id": "test_client",
            "response_type": "code",
            "redirect_uri": "https://client.example.com/callback",
            "scope": "openid profile",
            "state": "test_state"
        }

        response = client.get("/authorize", params=params)

        assert response.status_code == 302
        assert "client.example.com" in response.headers["location"]

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.rate_limiter')
    def test_authorization_rate_limited(self, mock_rate_limiter, mock_security_dep, client):
        """Test authorization endpoint rate limiting"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_rate_limiter.check_rate_limit.return_value = (
            False, {"retry_after": 60, "error": "rate_limit_exceeded"}
        )

        params = {
            "client_id": "test_client",
            "response_type": "code",
            "redirect_uri": "https://client.example.com/callback",
            "scope": "openid",
            "state": "test_state"
        }

        response = client.get("/authorize", params=params)

        # Should redirect with error
        assert response.status_code == 302
        location = response.headers["location"]
        assert "error=access_denied" in location
        assert "state=test_state" in location


class TestSecurityFeatures:
    """Test security features across endpoints"""

    def test_correlation_id_generation(self):
        """Test correlation ID generation"""
        from unittest.mock import Mock

        from fastapi import Request

        # Test with provided correlation ID
        request = Mock(spec=Request)
        request.headers = {"X-Correlation-ID": "user-provided-123"}

        async def test_func():
            return await get_correlation_id(request)

        correlation_id = asyncio.run(test_func())
        assert correlation_id == "user-provided-123"

        # Test with no correlation ID (should generate one)
        request.headers = {}
        correlation_id = asyncio.run(test_func())
        assert correlation_id is not None
        assert len(correlation_id) > 0

    @patch('api.oidc.security_manager')
    def test_security_check_dependency_block(self, mock_security_manager):
        """Test security check that blocks request"""
        from unittest.mock import Mock

        from fastapi import HTTPException, Request

        mock_security_manager.comprehensive_security_check.return_value = (
            SecurityAction.BLOCK,
            {
                "threats_detected": ["suspicious_user_agent"],
                "request_analysis": {"threat_level": "high"}
            }
        )

        request = Mock(spec=Request)
        request.client.host = "192.168.1.100"
        request.headers = {"User-Agent": "AttackBot/1.0"}
        request.url.path = "/test"

        async def test_func():
            return await security_check_dependency(request)

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(test_func())

        assert exc_info.value.status_code == 429
        assert "access_denied" in str(exc_info.value.detail)

    def test_cors_headers_production_domain(self):
        """Test CORS headers for production domains"""
        from unittest.mock import Mock

        from fastapi import Request

        request = Mock(spec=Request)
        request.headers = {"Origin": "https://app.ai"}

        headers = {}
        from api.oidc import _add_cors_headers
        result = _add_cors_headers(headers, request)

        assert "Access-Control-Allow-Origin" in result
        assert result["Access-Control-Allow-Origin"] == "https://app.ai"
        assert result["Access-Control-Allow-Credentials"] == "true"

    def test_cors_headers_invalid_domain(self):
        """Test CORS headers for invalid domains"""
        from unittest.mock import Mock

        from fastapi import Request

        request = Mock(spec=Request)
        request.headers = {"Origin": "https://evil.example.com"}

        headers = {}
        from api.oidc import _add_cors_headers
        result = _add_cors_headers(headers, request)

        assert "Access-Control-Allow-Origin" not in result


class TestPerformanceAndCompliance:
    """Test performance and compliance requirements"""

    @patch('api.oidc.security_check_dependency')
    @patch('api.oidc.get_oidc_provider')
    @patch('api.oidc.jwks_cache')
    @patch('api.oidc.rate_limiter')
    def test_jwks_sub_100ms_performance(
        self, mock_rate_limiter, mock_cache, mock_provider_dep, mock_security_dep, client
    ):
        """Test JWKS endpoint meets sub-100ms p95 latency requirement"""
        mock_security_dep.return_value = {
            "correlation_id": "test-123",
            "client_ip": "127.0.0.1",
            "security_report": {},
            "action": SecurityAction.ALLOW
        }

        mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 4})
        mock_cache.get.return_value = ({"keys": []}, True)  # Cache hit for speed

        # Measure multiple requests
        times = []
        for _ in range(10):
            start = time.perf_counter()
            response = client.get("/.well-known/jwks.json")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)  # Convert to ms

        # Check p95 latency (should be well under 100ms with cache)
        p95_latency = sorted(times)[int(len(times) * 0.95)]
        assert p95_latency < 100, f"P95 latency {p95_latency}ms exceeds 100ms requirement"

    def test_oidc_compliance_discovery_document(self, client):
        """Test OIDC compliance of discovery document"""
        with patch('api.oidc.security_check_dependency') as mock_security_dep, \
             patch('api.oidc.get_oidc_provider') as mock_provider_dep, \
             patch('api.oidc.rate_limiter') as mock_rate_limiter:

            mock_security_dep.return_value = {
                "correlation_id": "test-123",
                "client_ip": "127.0.0.1",
                "security_report": {},
                "action": SecurityAction.ALLOW
            }

            mock_rate_limiter.check_rate_limit.return_value = (True, {"remaining_minute": 9})

            mock_provider = Mock()
            mock_provider.get_discovery_document.return_value = {
                "issuer": "https://test.ai",
                "authorization_endpoint": "https://test.ai/oauth2/authorize",
                "token_endpoint": "https://test.ai/oauth2/token",
                "userinfo_endpoint": "https://test.ai/oauth2/userinfo",
                "jwks_uri": "https://test.ai/.well-known/jwks.json"
            }
            mock_provider_dep.return_value = mock_provider

            response = client.get("/.well-known/openid-configuration")

            assert response.status_code == 200
            data = response.json()

            # Check required OIDC Discovery fields
            required_fields = [
                "issuer", "authorization_endpoint", "token_endpoint",
                "userinfo_endpoint", "jwks_uri", "response_types_supported",
                "subject_types_supported", "id_token_signing_alg_values_supported"
            ]

            for field in required_fields:
                assert field in data, f"Required OIDC field '{field}' missing"

            # Check LUKHAS extensions
            assert data["tier_authentication_supported"] is True
            assert data["webauthn_supported"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
