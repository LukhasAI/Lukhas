"""
Authentication and authorization for OpenAI façade.

Enforces Bearer token presence, validates against policy guard,
and attaches verified claims (org, user, scopes) to request context.
"""
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Request
import logging
import hashlib

logger = logging.getLogger(__name__)

# OpenAI-compatible error responses
UNAUTHORIZED = {
    "error": {
        "type": "invalid_request_error",
        "message": "Invalid authentication. Please provide a valid Bearer token.",
        "code": "invalid_api_key"
    }
}

FORBIDDEN = {
    "error": {
        "type": "insufficient_permissions",
        "message": "The API key does not have permission for this operation.",
        "code": "insufficient_scope"
    }
}


class TokenClaims:
    """Verified token claims attached to request context."""
    def __init__(self, token: str, org_id: str = "default", user_id: str = "unknown", scopes: list = None):
        self.token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        self.org_id = org_id
        self.user_id = user_id
        self.scopes = scopes or ["api.read", "api.write"]


def verify_token_with_policy(token: str) -> TokenClaims:
    """
    Verify token against policy guard.

    TODO: Integrate with governance/policy_guard.py for:
    - Token signature verification
    - Organization/owner lookup
    - Scope/permission validation
    - Rate limit tier assignment

    For now, implements permissive stub that accepts any non-empty token.

    Args:
        token: Bearer token without "Bearer " prefix

    Returns:
        TokenClaims with org/user/scopes

    Raises:
        HTTPException: 401 if token invalid, 403 if insufficient permissions
    """
    # Stub implementation: accept any non-empty token
    # Real implementation would:
    # 1. Verify signature (JWT, PAT, service token)
    # 2. Lookup owner/org from policy database
    # 3. Check token expiry and revocation status
    # 4. Validate scopes match requested operation

    if not token or len(token) < 8:
        logger.warning(f"Token validation failed: token too short")
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)

    # Extract org from token prefix (stub logic)
    # Real tokens: sk-lukhas-{org}-{random}
    if token.startswith("sk-lukhas-"):
        parts = token.split("-")
        org_id = parts[2] if len(parts) > 2 else "default"
    else:
        org_id = "default"

    # Generate stable user ID from token
    user_id = hashlib.sha256(token.encode()).hexdigest()[:12]

    logger.debug(f"Token verified: org={org_id}, user={user_id}")

    return TokenClaims(
        token=token,
        org_id=org_id,
        user_id=user_id,
        scopes=["api.read", "api.write", "api.responses", "api.embeddings"]
    )


def require_bearer(
    authorization: Optional[str] = Header(default=None),
    required_scopes: list = None
) -> TokenClaims:
    """
    Enforce Bearer token authentication with scope validation.

    Args:
        authorization: Authorization header (Bearer {token})
        required_scopes: List of required scopes (default: any)

    Returns:
        TokenClaims with verified org/user/scopes

    Raises:
        HTTPException: 401 if auth missing/invalid, 403 if insufficient scopes

    Usage:
        @app.post("/v1/responses")
        def responses(claims: TokenClaims = Depends(require_bearer)):
            # claims.org_id, claims.user_id, claims.scopes available
            pass
    """
    # Check Authorization header present
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)

    # Check Bearer scheme
    if not authorization.lower().startswith("bearer "):
        logger.warning(f"Invalid auth scheme: {authorization[:20]}")
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)

    # Extract token
    token = authorization[7:].strip()  # Remove "Bearer " prefix

    # Verify token and get claims
    claims = verify_token_with_policy(token)

    # Check required scopes (if specified)
    if required_scopes:
        missing_scopes = set(required_scopes) - set(claims.scopes)
        if missing_scopes:
            logger.warning(
                f"Insufficient scopes for user {claims.user_id}: "
                f"missing {missing_scopes}"
            )
            raise HTTPException(status_code=403, detail=FORBIDDEN)

    return claims


def require_scope(*scopes: str):
    """
    Dependency factory for scope-based authorization.

    Usage:
        @app.post("/v1/admin")
        def admin(claims: TokenClaims = Depends(require_scope("admin.write"))):
            pass
    """
    def dependency(authorization: Optional[str] = Header(default=None)) -> TokenClaims:
        return require_bearer(authorization, required_scopes=list(scopes))
    return dependency
