# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for auth helpers
# estimate: 10min | priority: high | dependencies: none

import os
import time
from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from lukhas.api.auth import AuthManager

# --- Constants ---
SECRET_KEY = os.environ.get("SECRET_KEY", "a_very_secret_key")

# --- Role Hierarchy for RBAC ---
# Higher roles have more permissions.
# A user with a certain role has all permissions of the roles below it.
ROLE_HIERARCHY: dict[str, int] = {
    "guest": 0,
    "user": 1,
    "moderator": 2,
    "admin": 3,
}

# --- Storage Backend Configuration ---
from lukhas.api.storage import get_storage_backend

_storage_backend = get_storage_backend()

# --- Rate Limiting ---
_RATE_LIMIT = 100  # requests per minute
_RATE_LIMIT_WINDOW = 60  # seconds


def has_role(user_role: str, required_role: str) -> bool:
    """
    Check if a user's role meets the required role level.

    Args:
        user_role: The role of the current user.
        required_role: The minimum role required for the feature.

    Returns:
        True if the user has the required role, False otherwise.
    """
    user_level = ROLE_HIERARCHY.get(user_role, -1)
    required_level = ROLE_HIERARCHY.get(required_role, -1)

    if user_level == -1 or required_level == -1:
        return False  # Invalid role provided

    return user_level >= required_level


def check_rate_limit(identifier: str) -> bool:
    """
    Check if a given identifier has exceeded the rate limit.

    Uses configurable storage backend (in-memory or Redis).
    Storage backend is configured via STORAGE_BACKEND and REDIS_URL environment variables.

    Args:
        identifier: A unique identifier (e.g., user ID, IP address).

    Returns:
        True if within the rate limit, False otherwise.
    """
    now = time.time()
    key = f"rate_limit:{identifier}"

    # Get existing timestamps
    timestamps = _storage_backend.list_get(key)

    # Filter to keep only timestamps within the current window
    valid_timestamps = [ts for ts in timestamps if now - ts < _RATE_LIMIT_WINDOW]

    # Update stored timestamps
    if valid_timestamps:
        _storage_backend.list_filter(key, lambda ts: now - ts < _RATE_LIMIT_WINDOW)
    else:
        _storage_backend.delete(key)

    # Check if limit exceeded
    if len(valid_timestamps) >= _RATE_LIMIT:
        return False

    # Add new timestamp with TTL
    _storage_backend.list_append(key, now)
    _storage_backend.set(key, [*valid_timestamps, now], ttl=_RATE_LIMIT_WINDOW)

    return True

# --- Session Management ---
# Uses configurable storage backend (in-memory or Redis)
# Configure via STORAGE_BACKEND and REDIS_URL environment variables

_SESSION_TTL = 3600  # 1 hour default session lifetime


def create_session(user_id: str, session_data: dict, ttl: Optional[int] = None) -> str:
    """
    Creates a new session for a user.

    Args:
        user_id: User identifier
        session_data: Session data to store
        ttl: Session time-to-live in seconds (default: 1 hour)

    Returns:
        Session ID
    """
    session_id = f"session_{user_id}_{time.time()}"
    key = f"session:{session_id}"
    _storage_backend.set(key, session_data, ttl=ttl or _SESSION_TTL)
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieves session data.

    Args:
        session_id: Session identifier

    Returns:
        Session data dict or None if not found/expired
    """
    key = f"session:{session_id}"
    return _storage_backend.get(key)


def invalidate_session(session_id: str) -> bool:
    """
    Invalidates a user session.

    Args:
        session_id: Session identifier

    Returns:
        True if session existed and was deleted, False otherwise
    """
    key = f"session:{session_id}"
    return _storage_backend.delete(key)


# --- Dependencies ---

@lru_cache
def get_auth_manager() -> AuthManager:
    """Dependency to get the AuthManager instance."""
    return AuthManager(secret_key=SECRET_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> dict:
    """
    Dependency to verify JWT and get the current user.

    Returns:
        User dict with 'username' and optional 'role' from JWT claims
    """
    try:
        payload = auth_manager.verify_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract role from JWT if present
        user_data = {"username": username}
        if "role" in payload:
            user_data["role"] = payload["role"]

        return user_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
