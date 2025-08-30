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

# Feature flags for optional identity components (no sys.path hacks here)
try:
    import importlib.util

    # Prefer namespaced package lookups; do not mutate sys.path here.
    IDENTITY_CORE_AVAILABLE = (
        importlib.util.find_spec("lukhas.identity.identity_core") is not None
        or importlib.util.find_spec("identity.identity_core") is not None
        or importlib.util.find_spec("identity_core") is not None
    )
except Exception:
    IDENTITY_CORE_AVAILABLE = False

# Integrated authentication ecosystem (production-ready)
try:
    import importlib.util

    AUTHENTICATION_AVAILABLE = (
        importlib.util.find_spec("lukhas.identity.auth_integration") is not None
        and importlib.util.find_spec("lukhas.identity.qrg") is not None
        and importlib.util.find_spec("lukhas.identity.wallet") is not None
    )

except Exception:
    # Graceful fallback if integration components not available
    AUTHENTICATION_AVAILABLE = False

# Import authentication service
try:
    from .auth_service import AuthenticationService, AuthResult, UserProfile

    # Alias for backward compatibility
    IdentityService = AuthenticationService
except ImportError:
    AuthenticationService = None
    AuthResult = None
    UserProfile = None
    IdentityService = None

# Export components
__all__ = [
    "AUTHENTICATION_AVAILABLE",
    "IDENTITY_CORE_AVAILABLE",
    "AuthResult",
    "AuthenticationService",
    "IdentityService",  # Alias
    "UserProfile",
    "lambda_id",
    "webauthn",
]

# Add identity core components if available
if IDENTITY_CORE_AVAILABLE:
    __all__.extend(["AccessTier", "IdentityCore"])

# Add authentication components if available
if AUTHENTICATION_AVAILABLE:
    __all__.extend(["QRGAuthBridge", "WalletAuthBridge", "auth_integration"])
