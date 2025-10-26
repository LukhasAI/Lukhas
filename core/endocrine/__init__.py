"""Core endocrine system integration for hormonal modulation."""
from __future__ import annotations

from .hormone_system import (
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

# ΛTAG: endocrine
# Initialize the global endocrine system on import to prime receptors.
_system = get_endocrine_system()
