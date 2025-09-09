"""
Dependency Injection Container
=============================
Manages module dependencies without circular imports.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DependencyContainer:
    """Dependency injection container for LUKHAS modules"""

    def __init__(self):
        self._instances: dict[type, Any] = {}
        self._factories: dict[type, Any] = {}

    def register(self, interface: type, instance: Any):
        """Register a module instance"""
        self._instances[interface] = instance
        logger.info(f"Registered {interface.__name__} implementation")

    def register_factory(self, interface: type, factory: callable):
        """Register a factory function for lazy instantiation"""
        self._factories[interface] = factory
        logger.info(f"Registered factory for {interface.__name__}")

    def get(self, interface: type) -> Optional[Any]:
        """Get module instance by interface"""
        # Check if already instantiated
        if interface in self._instances:
            return self._instances[interface]

        # Check if factory exists
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance
            return instance

        logger.warning(f"No implementation found for {interface.__name__}")
        return None

    def resolve_dependencies(self, module: Any):
        """Inject dependencies into module"""
        # Check for dependency declarations
        if hasattr(module, "_dependencies"):
            for dep_name, dep_interface in module._dependencies.items():
                dep_instance = self.get(dep_interface)
                if dep_instance:
                    setattr(module, dep_name, dep_instance)
                else:
                    logger.warning(f"Could not resolve dependency {dep_name} for {module.__class__.__name__}")


# Global container instance
container = DependencyContainer()


# Decorator for dependency injection
def inject(**dependencies):
    """Decorator to inject dependencies into a class"""

    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            # Set dependencies attribute
            self._dependencies = dependencies

            # Call original init
            original_init(self, *args, **kwargs)

            # Resolve dependencies
            container.resolve_dependencies(self)

        cls.__init__ = new_init
        return cls

    return decorator


# Helper function to get module
def get_module(interface: type) -> Optional[Any]:
    """Get module instance from container"""
    return container.get(interface)