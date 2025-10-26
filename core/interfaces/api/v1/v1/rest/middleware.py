#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - API AUTHENTICATION MIDDLEWARE
║ Provides authentication and authorization for REST API endpoints
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: middleware.py
║ Path: lukhas/interfaces/api/v1/rest/middleware.py
║ Version: 1.0.0 | Created: 2025-07-26 | Modified: 2025-07-26
║ Authors: LUKHAS AI API Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Implements authentication middleware for the LUKHAS REST API, including:
║ - JWT token validation
║ - API key authentication
║ - Tier-based access control
║ - Request logging and monitoring
╚═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import functools
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional

# Replaced python-jose (vulnerable) with PyJWT for secure JWT handling
import jwt
import structlog
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from jwt.exceptions import InvalidTokenError as JWTError
from fastapi.responses import JSONResponse

from governance.identity.core.id_service import get_identity_manager

# Import centralized decorators and tier system

# Import validators
try:
    from interfaces.api.v1.common.validators import validate_api_key
except ImportError:
    # Fallback if validators not available

    def validate_api_key(api_key: str) -> bool:
        """Basic API key validation."""
        return len(api_key) >= 32


logger = structlog.get_logger(__name__)

# ΛTAG: identity_registry
IDENTITY_MANAGER = get_identity_manager()


def _extract_request_from_args(*args: Any, **kwargs: Any) -> Request:
    """Extract the FastAPI request object from decorator arguments."""

    # ΛTAG: request_introspection
    for candidate in list(args) + list(kwargs.values()):
        if isinstance(candidate, Request):
            return candidate
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Request context missing for tier enforcement",
    )


def _coerce_tier(value: Any) -> Optional[int]:
    """Normalize tier representation into an integer value."""

    # ΛTAG: tier_parsing
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        digits = "".join(ch for ch in value if ch.isdigit())
        if digits:
            return int(digits)
    return None


def require_tier(min_tier: int, *, identity_manager: Optional[Any] = None) -> Callable:
    """Decorator enforcing minimum tier access for FastAPI endpoints."""

    resolved_identity_manager = identity_manager or IDENTITY_MANAGER

    def decorator(func: Callable) -> Callable:
        """Wrap FastAPI endpoint with tier enforcement logic."""

        def _enforce(request: Request) -> None:
            user_tier = _coerce_tier(getattr(request.state, "user_tier", None))
            fallback_tier = _coerce_tier(getattr(request.state, "tier_level", None))
            effective_tier = user_tier if user_tier is not None else fallback_tier

            if effective_tier is None:
                if getattr(request.state, "user_id", None):
                    identity_record = resolved_identity_manager.get_user_identity(
                        request.state.user_id
                    )
                    effective_tier = _coerce_tier(identity_record.get("tier"))

            if effective_tier is None:
                logger.warning(
                    "tier_context_missing",
                    user_id=getattr(request.state, "user_id", None),
                    path=request.url.path,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tier information missing",
                )

            if effective_tier < min_tier:
                # ΛTAG: tier_violation
                logger.warning(
                    "tier_violation",
                    required_tier=min_tier,
                    user_tier=effective_tier,
                    user_id=getattr(request.state, "user_id", None),
                    path=request.url.path,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient access tier",
                )

            request.state.user_tier = effective_tier
            logger.info(
                "tier_access_granted",
                required_tier=min_tier,
                user_tier=effective_tier,
                user_id=getattr(request.state, "user_id", None),
                path=request.url.path,
            )

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any):
                request = _extract_request_from_args(*args, **kwargs)
                _enforce(request)
                return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            request = _extract_request_from_args(*args, **kwargs)
            _enforce(request)
            return func(*args, **kwargs)

        return sync_wrapper

    return decorator


@dataclass
class RateLimitConfig:
    """Configuration for a specific tier rate limit."""

    limit: Optional[int]
    window_seconds: int


