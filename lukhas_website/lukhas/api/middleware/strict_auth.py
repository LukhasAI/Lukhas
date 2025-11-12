"""Strict authentication middleware enforcing auth on all routes except allowlist.

SECURITY: OWASP A01 (Broken Access Control) mitigation
This middleware enforces authentication on ALL routes by default, with only
a minimal allowlist of public endpoints. This is a critical security control.
"""

import logging
from typing import ClassVar, Set

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from lukhas.governance.audit import AuditEventType, AuditLogger
from lukhas.governance.audit.config import get_default_config

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
    Enforce authentication on all routes except explicit allowlist.

    Security Policy:
    - ALL routes require valid JWT token by default
    - ONLY allowlisted paths are public
    - Invalid/missing tokens return 401
    - Logs all auth failures for monitoring
    - Attaches validated user context to request.state for downstream use

    This middleware addresses OWASP A01 (Broken Access Control) by implementing
    a secure-by-default policy where every endpoint requires authentication
    unless explicitly marked as public.
    """

    # PUBLIC ENDPOINTS ONLY (minimal surface area)
    # Each endpoint must have clear justification for being public
    ALLOWED_PATHS: ClassVar[Set[str]] = {
        "/health",              # Health check for monitoring/load balancers
        "/healthz",             # Kubernetes health probe
        "/readyz",              # Kubernetes readiness probe
        "/metrics",             # Prometheus metrics endpoint
        "/docs",                # OpenAPI documentation UI
        "/openapi.json",        # OpenAPI schema
        "/redoc",               # Alternative API documentation UI
        # Authentication endpoints (must be public to allow login/registration)
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/identity/authenticate",  # Identity authentication endpoint
        # WebAuthn endpoints (required for passwordless authentication)
        "/id/webauthn/challenge",
        "/id/webauthn/verify",
    }

    def __init__(self, app):
        super().__init__(app)
        # Initialize the authentication system singleton to handle JWT operations
        self.auth_system = get_auth_system()
        # Initialize audit logger for authentication events
        self.audit_logger = AuditLogger(config=get_default_config())
        logger.info(
            f"StrictAuthMiddleware initialized with {len(self.ALLOWED_PATHS)} "
            f"public endpoints: {sorted(self.ALLOWED_PATHS)}"
        )

    async def dispatch(self, request: Request, call_next):
        """Check authentication for all non-allowlisted routes."""

        # Allow public endpoints (bypass authentication)
        if request.url.path in self.ALLOWED_PATHS:
            return await call_next(request)

        # Require authentication for everything else
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            client_ip = request.client.host if request.client else None
            logger.warning(
                f"Missing auth header: {request.method} {request.url.path} "
                f"from {client_ip or 'unknown'}"
            )
            # Log authentication failure
            self.audit_logger.log_security_event(
                event_type=AuditEventType.UNAUTHORIZED_ACCESS,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                resource_type="endpoint",
                resource_id=request.url.path,
                success=False,
                error_message="Missing Authorization header",
                metadata={"method": request.method}
            )
            return self._unauthorized_response(
                "Authentication required. Include 'Authorization: Bearer <token>' header."
            )

        if not auth_header.startswith("Bearer "):
            client_ip = request.client.host if request.client else None
            logger.warning(
                f"Invalid auth format: {request.method} {request.url.path} "
                f"from {client_ip or 'unknown'}"
            )
            # Log authentication failure
            self.audit_logger.log_security_event(
                event_type=AuditEventType.UNAUTHORIZED_ACCESS,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                resource_type="endpoint",
                resource_id=request.url.path,
                success=False,
                error_message="Invalid Authorization header format",
                metadata={"method": request.method}
            )
            return self._unauthorized_response(
                "Invalid authorization header format. Use 'Bearer <token>'."
            )

        # Extract token
        token = auth_header.split(" ", 1)[-1].strip()

        if not token:
            client_ip = request.client.host if request.client else None
            logger.warning(
                f"Empty token: {request.method} {request.url.path} "
                f"from {client_ip or 'unknown'}"
            )
            # Log authentication failure
            self.audit_logger.log_security_event(
                event_type=AuditEventType.UNAUTHORIZED_ACCESS,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                resource_type="endpoint",
                resource_id=request.url.path,
                success=False,
                error_message="Empty Bearer token",
                metadata={"method": request.method}
            )
            return self._unauthorized_response("Bearer token is empty")

        # Validate token using existing ΛiD system
        client_ip = request.client.host if request.client else None
        try:
            claims = self.auth_system.verify_jwt(token)

            if not claims:
                logger.warning(
                    f"Token validation failed: {request.method} {request.url.path} "
                    f"from {client_ip or 'unknown'}"
                )
                # Log authentication failure
                self.audit_logger.log_authentication_event(
                    user_id="unknown",
                    event_type=AuditEventType.LOGIN_FAILURE,
                    ip_address=client_ip,
                    user_agent=request.headers.get("User-Agent"),
                    success=False,
                    error_message="Invalid or expired token",
                    metadata={"method": request.method, "path": request.url.path}
                )
                return self._unauthorized_response(
                    "Invalid or expired authentication token."
                )

            # Store validated user context in request state for downstream use
            # Using existing claim structure (user_id, not sub)
            request.state.user_id = claims.get("user_id")
            request.state.user_tier = claims.get("tier", 0)
            request.state.user_permissions = claims.get("permissions", [])
            request.state.user = claims  # Full claims for advanced use cases

            # Validation: ensure required claims exist
            if not request.state.user_id:
                logger.warning(
                    f"JWT missing user_id claim: {request.method} {request.url.path}"
                )
                # Log authentication failure
                self.audit_logger.log_authentication_event(
                    user_id="unknown",
                    event_type=AuditEventType.LOGIN_FAILURE,
                    ip_address=client_ip,
                    user_agent=request.headers.get("User-Agent"),
                    success=False,
                    error_message="Missing user_id claim",
                    metadata={"method": request.method, "path": request.url.path}
                )
                return self._unauthorized_response(
                    "Invalid token: missing user_id claim"
                )

            # Log successful authentication
            self.audit_logger.log_authentication_event(
                user_id=request.state.user_id,
                event_type=AuditEventType.LOGIN_SUCCESS,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                success=True,
                metadata={
                    "method": request.method,
                    "path": request.url.path,
                    "tier": request.state.user_tier
                }
            )

        except Exception as e:
            logger.warning(
                f"Token validation error: {request.method} {request.url.path} "
                f"from {client_ip or 'unknown'} - {e!s}",
                exc_info=True
            )
            # Log authentication failure
            self.audit_logger.log_authentication_event(
                user_id="unknown",
                event_type=AuditEventType.LOGIN_FAILURE,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                success=False,
                error_message=str(e),
                metadata={"method": request.method, "path": request.url.path}
            )
            return self._unauthorized_response(
                "Invalid or expired authentication token."
            )

        # Authentication successful, proceed with request
        response = await call_next(request)
        return response

    def _unauthorized_response(self, message: str) -> Response:
        """
        Creates and returns a standardized 401 Unauthorized JSON response.

        Error format follows OpenAI API convention for compatibility.
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
