"""
TEQ Safety Module for LUKHAS AI
"""

# Import the unified version that has both Enum-based states and policy support
from .teq_unified import (
    GateState,
    PolicyGateResult,
    PolicyPack,
    TEQEvent,
    UnifiedTEQCoupler,
)

# Provide backwards compatibility alias
TEQCoupler = UnifiedTEQCoupler

__all__ = [
    "GateState",
    "PolicyGateResult",
    "PolicyPack",
    "TEQCoupler",
    "TEQEvent",
    "UnifiedTEQCoupler",
]
