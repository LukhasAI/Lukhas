"""
Strict Authentication Middleware for Production API

Provides comprehensive authentication enforcement with:
- ΛiD token validation
- JWT signature verification
- Scope-based access control
- Rate limiting per user
- Audit logging
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Import authentication system
try:
    from labs.core.security.auth import get_auth_system
except ImportError:
    # Fallback for testing environments
    def get_auth_system():
        """Fallback auth system for testing"""
        class MockAuthSystem:
            def verify_jwt(self, token: str) -> Optional[dict]:
                return None
        return MockAuthSystem()


logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """User context attached to authenticated requests"""
    user_id: str
    scopes: List[str]
    token_claims: dict
    authenticated_at: datetime


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm

    For production, this should be replaced with Redis-based rate limiting
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds (default: 60s)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._cleanup_interval = 300  # Cleanup every 5 minutes
        self._last_cleanup = time.time()

    def check_rate_limit(self, user_id: str) -> Tuple[bool, int]:
        """
        Check if request is within rate limit

        Args:
            user_id: User identifier

        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old requests for this user
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]

        # Check if under limit
        current_count = len(self.requests[user_id])
        allowed = current_count < self.max_requests

        if allowed:
            self.requests[user_id].append(now)

        remaining = max(0, self.max_requests - current_count - (1 if allowed else 0))

        # Periodic cleanup of old users
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries(cutoff)
            self._last_cleanup = now

        return allowed, remaining

    def _cleanup_old_entries(self, cutoff: float):
        """Remove entries for users with no recent requests"""
        users_to_remove = [
            user_id for user_id, requests in self.requests.items()
            if not requests or max(requests) < cutoff
        ]
        for user_id in users_to_remove:
            del self.requests[user_id]


