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

import os
import time
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Optional

# Replaced python-jose (vulnerable) with PyJWT for secure JWT handling
import jwt
try:  # pragma: no cover - structlog optional in lightweight environments
    import structlog
except ImportError:  # pragma: no cover
    structlog = SimpleNamespace(get_logger=lambda name=None: logging.getLogger(name or __name__))
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from jwt.exceptions import InvalidTokenError as JWTError

from candidate.core.common import lukhas_tier_required
from candidate.core.interfaces.api.v1.common import ApiKeyCache, api_key_cache

# Import validators
try:
    from interfaces.api.v1.common.validators import validate_api_key
except ImportError:
    # Fallback if validators not available

    def validate_api_key(api_key: str) -> bool:
        """Basic API key validation."""
        return len(api_key) >= 32


logger = structlog.get_logger(__name__)

# Configuration
SECRET_KEY = os.getenv("LUKHAS_JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("LUKHAS_JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("LUKHAS_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security bearer
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for LUKHAS REST API."""

    def __init__(self, key_cache: Optional[ApiKeyCache] = None):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.excluded_paths = [
            "/api/v1/health",
            "/api/v1/docs",
            "/api/v1/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]
        self._api_key_cache = key_cache or api_key_cache

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
            request.state.auth_method = auth_result.get("auth_method")
            request.state.scopes = auth_result.get("scopes", ())

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

        metadata = self._api_key_cache.lookup(api_key)

        if metadata and metadata.revoked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key revoked",
            )

        if metadata and metadata.is_expired():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key expired",
            )

        if metadata:
            logger.info(
                "api_key_authenticated",
                user_id=metadata.user_id,
                tier_level=metadata.tier,
                scopes=list(metadata.scopes),
                source=metadata.attributes.get("source", "cache"),
            )
            return {
                "user_id": metadata.user_id,
                "tier_level": metadata.tier,
                "auth_method": "api_key",
                "scopes": metadata.scopes,
            }

        if self._api_key_cache.is_configured():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key not recognized",
            )

        tier_level = self._infer_tier_from_prefix(api_key)

        return {
            "user_id": f"api_user_{api_key[-8:]}",
            "tier_level": tier_level,
            "auth_method": "api_key",
            "scopes": (),
        }

    def _infer_tier_from_prefix(self, api_key: str) -> int:
        """Infer tier from historical prefix patterns when no registry is configured."""

        prefix_mapping: dict[str, int] = {
            "sk_live_admin_": 4,
            "sk_live_pro_": 3,
            "sk_live_std_": 2,
            "sk_live_": 1,
        }

        for prefix, tier in prefix_mapping.items():
            if api_key.startswith(prefix):
                return tier

        return 0


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


@lukhas_tier_required(level=1)
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
