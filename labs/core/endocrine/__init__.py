"""Compatibility layer for the LUKHAS endocrine system in labs lane."""

from __future__ import annotations

from core.endocrine.hormone_system import (
    EndocrineSystem,
    HormoneInteraction,
    HormoneLevel,
    HormoneType,
    get_endocrine_system,
    get_neuroplasticity,
    trigger_reward,
    trigger_stress,
)

__all__ = [
    "EndocrineSystem",
    "HormoneInteraction",
    "HormoneLevel",
    "HormoneType",
    "get_endocrine_system",
    "get_neuroplasticity",
    "trigger_reward",
    "trigger_stress",
]

# ΛTAG: endocrine-compat
# Initialize the shared endocrine system instance to mirror core behaviour.
_system = get_endocrine_system()
