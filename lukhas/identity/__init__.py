"""
LUKHAS AI - Identity Module
Identity management and authentication systems

Integrated Components:
- auth: Unified consciousness-aware authentication system
- wallet: WALLET identity management integration
- qrg: QRG advanced authentication integration
- webauthn: WebAuthn support
- lambda_id: Lambda ID system
- identity_core: Core identity management and access tiers
"""

# Core identity components
from . import lambda_id, webauthn

# Import IdentityCore from the correct location
try:
    import sys

    sys.path.insert(0, "/Users/agi_dev/LOCAL-REPOS/Lukhas")
    from identity.identity_core import AccessTier, IdentityCore

    IDENTITY_CORE_AVAILABLE = True
except ImportError:
    # Fallback: try relative import if absolute fails
    try:
        import os

        identity_path = os.path.join(os.path.dirname(__file__), "../../identity")
        sys.path.insert(0, identity_path)
        from identity_core import AccessTier, IdentityCore

        IDENTITY_CORE_AVAILABLE = True
    except ImportError:
        IDENTITY_CORE_AVAILABLE = False

# Integrated authentication ecosystem (production-ready)
try:
    from . import auth_integration
    from .qrg import QRGAuthBridge
    from .wallet import WalletAuthBridge

    # Authentication integration available
    AUTHENTICATION_AVAILABLE = True

except ImportError:
    # Graceful fallback if integration components not available
    AUTHENTICATION_AVAILABLE = False

# Export components
__all__ = [
    "lambda_id",
    "webauthn",
    "AUTHENTICATION_AVAILABLE",
    "IDENTITY_CORE_AVAILABLE",
]

# Add identity core components if available
if IDENTITY_CORE_AVAILABLE:
    __all__.extend(["IdentityCore", "AccessTier"])

# Add authentication components if available
if AUTHENTICATION_AVAILABLE:
    __all__.extend(["auth_integration", "WalletAuthBridge", "QRGAuthBridge"])
