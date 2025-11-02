"""
I.2 API Integration Tests
========================

Integration tests for the LUKHAS tiered authentication API endpoints.
Tests the complete API surface with realistic request/response flows.

Coverage:
- All authentication tier endpoints
- WebAuthn challenge/verification flows
- Biometric enrollment and authentication
- Session management
- Error handling and edge cases
- Performance under load
- Security validation
"""

import json
import time
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the API components
try:
    from api.identity import router as identity_router
    from governance.guardian_system import GuardianSystem
    from identity.biometrics import create_mock_biometric_provider
    from identity.security_hardening import create_security_hardening_manager
    from identity.tiers import SecurityPolicy, create_tiered_authenticator
    from identity.webauthn_enhanced import create_enhanced_webauthn_service

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


@pytest.fixture
def test_app():
    """Create test FastAPI application."""
    app = FastAPI()
    app.include_router(identity_router)
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""

    def test_t1_public_authentication(self, client):
        """Test T1 public authentication endpoint."""
        # Arrange
        request_data = {"tier": "T1", "correlation_id": "test_correlation_123"}

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tier"] == "T1"
        assert data["correlation_id"] == "test_correlation_123"
        assert "jwt_token" in data
        assert "expires_at" in data
        assert data["duration_ms"] < 100  # Performance requirement

    def test_t2_password_authentication_success(self, client):
        """Test T2 password authentication with valid credentials."""
        # Mock password verification
        with patch("identity.tiers.TieredAuthenticator._verify_password", return_value=True):
            # Arrange
            request_data = {
                "tier": "T2",
                "username": "test_user",
                "password": "test_password",
                "correlation_id": "test_t2_auth",
            }

            # Act
            response = client.post("/identity/authenticate", json=request_data)

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["tier"] == "T2"
            assert data["user_id"] == "test_user"

    def test_t2_password_authentication_failure(self, client):
        """Test T2 password authentication with invalid credentials."""
        # Arrange
        request_data = {"tier": "T2", "username": "test_user", "password": "wrong_password"}

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "error_code" in data
        assert "error_message" in data

    def test_missing_credentials_validation(self, client):
        """Test validation of missing credentials."""
        # Test T2 without username
        response = client.post("/identity/authenticate", json={"tier": "T2", "password": "test"})
        assert response.status_code == 401

        # Test T2 without password
        response = client.post("/identity/authenticate", json={"tier": "T2", "username": "test"})
        assert response.status_code == 401

    def test_invalid_tier_validation(self, client):
        """Test validation of invalid authentication tier."""
        # Arrange
        request_data = {"tier": "T99", "username": "test_user"}  # Invalid tier

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert
        assert response.status_code == 400
        assert "Invalid authentication tier" in response.json()["detail"]

    def test_tier_elevation_flow(self, client):
        """Test complete tier elevation flow."""
        # Mock all verification methods
        with (
            patch("identity.tiers.TieredAuthenticator._verify_password", return_value=True),
            patch("identity.tiers.TieredAuthenticator._verify_totp", return_value=True),
        ):

            # Step 1: T2 authentication
            t2_request = {"tier": "T2", "username": "test_user", "password": "test_password"}
            t2_response = client.post("/identity/authenticate", json=t2_request)
            assert t2_response.status_code == 200
            t2_data = t2_response.json()

            # Step 2: T3 elevation
            t3_request = {
                "tier": "T3",
                "username": "test_user",
                "existing_tier": "T2",
                "totp_token": "123456",
                "session_id": t2_data["session_id"],
            }
            t3_response = client.post("/identity/authenticate", json=t3_request)
            assert t3_response.status_code == 200
            t3_data = t3_response.json()
            assert t3_data["tier"] == "T3"
            assert "T1→T2→T3" in t3_data.get("tier_elevation_path", "")

    def test_session_elevation_endpoint(self, client):
        """Test session tier elevation endpoint."""
        with patch("identity.tiers.TieredAuthenticator._verify_password", return_value=True):
            # Arrange
            request_data = {"tier": "T2", "username": "test_user", "password": "test_password"}

            # Act
            response = client.post("/identity/session/elevate", json=request_data)

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["tier"] == "T2"


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestWebAuthnEndpoints:
    """Test WebAuthn API endpoints."""

    def test_webauthn_challenge_generation(self, client):
        """Test WebAuthn challenge generation."""
        # Arrange
        request_data = {"user_id": "test_user", "correlation_id": "test_webauthn_challenge"}

        # Act
        response = client.post("/identity/webauthn/challenge", json=request_data)

        # Assert - Should fail because user has no registered credentials
        assert response.status_code == 500  # Service error due to no credentials

    def test_webauthn_verification_invalid_challenge(self, client):
        """Test WebAuthn verification with invalid challenge."""
        # Arrange
        request_data = {
            "challenge_id": "invalid_challenge_id",
            "webauthn_response": {"id": "test", "response": {}},
            "correlation_id": "test_verification",
        }

        # Act
        response = client.post("/identity/webauthn/verify", json=request_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["error_code"] == "INVALID_CHALLENGE"


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestBiometricEndpoints:
    """Test biometric API endpoints."""

    def test_biometric_enrollment(self, client):
        """Test biometric template enrollment."""
        # Arrange
        request_data = {
            "user_id": "test_user",
            "modality": "fingerprint",
            "sample_data": "dGVzdF9maW5nZXJwcmludF9kYXRh",  # base64
            "device_info": {"device_id": "fp_scanner_001", "vendor": "Test Biometrics"},
        }

        # Act
        response = client.post("/identity/biometric/enroll", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "template_id" in data

    def test_biometric_enrollment_invalid_modality(self, client):
        """Test biometric enrollment with invalid modality."""
        # Arrange
        request_data = {"user_id": "test_user", "modality": "invalid_modality", "sample_data": "dGVzdA=="}

        # Act
        response = client.post("/identity/biometric/enroll", json=request_data)

        # Assert
        assert response.status_code == 400
        assert "Invalid biometric modality" in response.json()["detail"]

    def test_biometric_authentication_flow(self, client):
        """Test complete biometric authentication flow."""
        # Step 1: Enroll biometric template
        enroll_request = {"user_id": "test_user", "modality": "fingerprint", "sample_data": "dGVzdF9maW5nZXJwcmludA=="}
        enroll_response = client.post("/identity/biometric/enroll", json=enroll_request)
        assert enroll_response.status_code == 200

        # Step 2: Authenticate using biometric
        auth_request = {
            "user_id": "test_user",
            "modality": "fingerprint",
            "sample_data": "dGVzdF9maW5nZXJwcmludA==",
            "nonce": "unique_nonce_123",
        }
        auth_response = client.post("/identity/biometric/authenticate", json=auth_request)
        assert auth_response.status_code == 200
        auth_data = auth_response.json()
        assert auth_data["success"] is True
        assert "attestation" in auth_data

    def test_biometric_nonce_replay_protection(self, client):
        """Test biometric nonce replay protection."""
        # Enroll template first
        enroll_request = {"user_id": "test_user", "modality": "fingerprint", "sample_data": "dGVzdF9maW5nZXJwcmludA=="}
        client.post("/identity/biometric/enroll", json=enroll_request)

        nonce = "replay_test_nonce"

        # First authentication
        auth_request = {
            "user_id": "test_user",
            "modality": "fingerprint",
            "sample_data": "dGVzdF9maW5nZXJwcmludA==",
            "nonce": nonce,
        }
        response1 = client.post("/identity/biometric/authenticate", json=auth_request)
        assert response1.status_code == 200

        # Second authentication with same nonce (should fail)
        response2 = client.post("/identity/biometric/authenticate", json=auth_request)
        assert response2.status_code == 401


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestSessionManagement:
    """Test session management endpoints."""

    def test_session_status_unauthenticated(self, client):
        """Test session status for unauthenticated user."""
        # Act
        response = client.get("/identity/session/status")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False

    def test_session_status_with_token(self, client):
        """Test session status with authentication token."""
        # Arrange
        headers = {"Authorization": "Bearer test_jwt_token"}

        # Act
        response = client.get("/identity/session/status", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True  # Mock implementation returns True


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestMonitoringEndpoints:
    """Test monitoring and metrics endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        # Act
        response = client.get("/identity/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        # Act
        response = client.get("/identity/metrics")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "authentication_metrics" in data
        assert "webauthn_metrics" in data
        assert "biometric_metrics" in data
        assert "system_status" in data


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON requests."""
        # Act
        response = client.post(
            "/identity/authenticate", data="invalid json{", headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        # Act - Missing tier field
        response = client.post("/identity/authenticate", json={"username": "test"})

        # Assert
        assert response.status_code == 422
        assert "tier" in response.text

    def test_internal_server_error_handling(self, client):
        """Test handling of internal server errors."""
        # Mock an internal error
        with patch("api.identity.authenticator", None):
            # Act
            response = client.post("/identity/authenticate", json={"tier": "T1"})

            # Assert
            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"]

    def test_rate_limiting_headers(self, client):
        """Test rate limiting behavior."""
        # This test would need the rate limiting middleware enabled
        # For now, just verify the endpoint responds
        response = client.post("/identity/authenticate", json={"tier": "T1"})
        assert response.status_code in [200, 429]  # Success or rate limited


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestPerformanceRequirements:
    """Test API performance requirements."""

    def test_authentication_endpoint_performance(self, client):
        """Test authentication endpoint performance."""
        # Performance requirement: <100ms p95 for T1 authentication
        times = []

        for i in range(100):
            start = time.perf_counter()
            response = client.post("/identity/authenticate", json={"tier": "T1", "correlation_id": f"perf_test_{i}"})
            duration = (time.perf_counter() - start) * 1000
            times.append(duration)
            assert response.status_code == 200

        # Calculate p95
        times.sort()
        p95_time = times[94]  # 95th percentile

        assert p95_time < 100, f"API p95 latency {p95_time}ms exceeds 100ms SLA"

    def test_concurrent_request_handling(self, client):
        """Test handling of concurrent requests."""
        import queue
        import threading

        results = queue.Queue()

        def make_request(request_id):
            """Make a single authentication request."""
            start = time.perf_counter()
            response = client.post(
                "/identity/authenticate", json={"tier": "T1", "correlation_id": f"concurrent_test_{request_id}"}
            )
            duration = (time.perf_counter() - start) * 1000
            results.put((response.status_code, duration))

        # Create and start 20 concurrent threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        response_codes = []
        durations = []
        while not results.empty():
            code, duration = results.get()
            response_codes.append(code)
            durations.append(duration)

        # Assert all requests succeeded
        assert all(code == 200 for code in response_codes), "All concurrent requests should succeed"

        # Assert reasonable performance under load
        max_duration = max(durations)
        avg_duration = sum(durations) / len(durations)
        assert max_duration < 500, f"Max concurrent duration {max_duration}ms too high"
        assert avg_duration < 200, f"Average concurrent duration {avg_duration}ms too high"


@pytest.mark.skipif(not API_AVAILABLE, reason="API components not available")
class TestSecurityValidation:
    """Test security validation and hardening."""

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attempts."""
        # Arrange - SQL injection attempt in username
        request_data = {"tier": "T2", "username": "'; DROP TABLE users; --", "password": "test_password"}

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert - Should handle safely (either reject or sanitize)
        assert response.status_code in [400, 401, 422]  # Various safe responses

    def test_xss_protection(self, client):
        """Test protection against XSS attempts."""
        # Arrange - XSS attempt in correlation_id
        request_data = {"tier": "T1", "correlation_id": "<script>alert('xss')</script>"}

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert - Should handle safely
        assert response.status_code in [200, 400, 422]
        if response.status_code == 200:
            data = response.json()
            # Ensure no script tags in response
            assert "<script>" not in json.dumps(data)

    def test_large_payload_handling(self, client):
        """Test handling of excessively large payloads."""
        # Arrange - Very large username
        request_data = {"tier": "T2", "username": "a" * 10000, "password": "test_password"}  # 10KB username

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert - Should reject or handle gracefully
        assert response.status_code in [400, 413, 422]  # Bad request, payload too large, or validation error

    def test_invalid_characters_handling(self, client):
        """Test handling of invalid characters in input."""
        # Arrange - Null bytes and control characters
        request_data = {"tier": "T2", "username": "test\x00user\x01", "password": "pass\x02word"}

        # Act
        response = client.post("/identity/authenticate", json=request_data)

        # Assert - Should handle safely
        assert response.status_code in [400, 401, 422]


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
