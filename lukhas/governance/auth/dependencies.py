"""Authentication dependencies for FastAPI endpoints.

SECURITY: These dependencies extract validated user identity from JWT tokens.
They MUST be used by all endpoints that need user identity to prevent
identity spoofing attacks (OWASP A01).

The user data is extracted from request.state.user, which is populated by
StrictAuthMiddleware after validating the JWT token.
"""

import logging
from typing import Any, Dict

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Extract and validate current user from JWT token.

    This dependency MUST be used by all endpoints that need user identity.
    It extracts the validated user data that StrictAuthMiddleware stored
    in request.state.user after validating the JWT token.

    Returns:
        dict: User data with at minimum:
            - user_id: str (unique user identifier)
            - tier: int (user tier level)
            - permissions: List[str] (user roles/permissions)

    Raises:
        HTTPException 401: If no user found (auth middleware didn't run)
        HTTPException 500: If user data structure is invalid

    Security:
        - User data comes from validated JWT token ONLY
        - Client cannot spoof user_id via request body
        - StrictAuthMiddleware must be installed for this to work

    Example:
        ```python
        @router.post("/api/v1/protected")
        async def protected_endpoint(
            user_data: Dict[str, Any] = Depends(get_current_user)
        ):
            user_id = user_data["user_id"]
            return {"message": f"Hello user {user_id}"}
        ```
    """
    # Check if StrictAuthMiddleware populated request.state.user
    if not hasattr(request.state, "user"):
        logger.error(
            f"get_current_user called but request.state.user not set for "
            f"{request.method} {request.url.path}. "
            f"Is StrictAuthMiddleware installed?"
        )
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Authentication required. User context not found.",
                    "type": "authentication_error",
                    "code": "missing_user_context"
                }
            }
        )

    user_data = request.state.user

    # Validate user data structure
    if not isinstance(user_data, dict):
        logger.error(
            f"Invalid user data type: {type(user_data)} for "
            f"{request.method} {request.url.path}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": "Internal authentication error.",
                    "type": "internal_error",
                    "code": "invalid_user_data"
                }
            }
        )

    if "user_id" not in user_data:
        logger.error(
            f"User data missing user_id field for "
            f"{request.method} {request.url.path}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": "Internal authentication error.",
                    "type": "internal_error",
                    "code": "missing_user_id"
                }
            }
        )

    logger.debug(
        f"Authenticated user {user_data['user_id']} for "
        f"{request.method} {request.url.path}"
    )

    return user_data


async def get_current_user_id(request: Request) -> str:
    """
    Extract only the user_id from JWT token.

    Convenience dependency for endpoints that only need user_id.
    This is the most commonly used dependency for securing endpoints.

    Returns:
        str: User ID from validated JWT token

    Raises:
        HTTPException 401: If no user found
        HTTPException 500: If user data is invalid

    Security:
        - User ID is extracted from validated JWT token only
        - Client cannot provide or override this value
        - Prevents all identity spoofing attacks

    Example:
        ```python
        @router.post("/api/v1/feedback")
        async def submit_feedback(
            request: FeedbackRequest,
            user_id: str = Depends(get_current_user_id)
        ):
            # user_id is guaranteed to be from validated JWT
            await feedback_service.store(user_id=user_id, ...)
            return {"status": "success", "user_id": user_id}
        ```
    """
    user_data = await get_current_user(request)
    return user_data["user_id"]


async def get_current_user_tier(request: Request) -> int:
    """
    Extract user tier from JWT token.

    Convenience dependency for endpoints that need to check user tier
    for feature gating or rate limiting.

    Returns:
        int: User tier level (0 = free, 1 = basic, 2 = premium, etc.)

    Raises:
        HTTPException 401: If no user found

    Example:
        ```python
        @router.post("/api/v1/premium-feature")
        async def premium_endpoint(
            tier: int = Depends(get_current_user_tier)
        ):
            if tier < 2:
                raise HTTPException(403, "Premium tier required")
            return {"message": "Premium feature accessed"}
        ```
    """
    user_data = await get_current_user(request)
    return user_data.get("tier", 0)


async def require_admin(request: Request) -> Dict[str, Any]:
    """
    Require user to have admin role.

    Use this dependency for admin-only endpoints.

    Returns:
        dict: User data if user is admin

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If not admin

    Example:
        ```python
        @router.post("/api/v1/admin/users")
        async def admin_endpoint(
            admin_user: Dict[str, Any] = Depends(require_admin)
        ):
            return {"message": "Admin action performed"}
        ```
    """
    user_data = await get_current_user(request)
    permissions = user_data.get("permissions", [])

    if "admin" not in permissions:
        logger.warning(
            f"Access denied: User {user_data['user_id']} attempted admin action "
            f"for {request.method} {request.url.path}"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "message": "Admin privileges required.",
                    "type": "authorization_error",
                    "code": "insufficient_permissions"
                }
            }
        )

    logger.info(
        f"Admin access granted: User {user_data['user_id']} for "
        f"{request.method} {request.url.path}"
    )

    return user_data
