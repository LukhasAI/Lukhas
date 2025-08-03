"""
Identity Verification Colonies

Specialized agent colonies for distributed identity verification,
consensus-based authentication, and self-healing capabilities.
"""

from .biometric_verification_colony import BiometricVerificationColony
from .consciousness_verification_colony import ConsciousnessVerificationColony
from .dream_verification_colony import DreamVerificationColony
from .identity_governance_colony import IdentityGovernanceColony

__all__ = [
    'BiometricVerificationColony',
    'ConsciousnessVerificationColony',
    'DreamVerificationColony',
    'IdentityGovernanceColony'
]