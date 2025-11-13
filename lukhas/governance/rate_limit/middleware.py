"""
Rate limiting middleware for FastAPI.

Implements sliding window rate limiting with per-user and per-IP limits.
Integrates with StrictAuthMiddleware for user context.
"""

import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import RateLimitConfig
from .storage import InMemoryRateLimitStorage, RateLimitStorage

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.

    Features:
    - Per-user rate limiting (from JWT token)
    - Per-IP rate limiting (DDoS prevention)
    - Tier-based limits
    - Path-specific limits
    - Whitelisting and blacklisting
    - Standard rate limit headers

    Integration:
    - Must be added AFTER StrictAuthMiddleware to access user_id
    - Reads user_id from request.state.user_id (populated by auth middleware)
    - Reads user_tier from request.state.user_tier (optional)

    Security: OWASP A04 (Insecure Design) mitigation - prevents DoS attacks
    """

    def __init__(
        self,
        app,
        config: Optional[RateLimitConfig] = None,
        storage: Optional[RateLimitStorage] = None,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application instance
            config: Rate limit configuration (creates default if None)
            storage: Storage backend (creates InMemoryRateLimitStorage if None)
        """
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.storage = storage or InMemoryRateLimitStorage()
        logger.info(f"RateLimitMiddleware initialized: enabled={self.config.enabled}")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Flow:
        1. Check if rate limiting is enabled
        2. Extract client IP and user_id
        3. Check if IP is blocked/whitelisted
        4. Check per-IP rate limits
        5. Check per-user rate limits (if authenticated)
        6. If allowed, process request and add rate limit headers
        7. If denied, return 429 Too Many Requests

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response with rate limit headers or 429 error
        """
        # Skip if rate limiting is disabled
        if not self.config.enabled:
            return await call_next(request)

        # Extract client IP
        client_ip = self._get_client_ip(request)

        # Check if IP is blocked
        if self.config.is_ip_blocked(client_ip):
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "forbidden",
                    "message": "Access denied from this IP address",
                },
            )

        # Check if IP is whitelisted (skip rate limiting)
        if self.config.is_ip_whitelisted(client_ip):
            logger.debug(f"Whitelisted IP bypassing rate limits: {client_ip}")
            return await call_next(request)

        # Get request path
        path = request.url.path

        # Check per-IP rate limits (always applied)
        ip_result = self._check_ip_rate_limit(client_ip, path)
        if not ip_result.allowed:
            logger.warning(
                f"IP rate limit exceeded: {client_ip} on {path} "
                f"(limit: {ip_result.limit}, retry after: {ip_result.retry_after}s)"
            )
            return self._rate_limit_response(ip_result, scope="ip")

        # Check per-user rate limits (if authenticated)
        user_id = getattr(request.state, "user_id", None)
        user_tier = getattr(request.state, "user_tier", 0)  # Default to tier 0 (free)

        if user_id:
            user_result = self._check_user_rate_limit(user_id, user_tier, path)
            if not user_result.allowed:
                logger.warning(
                    f"User rate limit exceeded: {user_id} (tier {user_tier}) on {path} "
                    f"(limit: {user_result.limit}, retry after: {user_result.retry_after}s)"
                )
                return self._rate_limit_response(user_result, scope="user")

            # Use user result for headers (more specific)
            rate_result = user_result
        else:
            # Use IP result for headers
            rate_result = ip_result

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        self._add_rate_limit_headers(response, rate_result)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Checks X-Forwarded-For header (for proxies) and falls back to client host.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address as string
        """
        # Check X-Forwarded-For header (for proxies/load balancers)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP (client IP)
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header (alternative proxy header)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client host
        if request.client:
            return request.client.host

        # Default fallback (should never happen)
        return "unknown"

    def _check_ip_rate_limit(self, ip: str, path: str):
        """
        Check per-IP rate limits.

        Args:
            ip: Client IP address
            path: Request path

        Returns:
            RateLimitResult indicating if request is allowed
        """
        # Get applicable rules for this path
        rules = self.config.get_rules_for_ip(path)

        if not rules:
            # No rules apply - allow by default
            from .storage import RateLimitResult

            return RateLimitResult(
                allowed=True, remaining=999999, reset_time=time.time() + 3600, retry_after=0, limit=999999
            )

        # Check most specific rule first
        rule = rules[0]

        # Generate rate limit key
        key = f"ip:{ip}:path:{rule.path_pattern}"

        # Check rate limit
        return self.storage.check_rate_limit(key, rule.requests, rule.window_seconds)

    def _check_user_rate_limit(self, user_id: str, tier: int, path: str):
        """
        Check per-user rate limits.

        Args:
            user_id: Authenticated user ID
            tier: User tier level (0=free, 1=basic, 2+=pro)
            path: Request path

        Returns:
            RateLimitResult indicating if request is allowed
        """
        # Get applicable rules for this user/tier/path
        rules = self.config.get_rules_for_user(path, tier)

        if not rules:
            # No rules apply - allow by default
            from .storage import RateLimitResult

            return RateLimitResult(
                allowed=True, remaining=999999, reset_time=time.time() + 3600, retry_after=0, limit=999999
            )

        # Check most specific rule first
        rule = rules[0]

        # Generate rate limit key
        key = f"user:{user_id}:path:{rule.path_pattern}:tier:{tier}"

        # Check rate limit
        return self.storage.check_rate_limit(key, rule.requests, rule.window_seconds)

    def _rate_limit_response(self, result, scope: str = "user") -> JSONResponse:
        """
        Create 429 Too Many Requests response.

        Args:
            result: RateLimitResult with rate limit details
            scope: Rate limit scope ("user" or "ip")

        Returns:
            JSONResponse with 429 status and rate limit headers
        """
        response = JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded for {scope}. Please try again later.",
                "retry_after": result.retry_after,
                "limit": result.limit,
                "reset_time": int(result.reset_time),
            },
        )

        # Add standard rate limit headers
        self._add_rate_limit_headers(response, result)

        # Add Retry-After header (standard HTTP header for 429)
        response.headers["Retry-After"] = str(result.retry_after)

        return response

    def _add_rate_limit_headers(self, response: Response, result) -> None:
        """
        Add standard rate limit headers to response.

        Headers:
        - X-RateLimit-Limit: Maximum requests allowed
        - X-RateLimit-Remaining: Requests remaining in window
        - X-RateLimit-Reset: Unix timestamp when limit resets

        Args:
            response: Response object to modify
            result: RateLimitResult with rate limit details
        """
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(result.reset_time))
