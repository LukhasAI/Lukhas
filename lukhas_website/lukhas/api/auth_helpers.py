"""
Security helpers for LUKHAS API endpoints.

Provides authentication, authorization, and audit logging patterns
aligned with security requirements (target: 90+/100 vs current 55-70/100).

Based on LUKHAS Test Surgeon security patterns from audits.
"""
import logging
from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, Request, status

# Import tier system
try:
    from identity.tier_system import TierLevel, PermissionScope
    TIER_SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback if tier system not available
    from enum import Enum

    class TierLevel(Enum):
        PUBLIC = 0
        AUTHENTICATED = 1
        ELEVATED = 2
        PRIVILEGED = 3
        ADMIN = 4
        SYSTEM = 5

    class PermissionScope(Enum):
        RESOURCE_CREATE = "resource_create"
        RESOURCE_READ = "resource_read"
        RESOURCE_UPDATE = "resource_update"
        RESOURCE_DELETE = "resource_delete"

    TIER_SYSTEM_AVAILABLE = False

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> dict:
    """
    Extract current user from request state (set by StrictAuthMiddleware).

    Returns:
        dict with user_id, tier, permissions

    Raises:
        HTTPException 401: If not authenticated

    Pattern from security audit: "Extract current user from request state"
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Authentication required for this endpoint."
        )

    return {
        "user_id": request.state.user_id,
        "tier": getattr(request.state, "user_tier", TierLevel.PUBLIC.value),
        "permissions": getattr(request.state, "user_permissions", []),
    }


def lukhas_tier_required(tier_level: TierLevel, scope: PermissionScope):
    """
    Decorator to enforce tier-based authorization.

    Args:
        tier_level: Minimum required tier
        scope: Permission scope being accessed

    Usage:
        @router.post("/api/v1/resource")
        @lukhas_tier_required(TierLevel.AUTHENTICATED, PermissionScope.RESOURCE_CREATE)
        async def create_resource(current_user: dict = Depends(get_current_user)):
            ...

    Pattern from security audit: "@lukhas_tier_required decorator"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs (injected by Depends)
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_tier = current_user.get("tier", 0)

            # Check tier level
            if user_tier < tier_level.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient tier. Required: {tier_level.name}, Current: {user_tier}"
                )

            # Audit log
            logger.info(
                f"Tier access granted",
                extra={
                    "user_id": current_user.get("user_id"),
                    "tier": user_tier,
                    "required_tier": tier_level.value,
                    "scope": scope.value,
                    "endpoint": func.__name__
                }
            )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def audit_log_operation(operation: str, user_id: str, details: dict):
    """
    Log operation to audit trail with user_id.

    Pattern from security audit: "Audit log all operations with user_id"
    """
    logger.info(
        f"Operation: {operation}",
        extra={
            "audit": True,
            "user_id": user_id,
            "operation": operation,
            **details
        }
    )
