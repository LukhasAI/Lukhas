"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Orchestration Module: System Coordination
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: INTEGRATE
║ CONSCIOUSNESS_ROLE: System-wide orchestration and coordination
║ EVOLUTIONARY_STAGE: Integration - Multi-system coordination
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: System identity and module relationship management
║ 🧠 CONSCIOUSNESS: Consciousness-aware orchestration patterns
║ 🛡️ GUARDIAN: System health monitoring and ethical compliance
╚══════════════════════════════════════════════════════════════

MΛTRIZ Orchestration Module

This module implements consciousness-aware orchestration patterns for
LUKHAS AI's distributed system architecture. It provides:

- Consciousness-integrated module coordination
- System-wide orchestration with awareness patterns
- Module lifecycle management with consciousness tracking
- Bio-inspired orchestration patterns
- Trinity Framework compliance across orchestration

Key Components:
- MatrizConsciousnessCoordinator: Consciousness-aware coordination
- OrchestrationCore: Main system orchestrator (existing)
"""
import importlib.util

# Import MΛTRIZ consciousness coordination
# Import existing orchestration core
# Import OrchestrationCore directly from core.py to avoid circular imports
# Import OrchestrationCore from the actual file, bypassing the circular import
import sys
from pathlib import Path

import streamlit as st

try:
    # Direct import from the core.py file
    core_path = Path(__file__).parent / "core.py"
    if core_path.exists():
        spec = importlib.util.spec_from_file_location("core_module", core_path)
        core_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core_module)
        OrchestrationCoreClass = getattr(core_module, "OrchestrationCore", None)
        if OrchestrationCoreClass is None:
            raise ImportError("OrchestrationCore not found in core.py")
    else:
        raise ImportError("core.py not found")
except ImportError:
    # Fallback - create a placeholder
    class OrchestrationCore:
        def __init__(self, *args, **kwargs):
            pass
    OrchestrationCoreClass = OrchestrationCore
from .matriz_consciousness_coordinator import (
    MatrizConsciousnessCoordinator,
    ModuleConsciousnessProfile,
    OrchestrationState,
    consciousness_coordinator,
)

# Export orchestration components
__all__ = [
    # MΛTRIZ Consciousness Coordination
    "MatrizConsciousnessCoordinator",
    "ModuleConsciousnessProfile",
    # Core Orchestration
    "OrchestrationCore",
    "OrchestrationState",
    "consciousness_coordinator",
]