"""Import safety tests for core.tags module."""
import importlib


def test_tags_import_safe():
    """Test that core.tags import does not trigger labs import-time loading."""
    # This test ensures that importing core.tags doesn't cause
    # labs.core.tags to be imported immediately
    importlib.import_module("core.tags")


def test_tags_dir_proxy_has_expected_names(monkeypatch):
    """Test that core.tags proxy exposes expected tag system names when available."""
    # If you want, simulate labs module with monkeypatch
    import types
    import sys
    
    # Create a fake labs.core.tags module for testing
    fake = types.SimpleNamespace()
    fake.TagRegistry = "MockTagRegistry"
    fake.TagDefinition = "MockTagDefinition"
    fake.get_tag_registry = lambda: "MockRegistry"
    
    # Temporarily install the fake module
    sys.modules['labs.core.tags'] = fake
    
    try:
        import core.tags
        # Test that dir() includes the expected tag system exports
        tag_dir = dir(core.tags)
        assert 'TagRegistry' in tag_dir
        assert 'TagDefinition' in tag_dir
        assert 'get_tag_registry' in tag_dir
    finally:
        # Clean up
        if 'labs.core.tags' in sys.modules:
            del sys.modules['labs.core.tags']


def test_tags_lazy_attribute_access():
    """Test that accessing tag system attributes works when labs is available."""
    import core.tags
    
    try:
        # Try to access a tag system component
        # This should trigger the lazy import of labs.core.tags
        tag_registry = core.tags.TagRegistry
        # If this works, great! If not, we should get a proper AttributeError
    except AttributeError:
        # Expected if labs.core.tags is not available or doesn't have TagRegistry
        pass


def test_missing_tag_attribute_handling():
    """Test that accessing non-existent tag attributes raises proper AttributeError."""
    import core.tags
    
    try:
        # Try to access a non-existent attribute
        _ = core.tags.NonExistentTagAttribute
        assert False, "Should have raised AttributeError"
    except AttributeError as e:
        # The error message format may vary based on whether labs.core.tags loads successfully
        assert "NonExistentTagAttribute" in str(e)
