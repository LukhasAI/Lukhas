"""
Unit tests for JWT role claims feature in lukhas.api.auth.

Tests:
- Token creation with role claims
- Token verification and role extraction
- Backward compatibility with tokens without roles
- Integration with get_current_user dependency
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from lukhas.api.auth import AuthManager
from lukhas.api.auth_helpers import ROLE_HIERARCHY, get_current_user_from_token


class TestJWTRoleClaims:
    """Test JWT role claims feature."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager(secret_key="test_secret_key_12345")

    def test_create_token_with_role(self, auth_manager):
        """Test creating JWT with role claim."""
        token = auth_manager.create_access_token(
            data={"sub": "test_user"},
            role="admin"
        )

        assert token is not None

        # Verify token contains role
        payload = auth_manager.verify_token(token)
        assert payload["sub"] == "test_user"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_create_token_without_role(self, auth_manager):
        """Test creating JWT without role claim (backward compatibility)."""
        token = auth_manager.create_access_token(
            data={"sub": "test_user"}
        )

        assert token is not None

        # Verify token works without role
        payload = auth_manager.verify_token(token)
        assert payload["sub"] == "test_user"
        assert "role" not in payload
        assert "exp" in payload

    def test_create_token_with_multiple_roles(self, auth_manager):
        """Test creating JWT with different role values."""
        roles = ["guest", "user", "moderator", "admin"]

        for role in roles:
            token = auth_manager.create_access_token(
                data={"sub": "test_user"},
                role=role
            )
            payload = auth_manager.verify_token(token)
            assert payload["role"] == role

    def test_token_with_none_role(self, auth_manager):
        """Test that None role is not added to token."""
        token = auth_manager.create_access_token(
            data={"sub": "test_user"},
            role=None
        )

        payload = auth_manager.verify_token(token)
        assert "role" not in payload

    def test_token_with_empty_string_role(self, auth_manager):
        """Test that empty string role is not added to token."""
        token = auth_manager.create_access_token(
            data={"sub": "test_user"},
            role=""
        )

        payload = auth_manager.verify_token(token)
        assert "role" not in payload


class TestGetCurrentUserFromToken:
    """Test get_current_user_from_token with role extraction."""

    @pytest.fixture
    def auth_manager(self):
        """Create AuthManager instance for testing."""
        return AuthManager(secret_key="test_secret_key_12345")

    def test_extract_role_from_token(self, auth_manager):
        """Test extracting role from JWT in get_current_user_from_token."""
        # Create token with role
        token = auth_manager.create_access_token(
            data={"sub": "admin_user"},
            role="admin"
        )

        # Mock the dependency
        user_data = get_current_user_from_token(
            token=token,
            auth_manager=auth_manager
        )

        assert user_data["username"] == "admin_user"
        assert user_data["role"] == "admin"

    def test_token_without_role_returns_no_role(self, auth_manager):
        """Test backward compatibility with tokens without role claim."""
        # Create token without role
        token = auth_manager.create_access_token(
            data={"sub": "legacy_user"}
        )

        user_data = get_current_user_from_token(
            token=token,
            auth_manager=auth_manager
        )

        assert user_data["username"] == "legacy_user"
        assert "role" not in user_data

    def test_invalid_token_raises_401(self, auth_manager):
        """Test that invalid token raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_from_token(
                token="invalid_token",
                auth_manager=auth_manager
            )

        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    def test_token_without_subject_raises_401(self, auth_manager):
        """Test that token without 'sub' raises HTTPException."""
        # Manually create token without subject
        from datetime import datetime, timedelta

        import jwt

        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(minutes=30)},
            "test_secret_key_12345",
            algorithm="HS256"
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_from_token(
                token=token,
                auth_manager=auth_manager
            )

        assert exc_info.value.status_code == 401
        assert "no subject" in str(exc_info.value.detail).lower()


class TestGetCurrentUserWithRoles:
    """Test get_current_user dependency with JWT roles."""

    def test_jwt_role_used_when_present(self):
        """Test that JWT role is used when present in user dict."""
        from lukhas.api.features import get_current_user

        # Mock user data with role from JWT
        mock_user = {
            "username": "test_user",
            "role": "admin"
        }

        result = get_current_user(user=mock_user)

        assert result["username"] == "test_user"
        assert result["role"] == "admin"
        assert result["id"] == "test_user"

    def test_fallback_to_username_prefix_when_no_jwt_role(self):
        """Test fallback to username prefix when no JWT role."""
        from lukhas.api.features import get_current_user

        # Mock user data without role (legacy token)
        mock_user = {
            "username": "admin_test_user"
        }

        result = get_current_user(user=mock_user)

        assert result["username"] == "admin_test_user"
        assert result["role"] == "admin"
        assert result["id"] == "admin_test_user"

    def test_fallback_role_inference_for_all_prefixes(self):
        """Test role inference for all username prefixes."""
        from lukhas.api.features import get_current_user

        test_cases = [
            ("admin_user", "admin"),
            ("moderator_user", "moderator"),
            ("user_someone", "user"),
            ("random_username", "guest"),
        ]

        for username, expected_role in test_cases:
            mock_user = {"username": username}
            result = get_current_user(user=mock_user)
            assert result["role"] == expected_role, f"Failed for {username}"

    def test_jwt_role_overrides_username_prefix(self):
        """Test that JWT role takes precedence over username prefix."""
        from lukhas.api.features import get_current_user

        # User has admin prefix but JWT says moderator
        mock_user = {
            "username": "admin_user",
            "role": "moderator"
        }

        result = get_current_user(user=mock_user)

        # JWT role should take precedence
        assert result["role"] == "moderator"


class TestRoleHierarchyIntegration:
    """Test that JWT roles work with existing role hierarchy."""

    def test_all_roles_in_hierarchy(self):
        """Test that all expected roles are in ROLE_HIERARCHY."""
        expected_roles = ["guest", "user", "moderator", "admin"]

        for role in expected_roles:
            assert role in ROLE_HIERARCHY

        # Verify hierarchy levels
        assert ROLE_HIERARCHY["guest"] < ROLE_HIERARCHY["user"]
        assert ROLE_HIERARCHY["user"] < ROLE_HIERARCHY["moderator"]
        assert ROLE_HIERARCHY["moderator"] < ROLE_HIERARCHY["admin"]
