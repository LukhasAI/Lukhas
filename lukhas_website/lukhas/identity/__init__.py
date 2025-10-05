"""
LUKHAS AI - Identity Module (⚛️ Anchor Star)
============================================

Advanced identity management and authentication systems serving as the Anchor Star
in the Constellation Framework. Provides secure, multi-tier identity services with
consciousness-aware authentication and cross-constellation integration.

Constellation Framework Integration:
- ⚛️ Anchor Star: Primary identity coordination and authentication
- ✦ Trail Star: Identity-memory coupling and experience continuity
- 🔬 Horizon Star: Identity-aware natural language interfaces
- 🛡️ Watch Star: Identity governance and authentication oversight

Core Components:
- auth: Unified consciousness-aware authentication system with JWT/OAuth2
- lambda_id: ΛiD Core Identity System with multi-tier access (T1-T5)
- webauthn: WebAuthn/FIDO2 passkey authentication with namespace isolation
- identity_core: Core identity management with cross-device synchronization
- wallet: Secure credential storage and identity wallet management
- qrg: QRG advanced biometric authentication integration

Performance Targets:
- Authentication latency: <100ms p95
- Cross-device sync: <50ms
- Identity verification: 99.9% availability
- Namespace isolation: Complete separation guarantee

Security Features:
- Multi-factor authentication with biometric support
- WebAuthn passkey integration for passwordless authentication
- Namespace isolation preventing cross-tenant data access
- Complete audit trails for all identity operations
- GDPR/CCPA compliant identity data management
"""

import time

import streamlit as st

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
from typing import Any, Optional

# Pre-declare types to allow runtime fallbacks without breaking static typing
AuthenticationService: Optional[Any] = None
AuthResult: Optional[Any] = None
UserProfile: Optional[Any] = None
IdentityService: Optional[Any] = None

try:
    from .auth_service import AuthenticationService, AuthResult, UserProfile

    # Alias for backward compatibility
    IdentityService = AuthenticationService
except ImportError:
    AuthenticationService = None
    AuthResult = None

# ΛiD Token System - Production Schema v1.0.0 (Constellation Framework)
try:
    from .alias_format import ΛiDAlias, make_alias, parse_alias, validate_alias_format, verify_crc
    from .token_generator import EnvironmentSecretProvider, SecretProvider, TokenClaims, TokenGenerator, TokenResponse
    from .token_storage import KeyRotationRecord, StoredToken, TokenStatus, TokenStorage
    from .token_validator import TokenValidationError, TokenValidator, ValidationResult

    ΛTOKEN_SYSTEM_AVAILABLE = True
except ImportError:
    ΛTOKEN_SYSTEM_AVAILABLE = False

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

# Add ΛiD Token System components if available
if ΛTOKEN_SYSTEM_AVAILABLE:
    __all__.extend([
        "make_alias", "verify_crc", "parse_alias", "validate_alias_format", "ΛiDAlias",
        "TokenGenerator", "TokenClaims", "TokenResponse",
        "SecretProvider", "EnvironmentSecretProvider",
        "TokenValidator", "ValidationResult", "TokenValidationError",
        "TokenStorage", "StoredToken", "KeyRotationRecord", "TokenStatus",
        "ΛTOKEN_SYSTEM_AVAILABLE"
    ])

# Add identity core components if available
if IDENTITY_CORE_AVAILABLE:
    __all__.extend(["AccessTier", "IdentityCore"])

# Add authentication components if available
if AUTHENTICATION_AVAILABLE:
    __all__.extend(["QRGAuthBridge", "WalletAuthBridge", "auth_integration"])
