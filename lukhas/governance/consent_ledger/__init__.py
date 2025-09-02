"""
LUKHAS Consent Ledger API
========================

Minimal, safe consent recording with registry pattern.
- Works in DRY_RUN/OFFLINE with builtin provider (no network)
- Real providers can be registered at runtime via feature flags
"""

from .api import record_consent

__all__ = ["record_consent"]
