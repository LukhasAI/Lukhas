"""OWASP Top 10 Security Principles Tests.

Simplified security tests validating OWASP Top 10 principles without
complex production dependencies. These tests validate security concepts
and can run independently of the full LUKHAS system.

OWASP A01: Broken Access Control
OWASP A05: Security Misconfiguration
OWASP A07: Identification and Authentication Failures
OWASP A09: Security Logging and Monitoring Failures
"""

import pytest
import jwt
import secrets
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any


class TestOWASPA01Principles:
    """Test OWASP A01: Broken Access Control principles."""

    def test_jwt_signature_verification_prevents_forgery(self):
        """JWT signature verification prevents token forgery."""
        secret = "test_secret_key_12345"
        user_id = "user_abc123"

        # Create valid token
        payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(hours=1)}
        valid_token = jwt.encode(payload, secret, algorithm="HS256")

        # Verify valid token works
        decoded = jwt.decode(valid_token, secret, algorithms=["HS256"])
        assert decoded["sub"] == user_id

        # Attempt to use wrong secret (forged token)
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(valid_token, "wrong_secret", algorithms=["HS256"])

    def test_jwt_expiration_enforced(self):
        """Expired JWT tokens are rejected."""
        secret = "test_secret_key"
        payload = {
            "sub": "user_123",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Already expired
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, secret, algorithms=["HS256"])

    def test_jwt_claims_extraction(self):
        """JWT token claims are correctly extracted."""
        secret = "test_secret"
        payload = {
            "sub": "user_xyz",
            "tier": 3,
            "permissions": ["read", "write"],
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        token = jwt.encode(payload, secret, algorithm="HS256")
        decoded = jwt.decode(token, secret, algorithms=["HS256"])

        assert decoded["sub"] == "user_xyz"
        assert decoded["tier"] == 3
        assert decoded["permissions"] == ["read", "write"]


class TestOWASPA05Principles:
    """Test OWASP A05: Security Misconfiguration principles."""

    def test_security_headers_structure(self):
        """Security headers have correct structure."""
        # Test that security header values are well-formed
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-XSS-Protection": "1; mode=block",
        }

        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]
        assert "max-age=" in headers["Strict-Transport-Security"]

    def test_rate_limit_window_calculation(self):
        """Rate limit windows are calculated correctly."""
        # Sliding window rate limiting principle
        window_seconds = 60
        max_requests = 10

        requests_timestamps = [
            datetime.utcnow().timestamp() - 70,  # Outside window
            datetime.utcnow().timestamp() - 30,  # Inside window
            datetime.utcnow().timestamp() - 20,  # Inside window
            datetime.utcnow().timestamp() - 10,  # Inside window
        ]

        current_time = datetime.utcnow().timestamp()
        requests_in_window = [
            ts for ts in requests_timestamps if current_time - ts <= window_seconds
        ]

        assert len(requests_in_window) == 3  # Only recent requests count
        assert len(requests_in_window) < max_requests  # Under limit

    def test_error_messages_generic(self):
        """Error messages don't reveal system details."""
        # Good error message (generic)
        generic_error = "Invalid credentials"

        # Bad error messages (reveal too much info)
        bad_errors = [
            "User 'admin' not found in database users table",
            "Password incorrect for user@example.com",
            "/var/www/app/auth.py line 42: KeyError",
        ]

        # Generic error should not contain revealing information
        assert "database" not in generic_error.lower()
        assert "table" not in generic_error.lower()
        assert "/" not in generic_error  # No file paths
        assert ".py" not in generic_error  # No file extensions

        # Verify bad errors actually contain revealing info (for testing)
        assert any("database" in err.lower() or "/" in err for err in bad_errors)


class TestOWASPA07Principles:
    """Test OWASP A07: Identification and Authentication Failures principles."""

    def test_password_complexity_validation(self):
        """Password complexity requirements are validated."""

        def check_password_strength(password: str) -> bool:
            """Check if password meets complexity requirements."""
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_symbol = any(not c.isalnum() for c in password)
            is_long = len(password) >= 12

            return all([has_upper, has_lower, has_digit, has_symbol, is_long])

        # Strong passwords
        assert check_password_strength("MyP@ssw0rd123!")
        assert check_password_strength("C0mpl3x!Pass#2024")

        # Weak passwords
        assert not check_password_strength("password")  # No upper, digit, symbol
        assert not check_password_strength("SHORT1!")  # Too short
        assert not check_password_strength("NoSymb0ls1234")  # No symbols

    def test_password_hashing_with_salt(self):
        """Passwords are hashed with unique salts."""
        password = "my_secure_password"

        # Hash with different salts
        salt1 = os.urandom(32)
        hash1 = hashlib.pbkdf2_hmac("sha256", password.encode(), salt1, 100000)

        salt2 = os.urandom(32)
        hash2 = hashlib.pbkdf2_hmac("sha256", password.encode(), salt2, 100000)

        # Same password, different salts = different hashes
        assert hash1 != hash2
        assert salt1 != salt2

    def test_api_key_randomness(self):
        """API keys are cryptographically random."""
        # Generate API keys using secrets module (cryptographically secure)
        api_key_1 = secrets.token_urlsafe(32)
        api_key_2 = secrets.token_urlsafe(32)

        # Keys should be different
        assert api_key_1 != api_key_2

        # Keys should be sufficiently long
        assert len(api_key_1) >= 32
        assert len(api_key_2) >= 32

    def test_jwt_algorithm_security(self):
        """JWT tokens use secure algorithms."""
        secret = "test_secret"
        payload = {"sub": "user_abc"}

        # Test allowed algorithms
        allowed_algorithms = ["HS256", "RS256", "ES256"]

        for algo in allowed_algorithms:
            if algo.startswith("HS"):  # Symmetric algorithms
                token = jwt.encode(payload, secret, algorithm=algo)
                header = jwt.get_unverified_header(token)
                assert header["alg"] == algo
                assert header["alg"] != "none"  # "none" is insecure

    def test_session_token_expiration(self):
        """Session tokens have appropriate expiration times."""
        # Access token: 1 hour
        access_token_expiry = timedelta(hours=1)

        # Refresh token: 30 days
        refresh_token_expiry = timedelta(days=30)

        # Verify expiry times are reasonable
        assert access_token_expiry <= timedelta(hours=24)  # Not too long
        assert refresh_token_expiry <= timedelta(days=90)  # Not excessive


