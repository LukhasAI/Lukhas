"""
Provider Registry
=================
Runtime provider injection to eliminate import-time dependencies.

This module enables lazy loading of candidate/labs modules only when needed,
preventing import-time violations in the lane isolation architecture.

Architecture:
- lukhas/ (production) MUST NOT import candidate/ or labs/ at module load time
- Providers are loaded lazily at runtime via importlib
- Configuration is resolved from environment or test overrides
"""

import importlib
import logging
from typing import Any, Optional, TYPE_CHECKING

from core.adapters.config_resolver import Config

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # Import types for static analysis only
    from labs.consciousness.reflection.openai_modulated_service import OpenAIModulatedService


class ProviderRegistry:
    """
    Registry for runtime dependency injection.

    Provides lazy loading of candidate/labs modules to prevent import-time
    dependencies from production code.
    """

    def __init__(self, config: Config):
        """
        Initialize provider registry.

        Args:
            config: Configuration resolver
        """
        self.config = config
        self._providers: dict[str, Any] = {}
        self._initialized: dict[str, bool] = {}

        logger.debug(f"ProviderRegistry initialized (env={config.environment}, mock={config.mock_providers})")

    def get_openai(self) -> "OpenAIModulatedService":
        """
        Get OpenAI provider instance (lazy loaded).

        Returns:
            OpenAIModulatedService instance from labs

        Raises:
            ImportError: If labs module is not available
        """
        provider_key = "openai"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Lazy import at runtime
            module = importlib.import_module("labs.consciousness.reflection.openai_modulated_service")
            OpenAIModulatedService = getattr(module, "OpenAIModulatedService")

            # Create instance
            instance = OpenAIModulatedService(
                api_key=self.config.openai_api_key,
                model=self.config.openai_model,
                temperature=self.config.openai_temperature,
            )

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info(f"Loaded OpenAI provider: {self.config.openai_model}")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load OpenAI provider: {e}")
            raise ImportError(
                f"Cannot import OpenAI provider from labs. "
                f"Ensure labs.consciousness.reflection.openai_modulated_service is available. "
                f"Error: {e}"
            )

    def get_consciousness_service(self) -> Any:
        """
        Get consciousness service provider (lazy loaded).

        Returns:
            Consciousness service instance from candidate
        """
        provider_key = "consciousness"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Lazy import at runtime
            module = importlib.import_module("candidate.consciousness.unified_consciousness_service")
            ConsciousnessService = getattr(module, "UnifiedConsciousnessService")

            instance = ConsciousnessService()

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info("Loaded consciousness service provider")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load consciousness service: {e}")
            raise ImportError(
                f"Cannot import consciousness service from candidate. "
                f"Error: {e}"
            )

    def get_memory_service(self) -> Any:
        """
        Get memory service provider (lazy loaded).

        Returns:
            Memory service instance from candidate
        """
        provider_key = "memory"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Lazy import at runtime
            module = importlib.import_module("candidate.memory.memory_service")
            MemoryService = getattr(module, "MemoryService")

            instance = MemoryService()

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info("Loaded memory service provider")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load memory service: {e}")
            raise ImportError(
                f"Cannot import memory service from candidate. "
                f"Error: {e}"
            )

    def get_provider(self, name: str) -> Optional[Any]:
        """
        Get a registered provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance if registered, None otherwise
        """
        return self._providers.get(name)

    def register_provider(self, name: str, instance: Any) -> None:
        """
        Register a custom provider instance.

        Args:
            name: Provider name
            instance: Provider instance
        """
        self._providers[name] = instance
        self._initialized[name] = True
        logger.info(f"Registered custom provider: {name}")

    def is_initialized(self, name: str) -> bool:
        """Check if a provider is initialized."""
        return self._initialized.get(name, False)

    def clear(self) -> None:
        """Clear all providers (useful for testing)."""
        self._providers.clear()
        self._initialized.clear()
        logger.debug("Cleared all providers")
