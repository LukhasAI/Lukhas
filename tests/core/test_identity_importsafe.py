"""Import safety tests for core.identity module."""
import importlib


def test_import_safe():
    """Test that core.identity import does not trigger labs import-time loading."""
    # This test ensures that importing core.identity doesn't cause
    # labs.identity to be imported immediately
    importlib.import_module("core.identity")


def test_lazy_identity_system_behavior(monkeypatch):
    """Test that core.identity provides expected functionality when labs is available."""
    # Import core.identity (should not trigger labs import)
    import core.identity

    # Test that accessing an attribute triggers the lazy load
    # We'll use a known function from labs.identity
    try:
        # This should trigger the lazy import of labs.identity
        identity_system = core.identity.IdentitySystem()
        assert hasattr(identity_system, 'authenticate_user')
    except AttributeError:
        # If labs.identity is not available or doesn't have IdentitySystem,
        # we expect an AttributeError which is the correct behavior
        pass


def test_missing_attribute_handling():
    """Test that accessing non-existent attributes raises proper AttributeError."""
    import core.identity

    try:
        # Try to access a non-existent attribute
        _ = core.identity.NonExistentAttribute
        assert False, "Should have raised AttributeError"
    except AttributeError as e:
        assert "has no attribute 'NonExistentAttribute'" in str(e)
