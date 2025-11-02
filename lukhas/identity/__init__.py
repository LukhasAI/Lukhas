#!/usr/bin/env python3
"""
LUKHAS Identity Module (⚛️ pillar)

WebAuthn/FIDO2 authentication, ΛID namespace, and identity management.
"""

from lukhas.identity.webauthn_credential import (
    WebAuthnCredential,
    WebAuthnCredentialStore,
)
from lukhas.identity.webauthn_verify import (
    verify_assertion,
    VerificationResult,
    InvalidSignatureError,
    InvalidChallengeError,
    ReplayAttackError,
    InvalidAssertionError,
    CredentialNotFoundError,
)

__all__ = [
    # Credential storage
    "WebAuthnCredential",
    "WebAuthnCredentialStore",
    # Assertion verification
    "verify_assertion",
    "VerificationResult",
    # Exceptions
    "InvalidSignatureError",
    "InvalidChallengeError",
    "ReplayAttackError",
    "InvalidAssertionError",
    "CredentialNotFoundError",
]
