"""
LUKHAS Endocrine System
Simulates hormonal signaling for system-wide behavioral modulation
"""
import streamlit as st

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

# Initialize the global endocrine system on import
_system = get_endocrine_system()
