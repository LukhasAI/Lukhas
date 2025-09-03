#!/usr/bin/env python3
"""
Dependency Injection Container for Dream Commerce Orchestrator
Provides service registration, resolution, and lifecycle management
"""

import asyncio
import inspect
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional


class ServiceLifecycle(Enum):
    """Service lifecycle types"""

    SINGLETON = "singleton"  # One instance for entire application
    SCOPED = "scoped"  # One instance per scope/request
    TRANSIENT = "transient"  # New instance every time


class CircularDependencyError(Exception):
    """Raised when circular dependency is detected"""


class ServiceNotFoundError(Exception):
    """Raised when requested service is not registered"""


@dataclass
class ServiceDescriptor:
    """Describes a registered service"""

    name: str
    factory: Callable
    lifecycle: ServiceLifecycle
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    instance: Optional[Any] = None  # For singletons
    created_at: datetime = field(default_factory=datetime.now)


class DependencyContainer:
    """
    Advanced Dependency Injection Container

    Features:
    - Service registration with lifecycles
    - Automatic dependency resolution
    - Circular dependency detection
    - Scoped service management
    - Graceful degradation support
    - Service health monitoring
    """

    def __init__(self):
        self.services: dict[str, ServiceDescriptor] = {}
        self.scoped_instances: dict[str, dict[str, Any]] = {}
        self.resolution_stack: set[str] = set()
        self.health_checks: dict[str, Callable] = {}
        self.fallback_services: dict[str, str] = {}  # Primary -> Fallback mapping
        self._lock = asyncio.Lock()
        # Guardrails to avoid hangs during health checks/creation
        self.health_check_timeout = 0.5  # seconds
        self.instance_creation_timeout = 1.0  # seconds (for async factories)

    async def register_service(
        self,
        name: str,
        factory: Callable,
        lifecycle: ServiceLifecycle = ServiceLifecycle.TRANSIENT,
        dependencies: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Register a service with the container

        Args:
            name: Service name
            factory: Factory function or class to create service
            lifecycle: Service lifecycle type
            dependencies: List of dependency service names
            metadata: Additional metadata about the service
        """
        async with self._lock:
            # Auto-detect dependencies if not provided
            if dependencies is None:
                dependencies = await self._detect_dependencies(factory)

            descriptor = ServiceDescriptor(
                name=name,
                factory=factory,
                lifecycle=lifecycle,
                dependencies=dependencies or [],
                metadata=metadata or {},
            )

            self.services[name] = descriptor

    async def _detect_dependencies(self, factory: Callable) -> list[str]:
        """
        Auto-detect dependencies from factory function signature

        Args:
            factory: Factory function to analyze

        Returns:
            List of detected dependency names
        """
        dependencies = []

        if inspect.isclass(factory):
            # Check __init__ method for classes
            signature = inspect.signature(factory.__init__)
        else:
            signature = inspect.signature(factory)

        for param_name, param in signature.parameters.items():
            if param_name in ["self", "cls"]:
                continue

            # Check if parameter has a type annotation that matches a service
            if param.annotation != inspect.Parameter.empty:
                type_name = getattr(param.annotation, "__name__", str(param.annotation))

                # Check if this type is registered as a service
                for service_name in self.services:
                    if service_name.lower() == type_name.lower():
                        dependencies.append(service_name)
                        break

        return dependencies

    async def get_service(
        self, name: str, scope_id: Optional[str] = None, use_fallback: bool = True
    ) -> Any:
        """
        Get a service instance

        Args:
            name: Service name
            scope_id: Scope identifier for scoped services
            use_fallback: Whether to use fallback service if primary fails

        Returns:
            Service instance

        Raises:
            ServiceNotFoundError: If service is not registered
            CircularDependencyError: If circular dependency is detected
        """
        if name not in self.services:
            if use_fallback and name in self.fallback_services:
                return await self.get_service(
                    self.fallback_services[name], scope_id, False
                )
            raise ServiceNotFoundError(f"Service '{name}' is not registered")

        # Check for circular dependencies
        if name in self.resolution_stack:
            raise CircularDependencyError(
                f"Circular dependency detected: {' -> '.join(self.resolution_stack)} -> {name}"
            )

        descriptor = self.services[name]

        # Handle different lifecycles
        if descriptor.lifecycle == ServiceLifecycle.SINGLETON:
            return await self._get_singleton(descriptor)
        elif descriptor.lifecycle == ServiceLifecycle.SCOPED:
            return await self._get_scoped(descriptor, scope_id)
        else:  # TRANSIENT
            return await self._create_instance(descriptor)

    async def _get_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """
        Get or create singleton instance

        Args:
            descriptor: Service descriptor

        Returns:
            Singleton instance
        """
        async with self._lock:
            if descriptor.instance is None:
                descriptor.instance = await self._create_instance(descriptor)
            return descriptor.instance

    async def _get_scoped(
        self, descriptor: ServiceDescriptor, scope_id: Optional[str]
    ) -> Any:
        """
        Get or create scoped instance

        Args:
            descriptor: Service descriptor
            scope_id: Scope identifier

        Returns:
            Scoped instance
        """
        if scope_id is None:
            scope_id = "default"

        async with self._lock:
            if scope_id not in self.scoped_instances:
                self.scoped_instances[scope_id] = {}

            if descriptor.name not in self.scoped_instances[scope_id]:
                instance = await self._create_instance(descriptor)
                self.scoped_instances[scope_id][descriptor.name] = instance

            return self.scoped_instances[scope_id][descriptor.name]

    async def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """
        Create a new instance of a service

        Args:
            descriptor: Service descriptor

        Returns:
            New service instance
        """
        self.resolution_stack.add(descriptor.name)

        try:
            # Resolve dependencies
            dependencies = {}
            for dep_name in descriptor.dependencies:
                dependencies[dep_name] = await self.get_service(dep_name)

            # Create instance
            if inspect.iscoroutinefunction(descriptor.factory):
                # Protect against long-running async factories
                instance = await asyncio.wait_for(
                    descriptor.factory(**dependencies),
                    timeout=self.instance_creation_timeout,
                )
            else:
                # Synchronous factory; assume fast (can't timebox without thread)
                instance = descriptor.factory(**dependencies)

            return instance

        finally:
            self.resolution_stack.discard(descriptor.name)

    async def register_fallback(self, primary: str, fallback: str):
        """
        Register a fallback service for graceful degradation

        Args:
            primary: Primary service name
            fallback: Fallback service name
        """
        self.fallback_services[primary] = fallback

    async def register_health_check(self, service_name: str, health_check: Callable):
        """
        Register a health check for a service

        Args:
            service_name: Service name
            health_check: Async function that returns True if healthy
        """
        self.health_checks[service_name] = health_check

    async def check_service_health(self, service_name: str) -> bool:
        """
        Check if a service is healthy

        Args:
            service_name: Service name to check

        Returns:
            True if healthy, False otherwise
        """
        if service_name not in self.health_checks:
            return True  # Assume healthy if no check registered

        try:
            health_check = self.health_checks[service_name]
            if inspect.iscoroutinefunction(health_check):
                # Bound health checks to avoid hanging
                return await asyncio.wait_for(
                    health_check(), timeout=self.health_check_timeout
                )
            else:
                return health_check()
        except Exception:
            return False

    async def get_healthy_service(
        self, name: str, scope_id: Optional[str] = None
    ) -> Any:
        """
        Get a service instance, falling back if unhealthy

        Args:
            name: Service name
            scope_id: Scope identifier

        Returns:
            Healthy service instance
        """
        # Check primary service health
        if await self.check_service_health(name):
            return await self.get_service(name, scope_id, use_fallback=False)

        # Try fallback if available
        if name in self.fallback_services:
            fallback_name = self.fallback_services[name]
            if await self.check_service_health(fallback_name):
                return await self.get_service(
                    fallback_name, scope_id, use_fallback=False
                )

        # Return primary anyway if no healthy alternative
        return await self.get_service(name, scope_id, use_fallback=False)

    async def dispose_scope(self, scope_id: str):
        """
        Dispose all services in a scope

        Args:
            scope_id: Scope identifier to dispose
        """
        async with self._lock:
            if scope_id in self.scoped_instances:
                # Call dispose on any services that have it
                for _service_name, instance in self.scoped_instances[scope_id].items():
                    if hasattr(instance, "dispose"):
                        if inspect.iscoroutinefunction(instance.dispose):
                            await instance.dispose()
                        else:
                            instance.dispose()

                del self.scoped_instances[scope_id]

    async def dispose_all(self):
        """
        Dispose all services and clean up
        """
        # Dispose all scoped instances
        scope_ids = list(self.scoped_instances.keys())
        for scope_id in scope_ids:
            await self.dispose_scope(scope_id)

        # Dispose singletons
        for descriptor in self.services.values():
            if descriptor.instance and hasattr(descriptor.instance, "dispose"):
                if inspect.iscoroutinefunction(descriptor.instance.dispose):
                    await descriptor.instance.dispose()
                else:
                    descriptor.instance.dispose()

        # Clear all registrations
        self.services.clear()
        self.health_checks.clear()
        self.fallback_services.clear()

    def get_service_info(self) -> dict[str, Any]:
        """
        Get information about all registered services

        Returns:
            Dictionary with service information
        """
        info = {}
        for name, descriptor in self.services.items():
            info[name] = {
                "lifecycle": descriptor.lifecycle.value,
                "dependencies": descriptor.dependencies,
                "has_instance": descriptor.instance is not None,
                "has_health_check": name in self.health_checks,
                "has_fallback": name in self.fallback_services,
                "metadata": descriptor.metadata,
                "created_at": descriptor.created_at.isoformat(),
            }
        return info


# Example service implementations for testing
class MockDreamGenerator:
    """Mock dream generator service"""

    def __init__(self):
        self.generated_count = 0

    async def generate_dream(self, context: dict[str, Any]) -> str:
        self.generated_count += 1
        return f"Dream {self.generated_count} (type: standard)"


class MockEmotionalFilter:
    """Mock emotional filter service"""

    def __init__(self):
        self.filter_count = 0

    async def filter(self, emotional_state: dict[str, float]) -> bool:
        self.filter_count += 1
        return emotional_state.get("stress", 0) < 0.7


class MockVendorPortal:
    """Mock vendor portal service"""

    def __init__(self, dream_generator: MockDreamGenerator):
        self.dream_generator = dream_generator
        self.vendor_count = 0

    async def create_vendor_dream(self, vendor_id: str) -> str:
        self.vendor_count += 1
        dream = await self.dream_generator.generate_dream(
            {"type": "vendor", "id": vendor_id}
        )
        return f"Vendor {vendor_id}: {dream}"


if __name__ == "__main__":

    async def test_container():
        """Test the dependency injection container"""
        container = DependencyContainer()

        print("=" * 80)
        print("📦 DEPENDENCY INJECTION CONTAINER TEST")
        print("=" * 80)

        # Register services
        print("\n🔧 Registering services...")

        await container.register_service(
            "dream_generator", MockDreamGenerator, ServiceLifecycle.SINGLETON
        )

        await container.register_service(
            "emotional_filter", MockEmotionalFilter, ServiceLifecycle.SCOPED
        )

        # Register service with dependencies
        await container.register_service(
            "vendor_portal",
            MockVendorPortal,
            ServiceLifecycle.TRANSIENT,
            dependencies=["dream_generator"],
        )

        print("✅ Services registered")

        # Test singleton
        print("\n🧪 Testing singleton lifecycle...")
        gen1 = await container.get_service("dream_generator")
        gen2 = await container.get_service("dream_generator")
        print(f"Same instance: {gen1 is gen2}")

        # Test scoped
        print("\n🧪 Testing scoped lifecycle...")
        filter1 = await container.get_service("emotional_filter", scope_id="request1")
        filter2 = await container.get_service("emotional_filter", scope_id="request1")
        filter3 = await container.get_service("emotional_filter", scope_id="request2")
        print(f"Same in scope: {filter1 is filter2}")
        print(f"Different scope: {filter1 is filter3}")

        # Test dependency injection
        print("\n🧪 Testing dependency injection...")
        portal = await container.get_service("vendor_portal")
        result = await portal.create_vendor_dream("vendor_123")
        print(f"Vendor dream: {result}")

        # Test service info
        print("\n📊 Service Information:")
        info = container.get_service_info()
        for name, details in info.items():
            print(f"  {name}:")
            print(f"    Lifecycle: {details['lifecycle']}")
            print(f"    Dependencies: {details['dependencies']}")
            print(f"    Has instance: {details['has_instance']}")

        # Clean up
        await container.dispose_all()
        print("\n✅ Container disposed")

        print("\n" + "=" * 80)
        print("✅ Dependency Injection Container Test Complete")
        print("=" * 80)

    # Run test
    asyncio.run(test_container())
