"""
LUKHΛS Identity System (ΛiD)
============================

Complete identity management with Trinity Framework integration.
Provides authentication, authorization, and symbolic user tracking.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)

Main exports:
- identity_router: FastAPI router with all identity endpoints
- get_current_user: Dependency for authenticated routes
- require_tier: Decorator for tier-based access control
- AuthContext: User authentication context
"""

# Import main components
from .api import identity_router
from .login import LoginRequest, LoginResponse, UserProfile
from .middleware import (
    AuthContext,
    TierGate,
    extract_user_context,
    get_current_user,
    inject_user_context,
    require_permission,
    require_t1_or_above,
    require_t2_or_above,
    require_t3_or_above,
    require_t4_or_above,
    require_t5,
    require_tier,
    require_trinity_active,
)
from .registration import RegistrationRequest, RegistrationResponse
from .user_db import user_db
from .verify import VerifyResponse, get_tier_permissions

# Export main components
__all__ = [
    # Router
    "identity_router",

    # Database
    "user_db",

    # Middleware and dependencies
    "get_current_user",
    "AuthContext",
    "require_tier",
    "require_permission",
    "require_trinity_active",
    "require_t1_or_above",
    "require_t2_or_above",
    "require_t3_or_above",
    "require_t4_or_above",
    "require_t5",
    "TierGate",
    "inject_user_context",
    "extract_user_context",

    # Models
    "RegistrationRequest",
    "RegistrationResponse",
    "LoginRequest",
    "LoginResponse",
    "UserProfile",
    "VerifyResponse",

    # Utilities
    "get_tier_permissions"
]

# Module information
__version__ = "1.0.0"
__author__ = "LUKHΛS AI"
__description__ = "Identity and authentication system with symbolic tracking"
