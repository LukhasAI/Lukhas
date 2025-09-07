#!/usr/bin/env python3
"""
Service Registry
Central registry for dependency injection to break circular dependencies.
"""
from consciousness.qi import qi
from typing import List
import streamlit as st
from datetime import timezone

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceInterface(ABC):
    """Base interface that all services must implement"""

    @abstractmethod
    def get_service_info(self) -> dict[str, Any]:
        """Get information about this service"""


class ServiceRegistry:
    """
    Central service registry for dependency injection.

    This allows modules to register and retrieve services without
    directly importing each other, breaking circular dependencies.
    """

    def __init__(self):
        # Service instances
        self._services: dict[str, Any] = {}

        # Service factories for lazy initialization
        self._factories: dict[str, Callable[[], Any]] = {}

        # Service metadata
        self._metadata: dict[str, dict[str, Any]] = {}

        # Service initialization status
        self._initialized: dict[str, bool] = {}

    def register_service(
        self,
        name: str,
        service: Any,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Register a service instance.

        Args:
            name: Unique name for the service
            service: Service instance
            metadata: Optional metadata about the service
        """
        self._services[name] = service
        self._initialized[name] = True
        self._metadata[name] = metadata or {
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "type": type(service).__name__,
        }

        logger.info(f"Registered service: {name}")

    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Register a service factory for lazy initialization.

        Args:
            name: Unique name for the service
            factory: Factory function that creates the service
            metadata: Optional metadata about the service
        """
        self._factories[name] = factory
        self._initialized[name] = False
        self._metadata[name] = metadata or {
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "type": "factory",
            "lazy": True,
        }

        logger.info(f"Registered service factory: {name}")

    def get_service(self, name: str, service_type: Optional[type[T]] = None) -> T:
        """
        Get a service by name.

        Args:
            name: Service name
            service_type: Optional type hint for better IDE support

        Returns:
            Service instance

        Raises:
            KeyError: If service not found
        """
        # Check if service needs initialization
        if name in self._factories and not self._initialized.get(name, False):
            # Lazy initialize
            service = self._factories[name]()
            self._services[name] = service
            self._initialized[name] = True
            self._metadata[name]["initialized_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(f"Lazy initialized service: {name}")

        if name not in self._services:
            raise KeyError(f"Service '{name}' not found in registry")

        return self._services[name]

    def has_service(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._services or name in self._factories

    def list_services(self) -> dict[str, dict[str, Any]]:
        """List all registered services with metadata"""
        result = {}

        for name in set(list(self._services.keys()) + list(self._factories.keys())):
            result[name] = {
                "initialized": self._initialized.get(name, False),
                "metadata": self._metadata.get(name, {}),
                "type": (type(self._services[name]).__name__ if name in self._services else "factory"),
            }

        return result

    def unregister_service(self, name: str) -> bool:
        """
        Unregister a service.

        Returns:
            True if service was unregistered, False if not found
        """
        found = False

        if name in self._services:
            del self._services[name]
            found = True

        if name in self._factories:
            del self._factories[name]
            found = True

        if name in self._metadata:
            del self._metadata[name]

        if name in self._initialized:
            del self._initialized[name]

        if found:
            logger.info(f"Unregistered service: {name}")

        return found

    def clear(self) -> None:
        """Clear all registered services"""
        self._services.clear()
        self._factories.clear()
        self._metadata.clear()
        self._initialized.clear()
        logger.info("Cleared all services from registry")


# Global registry instance
_global_registry = ServiceRegistry()


def get_service_registry() -> ServiceRegistry:
    """Get the global service registry"""
    return _global_registry


# Convenience functions


def register_service(name: str, service: Any, metadata: Optional[dict[str, Any]] = None):
    """Register a service with the global registry"""
    _global_registry.register_service(name, service, metadata)


def register_factory(
    name: str,
    factory: Callable[[], Any],
    metadata: Optional[dict[str, Any]] = None,
):
    """Register a service factory with the global registry"""
    _global_registry.register_factory(name, factory, metadata)


def get_service(name: str, service_type: Optional[type[T]] = None) -> T:
    """Get a service from the global registry"""
    return _global_registry.get_service(name, service_type)


def inject_services(**service_names: str) -> Callable:
    """
    Decorator for dependency injection.

    Usage:
        @inject_services(memory='memory_service', learning='learning_service')

        def my_function(data, memory=None, learning=None):
            # memory and learning are automatically injected
            pass
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Inject services
            for param_name, service_name in service_names.items():
                if param_name not in kwargs:
                    kwargs[param_name] = get_service(service_name)

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Service provider classes for specific modules


class MemoryServiceProvider:
    """Provider for memory-related services"""

    @staticmethod
    def register():
        """Register memory services"""

        def create_memory_service():
            from lukhas.memory.core import MemoryCore

            return MemoryCore()

        register_factory(
            "memory_service",
            create_memory_service,
            {"module": "memory", "interface": "MemoryCore"},
        )


class LearningServiceProvider:
    """Provider for learning-related services"""

    @staticmethod
    def register():
        """Register learning services"""

        def create_learning_service():
            from learning.learning_gateway import get_learning_gateway

            return get_learning_gateway()

        register_factory(
            "learning_service",
            create_learning_service,
            {"module": "learning", "interface": "LearningGateway"},
        )


class ConsciousnessServiceProvider:
    """Provider for consciousness-related services"""

    @staticmethod
    def register():
        """Register consciousness services"""

        def create_consciousness_service():
            from lukhas.consciousness.bridge import ConsciousnessBridge

            return ConsciousnessBridge()

        register_factory(
            "consciousness_service",
            create_consciousness_service,
            {"module": "consciousness", "interface": "ConsciousnessBridge"},
        )


class IdentityServiceProvider:
    """Provider for identity-related services"""

    @staticmethod
    def register():
        """Register identity services"""

        def create_identity_service():
            from identity.connector import get_identity_connector

            return get_identity_connector()

        register_factory(
            "identity_service",
            create_identity_service,
            {"module": "identity", "interface": "IdentityConnector"},
        )


class QIBioOptimizerProvider:
    """Provider for quantum bio-optimization services"""

    @staticmethod
    def register():
        """Register quantum bio-optimization adapter"""

        def create_bio_optimizer():
            from qi.bio.bio_optimizer import (
                MockBioOrchestrator,
                QIBioOptimizationAdapter,
            )

            return QIBioOptimizationAdapter(MockBioOrchestrator())

        register_factory(
            "qi_bio_optimizer",
            create_bio_optimizer,
            {
                "module": "quantum",
                "interface": "QIBioOptimizationAdapter",
            },
        )


def register_all_providers():
    """Register all service providers"""
    MemoryServiceProvider.register()
    LearningServiceProvider.register()
    ConsciousnessServiceProvider.register()
    IdentityServiceProvider.register()
    QIBioOptimizerProvider.register()
    logger.info("All service providers registered")


__all__ = [
    "QIBioOptimizerProvider",
    "ServiceInterface",
    "ServiceRegistry",
    "get_service",
    "get_service_registry",
    "inject_services",
    "register_all_providers",
    "register_factory",
    "register_service",
]
