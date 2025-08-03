"""
Oscillator module for bio-quantum voice processing

Provides quantum oscillator and orchestration functionality.
"""

from .quantum_inspired_layer import QuantumBioOscillator, QuantumConfig
from .orchestrator import BioOrchestrator, HealthState, Priority

__all__ = [
    'QuantumBioOscillator',
    'QuantumConfig',
    'BioOrchestrator',
    'HealthState',
    'Priority'
]

# CLAUDE CHANGELOG
# - Created oscillator __init__.py with proper exports # CLAUDE_EDIT_v0.22