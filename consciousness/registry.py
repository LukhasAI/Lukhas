"""Compatibility bridge for ``consciousness.registry`` imports."""

from __future__ import annotations

from lukhas_website.lukhas.consciousness.registry import (
    ComponentInstance,
    ComponentMetadata,
    ComponentStatus,
    ComponentType,
    ConsciousnessComponentRegistry,
)

__all__ = [
    "ComponentInstance",
    "ComponentMetadata",
    "ComponentStatus",
    "ComponentType",
    "ConsciousnessComponentRegistry",
]
