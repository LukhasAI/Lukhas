"""
Core Adapters - Provider Pattern Infrastructure
===============================================
Runtime dependency injection to eliminate import-time dependencies.
Part of lane isolation initiative to prevent lukhas/ → candidate/ imports.
"""

from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver, Config

__all__ = ["ProviderRegistry", "make_resolver", "Config"]
