"""
LUKHΛS Authentication Middleware
================================

FastAPI middleware for tier-based route protection and user context injection.
Implements Trinity Framework security with symbolic tracking.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import logging
from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .identity_core import identity_core, resolve_access_tier

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthContext:
    """Authentication context injected into requests."""

    def __init__(self, user_data: dict):
        self.user_id = user_data["email"].split("@")[0].replace(".", "_").lower()
        self.email = user_data["email"]
        self.tier = user_data["tier"]
        self.lambda_id = user_data["lambda_id"]
        self.glyphs = user_data["glyphs"]
        self.trinity_score = user_data["metadata"]["trinity_score"]
        tier, permissions = resolve_access_tier({"tier": self.tier})
        self.permissions = permissions
        self.metadata = user_data["metadata"]
        self.raw_data = user_data

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return self.permissions.get(permission, False)

    def is_tier_or_above(self, min_tier: str) -> bool:
        """Check if user tier is at or above minimum."""
        tier_levels = {"T1": 1, "T2": 2, "T3": 3, "T4": 4, "T5": 5}
        user_level = tier_levels.get(self.tier, 0)
        min_level = tier_levels.get(min_tier, 5)
        return user_level >= min_level


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthContext:
    """
    Dependency to get current authenticated user.

    Usage:
        @router.get("/protected")
        async def protected_route(user: AuthContext = Depends(get_current_user)):
            return {"user": user.email, "tier": user.tier}
    """
    try:
        token = credentials.credentials

        # Verify token
        is_valid, user_data = identity_core.validate_symbolic_token(token)
        if not is_valid or not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create auth context
        return AuthContext(user_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_tier(min_tier: str):
    """
    Decorator to require minimum tier for endpoint access.

    Usage:
        @router.get("/admin")
        @require_tier("T5")
        async def admin_route(user: AuthContext = Depends(get_current_user)):
            return {"message": "Admin access granted"}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args, user: AuthContext = Depends(get_current_user), **kwargs
        ):
            if not user.is_tier_or_above(min_tier):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Requires {min_tier} or higher, you have {user.tier}",
                )
            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator


def require_permission(permission: str):
    """
    Decorator to require specific permission for endpoint access.

    Usage:
        @router.get("/quantum")
        @require_permission("can_use_quantum")
        async def quantum_route(user: AuthContext = Depends(get_current_user)):
            return {"message": "Quantum access granted"}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args, user: AuthContext = Depends(get_current_user), **kwargs
        ):
            if not user.has_permission(permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Missing permission: {permission}",
                )
            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator


def require_trinity_active():
    """
    Decorator to require active Trinity Framework (score >= 0.7).

    Usage:
        @router.get("/consciousness/deep")
        @require_trinity_active()
        async def deep_consciousness(user: AuthContext = Depends(get_current_user)):
            return {"message": "Trinity access granted"}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args, user: AuthContext = Depends(get_current_user), **kwargs
        ):
            if user.trinity_score < 0.7:
                raise HTTPException(
                    status_code=403,
                    detail=f"Trinity Framework not active. Score: {user.trinity_score}, required: 0.7",
                )
            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator


class TierGate:
    """
    Context manager for tier-based code execution.

    Usage:
        async with TierGate(user, "T3") as gate:
            if gate.allowed:
                # Execute T3+ code
                result = await advanced_function()
    """

    def __init__(self, user: AuthContext, min_tier: str):
        self.user = user
        self.min_tier = min_tier
        self.allowed = user.is_tier_or_above(min_tier)

    async def __aenter__(self):
        if not self.allowed:
            logger.warning(
                f"Tier gate blocked: User {self.user.email} ({self.user.tier}) "
                f"attempted to access {self.min_tier} content"
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def inject_user_context(request: Request, user: AuthContext):
    """
    Inject user context into request state.

    Allows downstream handlers to access user without re-verification.
    """
    request.state.user = user
    request.state.auth_context = {
        "user_id": user.user_id,
        "email": user.email,
        "tier": user.tier,
        "lambda_id": user.lambda_id,
        "glyphs": user.glyphs,
        "permissions": user.permissions,
    }


async def extract_user_context(request: Request) -> Optional[AuthContext]:
    """
    Extract user context from request state if available.

    Returns None if no authentication context exists.
    """
    return getattr(request.state, "user", None)


# Convenience functions for common tier checks
async def require_t1_or_above(
    user: AuthContext = Depends(get_current_user),
) -> AuthContext:
    """Require T1 tier or above (essentially any authenticated user)."""
    return user


async def require_t2_or_above(
    user: AuthContext = Depends(get_current_user),
) -> AuthContext:
    """Require T2 tier or above."""
    if not user.is_tier_or_above("T2"):
        raise HTTPException(status_code=403, detail="Requires T2 tier or above")
    return user


async def require_t3_or_above(
    user: AuthContext = Depends(get_current_user),
) -> AuthContext:
    """Require T3 tier or above."""
    if not user.is_tier_or_above("T3"):
        raise HTTPException(status_code=403, detail="Requires T3 tier or above")
    return user


async def require_t4_or_above(
    user: AuthContext = Depends(get_current_user),
) -> AuthContext:
    """Require T4 tier or above."""
    if not user.is_tier_or_above("T4"):
        raise HTTPException(status_code=403, detail="Requires T4 tier or above")
    return user


async def require_t5(user: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Require T5 tier (Guardian level)."""
    if user.tier != "T5":
        raise HTTPException(status_code=403, detail="Requires T5 (Guardian) tier")
    return user
