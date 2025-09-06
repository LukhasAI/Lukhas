"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Governance Module: Consciousness Governance System
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: REFLECT
║ CONSCIOUSNESS_ROLE: Ethical consciousness governance and oversight
║ EVOLUTIONARY_STAGE: Governance - Ethical consciousness supervision
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Governance identity and ethical authority validation
║ 🧠 CONSCIOUSNESS: Consciousness-aware ethical decision making
║ 🛡️ GUARDIAN: Primary guardian system implementation and oversight
╚══════════════════════════════════════════════════════════════

MΛTRIZ Governance Module

This module implements consciousness-aware governance patterns for
LUKHAS AI's distributed ethics architecture. It provides:

- Consciousness-integrated ethical assessment
- Real-time governance decision making
- Constitutional AI principles enforcement
- Policy-based consciousness oversight
- Guardian system coordination

Key Components:
- MatrizConsciousnessGovernanceSystem: Primary governance coordinator
- ConsciousnessEthicsAssessment: Ethics evaluation framework
- GovernancePolicy: Policy definition and enforcement
- Constitutional AI: Legacy constitutional principles (existing)
"""

# Import MΛTRIZ consciousness governance components
from .matriz_consciousness_governance import (
    ConsciousnessEthicsAssessment,
    ConsciousnessEthicsLevel,
    GovernanceDecisionType,
    GovernancePolicy,
    MatrizConsciousnessGovernanceSystem,
    consciousness_governance_system,
)

# Import existing governance components
try:
    from .constitutional_ai import ConstitutionalPrinciple
except ImportError:
    ConstitutionalPrinciple = None

try:
    from .guardian_system_2 import GuardianSystem
except ImportError:
    GuardianSystem = None

# Export governance components
__all__ = [
    # MΛTRIZ Consciousness Governance
    "ConsciousnessEthicsAssessment",
    "ConsciousnessEthicsLevel",
    "GovernanceDecisionType",
    "GovernancePolicy",
    "MatrizConsciousnessGovernanceSystem",
    "consciousness_governance_system",
    # Legacy Governance Components
    "ConstitutionalPrinciple",
    "GuardianSystem",
]
