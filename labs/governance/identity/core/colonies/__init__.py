"""
Identity Verification Colonies

Specialized agent colonies for distributed identity verification,
consensus-based authentication, and self-healing capabilities.
"""

import streamlit as st

from .biometric_verification_colony import BiometricVerificationColony
from .consciousness_verification_colony import ConsciousnessVerificationColony
from .dream_verification_colony import DreamVerificationColony

try:
    from .identity_governance_colony import IdentityGovernanceColony
except ImportError:
    IdentityGovernanceColony = None

__all__ = [
    "BiometricVerificationColony",
    "ConsciousnessVerificationColony",
    "DreamVerificationColony",
]

if IdentityGovernanceColony:
    __all__.append("IdentityGovernanceColony")
