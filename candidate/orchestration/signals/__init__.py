"""
LUKHAS Signal System
====================
Colony-wide endocrine-inspired signal system for adaptive behavior modulation.
"""
import streamlit as st

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
from .diagnostic_signal_type import DiagnosticSignalType

# For backward compatibility
SymbolicSignal = Signal

__all__ = [
    "AdaptiveModulator",
    "AuditTrail",
    "DiagnosticSignalType",
    "HomeostasisController",
    "ModulationParams",
    "OscillationDetector",
    "PromptModulation",
    "PromptModulator",
    # Modulator
    "PromptStyle",
    # Signal Bus
    "Signal",
    "SignalBus",
    "SignalPattern",
    "SignalType",
    "SymbolicSignal",
    # Homeostasis
    "SystemEvent",
    "emit_stress",
    "get_signal_bus",
]

# Version
__version__ = "1.0.0"
