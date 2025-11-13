"""
Comprehensive tests for Provider Registry infrastructure.

Tests the core provider pattern implementation including all available
providers, configuration management, and error handling.
"""

from core.adapters import Config, ProviderRegistry, make_resolver


class TestProviderRegistry:
    """Test suite for ProviderRegistry class."""

    def test_registry_initialization(self):
        """Test registry can be initialized with config."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        assert registry is not None
        assert registry.config is config
        assert len(registry._providers) == 0
        assert len(registry._initialized) == 0

    def test_make_resolver_defaults(self):
        """Test make_resolver creates config with defaults."""
        config = make_resolver()

        assert config is not None
        assert isinstance(config, Config)
        assert config.environment in ["development", "staging", "production"]
        assert config.openai_model == "gpt-4"
        assert config.openai_temperature == 0.7

    def test_custom_config(self):
        """Test custom configuration."""
        config = Config(
            environment="testing",
            openai_model="gpt-4-turbo",
            openai_temperature=0.9,
            mock_providers=True,
        )

        assert config.environment == "testing"
        assert config.openai_model == "gpt-4-turbo"
        assert config.openai_temperature == 0.9
        assert config.mock_providers is True

    def test_config_get_set(self):
        """Test config get/set methods."""
        config = Config()

        # Test get with default
        value = config.get("nonexistent", "default")
        assert value == "default"

        # Test set and get
        config.set("custom_key", "custom_value")
        value = config.get("custom_key")
        assert value == "custom_value"

    def test_register_custom_provider(self):
        """Test registering custom provider."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        # Create mock provider
        mock_provider = {"name": "mock"}

        # Register
        registry.register_provider("custom", mock_provider)

        # Verify
        assert registry.is_initialized("custom")
        assert registry.get_provider("custom") is mock_provider

    def test_provider_caching(self):
        """Test that providers are cached after first load."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        # Register mock provider
        mock_provider = {"name": "mock"}
        registry.register_provider("test", mock_provider)

        # Get twice
        provider1 = registry.get_provider("test")
        provider2 = registry.get_provider("test")

        # Should be same instance (cached)
        assert provider1 is provider2

    def test_clear_providers(self):
        """Test clearing all providers."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        # Register some providers
        registry.register_provider("test1", {"name": "test1"})
        registry.register_provider("test2", {"name": "test2"})

        assert len(registry._providers) == 2

        # Clear
        registry.clear()

        assert len(registry._providers) == 0
        assert len(registry._initialized) == 0

    def test_is_initialized_false_for_uninitialized(self):
        """Test is_initialized returns False for uninitialized provider."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        assert registry.is_initialized("nonexistent") is False

    def test_get_provider_returns_none_for_unregistered(self):
        """Test get_provider returns None for unregistered provider."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        provider = registry.get_provider("nonexistent")
        assert provider is None


class TestProviderMethods:
    """Test individual provider getter methods."""

    def test_provider_methods_exist(self):
        """Verify all provider getter methods exist."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        # Check methods exist
        assert hasattr(registry, "get_openai")
        assert hasattr(registry, "get_consciousness_service")
        assert hasattr(registry, "get_memory_service")
        assert hasattr(registry, "get_identity_service")
        assert hasattr(registry, "get_governance_service")

    def test_provider_methods_are_callable(self):
        """Verify all provider getter methods are callable."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        assert callable(registry.get_openai)
        assert callable(registry.get_consciousness_service)
        assert callable(registry.get_memory_service)
        assert callable(registry.get_identity_service)
        assert callable(registry.get_governance_service)


class TestImportSafety:
    """Test that registry doesn't trigger import-time dependencies."""

    def test_registry_import_safety(self):
        """Test registry can be imported without candidate/labs."""
        try:
            from core.adapters import Config, ProviderRegistry, make_resolver

            assert ProviderRegistry is not None
            assert Config is not None
            assert make_resolver is not None

        except ImportError as e:
            if "labs" in str(e) or "candidate" in str(e):
                raise AssertionError(
                    f"Registry has import-time dependency: {e}"
                ) from e
            raise

    def test_registry_instantiation_no_imports(self):
        """Test registry instantiation doesn't trigger imports."""
        from core.adapters import ProviderRegistry, make_resolver

        config = make_resolver()
        registry = ProviderRegistry(config)

        # Verify no providers loaded yet
        assert len(registry._providers) == 0
        assert all(not v for v in registry._initialized.values())


class TestErrorHandling:
    """Test error handling in provider registry."""

    def test_openai_import_error_handling(self):
        """Test graceful handling when OpenAI provider unavailable."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        try:
            # This may fail if labs.consciousness not available
            provider = registry.get_openai()
            # If it succeeds, verify it's cached
            assert registry.is_initialized("openai")
        except ImportError as e:
            # Should have clear error message
            assert "Cannot import OpenAI provider" in str(e)
            assert "labs.consciousness.reflection.openai_modulated_service" in str(e)

    def test_consciousness_service_error_handling(self):
        """Test graceful handling when consciousness service unavailable."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        try:
            provider = registry.get_consciousness_service()
            assert registry.is_initialized("consciousness")
        except ImportError as e:
            # Should try multiple locations
            assert "Could not find consciousness service" in str(e)
            assert "candidate.consciousness" in str(e) or "labs.consciousness" in str(e)

    def test_memory_service_error_handling(self):
        """Test graceful handling when memory service unavailable."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        try:
            provider = registry.get_memory_service()
            assert registry.is_initialized("memory")
        except ImportError as e:
            assert "Cannot import memory service" in str(e)
            assert "candidate.memory" in str(e)

    def test_identity_service_error_handling(self):
        """Test graceful handling when identity service unavailable."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        try:
            provider = registry.get_identity_service()
            assert registry.is_initialized("identity")
        except ImportError as e:
            assert "Cannot import identity service" in str(e)
            assert "candidate.identity" in str(e)

    def test_governance_service_error_handling(self):
        """Test graceful handling when governance service unavailable."""
        config = make_resolver()
        registry = ProviderRegistry(config)

        try:
            provider = registry.get_governance_service()
            assert registry.is_initialized("governance")
        except ImportError as e:
            assert "Cannot import governance service" in str(e)


if __name__ == "__main__":
    # Run basic tests
    test = TestProviderRegistry()
    test.test_registry_initialization()
    test.test_make_resolver_defaults()
    test.test_custom_config()
    test.test_config_get_set()
    test.test_register_custom_provider()
    test.test_provider_caching()
    test.test_clear_providers()

    test_methods = TestProviderMethods()
    test_methods.test_provider_methods_exist()
    test_methods.test_provider_methods_are_callable()

    test_import = TestImportSafety()
    test_import.test_registry_import_safety()
    test_import.test_registry_instantiation_no_imports()

    print("✅ All provider registry tests passed")
