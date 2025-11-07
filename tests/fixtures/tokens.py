#!/usr/bin/env python3
"""
Golden Token Kit: Standard auth headers with known-good scopes for test stability.

Provides:
- Reusable auth fixtures for tests
- Known-good token scopes (chat, embeddings, models)
- Tenant isolation patterns

Usage:
  from tests.fixtures.tokens import golden_chat_headers, golden_embed_headers

  def test_chat_completion(golden_chat_headers):
      response = client.post("/v1/chat/completions", headers=golden_chat_headers, ...)
      assert response.status_code == 200
"""
import os
# from typing import Dict  # All imports converted to builtins (PEP 585)


# Environment-aware token configuration
def _get_auth_token() -> str:
    """Get auth token from environment or use test default."""
    return os.getenv("LUKHAS_AUTH_TOKEN", "test-golden-token-chat-v1")


def _get_tenant_id() -> str:
    """Get tenant ID from environment or use test default."""
    return os.getenv("LUKHAS_TENANT_ID", "tenant-default-test")


# Golden headers for different scopes
def golden_chat_headers() -> dict[str, str]:
    """
    Standard headers for /v1/chat/completions endpoints.

    Includes:
    - Authorization with known-good token
    - Content-Type application/json
    - X-Tenant-ID for tenant isolation
    """
    return {
        "Authorization": f"Bearer {_get_auth_token()}",
        "Content-Type": "application/json",
        "X-Tenant-ID": _get_tenant_id()
    }


def golden_embed_headers() -> dict[str, str]:
    """
    Standard headers for /v1/embeddings endpoints.

    Includes:
    - Authorization with embeddings-specific token
    - Content-Type application/json
    - X-Tenant-ID for tenant isolation
    """
    token = os.getenv("LUKHAS_AUTH_TOKEN_EMBED", "test-golden-token-embed-v1")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": _get_tenant_id()
    }


def golden_models_headers() -> dict[str, str]:
    """
    Standard headers for /v1/models endpoints.

    Includes:
    - Authorization with models-specific token (read-only scope)
    - Content-Type application/json
    - X-Tenant-ID for tenant isolation
    """
    token = os.getenv("LUKHAS_AUTH_TOKEN_MODELS", "test-golden-token-models-v1")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Tenant-ID": _get_tenant_id()
    }


def golden_admin_headers() -> dict[str, str]:
    """
    Standard headers for admin endpoints (internal APIs).

    Includes:
    - Authorization with admin token (full scope)
    - Content-Type application/json
    - X-Admin-Request marker
    """
    token = os.getenv("LUKHAS_AUTH_TOKEN_ADMIN", "test-golden-token-admin-v1")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Admin-Request": "true"
    }


# Pytest fixtures (if using pytest)
try:
    import pytest

    @pytest.fixture
    def chat_headers() -> dict[str, str]:
        """Pytest fixture for chat completion headers."""
        return golden_chat_headers()

    @pytest.fixture
    def embed_headers() -> dict[str, str]:
        """Pytest fixture for embeddings headers."""
        return golden_embed_headers()

    @pytest.fixture
    def models_headers() -> dict[str, str]:
        """Pytest fixture for models list headers."""
        return golden_models_headers()

    @pytest.fixture
    def admin_headers() -> dict[str, str]:
        """Pytest fixture for admin headers."""
        return golden_admin_headers()

except ImportError:
    # pytest not installed, skip fixture definitions
    pass


# Token validation helpers
def validate_token_format(token: str) -> bool:
    """
    Validate token format (basic sanity check).

    Returns:
        True if token looks valid, False otherwise
    """
    if not token or not isinstance(token, str):
        return False

    # Basic checks:
    # - Non-empty
    # - Minimum length (avoid stub tokens like "test")
    # - No whitespace
    if len(token) < 10 or token.strip() != token:
        return False

    return True


def is_test_environment() -> bool:
    """
    Detect if we're in a test environment.

    Returns:
        True if LUKHAS_ENV=test or pytest is running
    """
    env = os.getenv("LUKHAS_ENV", "").lower()
    if env == "test":
        return True

    # Check if pytest is running
    import sys
    return "pytest" in sys.modules


# Token scopes reference (for documentation)
TOKEN_SCOPES = {
    "chat": [
        "chat.completions.create",
        "chat.completions.read"
    ],
    "embeddings": [
        "embeddings.create",
        "embeddings.read"
    ],
    "models": [
        "models.list",
        "models.read"
    ],
    "admin": [
        "admin.*",
        "tenant.manage",
        "quota.manage"
    ]
}


def get_scope_for_endpoint(endpoint: str) -> str:
    """
    Map endpoint path to required token scope.

    Args:
        endpoint: API endpoint path (e.g., "/v1/chat/completions")

    Returns:
        Scope name ("chat", "embeddings", "models", "admin")
    """
    if "/chat/completions" in endpoint:
        return "chat"
    elif "/embeddings" in endpoint:
        return "embeddings"
    elif "/models" in endpoint:
        return "models"
    elif "/admin" in endpoint or "/internal" in endpoint:
        return "admin"
    else:
        return "unknown"
