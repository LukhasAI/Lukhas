"""Golden Token Kit - Deterministic auth fixtures for testing.

Provides fixed org_id/user_id/project_id combinations and standard scope sets
for testing LUKHAS API endpoints without ad-hoc header setup.

Example:
    >>> from tests.fixtures.auth_tokens import get_auth_headers, Scopes
    >>> headers = get_auth_headers(scopes=Scopes.MODELS_READ)
    >>> response = client.get("/v1/models", headers=headers)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import os


# Fixed test identifiers (deterministic, non-production)
TEST_ORG_ID = "org_test_lukhas_00000001"
TEST_USER_ID = "user_test_alice_00000001"
TEST_PROJECT_ID = "proj_test_main_00000001"

# Additional test identities for multi-user scenarios
TEST_USER_BOB = "user_test_bob_00000002"
TEST_USER_CHARLIE = "user_test_charlie_00000003"

# Fixed API key for testing (never use in production)
TEST_API_KEY = os.getenv("LUKHAS_TEST_API_KEY", "sk-test-lukhas-golden-token-kit-v1")


@dataclass
class Scopes:
    """Standard scope sets for LUKHAS API testing."""

    # Read-only scopes
    MODELS_READ: List[str] = None
    EMBEDDINGS_READ: List[str] = None
    DREAMS_READ: List[str] = None

    # Write scopes
    RESPONSES_WRITE: List[str] = None
    DREAMS_WRITE: List[str] = None

    # Admin scopes
    ADMIN_ALL: List[str] = None

    def __init__(self):
        """Initialize scope sets."""
        self.MODELS_READ = ["models:read"]
        self.EMBEDDINGS_READ = ["embeddings:read"]
        self.DREAMS_READ = ["dreams:read"]
        self.RESPONSES_WRITE = ["responses:write", "models:read"]
        self.DREAMS_WRITE = ["dreams:write", "dreams:read"]
        self.ADMIN_ALL = [
            "models:read", "models:write",
            "embeddings:read", "embeddings:write",
            "responses:read", "responses:write",
            "dreams:read", "dreams:write",
            "admin:full"
        ]


# Singleton instance
SCOPES = Scopes()


def get_auth_headers(
    scopes: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    project_id: Optional[str] = None,
    api_key: Optional[str] = None,
    include_openai_headers: bool = True
) -> Dict[str, str]:
    """Get standardized auth headers for testing.

    Args:
        scopes: List of OAuth scopes (default: models:read).
        user_id: User identifier (default: TEST_USER_ID).
        org_id: Organization identifier (default: TEST_ORG_ID).
        project_id: Project identifier (default: TEST_PROJECT_ID).
        api_key: API key (default: TEST_API_KEY).
        include_openai_headers: Include OpenAI-compatible headers (default: True).

    Returns:
        Dict of HTTP headers ready for API requests.

    Example:
        >>> headers = get_auth_headers(scopes=SCOPES.MODELS_READ)
        >>> headers = get_auth_headers(scopes=SCOPES.RESPONSES_WRITE, user_id=TEST_USER_BOB)
    """
    scopes = scopes or SCOPES.MODELS_READ
    user_id = user_id or TEST_USER_ID
    org_id = org_id or TEST_ORG_ID
    project_id = project_id or TEST_PROJECT_ID
    api_key = api_key or TEST_API_KEY

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-User-ID": user_id,
        "X-Org-ID": org_id,
        "X-Project-ID": project_id,
        "X-Scopes": ",".join(scopes),
        "Content-Type": "application/json",
    }

    if include_openai_headers:
        headers.update({
            "OpenAI-Organization": org_id,
            "OpenAI-Project": project_id,
        })

    return headers


def get_minimal_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Get minimal auth headers (API key only).

    Args:
        api_key: API key (default: TEST_API_KEY).

    Returns:
        Dict with minimal authentication headers.

    Example:
        >>> headers = get_minimal_headers()
    """
    api_key = api_key or TEST_API_KEY
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def get_multi_user_headers() -> Dict[str, Dict[str, str]]:
    """Get headers for multiple test users (Alice, Bob, Charlie).

    Returns:
        Dict mapping user names to their auth headers.

    Example:
        >>> users = get_multi_user_headers()
        >>> alice_response = client.get("/v1/dreams", headers=users["alice"])
        >>> bob_response = client.get("/v1/dreams", headers=users["bob"])
    """
    return {
        "alice": get_auth_headers(user_id=TEST_USER_ID, scopes=SCOPES.MODELS_READ),
        "bob": get_auth_headers(user_id=TEST_USER_BOB, scopes=SCOPES.MODELS_READ),
        "charlie": get_auth_headers(user_id=TEST_USER_CHARLIE, scopes=SCOPES.MODELS_READ),
    }
