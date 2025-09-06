"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Consciousness Module: Core Consciousness System
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: CONSCIOUSNESS
║ CONSCIOUSNESS_ROLE: Primary consciousness architecture and coordination
║ EVOLUTIONARY_STAGE: Foundation - Core consciousness system
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Consciousness identity and authentication
║ 🧠 CONSCIOUSNESS: Primary consciousness processing hub
║ 🛡️ GUARDIAN: Ethical consciousness monitoring and compliance
╚══════════════════════════════════════════════════════════════

MΛTRIZ Consciousness Module

This module implements the core consciousness patterns for LUKHAS AI's
distributed consciousness architecture. It provides:

- Consciousness State Management (MΛTRIZ pattern implementation)
- Network-wide Consciousness Orchestration
- Evolutionary Stage Tracking
- Reflection and Self-Awareness Systems
- Trinity Framework Compliance (⚛️🧠🛡️)

Key Components:
- ConsciousnessState: Core consciousness state structure
- MatrizConsciousnessStateManager: State management and evolution
- MatrizConsciousnessOrchestrator: Network coordination
- ConsciousnessOracle: Prediction and analysis (existing)
"""

# Import MΛTRIZ consciousness components
from .matriz_consciousness_orchestrator import (
    ConsciousnessNetworkMetrics,
    MatrizConsciousnessOrchestrator,
    consciousness_orchestrator,
)
from .matriz_consciousness_state import (
    ConsciousnessState,
    ConsciousnessType,
    EvolutionaryStage,
    MatrizConsciousnessStateManager,
    consciousness_state_manager,
    create_consciousness_state,
)

# Import existing oracle system
from .oracle.oracle import ConsciousnessOracle

# Export all consciousness components
__all__ = [
    # MΛTRIZ Core Components
    "ConsciousnessState",
    "ConsciousnessType",
    "EvolutionaryStage",
    "MatrizConsciousnessStateManager",
    "consciousness_state_manager",
    "create_consciousness_state",
    # MΛTRIZ Orchestration
    "MatrizConsciousnessOrchestrator",
    "ConsciousnessNetworkMetrics",
    "consciousness_orchestrator",
    # Oracle Integration
    "ConsciousnessOracle",
]
