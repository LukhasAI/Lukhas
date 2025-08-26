"""
Healthcare Provider Templates

This package provides templates and base classes for integrating with
various healthcare providers across different regions and countries.
"""

from .base_provider import BaseHealthcareProvider, ProviderConfig, SecurityConfig

__version__ = "1.0.0"
__all__ = [
    "BaseHealthcareProvider",
    "ProviderConfig",
    "SecurityConfig"
]
