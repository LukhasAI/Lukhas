"""Provider Registry - Runtime dependency injection for optional providers.

Enables production modules to use optional 'labs' features without
import-time dependencies. Providers are resolved at runtime with
graceful degradation when unavailable.

Usage:
    from core.adapters.provider_registry import ProviderRegistry
    from core.adapters.config_resolver import make_resolver

    registry = ProviderRegistry(make_resolver())
    openai = registry.get_openai()
    if openai is None:
        raise RuntimeError("OpenAI provider unavailable")
"""

import importlib
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Central registry for runtime provider injection.

    Resolves optional dependencies (labs modules) at runtime
    without requiring import-time availability.
    """

    def __init__(self, config_resolver):
        """Initialize registry with configuration resolver.

        Args:
            config_resolver: Configuration resolver instance
        """
        self.config = config_resolver
        self._cache: Dict[str, Optional[Any]] = {}

    def get_openai(self) -> Optional[Any]:
        """Get OpenAI provider instance.

        Returns:
            OpenAI client or None if unavailable
        """
        if "openai" not in self._cache:
            self._cache["openai"] = self._load_provider(
                "labs.providers.openai",
                "OpenAIProvider"
            )
        return self._cache["openai"]

    def get_anthropic(self) -> Optional[Any]:
        """Get Anthropic provider instance.

        Returns:
            Anthropic client or None if unavailable
        """
        if "anthropic" not in self._cache:
            self._cache["anthropic"] = self._load_provider(
                "labs.providers.anthropic",
                "AnthropicProvider"
            )
        return self._cache["anthropic"]

    def get_memory(self) -> Optional[Any]:
        """Get memory provider instance.

        Returns:
            Memory provider or None if unavailable
        """
        if "memory" not in self._cache:
            self._cache["memory"] = self._load_provider(
                "labs.memory.fold_system.memory_fold_system",
                "MemoryFoldSystem"
            )
        return self._cache["memory"]

    def get_guardian(self) -> Optional[Any]:
        """Get guardian provider instance.

        Returns:
            Guardian provider or None if unavailable
        """
        if "guardian" not in self._cache:
            self._cache["guardian"] = self._load_provider(
                "labs.governance.guardian_sentinel",
                "GuardianSentinel"
            )
        return self._cache["guardian"]

    def get_provider(self, provider_name: str) -> Optional[Any]:
        """Get provider by name with caching.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider instance or None if unavailable
        """
        if provider_name not in self._cache:
            # Try to load from config
            module_path = self.config.get(f"providers.{provider_name}.module")
            class_name = self.config.get(f"providers.{provider_name}.class")

            if module_path and class_name:
                self._cache[provider_name] = self._load_provider(
                    module_path,
                    class_name
                )
            else:
                logger.warning(f"Provider '{provider_name}' not configured")
                self._cache[provider_name] = None

        return self._cache[provider_name]

    def _load_provider(
        self,
        module_path: str,
        class_name: str
    ) -> Optional[Any]:
        """Load provider class dynamically.

        Args:
            module_path: Python module path
            class_name: Class name to import

        Returns:
            Provider instance or None if load fails
        """
        try:
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)
            return provider_class()
        except (ImportError, AttributeError) as e:
            logger.debug(
                f"Provider {class_name} from {module_path} unavailable: {e}"
            )
            return None

    def clear_cache(self):
        """Clear provider cache (useful for testing)."""
        self._cache.clear()

    def is_available(self, provider_name: str) -> bool:
        """Check if provider is available.

        Args:
            provider_name: Name of the provider

        Returns:
            True if provider is available, False otherwise
        """
        provider = self.get_provider(provider_name)
        return provider is not None
