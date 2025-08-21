#!/usr/bin/env python3
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
from typing import Any, Optional

import structlog
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

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
            )

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
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
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

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

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


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[int] = None
) -> str:
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
        expire = datetime.now(timezone.utc).timestamp() + (
            ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

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
