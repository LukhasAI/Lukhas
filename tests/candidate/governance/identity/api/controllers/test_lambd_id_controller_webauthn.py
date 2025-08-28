import pytest
from pathlib import Path
from candidate.governance.identity.api.controllers.lambd_id_controller import LambdaIDController

@pytest.fixture
def controller():
    """Fixture to create a LambdaIDController instance."""
    # The controller will load the default settings, which is fine for these tests.
    return LambdaIDController()

def test_webauthn_generate_registration_options(controller):
    """Test generating WebAuthn registration options."""
    result = controller.webauthn_generate_registration_options(
        user_id="test_user",
        user_name="Test User",
        user_display_name="Test User",
        user_tier=1
    )
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "options" in result

def test_webauthn_verify_registration_response_invalid(controller):
    """Test verifying an invalid WebAuthn registration response."""
    result = controller.webauthn_verify_registration_response("invalid_id", {})
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "error" in result

def test_webauthn_verify_authentication_response_invalid(controller):
    """Test verifying an invalid WebAuthn authentication response."""
    result = controller.webauthn_verify_authentication_response("invalid_id", {})
    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "error" in result
