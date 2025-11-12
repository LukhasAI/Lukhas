"""Core adapters for runtime provider injection.

Provides ProviderRegistry and ConfigResolver for dynamic dependency resolution.
"""

from core.adapters.config_resolver import ConfigResolver, make_resolver
from core.adapters.provider_registry import ProviderRegistry

__all__ = [
    "ConfigResolver",
    "make_resolver",
    "ProviderRegistry",
]
