"""
Core Registry - Component registration and discovery.

Provides register() function and _REG registry.
"""
from __future__ import annotations

try:
    from candidate.core.identity.registry import _REG, register
except Exception:
    # Fallback minimal definitions
    def register(*args, **kwargs):
        """Register a component (placeholder)."""
        pass

    _REG = {}

__all__ = ["register", "_REG"]
