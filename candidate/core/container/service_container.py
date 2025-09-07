"""
LUKHAS Service Container - Professional Dependency Injection
Centralizes service management without adding bridge components
"""
import inspect
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Union

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Service lifetime scopes"""

    SINGLETON = "singleton"  # One instance for entire application
    TRANSIENT = "transient"  # New instance each time
    SCOPED = "scoped"  # One instance per scope (e.g., request)


class ServiceDescriptor:
    """Describes a registered service"""

    def __init__(
        self,
        service_type: type,
        implementation: Union[type, Callable, Any],
        lifetime: ServiceLifetime,
        factory: Optional[Callable] = None,
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.factory = factory
        self.instance = None  # For singletons


class IServiceProvider(ABC):
    """Interface for service resolution"""

    @abstractmethod
    def get_service(self, service_type: type[T]) -> Optional[T]:
        """Get a service instance"""

    @abstractmethod
    def get_required_service(self, service_type: type[T]) -> T:
        """Get a service instance, raise if not found"""


class ServiceContainer(IServiceProvider):
    """Professional dependency injection container"""

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}
        self._scoped_instances: dict[type, Any] = {}
        self._resolving: set = set()  # Prevent circular dependencies

    def register_singleton(
        self,
        service_type: type[T],
        implementation: Union[type[T], T, Callable[[], T]],
    ) -> "ServiceContainer":
        """Register a singleton service"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON,
        )
        self._services[service_type] = descriptor
        return self

    def register_transient(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[[], T]],
    ) -> "ServiceContainer":
        """Register a transient service"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT,
        )
        self._services[service_type] = descriptor
        return self

    def register_scoped(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[[], T]],
    ) -> "ServiceContainer":
        """Register a scoped service"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED,
        )
        self._services[service_type] = descriptor
        return self

    def register_factory(
        self,
        service_type: type[T],
        factory: Callable[[IServiceProvider], T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ) -> "ServiceContainer":
        """Register a service with a factory function"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=None,
            lifetime=lifetime,
            factory=factory,
        )
        self._services[service_type] = descriptor
        return self

    def get_service(self, service_type: type[T]) -> Optional[T]:
        """Resolve a service"""
        try:
            return self._resolve_service(service_type)
        except Exception as e:
            logger.debug(f"Failed to resolve {service_type.__name__}: {e}")
            return None

    def get_required_service(self, service_type: type[T]) -> T:
        """Resolve a required service"""
        service = self._resolve_service(service_type)
        if service is None:
            raise ValueError(f"Service {service_type.__name__} not registered")
        return service

    def _resolve_service(self, service_type: type[T]) -> Optional[T]:
        """Internal service resolution"""
        if service_type not in self._services:
            return None

        # Circular dependency check
        if service_type in self._resolving:
            raise ValueError(f"Circular dependency detected for {service_type.__name__}")

        descriptor = self._services[service_type]

        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is None:
                self._resolving.add(service_type)
                try:
                    descriptor.instance = self._create_instance(descriptor)
                finally:
                    self._resolving.remove(service_type)
            return descriptor.instance

        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type not in self._scoped_instances:
                self._resolving.add(service_type)
                try:
                    self._scoped_instances[service_type] = self._create_instance(descriptor)
                finally:
                    self._resolving.remove(service_type)
            return self._scoped_instances[service_type]

        else:  # TRANSIENT
            self._resolving.add(service_type)
            try:
                return self._create_instance(descriptor)
            finally:
                self._resolving.remove(service_type)

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a service instance"""
        # Use factory if provided
        if descriptor.factory:
            return descriptor.factory(self)

        implementation = descriptor.implementation

        # If already an instance, return it
        if not inspect.isclass(implementation):
            return implementation

        # Create instance with dependency injection
        return self._instantiate_with_injection(implementation)

    def _instantiate_with_injection(self, cls: type) -> Any:
        """Instantiate a class with constructor injection"""
        sig = inspect.signature(cls.__init__)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Try to resolve by type annotation
            if param.annotation != param.empty:
                service = self.get_service(param.annotation)
                if service is not None:
                    kwargs[param_name] = service
                elif param.default == param.empty:
                    raise ValueError(f"Cannot resolve required parameter {param_name} of type {param.annotation}")

        return cls(**kwargs)

    def create_scope(self) -> "ServiceScope":
        """Create a new service scope"""
        return ServiceScope(self)


class ServiceScope(IServiceProvider):
    """Scoped service provider"""

    def __init__(self, parent: ServiceContainer):
        self._parent = parent
        self._scoped_instances: dict[type, Any] = {}

    def get_service(self, service_type: type[T]) -> Optional[T]:
        """Get service within scope"""
        descriptor = self._parent._services.get(service_type)
        if not descriptor:
            return None

        if descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type not in self._scoped_instances:
                self._scoped_instances[service_type] = self._parent._create_instance(descriptor)
            return self._scoped_instances[service_type]

        return self._parent.get_service(service_type)

    def get_required_service(self, service_type: type[T]) -> T:
        """Get required service within scope"""
        service = self.get_service(service_type)
        if service is None:
            raise ValueError(f"Service {service_type.__name__} not registered")
        return service

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup scoped instances if needed
        self._scoped_instances.clear()


# Global container instance
_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container"""
    return _container


# Decorator for automatic registration


def injectable(lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
    """Decorator to mark a class as injectable"""

    def decorator(cls: type[T]) -> type[T]:
        # Auto-register with container
        if lifetime == ServiceLifetime.SINGLETON:
            _container.register_singleton(cls, cls)
        elif lifetime == ServiceLifetime.SCOPED:
            _container.register_scoped(cls, cls)
        else:
            _container.register_transient(cls, cls)

        # Mark as injectable
        cls._injectable = True
        cls._lifetime = lifetime
        return cls

    return decorator


# Neuroplastic tags
# TAG:core
# TAG:container
# TAG:dependency_injection
# TAG:professional_architecture
