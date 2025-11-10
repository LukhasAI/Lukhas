from typing import Dict, List

# Role hierarchy: Higher roles have more permissions.
# A user with a certain role has all permissions of the roles below it.
ROLE_HIERARCHY: Dict[str, int] = {
    "guest": 0,
    "user": 1,
    "moderator": 2,
    "admin": 3,
}

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
