"""
Strict Authentication Middleware
"""

import logging
from typing import Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

try:
    # Prefer the stable 'core' bridge module for imports
    from core.security.auth import get_auth_system
except ImportError:
    # Fallback to the direct 'labs' implementation if the bridge is not available
    # This might happen in certain testing contexts or isolated environments.
    logger.warning("Could not import get_auth_system from core.security.auth, falling back to labs.")
    from labs.core.security.auth import get_auth_system


class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Validates JWT Bearer tokens for protected routes and attaches user context to the request.

    - Enforces JWT validation for all /v1/* and /api/* paths.
    - Bypasses authentication for health and metrics endpoints.
    - Extracts user_id, tier, and permissions from valid JWT claims.
    - Attaches user context to request.state.
    - Returns a 401 Unauthorized response for missing or invalid tokens.
    """

    def __init__(self, app):
        super().__init__(app)
        # Initialize the authentication system singleton to handle JWT operations
        self.auth_system = get_auth_system()
        # Define a set of paths that bypass authentication checks
        self.bypassed_paths = {"/healthz", "/health", "/readyz", "/metrics"}
        # Define prefixes for paths that require authentication
        self.protected_prefixes = ("/v1/", "/api/")

    async def dispatch(self, request: Request, call_next):
        """
        The middleware entrypoint. It processes the request, performs authentication,
        and then passes it to the next handler in the chain.
        """
        # Bypass authentication for configured health and metrics endpoints
        if request.url.path in self.bypassed_paths:
            return await call_next(request)

        # Enforce authentication only for protected paths
        if not request.url.path.startswith(self.protected_prefixes):
            return await call_next(request)

        # Extract the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._unauthorized_response("Authorization header is missing")

        # Validate the Bearer token scheme
        if not auth_header.startswith("Bearer "):
            return self._unauthorized_response("Authorization header must use Bearer scheme")

        token = auth_header.split(" ")[-1].strip()
        if not token:
            return self._unauthorized_response("Bearer token is empty")

        # Verify the JWT using the authentication system
        claims = self.auth_system.verify_jwt(token)
        if not claims:
            return self._unauthorized_response("JWT is invalid, expired, or malformed")

        # Attach user context to the request state for use in downstream endpoints
        try:
            # The prompt mentions `sub` claim, but the codebase's `generate_jwt` uses `user_id`.
            # We will adhere to the existing implementation which uses the `user_id` claim.
            # If the JWT format standardizes on `sub`, `generate_jwt` should be updated.
            request.state.user_id = claims["user_id"]
            request.state.user_tier = claims.get("tier", 0)
            request.state.user_permissions = claims.get("permissions", [])
        except KeyError:
            logger.warning("JWT is valid but missing the 'user_id' claim.")
            return self._unauthorized_response("JWT is missing the required 'user_id' claim")

        # Proceed to the next middleware or the endpoint itself
        response = await call_next(request)
        return response

    def _unauthorized_response(self, message: str) -> Response:
        """
        Creates and returns a standardized 401 Unauthorized JSON response.
        """
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "message": message,
                    "type": "invalid_request_error",
                    "param": None,
                    "code": "authentication_error",
                }
            },
        )
