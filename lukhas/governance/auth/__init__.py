"""LUKHAS Governance Authentication Module.

This module provides authentication and authorization primitives for
securing API endpoints.

Security Features:
- JWT token validation
- User identity extraction from validated tokens
- Role-based access control (RBAC)
- Admin privilege checking

Usage:
    from lukhas.governance.auth.dependencies import (
        get_current_user,
        get_current_user_id,
        require_admin
    )

    @router.post("/api/v1/protected")
    async def protected_endpoint(
        user_id: str = Depends(get_current_user_id)
    ):
        # user_id is guaranteed to be from validated JWT token
        return {"user_id": user_id}
"""

from lukhas.governance.auth.dependencies import (
    get_current_user,
    get_current_user_id,
    get_current_user_tier,
    require_admin,
)

__all__ = [
    "get_current_user",
    "get_current_user_id",
    "get_current_user_tier",
    "require_admin",
]
