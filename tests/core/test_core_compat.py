"""
Core Compatibility Alias Tests

Tests for the robust legacy 'core' import alias system.
Ensures all import styles work and resolve to lukhas.core correctly.
"""

import importlib
import os
import sys
import warnings


class TestCoreCompatAlias:
    """Test suite for core compatibility alias system."""

    def test_core_alias_always_available(self):
        """Test that core alias is always available (robust system)."""
        # Clean up any existing core module imports
        for module_name in list(sys.modules.keys()):
            if module_name == "core" or module_name.startswith("core."):
                del sys.modules[module_name]

        # Clear import cache
        importlib.invalidate_caches()

        # Should work without environment variables (always available)
        import core  # noqa: F401
        assert core is not None

    def test_deprecation_warning_toggle(self, monkeypatch):
        """Test reversible deprecation warning toggle."""
        # Clean up
        for module_name in list(sys.modules.keys()):
            if module_name == "core" or module_name.startswith("core."):
                del sys.modules[module_name]

        # Test warning enabled
        monkeypatch.setenv("LUKHAS_WARN_LEGACY_CORE", "1")
        importlib.invalidate_caches()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import core  # noqa: F401

            # Should issue ImportWarning when enabled
            assert len(w) >= 1
            assert any("Legacy 'core' import in use" in str(warning.message) for warning in w)

    def test_alias_functionality(self):
        """Test that alias provides access to lukhas.core functionality."""
        # Clean up
        for module_name in list(sys.modules.keys()):
            if module_name == "core" or module_name.startswith("core."):
                del sys.modules[module_name]

        importlib.invalidate_caches()

        # Import and test functionality
        import core

        # Should be able to access lukhas.core attributes
        assert hasattr(core, "__doc__")
        assert core.__doc__ is not None

    def test_warning_off_by_default(self):
        """Test that warnings are off by default."""
        # Clean up
        for module_name in list(sys.modules.keys()):
            if module_name == "core" or module_name.startswith("core."):
                del sys.modules[module_name]

        # Ensure warning env var is not set
        os.environ.pop("LUKHAS_WARN_LEGACY_CORE", None)
        importlib.invalidate_caches()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import core  # noqa: F401

            # Should NOT issue ImportWarning by default
            legacy_warnings = [warning for warning in w if "Legacy 'core' import" in str(warning.message)]
            assert len(legacy_warnings) == 0

    def teardown_method(self):
        """Clean up after each test."""
        # Remove core modules if they exist
        for module_name in list(sys.modules.keys()):
            if module_name == "core" or module_name.startswith("core."):
                del sys.modules[module_name]

        # Clear env vars
        os.environ.pop("LUKHAS_WARN_LEGACY_CORE", None)

        # Clear import cache
        importlib.invalidate_caches()
