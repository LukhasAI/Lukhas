"""
💉 Dependency Injection System
=============================
Provides dependency injection to break circular dependencies.
"""

import asyncio
import functools
import inspect
import logging
from typing import Any, Callable, Optional, TypeVar, Union

T = TypeVar("T")

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Registry for dependency injection services"""

    def __init__(self):
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}
        self._interfaces: dict[type, str] = {}

    def register_service(self, name: str, service: Any, singleton: bool = True) -> None:
        """Register a service instance"""
        if singleton:
            self._singletons[name] = service
        else:
            self._services[name] = service

        # Register interface mapping if service implements one
        for base in inspect.getmro(type(service)):
            if base != object and hasattr(base, "__abstractmethods__"):
                self._interfaces[base] = name

        logger.debug(f"Registered service: {name}")

    def register_factory(self, name: str, factory: Callable, singleton: bool = True) -> None:
        """Register a service factory function"""
        self._factories[name] = (factory, singleton)
        logger.debug(f"Registered factory: {name}")

    def register_interface(self, interface: type, implementation_name: str) -> None:
        """Register interface to implementation mapping"""
        self._interfaces[interface] = implementation_name

    def get_service(self, name: str) -> Any:
        """Get a service by name"""
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]

        # Check registered services
        if name in self._services:
            return self._services[name]

        # Check factories
        if name in self._factories:
            factory, is_singleton = self._factories[name]
            instance = factory()

            if is_singleton:
                self._singletons[name] = instance

            return instance

        raise ValueError(f"Service '{name}' not found in registry")

    def get_by_interface(self, interface: type[T]) -> T:
        """Get service by interface type"""
        if interface in self._interfaces:
            name = self._interfaces[interface]
            return self.get_service(name)
        else:
            raise ValueError(f"No implementation registered for interface {interface}")

    def has_service(self, name: str) -> bool:
        """Check if service is registered"""
        return name in self._singletons or name in self._services or name in self._factories

    def clear(self) -> None:
        """Clear all registered services"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._interfaces.clear()

    def list_services(self) -> dict[str, str]:
        """List all registered services"""
        services = {}

        for name in self._singletons:
            services[name] = f"singleton: {type(self._singletons[name]).__name__}"

        for name in self._services:
            services[name] = f"instance: {type(self._services[name]).__name__}"

        for name in self._factories:
            services[name] = "factory"

        return services


# Global registry instance
_global_registry = ServiceRegistry()


def get_registry() -> ServiceRegistry:
    """Get the global service registry"""
    return _global_registry


def register_service(name: str, service: Any, singleton: bool = True) -> None:
    """Register a service in the global registry"""
    _global_registry.register_service(name, service, singleton)


def register_factory(name: str, factory: Callable, singleton: bool = True) -> None:
    """Register a service factory in the global registry"""
    _global_registry.register_factory(name, factory, singleton)


def register_interface(interface: type, implementation_name: str) -> None:
    """Register interface mapping in the global registry"""
    _global_registry.register_interface(interface, implementation_name)


def get_service(name: str) -> Any:
    """Get a service from the global registry"""
    return _global_registry.get_service(name)


def get_by_interface(interface: type[T]) -> T:
    """Get service by interface from the global registry"""
    return _global_registry.get_by_interface(interface)


def clear_registry() -> None:
    """Clear the global registry"""
    _global_registry.clear()


def inject(service_name: Optional[str] = None, interface: Optional[type] = None):
    """
    Decorator for dependency injection.

    Args:
        service_name: Name of service to inject
        interface: Interface type to inject

    Usage:
        @inject(service_name="memory_service")

        def process_data(data, memory_service=None):
            return memory_service.store(data)

        @inject(interface=MemoryInterface)

        def process_data(data, memory_interface=None):
            return memory_interface.store(data)
    """

    def decorator(func):
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Inject dependencies
            if service_name and service_name not in kwargs:
                if len(args) < len(param_names) or param_names[-1] not in kwargs:
                    try:
                        service = get_service(service_name)
                        kwargs[service_name.replace("_service", "_interface" if interface else "")] = service
                    except ValueError:
                        logger.warning(f"Service '{service_name}' not found for injection")

            if interface and not any(isinstance(v, interface) for v in kwargs.values()):
                try:
                    service = get_by_interface(interface)
                    # Find parameter name for this interface
                    interface_param = None
                    for param_name, param in sig.parameters.items():
                        if param.annotation == interface or (
                            hasattr(param.annotation, "__origin__")
                            and param.annotation.__origin__ is Union
                            and interface in param.annotation.__args__
                        ):
                            interface_param = param_name
                            break

                    if interface_param and interface_param not in kwargs:
                        kwargs[interface_param] = service

                except ValueError:
                    logger.warning(f"No implementation found for interface {interface}")

            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Same injection logic for sync functions
            if service_name and service_name not in kwargs:
                if len(args) < len(param_names) or param_names[-1] not in kwargs:
                    try:
                        service = get_service(service_name)
                        kwargs[service_name.replace("_service", "_interface" if interface else "")] = service
                    except ValueError:
                        logger.warning(f"Service '{service_name}' not found for injection")

            if interface and not any(isinstance(v, interface) for v in kwargs.values()):
                try:
                    service = get_by_interface(interface)
                    # Find parameter name for this interface
                    interface_param = None
                    for param_name, param in sig.parameters.items():
                        if param.annotation == interface or (
                            hasattr(param.annotation, "__origin__")
                            and param.annotation.__origin__ is Union
                            and interface in param.annotation.__args__
                        ):
                            interface_param = param_name
                            break

                    if interface_param and interface_param not in kwargs:
                        kwargs[interface_param] = service

                except ValueError:
                    logger.warning(f"No implementation found for interface {interface}")

            return func(*args, **kwargs)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ServiceLocator:
    """Service locator pattern implementation"""

    @staticmethod
    def get_memory_service():
        """Get memory service"""
        try:
            return get_service("memory_service")
        except ValueError:
            logger.warning("Memory service not registered")
            return None

    @staticmethod
    def get_consciousness_service():
        """Get consciousness service"""
        try:
            return get_service("consciousness_service")
        except ValueError:
            logger.warning("Consciousness service not registered")
            return None

    @staticmethod
    def get_guardian_service():
        """Get guardian service"""
        try:
            return get_service("guardian_service")
        except ValueError:
            logger.warning("Guardian service not registered")
            return None

    @staticmethod
    def get_orchestration_service():
        """Get orchestration service"""
        try:
            return get_service("orchestration_service")
        except ValueError:
            logger.warning("Orchestration service not registered")
            return None


# Lazy loading utilities


class LazyProxy:
    """Proxy for lazy loading of services"""

    def __init__(self, service_name: str):
        self._service_name = service_name
        self._service = None

    def _get_service(self):
        if self._service is None:
            self._service = get_service(self._service_name)
        return self._service

    def __getattr__(self, name):
        return getattr(self._get_service(), name)

    def __call__(self, *args, **kwargs):
        return self._get_service()(*args, **kwargs)


def lazy_service(service_name: str) -> LazyProxy:
    """Create a lazy proxy for a service"""
    return LazyProxy(service_name)


# Module-level lazy services for common modules
memory_service = lazy_service("memory_service")
consciousness_service = lazy_service("consciousness_service")
guardian_service = lazy_service("guardian_service")
orchestration_service = lazy_service("orchestration_service")
