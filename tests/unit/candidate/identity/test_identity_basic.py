"""Test identity module basic functionality."""

from importlib.util import find_spec

import pytest

HAS_AUTH_SERVICE = find_spec("identity.AuthenticationService") is not None
HAS_LAMBDA_ID = find_spec("identity.lambda_id") is not None
HAS_IDENTITY = find_spec("identity") is not None


@pytest.mark.skipif(not HAS_AUTH_SERVICE, reason="Authentication service not available")
def test_auth_service_import():
    """Test AuthenticationService imports and basic init."""
    from identity import AuthenticationService

    # Test creation
    service = AuthenticationService()
    assert service is not None
    assert hasattr(service, "authenticate_user")


@pytest.mark.skipif(not HAS_LAMBDA_ID, reason="LambdaID not available")
def test_lambda_id_import():
    """Test LambdaID imports."""
    from identity.lambda_id import LambdaIDService

    # Check class exists
    assert LambdaIDService is not None


@pytest.mark.skipif(not HAS_IDENTITY, reason="Identity module not available")
def test_identity_exports():
    """Test identity module exports."""
    import identity as identity

    # Check key exports
    assert hasattr(identity, "AuthenticationService")
    assert hasattr(identity, "IdentityService")
