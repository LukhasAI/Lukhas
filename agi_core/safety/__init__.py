"""
Constitutional AI Safety Layer for AGI

Advanced safety system that implements constitutional AI principles,
ethical constraints, and safety monitoring for AGI systems.
"""

from .constitutional_ai import Constitution, ConstitutionalAI, SafetyPrinciple
from .ethical_reasoning import EthicalDecision, EthicalDilemma, EthicalReasoningEngine
from .guardian_integration import GuardianIntegration, GuardianResponse, SafetyAction
from .safety_monitor import SafetyAlert, SafetyMonitor, SafetyViolation

__all__ = [
    "ConstitutionalAI",
    "Constitution",
    "SafetyPrinciple",
    "SafetyMonitor",
    "SafetyViolation",
    "SafetyAlert",
    "EthicalReasoningEngine",
    "EthicalDilemma",
    "EthicalDecision",
    "GuardianIntegration",
    "GuardianResponse",
    "SafetyAction",
]
