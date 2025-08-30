"""Test exception module branches for coverage."""

import pytest


def test_exception_none_handling():
    """Test exceptions handle None values properly."""
    from lukhas.core.common.exceptions import ResourceExhaustedError

    # Test with None current_usage
    err = ResourceExhaustedError(message="Test error", resource_type="memory", current_usage=None, limit=100.0)
    assert err.details["usage_percentage"] == 100

    # Test with valid values
    err2 = ResourceExhaustedError(message="Test error", resource_type="memory", current_usage=50.0, limit=100.0)
    assert err2.details["usage_percentage"] == 50.0
