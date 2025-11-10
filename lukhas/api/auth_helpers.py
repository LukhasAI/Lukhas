from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette import status
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- In-memory user data (replace with actual database) ---
# --- This is a placeholder for demonstration purposes. ---
# --- In a real application, fetch user data from a database. ---
# --- and use a secure method for API key validation. ---
USERS_DATA = {
    "user_free_123": {"username": "user_free", "tier": "free", "api_key": "free_key"},
    "user_pro_456": {"username": "user_pro", "tier": "pro", "api_key": "pro_key"},
    "user_premium_789": {
        "username": "user_premium",
        "tier": "premium",
        "api_key": "premium_key",
    },
    "admin_user_001": {
        "username": "admin_user",
        "tier": "admin",
        "api_key": "admin_key",
    },
}

# --- Feature access control ---
# --- Define which tiers have access to which features. ---
# --- This could be loaded from a configuration file. ---
FEATURE_ACCESS = {
    "free": ["feature1", "feature2"],
    "pro": ["feature1", "feature2", "feature3"],
    "premium": ["feature1", "feature2", "feature3", "feature4"],
    "admin": ["feature1", "feature2", "feature3", "feature4", "admin_feature"],
}

# --- API Key Authentication ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency to verify the API key.
    """
    if not api_key or api_key not in [
        user["api_key"] for user in USERS_DATA.values()
    ]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key"
        )
    return api_key


async def get_current_user(api_key: str = Depends(require_api_key)):
    """
    Get the current user based on the API key.
    """
    for user_id, user_data in USERS_DATA.items():
        if user_data["api_key"] == api_key:
            return user_data
    return None  # Should not be reached due to require_api_key dependency


def has_feature_access(user_tier: str, feature: str) -> bool:
    """
    Check if a user's tier has access to a specific feature.
    """
    if user_tier in FEATURE_ACCESS:
        return feature in FEATURE_ACCESS[user_tier]
    return False


def require_feature_access(feature: str):
    """
    Factory for a dependency that checks if the current user has access to a feature.
    """

    async def _feature_access_dependency(
        current_user: dict = Depends(get_current_user),
    ):
        """
        Inner dependency that checks for feature access.
        """
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user_tier = current_user.get("tier", "free")
        if not has_feature_access(user_tier, feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return _feature_access_dependency