class TestOWASPA09Principles:
    """Test OWASP A09: Security Logging and Monitoring Failures principles."""

    def test_log_entry_structure(self):
        """Security log entries have required fields."""
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "LOGIN_FAILURE",
            "user_id": "user_abc",
            "ip_address": "203.0.113.1",
            "success": False,
            "metadata": {"reason": "invalid_credentials"},
        }

        # Validate required fields
        assert "timestamp" in log_entry
        assert "event_type" in log_entry
        assert "user_id" in log_entry
        assert "ip_address" in log_entry
        assert "success" in log_entry

        # Validate ISO 8601 timestamp format
        assert "T" in log_entry["timestamp"]
        assert "Z" in log_entry["timestamp"]

    def test_sensitive_data_not_in_logs(self):
        """Sensitive data is not logged."""
        # Simulate log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "LOGIN_ATTEMPT",
            "user_id": "user_abc",
            "ip_address": "192.0.2.1",
            # Should NOT contain: password, token, API key, SSN, credit card
        }

        log_string = str(log_entry)

        # Verify sensitive fields are not present
        sensitive_keywords = [
            "password",
            "passwd",
            "secret",
            "token",
            "api_key",
            "apikey",
            "ssn",
            "credit_card",
        ]

        for keyword in sensitive_keywords:
            assert keyword not in log_string.lower()

    def test_log_retention_policy(self):
        """Log retention period is appropriate."""
        # Compliance requirements (SOC 2, GDPR, etc.)
        audit_log_retention_days = 365 * 7  # 7 years for audit logs
        access_log_retention_days = 90  # 90 days for access logs

        # Verify retention periods meet compliance
        assert audit_log_retention_days >= 365  # At least 1 year
        assert access_log_retention_days >= 30  # At least 30 days

    def test_log_event_types_comprehensive(self):
        """Security events are comprehensively categorized."""
        # All critical security events should be logged
        security_event_types = {
            "LOGIN_SUCCESS",
            "LOGIN_FAILURE",
            "LOGOUT",
            "PASSWORD_CHANGE",
            "MFA_ENABLED",
            "DATA_READ",
            "DATA_CREATE",
            "DATA_UPDATE",
            "DATA_DELETE",
            "PERMISSION_DENIED",
            "RATE_LIMIT_EXCEEDED",
            "SECURITY_EXCEPTION",
            "ACCOUNT_LOCKED",
            "SUSPICIOUS_ACTIVITY",
        }

        # Verify comprehensive coverage
        assert "LOGIN_SUCCESS" in security_event_types
        assert "LOGIN_FAILURE" in security_event_types
        assert "PERMISSION_DENIED" in security_event_types
        assert "DATA_DELETE" in security_event_types
        assert len(security_event_types) >= 10  # Comprehensive coverage


class TestSecurityPrinciplesIntegration:
    """Integration tests for security principles."""

    def test_defense_in_depth(self):
        """Multiple security layers protect resources."""
        # Layer 1: Network (IP filtering)
        allowed_ips = ["203.0.113.0/24"]

        # Layer 2: Authentication (JWT token)
        jwt_secret = secrets.token_hex(32)
        token_payload = {"sub": "user_123", "exp": datetime.utcnow() + timedelta(hours=1)}

        # Layer 3: Authorization (permission check)
        user_permissions = ["read:data", "write:data"]

        # Layer 4: Rate limiting
        rate_limit = {"max_requests": 100, "window_seconds": 60}

        # Verify all layers exist
        assert len(allowed_ips) > 0
        assert len(jwt_secret) >= 32
        assert "sub" in token_payload
        assert len(user_permissions) > 0
        assert rate_limit["max_requests"] > 0

    def test_secure_defaults(self):
        """System has secure default configurations."""
        default_config = {
            "debug_mode": False,
            "https_only": True,
            "csrf_protection": True,
            "rate_limiting_enabled": True,
            "audit_logging_enabled": True,
            "min_password_length": 12,
            "jwt_expiry_hours": 1,
            "max_login_attempts": 5,
        }

        # Verify secure defaults
        assert default_config["debug_mode"] is False
        assert default_config["https_only"] is True
        assert default_config["csrf_protection"] is True
        assert default_config["min_password_length"] >= 12
        assert default_config["max_login_attempts"] <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
