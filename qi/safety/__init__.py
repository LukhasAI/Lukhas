"""
TEQ Safety Module for LUKHAS AI
"""

# Import the unified version that has both Enum-based states and policy support
from .teq_unified import (
    UnifiedTEQCoupler,
    GateState,
    TEQEvent,
    PolicyGateResult,
    PolicyPack
)

# Provide backwards compatibility alias
TEQCoupler = UnifiedTEQCoupler

__all__ = [
    'UnifiedTEQCoupler',
    'TEQCoupler',
    'GateState',
    'TEQEvent', 
    'PolicyGateResult',
    'PolicyPack'
]