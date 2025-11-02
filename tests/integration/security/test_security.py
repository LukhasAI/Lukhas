# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.authentication
# criticality: P1

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from bridge.api.validation import AuthenticationValidator, ValidationErrorType


@pytest.mark.asyncio
@pytest.mark.tier3
@pytest.mark.security
@pytest.mark.integration
class TestAuthenticationValidator:
    """
    Tests for the AuthenticationValidator class.
    """

    @pytest.fixture
    def validator(self):
        return AuthenticationValidator(jwt_secret="test-secret")

    def create_jwt(self, secret, payload):
        return jwt.encode(payload, secret, algorithm="HS256")

    async def test_valid_jwt_token(self, validator: AuthenticationValidator):
        """Tests a valid JWT token."""
        payload = {
            "user_id": "test-user",
            "tier": "LAMBDA_TIER_3",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }
        token = self.create_jwt("test-secret", payload)
        result = await validator.validate_jwt_token(token)
        assert result.is_valid is True
        assert result.metadata["user_id"] == "test-user"

    async def test_expired_jwt_token(self, validator: AuthenticationValidator):
        """Tests an expired JWT token."""
        payload = {
            "user_id": "test-user",
            "tier": "LAMBDA_TIER_3",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        token = self.create_jwt("test-secret", payload)
        result = await validator.validate_jwt_token(token)
        assert result.is_valid is False
        assert result.errors[0]["type"] == ValidationErrorType.AUTHENTICATION_FAILED.value
        assert "expired" in result.errors[0]["message"]

    async def test_invalid_api_key(self, validator: AuthenticationValidator):
        """Tests an invalid API key."""
        result = await validator.validate_api_key("invalid-key", required_permissions=["orchestration"])
        assert result.is_valid is False
        assert result.errors[0]["type"] == ValidationErrorType.AUTHENTICATION_FAILED.value

    async def test_valid_api_key_with_sufficient_permissions(self, validator: AuthenticationValidator):
        """Tests a valid API key with sufficient permissions."""
        result = await validator.validate_api_key("lukhas-test-key-long-enough", required_permissions=["orchestration"])
        assert result.is_valid is True
        assert result.metadata["user_id"] == "test-user"

    async def test_valid_api_key_with_insufficient_permissions(self, validator: AuthenticationValidator):
        """Tests a valid API key with insufficient permissions."""
        result = await validator.validate_api_key("lukhas-test-key-long-enough", required_permissions=["admin"])
        assert result.is_valid is False
        assert result.errors[0]["type"] == ValidationErrorType.AUTHORIZATION_FAILED.value
