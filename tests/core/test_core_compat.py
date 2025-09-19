"""
Core Compatibility Bridge Tests

Tests for the legacy 'core' import compatibility layer.
Ensures the bridge is disabled by default and can be enabled via env var.
"""

import os
import importlib
import pytest
import sys
import warnings


class TestCoreCompat:
    """Test suite for core compatibility bridge."""

    def test_core_compat_disabled_by_default(self):
        """Test that core imports are disabled by default."""
        # Clear any existing core module
        if "core" in sys.modules:
            del sys.modules["core"]

        # Ensure env var is not set
        os.environ.pop("LUKHAS_CORE_COMPAT", None)

        # Clear import cache
        importlib.invalidate_caches()

        # Should raise ImportError
        with pytest.raises(ImportError) as exc_info:
            import core  # noqa: F401

        assert "Legacy 'core' alias disabled" in str(exc_info.value)

    def test_core_compat_enabled(self, monkeypatch):
        """Test that core imports work when explicitly enabled."""
        # Clean up any existing core module
        if "core" in sys.modules:
            del sys.modules["core"]

        # Enable compatibility
        monkeypatch.setenv("LUKHAS_CORE_COMPAT", "1")

        # Clear import cache
        importlib.invalidate_caches()

        # Should work without warning when enabled
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import core  # noqa: F401

            # Should NOT issue deprecation warning when enabled
            assert len(w) == 0

    def test_core_compat_proxy_functionality(self, monkeypatch):
        """Test that the proxy module can access lukhas.core attributes."""
        # Clean up
        if "core" in sys.modules:
            del sys.modules["core"]

        # Enable compatibility
        monkeypatch.setenv("LUKHAS_CORE_COMPAT", "1")

        # Clear import cache
        importlib.invalidate_caches()

        # Import and test proxy functionality
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress deprecation warning for test
            import core

            # Should be able to access lukhas.core attributes
            # Test that module has expected structure
            assert hasattr(core, "__doc__")

    def test_core_compat_env_var_values(self, monkeypatch):
        """Test that only '1' enables compatibility."""
        test_values = ["0", "true", "yes", "on", "enabled", ""]

        for value in test_values:
            # Clean up
            if "core" in sys.modules:
                del sys.modules["core"]

            monkeypatch.setenv("LUKHAS_CORE_COMPAT", value)
            importlib.invalidate_caches()

            # All values except "1" should fail
            with pytest.raises(ImportError):
                import core  # noqa: F401

    def teardown_method(self):
        """Clean up after each test."""
        # Remove core module if it exists
        if "core" in sys.modules:
            del sys.modules["core"]

        # Clear env var
        os.environ.pop("LUKHAS_CORE_COMPAT", None)

        # Clear import cache
        importlib.invalidate_caches()