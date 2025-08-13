#!/usr/bin/env python3
"""
Test Feature Flags System
=========================
"""

import os
import sys
from pathlib import Path

from lukhas.flags import get_flags, require_feature, when_enabled

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_default_flags():
    """Test default flag values"""
    flags = get_flags()

    # Check some defaults
    assert flags.is_enabled("tool_governance")
    assert not flags.is_enabled("dna_helix_memory")
    assert flags.is_enabled("auto_safety_tightening")

    print("✅ Default flags test passed")


def test_override():
    """Test flag override functionality"""
    flags = get_flags()

    # Override a flag
    original = flags.is_enabled("dna_helix_memory")
    flags.override("dna_helix_memory", True)
    assert flags.is_enabled("dna_helix_memory")

    # Clear override
    flags.clear_override("dna_helix_memory")
    assert flags.is_enabled("dna_helix_memory") == original

    print("✅ Override test passed")


def test_env_override():
    """Test environment variable override"""
    # Set env var
    os.environ["FF_QUANTUM_PROCESSING"] = "true"

    # Create new instance to pick up env
    from lukhas.flags.ff import FeatureFlags

    flags = FeatureFlags()

    assert flags.is_enabled("quantum_processing")

    # Clean up
    del os.environ["FF_QUANTUM_PROCESSING"]

    print("✅ Environment override test passed")


def test_decorator():
    """Test when_enabled decorator"""
    get_flags()

    @when_enabled("tool_governance")
    def enabled_func():
        return "executed"

    @when_enabled("dna_helix_memory")
    def disabled_func():
        return "should not execute"

    assert enabled_func() == "executed"
    assert disabled_func() is None

    print("✅ Decorator test passed")


def test_require_feature():
    """Test require_feature guard"""
    # Should not raise for enabled feature
    try:
        require_feature("tool_governance")
        print("✅ Require enabled feature passed")
    except RuntimeError:
        raise AssertionError("Should not raise for enabled feature")

    # Should raise for disabled feature
    try:
        require_feature("dna_helix_memory")
        raise AssertionError("Should have raised RuntimeError")
    except RuntimeError as e:
        assert "dna_helix_memory" in str(e)
        print("✅ Require disabled feature passed")


def test_get_enabled_features():
    """Test getting list of enabled features"""
    flags = get_flags()
    enabled = flags.get_enabled_features()

    assert "tool_governance" in enabled
    assert "auto_safety_tightening" in enabled
    assert "dna_helix_memory" not in enabled

    print("✅ Get enabled features test passed")


def main():
    """Run all tests"""
    print("🧪 Testing Feature Flags System...")
    print("=" * 50)

    try:
        test_default_flags()
        test_override()
        test_env_override()
        test_decorator()
        test_require_feature()
        test_get_enabled_features()

        print("\n" + "=" * 50)
        print("🎉 All feature flag tests passed!")
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
