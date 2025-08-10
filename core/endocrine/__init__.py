"""
LUKHAS Endocrine System
Simulates hormonal signaling for system-wide behavioral modulation
"""

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
    "HormoneType",
    "HormoneLevel",
    "HormoneInteraction",
    "EndocrineSystem",
    "get_endocrine_system",
    "trigger_stress",
    "trigger_reward",
    "get_neuroplasticity",
]

# Initialize the global endocrine system on import
_system = get_endocrine_system()
