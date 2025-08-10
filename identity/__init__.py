"""
LUKHΛS Identity Module (Compatibility Forwarder)
================================================

Purpose:
- Preserve existing identity_core exports for local callers
- Seamlessly forward all identity.* imports to governance.identity
    so older paths like `from identity.interface import IdentityClient`
    resolve to the new namespace without code-wide refactors.

This module injects governance.identity as the active `identity` package
in sys.modules while copying key identity_core exports onto it.
"""

import logging
import sys
from typing import Any

from .identity_core import (
    AccessTier,
    IdentityCore,
    generate_identity_glyph,
    identity_core,
    resolve_access_tier,
    validate_symbolic_token,
)

logger = logging.getLogger(__name__)

try:
    # Import the canonical governance identity package
    import governance.identity as _gov_identity

    # Expose identity_core symbols on the governance identity module
    _exports: dict[str, Any] = {
        "IdentityCore": IdentityCore,
        "AccessTier": AccessTier,
        "identity_core": identity_core,
        "validate_symbolic_token": validate_symbolic_token,
        "resolve_access_tier": resolve_access_tier,
        "generate_identity_glyph": generate_identity_glyph,
    }
    for _name, _obj in _exports.items():
        setattr(_gov_identity, _name, _obj)

    # Replace this module in sys.modules with governance.identity
    # so that `import identity.interface` maps to governance.identity.interface
    sys.modules[__name__] = _gov_identity
    # Also ensure base alias exists
    sys.modules.setdefault("governance.identity", _gov_identity)

except Exception as e:
    # If forwarding fails, fall back to exposing only identity_core symbols
    # This keeps local imports working even if governance package is missing
    logger.warning(
        "Identity forwarder: failed to attach governance.identity (%s). "
        "Proceeding with local identity_core exports only.",
        e,
    )

__all__ = [
    "IdentityCore",
    "AccessTier",
    "identity_core",
    "validate_symbolic_token",
    "resolve_access_tier",
    "generate_identity_glyph",
]
