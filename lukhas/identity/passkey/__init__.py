"""
LUKHAS Passkey Verification API
==============================

Minimal, safe passkey verification with registry pattern.
- Works with builtin provider (stub) in DRY_RUN
- Real WebAuthn provider can be registered via registry when enabled
"""

from .api import verify_passkey

__all__ = ["verify_passkey"]
