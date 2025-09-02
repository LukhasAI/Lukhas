"""
LUKHAS Signal System
====================
Colony-wide endocrine-inspired signal system for adaptive behavior modulation.
"""

from .homeostasis import (
    AuditTrail,
    HomeostasisController,
    ModulationParams,
    OscillationDetector,
    SystemEvent,
)
from .modulator import AdaptiveModulator, PromptModulation, PromptModulator, PromptStyle
from .signal_bus import (
    Signal,
    SignalBus,
    SignalPattern,
    SignalType,
    emit_stress,
    get_signal_bus,
)

__all__ = [
    # Signal Bus
    "Signal",
    "SignalType",
    "SignalPattern",
    "SignalBus",
    "get_signal_bus",
    "emit_stress",
    # Homeostasis
    "SystemEvent",
    "ModulationParams",
    "AuditTrail",
    "OscillationDetector",
    "HomeostasisController",
    # Modulator
    "PromptStyle",
    "PromptModulation",
    "PromptModulator",
    "AdaptiveModulator",
]

# Version
__version__ = "1.0.0"
