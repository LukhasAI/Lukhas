import pytest
from lukhas.identity.webauthn import WebAuthnManager

def test_webauthn_manager_instantiation():
    """Test that WebAuthnManager can be instantiated."""
    try:
        manager = WebAuthnManager()
        assert manager is not None
    except Exception as e:
        pytest.fail(f"WebAuthnManager instantiation failed: {e}")

def test_webauthn_manager_methods_exist():
    """Test that key methods exist on WebAuthnManager."""
    manager = WebAuthnManager()
    assert hasattr(manager, "generate_registration_options")
    assert hasattr(manager, "verify_registration_response")
    assert hasattr(manager, "generate_authentication_options")
    assert hasattr(manager, "verify_authentication_response")
    assert hasattr(manager, "_get_device_type_distribution")

def test_get_device_type_distribution_empty():
    """Test _get_device_type_distribution with no credentials."""
    manager = WebAuthnManager()
    dist = manager._get_device_type_distribution()
    assert dist == {}
