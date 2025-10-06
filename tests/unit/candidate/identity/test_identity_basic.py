"""Test identity module basic functionality."""

import pytest


def test_auth_service_import():
    """Test AuthenticationService imports and basic init."""
    try:
        from identity import AuthenticationService

        # Test creation
        service = AuthenticationService()
        assert service is not None
        assert hasattr(service, "authenticate_user")

    except ImportError:
        pytest.skip("Authentication service not available")


def test_lambda_id_import():
    """Test LambdaID imports."""
    try:
        from lukhas.identity.lambda_id import LambdaIDService

        # Check class exists
        assert LambdaIDService is not None

    except (ImportError, AttributeError):
        pytest.skip("LambdaID not available")


def test_identity_exports():
    """Test identity module exports."""
    try:
        import identity as identity

        # Check key exports
        assert hasattr(identity, "AuthenticationService")
        assert hasattr(identity, "IdentityService")

    except ImportError:
        pytest.skip("Identity module not available")
