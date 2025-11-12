import os
import time
from functools import lru_cache
from typing import Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from lukhas.api.auth import AuthManager

# --- Constants ---
SECRET_KEY = os.environ.get("SECRET_KEY", "a_very_secret_key")

# --- Rate Limiting (In-Memory Placeholder) ---
# TODO: Replace with a more robust solution (e.g., Redis-based) for production.
# This implementation is not suitable for multi-process or multi-server deployments.
_rate_limit_store: Dict[str, List[float]] = {}
_RATE_LIMIT = 100  # requests per minute
_RATE_LIMIT_WINDOW = 60  # seconds


def check_rate_limit(identifier: str) -> bool:
    """
    Check if a given identifier has exceeded the rate limit.

    Args:
        identifier: A unique identifier (e.g., user ID, IP address).

    Returns:
        True if within the rate limit, False otherwise.
    """
    now = time.time()
    if identifier not in _rate_limit_store:
        _rate_limit_store[identifier] = []

    # Remove timestamps outside the current window
    valid_timestamps = [
        ts for ts in _rate_limit_store[identifier] if now - ts < _RATE_LIMIT_WINDOW
    ]
    _rate_limit_store[identifier] = valid_timestamps

    if len(valid_timestamps) >= _RATE_LIMIT:
        return False

    _rate_limit_store[identifier].append(now)
    return True

# --- Session Management (In-Memory Placeholder) ---
# TODO: Replace with a persistent session store (e.g., Redis) for production.
# This implementation is not suitable for multi-process or multi-server deployments.
_sessions: Dict[str, dict] = {}

def create_session(user_id: str, session_data: dict) -> str:
    """Creates a new session for a user."""
    session_id = f"session_{user_id}_{time.time()}"
    _sessions[session_id] = session_data
    return session_id

def get_session(session_id: str) -> dict | None:
    """Retrieves session data."""
    return _sessions.get(session_id)

def invalidate_session(session_id: str) -> bool:
    """Invalidates a user session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


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
        return {"username": username}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