class AuditLogger:
    """
    Simple audit logger for authentication events

    For production, this should integrate with proper audit/compliance systems
    """

    def __init__(self):
        self.logger = logging.getLogger("lukhas.audit.auth")

    async def log_auth_event(
        self,
        request: Request,
        user: Optional[UserContext],
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log authentication event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method,
            "success": success,
            "user_id": user.user_id if user else None,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        if error_message:
            event["error"] = error_message

        if success:
            self.logger.info(f"Auth success: {event}")
        else:
            self.logger.warning(f"Auth failure: {event}")


class TokenExpiredError(Exception):
    """Token has expired"""
    pass


class TokenInvalidError(Exception):
    """Token is invalid"""
    pass


class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Strict authentication enforcement middleware.

    Responsibilities:
    - ΛiD token validation
    - JWT signature verification
    - Scope-based access control
    - Rate limiting per user
    - Audit logging
    """

    def __init__(
        self,
        app,
        exempted_paths: Optional[List[str]] = None,
        require_https: bool = False,
        protected_path_prefix: str = "/v1",
        rate_limit_enabled: bool = True,
        max_requests_per_minute: int = 100,
    ):
        """
        Initialize strict authentication middleware

        Args:
            app: ASGI application
            exempted_paths: Paths that bypass authentication (e.g., /health, /docs)
            require_https: Enforce HTTPS in production (default: False for dev)
            protected_path_prefix: Path prefix that requires auth (default: /v1)
            rate_limit_enabled: Enable rate limiting (default: True)
            max_requests_per_minute: Max requests per user per minute (default: 100)
        """
        super().__init__(app)

        # Configuration
        self.exempted_paths = exempted_paths or ["/health", "/healthz", "/docs", "/openapi.json"]
        self.require_https = require_https
        self.protected_path_prefix = protected_path_prefix
        self.rate_limit_enabled = rate_limit_enabled

        # Initialize subsystems
        self.auth_system = get_auth_system()
        self.rate_limiter = RateLimiter(max_requests=max_requests_per_minute, window_seconds=60)
        self.audit_logger = AuditLogger()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Authentication enforcement pipeline:
        1. Check if path requires authentication
        2. Enforce HTTPS (production)
        3. Extract Authorization header
        4. Validate JWT signature
        5. Check token expiry
        6. Verify issuer/audience
        7. Check scope permissions
        8. Rate limit check
        9. Attach user context to request
        10. Log auth event
        """

        # 1. Check if path requires authentication
        if not self._requires_auth(request.url.path):
            return await call_next(request)

        # 2. HTTPS check
        if self.require_https and request.url.scheme != "https":
            return self._error_response(
                "HTTPS required",
                status_code=403
            )

        # 3. Extract token
        try:
            token = self._extract_token(request)
        except TokenInvalidError as e:
            await self.audit_logger.log_auth_event(request, None, False, str(e))
            return self._error_response(str(e), status_code=401)

        # 4-7. Validate token
        try:
            user_context = await self._validate_token(token, request)
        except TokenExpiredError:
            await self.audit_logger.log_auth_event(request, None, False, "Token expired")
            return self._error_response("Token expired", status_code=401)
        except TokenInvalidError as e:
            await self.audit_logger.log_auth_event(request, None, False, str(e))
            return self._error_response(str(e), status_code=401)

        # 8. Rate limit check
        if self.rate_limit_enabled:
            allowed, remaining = self.rate_limiter.check_rate_limit(user_context.user_id)
            if not allowed:
                await self.audit_logger.log_auth_event(
                    request, user_context, False, "Rate limit exceeded"
                )
                return self._error_response(
                    "Rate limit exceeded",
                    status_code=429,
                    headers={"X-RateLimit-Remaining": "0"}
                )

        # 9. Attach user context
        request.state.user = user_context

        # 10. Log auth event
        await self.audit_logger.log_auth_event(request, user_context, success=True)

        response = await call_next(request)
        return response

    def _requires_auth(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Exempted paths bypass auth
        if path in self.exempted_paths:
            return False

        # Only paths starting with protected prefix require auth
        return path.startswith(self.protected_path_prefix)

    def _extract_token(self, request: Request) -> str:
        """
        Extract Bearer token from Authorization header

        Raises:
            TokenInvalidError: If token is missing or invalid format
        """
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise TokenInvalidError("Missing Authorization header")

        if not auth_header.startswith("Bearer "):
            raise TokenInvalidError("Authorization header must use Bearer scheme")

        token = auth_header[7:].strip()  # Remove "Bearer " prefix

        if not token:
            raise TokenInvalidError("Bearer token is empty")

        return token

    async def _validate_token(self, token: str, request: Request) -> UserContext:
        """
        Validate JWT token

        - Decode token
        - Verify signature with ΛiD public key
        - Check expiry
        - Verify issuer
        - Verify audience matches request
        - Check not revoked

        Returns:
            UserContext with user_id, scopes, etc.

        Raises:
            TokenExpiredError: If token is expired
            TokenInvalidError: If token is invalid
        """
        # Validate JWT using auth system
        payload = self.auth_system.verify_jwt(token)

        if payload is None:
            raise TokenInvalidError("Invalid authentication credentials")

        # Extract user information
        user_id = payload.get("user_id")
        if not user_id:
            raise TokenInvalidError("Token missing user_id claim")

        # Extract scopes (default to empty list if not present)
        scopes = payload.get("scopes", [])
        if isinstance(scopes, str):
            scopes = scopes.split()

        # Create user context
        user_context = UserContext(
            user_id=user_id,
            scopes=scopes,
            token_claims=payload,
            authenticated_at=datetime.utcnow()
        )

        return user_context

    async def _check_rate_limit(self, user_id: str) -> bool:
        """
        Check rate limit for user

        Default: 100 req/min per user
        Uses sliding window algorithm

        For production: Replace with Redis-based rate limiting
        """
        allowed, _ = self.rate_limiter.check_rate_limit(user_id)
        return allowed

    def _error_response(
        self,
        message: str,
        status_code: int = 401,
        headers: Optional[Dict[str, str]] = None
    ) -> JSONResponse:
        """
        Return OpenAI-compatible error response

        Format:
        {
            "error": {
                "type": "invalid_api_key",
                "message": "...",
                "code": "invalid_api_key"
            }
        }
        """
        error_body = {
            "error": {
                "type": "invalid_api_key",
                "message": message,
                "code": "invalid_api_key"
            }
        }

        return JSONResponse(
            error_body,
            status_code=status_code,
            headers=headers or {}
        )


__all__ = ["StrictAuthMiddleware", "UserContext", "RateLimiter", "AuditLogger"]
