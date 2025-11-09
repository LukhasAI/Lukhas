"""Strategic coverage test for branding_bridge.py - 213 lines, 22% -> target 60%"""

import pytest
from importlib.util import find_spec

HAS_BRANDING_BRIDGE = find_spec("branding_bridge") is not None

if HAS_BRANDING_BRIDGE:
    from branding_bridge import BrandingBridge


@pytest.mark.skipif(not HAS_BRANDING_BRIDGE, reason="BrandingBridge not available")
def test_branding_bridge_import():
    """Test branding bridge imports and basic initialization."""
    # Test basic instantiation
    bridge = BrandingBridge()
    assert bridge is not None

    # Test key methods exist
    assert hasattr(bridge, "get_brand_context")
    assert hasattr(bridge, "validate_message")
    assert hasattr(bridge, "apply_tone_system")


@pytest.mark.skipif(not HAS_BRANDING_BRIDGE, reason="BrandingBridge not available")
def test_branding_bridge_get_context():
    """Test brand context retrieval."""
    bridge = BrandingBridge()

    # Test context retrieval
    context = bridge.get_brand_context()
    assert isinstance(context, dict)

    # Test with specific domain
    context = bridge.get_brand_context(domain="ai")
    assert isinstance(context, dict)


@pytest.mark.skipif(not HAS_BRANDING_BRIDGE, reason="BrandingBridge not available")
def test_branding_bridge_message_validation():
    """Test message validation functionality."""
    bridge = BrandingBridge()

    # Test basic message validation
    result = bridge.validate_message("LUKHAS AI is a consciousness system")
    assert isinstance(result, dict)
    assert "valid" in result

    # Test with problematic message
    result = bridge.validate_message("LUKHAS is perfect and revolutionary")
    assert isinstance(result, dict)


@pytest.mark.skipif(not HAS_BRANDING_BRIDGE, reason="BrandingBridge not available")
def test_branding_bridge_tone_system():
    """Test 3-layer tone system application."""
    bridge = BrandingBridge()

    # Test tone application
    result = bridge.apply_tone_system("Technical message")
    assert isinstance(result, dict)

    # Test with layer specification
    result = bridge.apply_tone_system("Message", layer="narrative")
    assert isinstance(result, dict)


@pytest.mark.skipif(not HAS_BRANDING_BRIDGE, reason="BrandingBridge not available")
def test_branding_bridge_error_handling():
    """Test error handling in branding bridge."""
    bridge = BrandingBridge()

    # Test with None input
    result = bridge.validate_message(None)
    assert isinstance(result, dict)
    assert not result.get("valid", True)  # Should be invalid

    # Test with empty string
    result = bridge.validate_message("")
    assert isinstance(result, dict)
