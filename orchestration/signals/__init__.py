"""
LUKHAS Signal System
====================
Colony-wide endocrine-inspired signal system for adaptive behavior modulation.
"""

from .signal_bus import (
    Signal,
    SignalType,
    SignalPattern,
    SignalBus,
    get_signal_bus,
    emit_signal
)

from .homeostasis import (
    SystemEvent,
    ModulationParams,
    AuditTrail,
    OscillationDetector,
    HomeostasisController
)

from .modulator import (
    PromptStyle,
    PromptModulation,
    PromptModulator,
    AdaptiveModulator
)

__all__ = [
    # Signal Bus
    "Signal",
    "SignalType",
    "SignalPattern",
    "SignalBus",
    "get_signal_bus",
    "emit_signal",
    
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
    "AdaptiveModulator"
]

# Version
__version__ = "1.0.0"