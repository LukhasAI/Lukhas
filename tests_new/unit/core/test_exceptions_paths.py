"""Test exception module branches for coverage."""


def test_exception_none_handling():
    """Test exceptions handle None values properly."""
    from lukhas.core.common.exceptions import ResourceExhaustedError

    # Test with None current_usage
    err = ResourceExhaustedError(message="Test error", resource_type="memory", current_usage=None, limit=100.0)
    assert err.details["usage_percentage"] == 100

    # Test with valid values
    err2 = ResourceExhaustedError(message="Test error", resource_type="memory", current_usage=50.0, limit=100.0)
    assert err2.details["usage_percentage"] == 50.0


def test_more_exception_types():
    """Test various exception types for coverage."""
    from lukhas.core.common.exceptions import (
        AuthenticationError,
        ConfigurationError,
        LukhasError,
        ModuleNotFoundError,
        ValidationError,
    )

    # Test basic exceptions
    base = LukhasError(message="Base error")
    assert "Base error" in str(base)

    config = ConfigurationError(message="Config error", config_key="test_param")
    assert config.details["config_key"] == "test_param"

    validation = ValidationError(message="Validation error", field="test_field", value="invalid")
    assert validation.details["field"] == "test_field"

    auth = AuthenticationError(message="Auth error", auth_method="password")
    assert auth.details["auth_method"] == "password"

    module_error = ModuleNotFoundError(module_name="test_module")
    assert module_error.details["module_name"] == "test_module"