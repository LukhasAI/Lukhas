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
from typing import TYPE_CHECKING, Any, Optional

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
            OpenAIModulatedService = module.OpenAIModulatedService

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

        This provider loads the unified consciousness service from candidate/
        at runtime, enabling consciousness processing without import-time
        dependencies.

        Returns:
            UnifiedConsciousnessService instance from candidate

        Raises:
            ImportError: If candidate.consciousness module is not available
        """
        provider_key = "consciousness"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Try multiple possible locations for consciousness service
            possible_modules = [
                "candidate.consciousness.unified_consciousness_service",
                "candidate.consciousness.consciousness_service",
                "labs.consciousness.consciousness_service",
            ]

            service_class = None
            loaded_module_name = None

            for module_name in possible_modules:
                try:
                    module = importlib.import_module(module_name)
                    # Try different class names
                    for class_name in ["UnifiedConsciousnessService", "ConsciousnessService"]:
                        service_class = getattr(module, class_name, None)
                        if service_class:
                            loaded_module_name = module_name
                            break
                    if service_class:
                        break
                except ImportError:
                    continue

            if not service_class:
                raise ImportError(
                    f"Could not find consciousness service in any of: {possible_modules}"
                )

            instance = service_class()

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info(f"Loaded consciousness service provider from {loaded_module_name}")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load consciousness service: {e}")
            raise ImportError(
                f"Cannot import consciousness service from labs. "
                f"Ensure candidate.consciousness is available. "
                f"Error: {e}"
            )

    def get_memory_service(self) -> Any:
        """
        Get memory service provider (lazy loaded).

        This provider loads memory system services from candidate/ at runtime,
        enabling memory operations (fold systems, emotional memory, temporal
        memory) without import-time dependencies.

        Returns:
            MemoryService instance from candidate

        Raises:
            ImportError: If candidate.memory module is not available
        """
        provider_key = "memory"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Try multiple possible locations for memory service
            possible_modules = [
                "candidate.memory.memory_service",
                "candidate.memory.unified_memory",
                "labs.memory.memory_service",
            ]

            service_class = None
            loaded_module_name = None

            for module_name in possible_modules:
                try:
                    module = importlib.import_module(module_name)
                    # Try different class names
                    for class_name in ["MemoryService", "UnifiedMemory", "MemorySystem"]:
                        service_class = getattr(module, class_name, None)
                        if service_class:
                            loaded_module_name = module_name
                            break
                    if service_class:
                        break
                except ImportError:
                    continue

            if not service_class:
                raise ImportError(
                    f"Could not find memory service in any of: {possible_modules}"
                )

            instance = service_class()

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info(f"Loaded memory service provider from {loaded_module_name}")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load memory service: {e}")
            raise ImportError(
                f"Cannot import memory service from labs. "
                f"Ensure candidate.memory is available. "
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

    def get_identity_service(self) -> Any:
        """
        Get identity service provider (lazy loaded).

        This provider loads the Lambda ID identity system from candidate/
        at runtime, enabling identity operations (Lambda ID, namespace
        isolation, multi-modal auth) without import-time dependencies.

        Returns:
            Identity service instance from candidate

        Raises:
            ImportError: If candidate.identity module is not available
        """
        provider_key = "identity"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Try multiple possible locations for identity service
            possible_modules = [
                "candidate.identity.lambda_id",
                "candidate.identity.identity_service",
                "lukhas.identity.lambda_id",
            ]

            service_class = None
            loaded_module_name = None

            for module_name in possible_modules:
                try:
                    module = importlib.import_module(module_name)
                    # Try different class names
                    for class_name in ["LambdaIDService", "IdentityService", "LambdaID"]:
                        service_class = getattr(module, class_name, None)
                        if service_class:
                            loaded_module_name = module_name
                            break
                    if service_class:
                        break
                except ImportError:
                    continue

            if not service_class:
                raise ImportError(
                    f"Could not find identity service in any of: {possible_modules}"
                )

            instance = service_class()

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info(f"Loaded identity service provider from {loaded_module_name}")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load identity service: {e}")
            raise ImportError(
                f"Cannot import identity service from labs. "
                f"Ensure candidate.identity is available. "
                f"Error: {e}"
            )

    def get_governance_service(self) -> Any:
        """
        Get governance service provider (lazy loaded).

        This provider loads governance and Guardian systems from candidate/
        at runtime, enabling constitutional AI and ethics validation without
        import-time dependencies.

        Returns:
            Governance service instance from candidate

        Raises:
            ImportError: If governance module is not available
        """
        provider_key = "governance"

        if provider_key in self._providers:
            return self._providers[provider_key]

        try:
            # Try multiple possible locations for governance service
            possible_modules = [
                "candidate.governance.unified_constitutional_ai",
                "candidate.governance.governance_service",
                "labs.governance.guardian_service",
            ]

            service_class = None
            loaded_module_name = None

            for module_name in possible_modules:
                try:
                    module = importlib.import_module(module_name)
                    # Try different class names
                    for class_name in [
                        "UnifiedConstitutionalAI",
                        "GovernanceService",
                        "GuardianService",
                    ]:
                        service_class = getattr(module, class_name, None)
                        if service_class:
                            loaded_module_name = module_name
                            break
                    if service_class:
                        break
                except ImportError:
                    continue

            if not service_class:
                raise ImportError(
                    f"Could not find governance service in any of: {possible_modules}"
                )

            instance = service_class()

            self._providers[provider_key] = instance
            self._initialized[provider_key] = True

            logger.info(f"Loaded governance service provider from {loaded_module_name}")

            return instance

        except ImportError as e:
            logger.error(f"Failed to load governance service: {e}")
            raise ImportError(
                f"Cannot import governance service. "
                f"Ensure governance modules are available. "
                f"Error: {e}"
            )

    def clear(self) -> None:
        """Clear all providers (useful for testing)."""
        self._providers.clear()
        self._initialized.clear()
        logger.debug("Cleared all providers")