class RateLimitMiddleware:
    """Rate limiting middleware with tier-based policies."""

    DEFAULT_LIMITS: Dict[int, RateLimitConfig] = {
        0: RateLimitConfig(limit=1000, window_seconds=3600),
        1: RateLimitConfig(limit=5000, window_seconds=3600),
    }

    def __init__(
        self,
        *,
        rate_limits: Optional[Dict[int, RateLimitConfig]] = None,
        identity_manager: Optional[Any] = None,
        time_provider: Callable[[], float] = time.time,
    ) -> None:
        self.rate_limits = rate_limits or self.DEFAULT_LIMITS.copy()
        self.identity_manager = identity_manager or IDENTITY_MANAGER
        self.time_provider = time_provider
        self._request_counts: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    def _resolve_key(self, request: Request) -> str:
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key}"
        client_host = getattr(request.client, "host", "anonymous")
        return f"ip:{client_host}"

    def _resolve_limit(self, tier: Optional[int]) -> Optional[RateLimitConfig]:
        if tier is None:
            return self.rate_limits.get(0)
        if tier >= 2:
            return RateLimitConfig(limit=None, window_seconds=3600)
        return self.rate_limits.get(tier) or self.rate_limits.get(0)

    async def _increment_counter(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> tuple[int, float]:
        now = self.time_provider()
        async with self._locks[key]:
            record = self._request_counts[key]
            reset_at = record.get("reset_at", now + config.window_seconds)

            if now >= reset_at:
                record = {"count": 0, "reset_at": now + config.window_seconds}

            record["count"] = record.get("count", 0) + 1
            self._request_counts[key] = record
            return int(record["count"]), float(record["reset_at"])

    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Any]]):
        tier = _coerce_tier(getattr(request.state, "user_tier", None))
        if tier is None:
            identity = None
            if getattr(request.state, "user_id", None):
                identity = self.identity_manager.get_user_identity(request.state.user_id)
            if identity:
                tier = _coerce_tier(identity.get("tier"))
            if tier is None:
                tier = _coerce_tier(getattr(request.state, "tier_level", None))

        config = self._resolve_limit(tier)
        if config is None:
            response = await call_next(request)
            return response

        key = self._resolve_key(request)

        if config.limit is None:
            headers = self._build_headers(limit="unlimited", remaining="unlimited", reset=0)
            response = await call_next(request)
            response.headers.update(headers)
            request.state.rate_limit_remaining = "unlimited"
            return response

        count, reset_at = await self._increment_counter(key, config)
        remaining = max(config.limit - count, 0)
        reset_delta = max(reset_at - self.time_provider(), 0)

        headers = self._build_headers(
            limit=config.limit,
            remaining=remaining,
            reset=round(reset_delta, 3),
        )

        if count > config.limit:
            # ΛTAG: rate_limit_guard
            logger.warning(
                "rate_limit_exceeded",
                key=key,
                tier=tier,
                limit=config.limit,
                window_seconds=config.window_seconds,
            )
            request.state.rate_limit_remaining = 0
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
                headers=headers,
            )

        response = await call_next(request)
        response.headers.update(headers)
        request.state.rate_limit_remaining = remaining
        return response

    @staticmethod
    def _build_headers(limit: Any, remaining: Any, reset: Any) -> Dict[str, str]:
        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
        }

# Configuration
SECRET_KEY = os.getenv("LUKHAS_JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("LUKHAS_JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("LUKHAS_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security bearer
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for LUKHAS REST API."""

    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.excluded_paths = [
            "/api/v1/health",
            "/api/v1/docs",
            "/api/v1/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]

    async def __call__(self, request: Request, call_next):
        """Process authentication for incoming requests."""
        start_time = time.time()

        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            response = await call_next(request)
            return response

        try:
            # Extract authentication credentials
            auth_result = await self.authenticate_request(request)

            # Add authentication info to request state
            request.state.user_id = auth_result.get("user_id")
            request.state.tier_level = auth_result.get("tier_level", 0)
            # ΛTAG: tier_state_alias
            request.state.user_tier = request.state.tier_level
            request.state.auth_method = auth_result.get("auth_method")

            # Log authentication success
            process_time = time.time() - start_time
            logger.info(
                "auth_success",
                user_id=request.state.user_id,
                tier_level=request.state.tier_level,
                auth_method=request.state.auth_method,
                path=request.url.path,
                method=request.method,
                process_time=process_time,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Process request
            response = await call_next(request)

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"

            return response

        except HTTPException as e:
            # Log authentication failure
            process_time = time.time() - start_time
            logger.warning(
                "auth_failed",
                error=str(e.detail),
                path=request.url.path,
                method=request.method,
                process_time=process_time,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            raise

        except Exception as e:
            # Log unexpected error
            process_time = time.time() - start_time
            logger.error(
                "auth_error",
                error=str(e),
                error_type=type(e).__name__,
                path=request.url.path,
                method=request.method,
                process_time=process_time,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error",
            ) from e

    async def authenticate_request(self, request: Request) -> dict[str, Any]:
        """Authenticate the incoming request.

        Returns:
            Dict containing user_id, tier_level, and auth_method
        """
        # Check for JWT token in Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            return await self.validate_jwt_token(token)

        # Check for API key in X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return await self.validate_api_key(api_key)

        # No valid authentication found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def validate_jwt_token(self, token: str) -> dict[str, Any]:
        """Validate JWT token and extract user information."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return {
                "user_id": payload.get("sub"),
                "tier_level": payload.get("tier_level", 1),
                "auth_method": "jwt",
            }

        except JWTError as jwt_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from jwt_error

    async def validate_api_key(self, api_key: str) -> dict[str, Any]:
        """Validate API key and extract associated information."""
        # Use the validator to check API key format
        if not validate_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
            )

        # TODO: Implement actual API key lookup from database/cache
        # For now, use a simple validation based on key pattern

        # Example tier mapping based on API key prefix
        if api_key.startswith("sk_live_admin_"):
            tier_level = 4
        elif api_key.startswith("sk_live_pro_"):
            tier_level = 3
        elif api_key.startswith("sk_live_std_"):
            tier_level = 2
        elif api_key.startswith("sk_live_"):
            tier_level = 1
        else:
            tier_level = 0

        return {
            # Extract last 8 chars as user identifier
            "user_id": f"api_user_{api_key[-8:]}",
            "tier_level": tier_level,
            "auth_method": "api_key",
        }


# Create singleton instance
auth_middleware = AuthMiddleware()


def create_access_token(data: dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time in minutes

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc).timestamp() + (expires_delta * 60)
    else:
        expire = datetime.now(timezone.utc).timestamp() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# TODO: Import lukhas_tier_required decorator
# @lukhas_tier_required(level=1)
def get_current_user(request: Request) -> dict[str, Any]:
    """Get current authenticated user from request.

    Args:
        request: FastAPI request object

    Returns:
        User information dict
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return {
        "user_id": request.state.user_id,
        "tier_level": request.state.tier_level,
        "auth_method": request.state.auth_method,
    }
