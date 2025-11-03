#!/usr/bin/env python3
"""LUKHAS Identity Module (⚛️ pillar)

Exports a stable façade that mirrors the richer ``labs.identity`` surface while
preserving the historic local implementations used by downstream tools.
"""

from importlib import import_module

from _bridgeutils import export_from, safe_guard

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


def _merge_backend(module_name: str) -> None:
    """Merge public symbols from ``module_name`` into this façade."""

    try:
        backend = import_module(module_name)
    except Exception:
        return

    for name, value in export_from(backend).items():
        if name not in globals():
            globals()[name] = value
        if name not in __all__:
            __all__.append(name)


for _candidate in (
    "lukhas_website.identity",
    "labs.identity",
    "governance.identity",
):
    _merge_backend(_candidate)

safe_guard(__name__, __all__)
