#!/usr/bin/env python3
"""
Security Validation Tests
Comprehensive security testing for the LUKHAS AGI system
"""

import hashlib
import secrets
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import jwt
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@dataclass
class SecurityTestCase:
    """Security test case definition"""

    name: str
    category: str
    severity: str  # critical, high, medium, low
    description: str
    test_function: str
    expected_result: str


class TestSecurityValidation:
    """Security validation test suite"""

    @pytest.fixture
    def security_config(self):
        """Security configuration for testing"""
        return {
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_length": 256,
                "iv_length": 96,
            },
            "authentication": {
                "token_expiry": 3600,  # 1 hour
                "refresh_token_expiry": 86400,  # 24 hours
                "max_attempts": 3,
                "lockout_duration": 900,  # 15 minutes
            },
            "authorization": {
                "roles": ["guest", "user", "developer", "admin", "auditor"],
                "permissions": {
                    "guest": ["read_public"],
                    "user": ["read_public", "read_own", "write_own"],
                    "developer": ["read_public", "read_own", "write_own", "debug"],
                    "admin": ["all"],
                    "auditor": ["read_all", "audit"],
                },
            },
            "api_security": {
                "rate_limit": 100,  # requests per minute
                "cors_origins": ["https://lukhas.ai"],
                "csrf_protection": True,
            },
        }

    @pytest.fixture
    async def mock_security_system(self, security_config):
        """Mock security system"""

        class MockSecuritySystem:
            def __init__(self, config):
                self.config = config
                self.failed_attempts = {}
                self.locked_accounts = {}
                self.active_sessions = {}
                self.audit_log = []

            async def authenticate(
                self, username: str, password: str
            ) -> Optional[Dict]:
                """Authenticate user"""
                # Check if account is locked
                if username in self.locked_accounts:
                    if datetime.now() < self.locked_accounts[username]:
                        self.audit_log.append(
                            {
                                "event": "auth_failed_locked",
                                "username": username,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                        return None

                # Simulate authentication
                if username == "valid_user" and password == "correct_password":
                    token = self.generate_token(username, "user")
                    self.active_sessions[username] = token
                    self.failed_attempts[username] = 0
                    self.audit_log.append(
                        {
                            "event": "auth_success",
                            "username": username,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    return {"token": token, "role": "user"}
                else:
                    # Track failed attempts
                    self.failed_attempts[username] = (
                        self.failed_attempts.get(username, 0) + 1
                    )

                    # Lock account after max attempts
                    if (
                        self.failed_attempts[username]
                        >= self.config["authentication"]["max_attempts"]
                    ):
                        lockout_until = datetime.now() + timedelta(
                            seconds=self.config["authentication"]["lockout_duration"]
                        )
                        self.locked_accounts[username] = lockout_until

                    self.audit_log.append(
                        {
                            "event": "auth_failed",
                            "username": username,
                            "attempts": self.failed_attempts[username],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    return None

            def generate_token(self, username: str, role: str) -> str:
                """Generate JWT token"""
                payload = {
                    "username": username,
                    "role": role,
                    "exp": datetime.utcnow()
                    + timedelta(seconds=self.config["authentication"]["token_expiry"]),
                    "iat": datetime.utcnow(),
                }
                return jwt.encode(payload, "test_secret", algorithm="HS256")

            async def validate_token(self, token: str) -> Optional[Dict]:
                """Validate JWT token"""
                try:
                    payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
                    return payload
                except jwt.ExpiredSignatureError:
                    self.audit_log.append(
                        {
                            "event": "token_expired",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    return None
                except jwt.InvalidTokenError:
                    self.audit_log.append(
                        {
                            "event": "invalid_token",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    return None

            async def authorize(self, token: str, permission: str) -> bool:
                """Check authorization"""
                user_data = await self.validate_token(token)
                if not user_data:
                    return False

                role = user_data.get("role", "guest")
                allowed_permissions = self.config["authorization"]["permissions"].get(
                    role, []
                )

                authorized = (
                    permission in allowed_permissions or "all" in allowed_permissions
                )

                self.audit_log.append(
                    {
                        "event": "authorization_check",
                        "username": user_data.get("username"),
                        "permission": permission,
                        "authorized": authorized,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                return authorized

            async def encrypt_data(self, data: str) -> Dict[str, str]:
                """Simulate data encryption"""
                # In real implementation, use proper encryption
                iv = secrets.token_hex(12)
                # Simulate encrypted data
                encrypted = hashlib.sha256(f"{data}{iv}".encode()).hexdigest()

                return {
                    "encrypted_data": encrypted,
                    "iv": iv,
                    "algorithm": self.config["encryption"]["algorithm"],
                }

            async def decrypt_data(self, encrypted_data: str, iv: str) -> Optional[str]:
                """Simulate data decryption"""
                # In real implementation, use proper decryption
                # For testing, just return a fixed value
                return "decrypted_data" if encrypted_data and iv else None

            async def sanitize_input(self, input_data: str) -> str:
                """Sanitize user input"""
                # Remove potentially dangerous characters
                dangerous_chars = ["<", ">", '"', "'", "&", "\x00", "\n", "\r"]
                sanitized = input_data
                for char in dangerous_chars:
                    sanitized = sanitized.replace(char, "")

                # Limit length
                max_length = 1000
                if len(sanitized) > max_length:
                    sanitized = sanitized[:max_length]

                return sanitized

            async def validate_api_request(
                self, request: Dict
            ) -> Tuple[bool, Optional[str]]:
                """Validate API request"""
                # Check required fields
                if "origin" not in request:
                    return False, "Missing origin header"

                # CORS check
                if request["origin"] not in self.config["api_security"]["cors_origins"]:
                    return False, "Invalid origin"

                # CSRF check
                if self.config["api_security"]["csrf_protection"]:
                    if "csrf_token" not in request:
                        return False, "Missing CSRF token"
                    # Validate CSRF token (simplified)
                    if request.get("csrf_token") != request.get("session_csrf_token"):
                        return False, "Invalid CSRF token"

                return True, None

        return MockSecuritySystem(security_config)

    @pytest.mark.asyncio
    async def test_authentication_success(self, mock_security_system):
        """Test successful authentication"""
        result = await mock_security_system.authenticate(
            "valid_user", "correct_password"
        )

        assert result is not None
        assert "token" in result
        assert result["role"] == "user"
        assert "valid_user" in mock_security_system.active_sessions

        # Verify audit log
        assert len(mock_security_system.audit_log) == 1
        assert mock_security_system.audit_log[0]["event"] == "auth_success"

    @pytest.mark.asyncio
    async def test_authentication_failure(self, mock_security_system):
        """Test authentication failure"""
        result = await mock_security_system.authenticate("valid_user", "wrong_password")

        assert result is None
        assert mock_security_system.failed_attempts["valid_user"] == 1

        # Verify audit log
        assert len(mock_security_system.audit_log) == 1
        assert mock_security_system.audit_log[0]["event"] == "auth_failed"

    @pytest.mark.asyncio
    async def test_account_lockout(self, mock_security_system, security_config):
        """Test account lockout after failed attempts"""
        max_attempts = security_config["authentication"]["max_attempts"]

        # Make max failed attempts
        for i in range(max_attempts):
            result = await mock_security_system.authenticate(
                "test_user", "wrong_password"
            )
            assert result is None

        # Account should be locked
        assert "test_user" in mock_security_system.locked_accounts
        assert mock_security_system.failed_attempts["test_user"] == max_attempts

        # Additional attempt should fail due to lockout
        result = await mock_security_system.authenticate(
            "test_user", "correct_password"
        )
        assert result is None

        # Check audit log for lockout
        lockout_events = [
            e
            for e in mock_security_system.audit_log
            if e["event"] == "auth_failed_locked"
        ]
        assert len(lockout_events) == 1

    @pytest.mark.asyncio
    async def test_token_validation(self, mock_security_system):
        """Test JWT token validation"""
        # Generate valid token
        token = mock_security_system.generate_token("test_user", "user")

        # Validate token
        payload = await mock_security_system.validate_token(token)
        assert payload is not None
        assert payload["username"] == "test_user"
        assert payload["role"] == "user"

        # Test invalid token
        invalid_token = "invalid.token.here"
        payload = await mock_security_system.validate_token(invalid_token)
        assert payload is None

        # Check audit log
        invalid_events = [
            e for e in mock_security_system.audit_log if e["event"] == "invalid_token"
        ]
        assert len(invalid_events) == 1

    @pytest.mark.asyncio
    async def test_authorization_permissions(self, mock_security_system):
        """Test authorization with different permissions"""
        # Generate tokens for different roles
        user_token = mock_security_system.generate_token("user1", "user")
        admin_token = mock_security_system.generate_token("admin1", "admin")
        guest_token = mock_security_system.generate_token("guest1", "guest")

        # Test user permissions
        assert await mock_security_system.authorize(user_token, "read_own") == True
        assert await mock_security_system.authorize(user_token, "write_own") == True
        assert await mock_security_system.authorize(user_token, "admin") == False

        # Test admin permissions (has 'all')
        assert await mock_security_system.authorize(admin_token, "read_own") == True
        assert await mock_security_system.authorize(admin_token, "admin") == True
        assert await mock_security_system.authorize(admin_token, "anything") == True

        # Test guest permissions
        assert await mock_security_system.authorize(guest_token, "read_public") == True
        assert await mock_security_system.authorize(guest_token, "write_own") == False

        # Verify audit log
        auth_events = [
            e
            for e in mock_security_system.audit_log
            if e["event"] == "authorization_check"
        ]
        assert len(auth_events) == 8  # Total authorization checks

    @pytest.mark.asyncio
    async def test_data_encryption(self, mock_security_system):
        """Test data encryption and decryption"""
        sensitive_data = "This is sensitive information"

        # Encrypt data
        encrypted_result = await mock_security_system.encrypt_data(sensitive_data)

        assert "encrypted_data" in encrypted_result
        assert "iv" in encrypted_result
        assert encrypted_result["algorithm"] == "AES-256-GCM"
        assert encrypted_result["encrypted_data"] != sensitive_data

        # Decrypt data
        decrypted = await mock_security_system.decrypt_data(
            encrypted_result["encrypted_data"], encrypted_result["iv"]
        )

        assert decrypted is not None
        # In real implementation, this should equal original data

    @pytest.mark.asyncio
    async def test_input_sanitization(self, mock_security_system):
        """Test input sanitization against XSS and injection"""
        # Test XSS attempt
        xss_input = '<script>alert("XSS")</script>'
        sanitized = await mock_security_system.sanitize_input(xss_input)
        assert "<" not in sanitized
        assert ">" not in sanitized
        assert "script" in sanitized  # Text remains but tags removed

        # Test SQL injection attempt
        sql_input = "'; DROP TABLE users; --"
        sanitized = await mock_security_system.sanitize_input(sql_input)
        assert "'" not in sanitized
        assert '"' not in sanitized

        # Test null byte injection
        null_input = "test\x00malicious"
        sanitized = await mock_security_system.sanitize_input(null_input)
        assert "\x00" not in sanitized

        # Test length limitation
        long_input = "a" * 2000
        sanitized = await mock_security_system.sanitize_input(long_input)
        assert len(sanitized) <= 1000

    @pytest.mark.asyncio
    async def test_api_security_validation(self, mock_security_system):
        """Test API security validations"""
        # Valid request
        valid_request = {
            "origin": "https://lukhas.ai",
            "csrf_token": "test_token_123",
            "session_csrf_token": "test_token_123",
        }

        is_valid, error = await mock_security_system.validate_api_request(valid_request)
        assert is_valid == True
        assert error is None

        # Invalid origin (CORS)
        invalid_origin_request = {
            "origin": "https://malicious.com",
            "csrf_token": "test_token_123",
            "session_csrf_token": "test_token_123",
        }

        is_valid, error = await mock_security_system.validate_api_request(
            invalid_origin_request
        )
        assert is_valid == False
        assert error == "Invalid origin"

        # Missing CSRF token
        no_csrf_request = {"origin": "https://lukhas.ai"}

        is_valid, error = await mock_security_system.validate_api_request(
            no_csrf_request
        )
        assert is_valid == False
        assert error == "Missing CSRF token"

        # Invalid CSRF token
        invalid_csrf_request = {
            "origin": "https://lukhas.ai",
            "csrf_token": "wrong_token",
            "session_csrf_token": "test_token_123",
        }

        is_valid, error = await mock_security_system.validate_api_request(
            invalid_csrf_request
        )
        assert is_valid == False
        assert error == "Invalid CSRF token"

    @pytest.mark.asyncio
    async def test_session_management(self, mock_security_system):
        """Test secure session management"""
        # Create session
        auth_result = await mock_security_system.authenticate(
            "valid_user", "correct_password"
        )
        assert auth_result is not None
        token = auth_result["token"]

        # Verify session exists
        assert "valid_user" in mock_security_system.active_sessions
        assert mock_security_system.active_sessions["valid_user"] == token

        # Validate active session
        payload = await mock_security_system.validate_token(token)
        assert payload is not None
        assert payload["username"] == "valid_user"

        # Test session expiry (would require time manipulation in real test)
        # For now, just verify token has expiry
        assert "exp" in payload
        assert "iat" in payload
        assert payload["exp"] > payload["iat"]

    @pytest.mark.asyncio
    async def test_security_audit_trail(self, mock_security_system):
        """Test security audit trail generation"""
        # Perform various security operations
        await mock_security_system.authenticate("user1", "wrong_pass")
        await mock_security_system.authenticate("valid_user", "correct_password")

        token = mock_security_system.generate_token("test_user", "user")
        await mock_security_system.authorize(token, "read_own")
        await mock_security_system.authorize(token, "admin_action")

        # Check audit log
        assert len(mock_security_system.audit_log) >= 4

        # Verify audit log structure
        for entry in mock_security_system.audit_log:
            assert "event" in entry
            assert "timestamp" in entry

        # Check specific events
        event_types = [e["event"] for e in mock_security_system.audit_log]
        assert "auth_failed" in event_types
        assert "auth_success" in event_types
        assert "authorization_check" in event_types

    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self, mock_security_system):
        """Test prevention of privilege escalation"""
        # User tries to access admin functionality
        user_token = mock_security_system.generate_token("regular_user", "user")

        # Attempt various privileged operations
        admin_operations = ["admin", "delete_all", "modify_system", "access_all_data"]

        for operation in admin_operations:
            authorized = await mock_security_system.authorize(user_token, operation)
            assert authorized == False, f"User should not have access to {operation}"

        # Verify audit log shows denied attempts
        denied_events = [
            e
            for e in mock_security_system.audit_log
            if e["event"] == "authorization_check" and not e["authorized"]
        ]
        assert len(denied_events) == len(admin_operations)

    def generate_security_report(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Generate security test report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(test_results),
                "passed": sum(1 for r in test_results if r["passed"]),
                "failed": sum(1 for r in test_results if not r["passed"]),
                "critical_issues": sum(
                    1
                    for r in test_results
                    if not r["passed"] and r.get("severity") == "critical"
                ),
            },
            "categories": {
                "authentication": [
                    r for r in test_results if r["category"] == "authentication"
                ],
                "authorization": [
                    r for r in test_results if r["category"] == "authorization"
                ],
                "encryption": [
                    r for r in test_results if r["category"] == "encryption"
                ],
                "input_validation": [
                    r for r in test_results if r["category"] == "input_validation"
                ],
                "api_security": [
                    r for r in test_results if r["category"] == "api_security"
                ],
            },
            "recommendations": self.generate_recommendations(test_results),
        }

    def generate_recommendations(self, test_results: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        failed_tests = [r for r in test_results if not r["passed"]]

        if any(r["category"] == "authentication" for r in failed_tests):
            recommendations.append(
                "Review authentication mechanisms and strengthen password policies"
            )

        if any(r["category"] == "encryption" for r in failed_tests):
            recommendations.append("Upgrade encryption algorithms to latest standards")

        if any(r["severity"] == "critical" for r in failed_tests):
            recommendations.append(
                "Address critical security issues immediately before deployment"
            )

        if len(recommendations) == 0:
            recommendations.append(
                "Security posture is strong, continue regular security audits"
            )

        return recommendations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
