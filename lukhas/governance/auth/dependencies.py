"""Authentication dependencies for FastAPI endpoints.

This module provides dependency injection helpers for extracting validated
user context from JWT tokens. The user data is populated by StrictAuthMiddleware
and stored in request.state.user.

Security:
- User data comes from validated JWT tokens ONLY
- Clients cannot spoof user_id via request body
- StrictAuthMiddleware must be installed for these dependencies to work
"""

# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for auth dependencies
# estimate: 10min | priority: high | dependencies: none

from fastapi import Depends, HTTPException, Request
from typing import Any
import logging

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> dict[str, Any]:
    """
    Extract and validate current user from JWT token.

    This dependency MUST be used by all endpoints that need user identity.
    It extracts the validated user data that StrictAuthMiddleware stored
    in request.state.user.

    Returns:
        dict: User data with at minimum:
            - user_id: str (unique user identifier)
            - tier: int (user tier/permission level)
            - permissions: List[str] (user roles/permissions)

    Raises:
        HTTPException 401: If no user found (auth middleware didn't run)
        HTTPException 500: If user data is invalid format

    Security:
        - User data comes from validated JWT token ONLY
        - Client cannot spoof user_id via request body
        - StrictAuthMiddleware must be installed for this to work

    Example:
        ```python
        @router.post("/api/v1/feedback")
        async def submit_feedback(
            request: FeedbackRequest,
            user: dict = Depends(get_current_user)
        ):
            user_id = user["user_id"]
            # Use validated user_id for operations
        ```
    """
    # Check if StrictAuthMiddleware populated request.state.user
    if not hasattr(request.state, "user_id"):
        logger.error(
            "get_current_user called but request.state.user_id not set. "
            "Is StrictAuthMiddleware installed?"
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication required. User context not found."
        )

    # Reconstruct user dict from request.state fields
    user_data = {
        "user_id": request.state.user_id,
        "tier": getattr(request.state, "user_tier", 0),
        "permissions": getattr(request.state, "user_permissions", []),
    }

    # Include full claims if available
    if hasattr(request.state, "user"):
        user_data = request.state.user

    # Validate user data structure
    if not isinstance(user_data, dict):
        logger.error(f"Invalid user data type: {type(user_data)}")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error."
        )

    if "user_id" not in user_data or not user_data["user_id"]:
        logger.error("User data missing or empty user_id field")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error."
        )

    return user_data


async def get_current_user_id(request: Request) -> str:
    """
    Extract only the user_id from JWT token.

    Convenience dependency for endpoints that only need user_id.
    This is more efficient than get_current_user() if you only need the ID.

    Returns:
        str: User ID from validated JWT token

    Raises:
        HTTPException 401: If no user found
        HTTPException 500: If user_id is invalid

    Security:
        - User ID comes from validated JWT token ONLY
        - Cannot be spoofed by client via request body

    Example:
        ```python
        @router.post("/api/v1/feedback")
        async def submit_feedback(
            request: FeedbackRequest,
            user_id: str = Depends(get_current_user_id)
        ):
            # user_id is validated from JWT token
            await feedback_service.store(user_id=user_id, ...)
        ```
    """
    # Check if StrictAuthMiddleware populated request.state.user_id
    if not hasattr(request.state, "user_id"):
        logger.error(
            "get_current_user_id called but request.state.user_id not set. "
            "Is StrictAuthMiddleware installed?"
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication required. User context not found."
        )

    user_id = request.state.user_id

    # Validate user_id
    if not user_id or not isinstance(user_id, str):
        logger.error(f"Invalid user_id: {user_id}")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error."
        )

    return user_id
