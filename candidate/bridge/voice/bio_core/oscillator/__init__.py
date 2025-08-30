"""
Oscillator module for bio-quantum voice processing

Provides quantum oscillator and orchestration functionality.
"""

from .orchestrator import BioOrchestrator, HealthState, Priority
from .qi_inspired_layer import QIBioOscillator, QIConfig

__all__ = [
    "BioOrchestrator",
    "HealthState",
    "Priority",
    "QIBioOscillator",
    "QIConfig",
]

# CLAUDE CHANGELOG
# - Created oscillator __init__.py with proper exports # CLAUDE_EDIT_v0.22
