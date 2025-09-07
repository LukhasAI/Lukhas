import logging

logger = logging.getLogger(__name__)
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: service_registry.py
# MODULE: orchestration.service_registry
# DESCRIPTION: Service registry for managing high-level services without circular dependencies
# DEPENDENCIES: typing, structlog
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
Service Registry for LUKHAS AI System

This module provides a centralized registry for high-level services (learning, etc.)
to avoid circular dependencies between core and feature modules.

Architecture principle: core → memory → orchestration → consciousness → features → api
Services registered here can be accessed by core modules without importing from higher layers.
"""

from typing import Any, Callable, Optional

import structlog

# Initialize logger
logger = structlog.get_logger("ΛTRACE.orchestration.service_registry")


class ServiceRegistry:
    """
    Central registry for high-level services.

    This registry follows the Inversion of Control (IoC) pattern to prevent
    circular dependencies between layers. Services are registered by name
    and can be retrieved by any module without direct imports.
    """

    def __init__(self):
        """Initialize the service registry."""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        logger.info("ΛTRACE: ServiceRegistry initialized")

    def register_service(self, name: str, service: Any) -> None:
        """
        Register a service instance.

        Args:
            name: Service identifier (e.g., 'learning', 'quantum')
            service: The service instance
        """
        self._services[name] = service
        logger.info(
            f"ΛTRACE: Registered service '{name}'",
            service_type=type(service).__name__,
        )

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a service factory for lazy initialization.

        Args:
            name: Service identifier
            factory: Callable that returns a service instance
        """
        self._factories[name] = factory
        logger.info(f"ΛTRACE: Registered factory for service '{name}'")

    def get_service(self, name: str) -> Optional[Any]:
        """
        Retrieve a service by name.

        If the service hasn't been instantiated but a factory exists,
        it will be created on first access (lazy initialization).

        Args:
            name: Service identifier

        Returns:
            The service instance or None if not found
        """
        # Check if service is already instantiated
        if name in self._services:
            return self._services[name]

        # Check if we have a factory for lazy initialization
        if name in self._factories:
            logger.info(f"ΛTRACE: Lazy-initializing service '{name}'")
            try:
                service = self._factories[name]()
                self._services[name] = service
                return service
            except Exception as e:
                logger.error(
                    f"ΛTRACE: Failed to initialize service '{name}'",
                    error=str(e),
                    exc_info=True,
                )
                return None

        logger.warning(f"ΛTRACE: Service '{name}' not found in registry")
        return None

    def unregister_service(self, name: str) -> bool:
        """
        Remove a service from the registry.

        Args:
            name: Service identifier

        Returns:
            True if service was removed, False if not found
        """
        removed = False
        if name in self._services:
            del self._services[name]
            removed = True
        if name in self._factories:
            del self._factories[name]
            removed = True

        if removed:
            logger.info(f"ΛTRACE: Unregistered service '{name}'")
        else:
            logger.warning(f"ΛTRACE: Service '{name}' not found for removal")

        return removed

    def list_services(self) -> dict[str, str]:
        """
        List all registered services and their status.

        Returns:
            Dictionary mapping service names to their status
        """
        services = {}

        # Add instantiated services
        for name in self._services:
            services[name] = "active"

        # Add factory-only services
        for name in self._factories:
            if name not in self._services:
                services[name] = "registered (not initialized)"

        return services

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        logger.info("ΛTRACE: Service registry cleared")


# Global service registry instance
_service_registry = ServiceRegistry()

# Convenience functions for module-level access


def register_service(name: str, service: Any) -> None:
    """Register a service in the global registry."""
    _service_registry.register_service(name, service)


def register_factory(name: str, factory: Callable[[], Any]) -> None:
    """Register a service factory in the global registry."""
    _service_registry.register_factory(name, factory)


def get_service(name: str) -> Optional[Any]:
    """Get a service from the global registry."""
    return _service_registry.get_service(name)


def unregister_service(name: str) -> bool:
    """Remove a service from the global registry."""
    return _service_registry.unregister_service(name)


def list_services() -> dict[str, str]:
    """List all services in the global registry."""
    return _service_registry.list_services()


# Service name constants to avoid typos


class ServiceNames:
    """Constants for service names."""

    LEARNING = "learning"
    QUANTUM = "quantum"
    ETHICS = "ethics"
    MEMORY = "memory"
    CREATIVITY = "creativity"
    CONSCIOUSNESS = "consciousness"
    IDENTITY = "identity"


if __name__ == "__main__":
    # Example usage
    logger.info("ΛTRACE: Service Registry example")

    # Register a mock service

    class MockLearningService:
        def learn_from_data(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
            return {"success": True, "message": "Mock learning completed"}

    # Register directly
    register_service(ServiceNames.LEARNING, MockLearningService())

    # Or register with factory
    register_factory(
        ServiceNames.QUANTUM,
        lambda: type("QIService", (), {"compute": lambda: "quantum"})(),
    )

    # List services
    print("Registered services:", list_services())

    # Get and use service
    learning_service = get_service(ServiceNames.LEARNING)
    if learning_service:
        result = learning_service.learn_from_data("test_user", {"data": "test"})
        print("Learning result:", result)
