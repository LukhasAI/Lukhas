"""
LUKHAS Endocrine System
Simulates hormonal signaling for system-wide behavioral modulation
"""

from .hormone_system import (
    HormoneType,
    HormoneLevel,
    HormoneInteraction,
    EndocrineSystem,
    get_endocrine_system,
    trigger_stress,
    trigger_reward,
    get_neuroplasticity
)

__all__ = [
    'HormoneType',
    'HormoneLevel',
    'HormoneInteraction',
    'EndocrineSystem',
    'get_endocrine_system',
    'trigger_stress',
    'trigger_reward',
    'get_neuroplasticity'
]

# Initialize the global endocrine system on import
_system = get_endocrine_system()