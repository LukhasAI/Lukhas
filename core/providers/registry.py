from __future__ import annotations

import threading
from typing import Any, Callable, List, Optional

class ProviderRegistry:
    """Central registry for optional providers and components."""

    def __init__(self):
        self._providers: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register(self, name: str, provider: Any, namespace: Optional[str] = None) -> None:
        """
        Register a provider in a given namespace.
        If no namespace is provided, it defaults to 'default'.
        """
        namespace = namespace or "default"
        with self._lock:
            if namespace not in self._providers:
                self._providers[namespace] = {}
            self._providers[namespace][name] = provider

    def get(self, name: str, namespace: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a provider from a namespace with a fallback default.
        """
        namespace = namespace or "default"
        with self._lock:
            return self._providers.get(namespace, {}).get(name, default)

    def has(self, name: str, namespace: Optional[str] = None) -> bool:
        """
        Check if a provider exists in a given namespace.
        """
        namespace = namespace or "default"
        with self._lock:
            return name in self._providers.get(namespace, {})

    def list_providers(self, namespace: Optional[str] = None) -> List[str]:
        """
        List all registered providers in a given namespace.
        """
        namespace = namespace or "default"
        with self._lock:
            return sorted(list(self._providers.get(namespace, {}).keys()))

    def register_provider(self, name: str, namespace: Optional[str] = None) -> Callable:
        """Decorator to register a provider class or function."""
        def decorator(provider_class: Any) -> Any:
            self.register(name, provider_class, namespace=namespace)
            return provider_class
        return decorator

# Global instance for easy access
registry = ProviderRegistry()
