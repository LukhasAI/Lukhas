"""Tests for ProviderRegistry."""

from unittest.mock import MagicMock, patch

import pytest
from core.adapters.config_resolver import make_resolver
from core.adapters.provider_registry import ProviderRegistry


class TestProviderRegistry:
    """Test ProviderRegistry functionality."""

    def test_initialization(self):
        """Test registry initialization."""
        config = make_resolver()
        registry = ProviderRegistry(config)
        assert registry.config is config
        assert registry._cache == {}

    def test_get_provider_with_caching(self):
        """Test provider retrieval with caching."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        # Mock a provider
        with patch.object(registry, '_load_provider') as mock_load:
            mock_provider = MagicMock()
            mock_load.return_value = mock_provider

            # First call should load
            result1 = registry.get_openai()
            assert result1 is mock_provider
            assert mock_load.call_count == 1

            # Second call should use cache
            result2 = registry.get_openai()
            assert result2 is mock_provider
            assert mock_load.call_count == 1  # Not called again

    def test_get_provider_unavailable(self):
        """Test getting unavailable provider returns None."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        with patch.object(registry, '_load_provider', return_value=None):
            result = registry.get_openai()
            assert result is None

    def test_clear_cache(self):
        """Test cache clearing."""
        config = make_resolver()
        registry = ProviderRegistry(config)
        registry._cache["test"] = "value"

        registry.clear_cache()
        assert registry._cache == {}

    def test_is_available(self):
        """Test provider availability check."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        with patch.object(registry, '_load_provider') as mock_load:
            mock_load.return_value = MagicMock()
            config.set("providers.test.module", "test.module")
            config.set("providers.test.class", "TestClass")

            assert registry.is_available("test") is True

            registry.clear_cache()
            mock_load.return_value = None
            assert registry.is_available("test") is False

    def test_load_provider_success(self):
        """Test successful provider loading."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_class = MagicMock()
            mock_module.TestClass = mock_class
            mock_import.return_value = mock_module

            result = registry._load_provider("test.module", "TestClass")
            assert result == mock_class.return_value
            mock_class.assert_called_once()

    def test_load_provider_import_error(self):
        """Test provider loading with import error."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        with patch('importlib.import_module', side_effect=ImportError):
            result = registry._load_provider("nonexistent.module", "Class")
            assert result is None

    def test_load_provider_attribute_error(self):
        """Test provider loading with attribute error."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock(spec=[])  # No attributes
            mock_import.return_value = mock_module

            result = registry._load_provider("test.module", "NonexistentClass")
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
