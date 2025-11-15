"""
QRS (Quantum-Resistant Security) Module

Provides quantum-resistant cryptographic primitives for LUKHAS AI's identity
and governance systems, including post-quantum token generation and verification.

LUKHAS AI - Consciousness-aware AI Development Platform
"""

from governance.identity.core.qrs.qrg_generator import (
    QRGGenerator,
    QRGTokenError,
    QRGTokenExpiredError,
    QRGVerificationError,
)

__all__ = [
    "QRGGenerator",
    "QRGTokenError",
    "QRGVerificationError",
    "QRGTokenExpiredError",
]
