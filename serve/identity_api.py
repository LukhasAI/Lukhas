"""
ΛiD Identity API Routes
=======================
FastAPI routes for LUKHAS Lambda ID (ΛiD) authentication system.

This module provides:
- User authentication with credentials
- JWT token generation and refresh
- User profile management
- Token revocation and logout

SECURITY:
- Uses JWT with RS256 algorithm by default
- Access tokens: 1 hour TTL
- Refresh tokens: 7 days TTL
- Passwords hashed with bcrypt
- Token revocation support via in-memory blacklist

Integration:
- governance.identity: User lookup and validation
- governance.identity.auth_integrations.qrg_bridge: QRG token support
- serve.middleware.strict_auth: Token validation middleware
"""

import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator

from lukhas.governance.auth.dependencies import get_current_user

# Try to import JWT utilities (with fallback for testing)
try:
    from lukhas_website.lukhas.identity.jwt_utils import JWTManager, get_jwt_manager
    JWT_AVAILABLE = True
except ImportError:
    # Fallback for environments where lukhas_website is not available
    JWT_AVAILABLE = False
    JWTManager = None

    def get_jwt_manager():
        """Fallback JWT manager."""
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": "JWT utilities not available",
                    "type": "internal_error",
                    "code": "jwt_unavailable"
                }
            }
        )

# Try to import QRG bridge (with fallback)
try:
    from governance.identity.auth_integrations.qrg_bridge import QRGBridge
    QRG_AVAILABLE = True
except ImportError:
    QRG_AVAILABLE = False
    QRGBridge = None

# Try to import bcrypt for password hashing (with fallback)
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/identity", tags=["identity"])

# In-memory storage for demo purposes
# TODO: Replace with proper database integration
USERS_DB: Dict[str, Dict[str, Any]] = {
    "demo_user": {
        "user_id": "user_demo_001",
        "username": "demo_user",
        # Password: "demo_password" hashed with bcrypt
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eDJ8guWfJWem",
        "email": "demo@lukhas.ai",
        "created_at": datetime.utcnow().isoformat(),
        "scopes": ["read", "write"],
        "tier": 1,
        "permissions": ["user"],
    }
}

# Token revocation list (in-memory)
# TODO: Replace with Redis or database-backed solution
REVOKED_TOKENS: set = set()
REFRESH_TOKENS: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Request/Response Models
# ============================================================================

class AuthCredentials(BaseModel):
    """Authentication credentials request model."""

    username: str = Field(..., min_length=1, max_length=256, description="Username")
    password: str = Field(..., min_length=1, max_length=256, description="Password")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        # Prevent injection attacks
        if any(char in v for char in ['<', '>', '"', "'", '&', '\n', '\r', '\t']):
            raise ValueError("Username contains invalid characters")
        return v.lower()


class AuthResponse(BaseModel):
    """Authentication response with tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token for token renewal")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user_id: str = Field(..., description="Authenticated user ID")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")


class TokenRefreshRequest(BaseModel):
    """Token refresh request model."""

    refresh_token: str = Field(..., min_length=1, description="Refresh token")


class UserProfile(BaseModel):
    """User profile response model."""

    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email address")
    scopes: List[str] = Field(default_factory=list, description="User scopes")
    tier: int = Field(default=0, description="User tier level")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    created_at: str = Field(..., description="Account creation timestamp")


class LogoutResponse(BaseModel):
    """Logout response model."""

    message: str = Field(..., description="Logout confirmation message")
    revoked_tokens: int = Field(..., description="Number of tokens revoked")


# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    if BCRYPT_AVAILABLE:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    else:
        # Fallback to SHA-256 (NOT recommended for production)
        logger.warning("bcrypt not available, using SHA-256 (INSECURE for production)")
        salt = secrets.token_hex(16)
        return f"sha256${salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Plain text password
        password_hash: Hashed password

    Returns:
        True if password matches hash
    """
    if BCRYPT_AVAILABLE and password_hash.startswith("$2b$"):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    elif password_hash.startswith("sha256$"):
        # Fallback SHA-256 verification
        parts = password_hash.split("$")
        if len(parts) == 3:
            salt = parts[1]
            expected_hash = parts[2]
            actual_hash = hashlib.sha256((salt + password).encode()).hexdigest()
            return actual_hash == expected_hash
    return False


def generate_refresh_token() -> str:
    """
    Generate a secure refresh token.

    Returns:
        Random refresh token
    """
    return f"rt_{secrets.token_urlsafe(32)}"


def store_refresh_token(user_id: str, refresh_token: str, expires_in: int = 604800):
    """
    Store refresh token with expiry.

    Args:
        user_id: User ID
        refresh_token: Refresh token to store
        expires_in: Token expiry in seconds (default: 7 days)
    """
    REFRESH_TOKENS[refresh_token] = {
        "user_id": user_id,
        "expires_at": time.time() + expires_in,
        "created_at": time.time()
    }


def verify_refresh_token(refresh_token: str) -> Optional[str]:
    """
    Verify refresh token and return user ID.

    Args:
        refresh_token: Refresh token to verify

    Returns:
        User ID if token is valid, None otherwise
    """
    token_data = REFRESH_TOKENS.get(refresh_token)
    if not token_data:
        return None

    # Check if token is expired
    if token_data["expires_at"] < time.time():
        # Clean up expired token
        REFRESH_TOKENS.pop(refresh_token, None)
        return None

    # Check if token is revoked
    if refresh_token in REVOKED_TOKENS:
        return None

    return token_data["user_id"]


def revoke_token(token: str):
    """
    Add token to revocation list.

    Args:
        token: Token to revoke
    """
    REVOKED_TOKENS.add(token)


def is_token_revoked(token: str) -> bool:
    """
    Check if token is revoked.

    Args:
        token: Token to check

    Returns:
        True if token is revoked
    """
    return token in REVOKED_TOKENS


# ============================================================================
# API Routes
# ============================================================================

@router.post(
    "/auth",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate with ΛiD",
    description="Authenticate with Lambda ID credentials and receive JWT tokens.",
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "rt_abc123...",
                        "token_type": "bearer",
                        "expires_in": 3600,
                        "user_id": "user_demo_001",
                        "scopes": ["read", "write"]
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "Invalid credentials",
                            "type": "authentication_error",
                            "code": "invalid_credentials"
                        }
                    }
                }
            }
        }
    }
)
async def authenticate(credentials: AuthCredentials) -> AuthResponse:
    """
    Authenticate with ΛiD and return tokens.

    This endpoint validates user credentials and returns:
    - Access token (JWT, 1 hour TTL)
    - Refresh token (7 days TTL)

    The access token should be used in the Authorization header:
    `Authorization: Bearer {access_token}`

    Args:
        credentials: Username and password

    Returns:
        AuthResponse with tokens and user info

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 500: If JWT generation fails
    """
    logger.info(f"Authentication attempt for user: {credentials.username}")

    # 1. Validate credentials
    user = USERS_DB.get(credentials.username)
    if not user:
        logger.warning(f"Authentication failed: user not found - {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid credentials",
                    "type": "authentication_error",
                    "code": "invalid_credentials"
                }
            }
        )

    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning(f"Authentication failed: invalid password - {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid credentials",
                    "type": "authentication_error",
                    "code": "invalid_credentials"
                }
            }
        )

    # 2. Generate access token (JWT, 1 hour TTL)
    try:
        jwt_manager = get_jwt_manager()
        access_token = jwt_manager.create_access_token(
            user_id=user["user_id"],
            client_id="lukhas-web",
            scopes=user["scopes"],
            tier=str(user.get("tier", 0)),
            permissions=user.get("permissions", [])
        )
    except Exception as e:
        logger.error(f"JWT generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": "Token generation failed",
                    "type": "internal_error",
                    "code": "token_generation_failed"
                }
            }
        )

    # 3. Generate refresh token (7 days TTL)
    refresh_token = generate_refresh_token()

    # 4. Store refresh token in session store
    store_refresh_token(user["user_id"], refresh_token, expires_in=604800)  # 7 days

    # 5. Return tokens
    logger.info(f"Authentication successful for user: {credentials.username}")

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,  # 1 hour
        user_id=user["user_id"],
        scopes=user["scopes"]
    )


@router.post(
    "/token/refresh",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Refresh an access token using a valid refresh token.",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "rt_xyz789...",
                        "token_type": "bearer",
                        "expires_in": 3600,
                        "user_id": "user_demo_001",
                        "scopes": ["read", "write"]
                    }
                }
            }
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "Invalid refresh token",
                            "type": "authentication_error",
                            "code": "invalid_refresh_token"
                        }
                    }
                }
            }
        }
    }
)
async def refresh_token(request: TokenRefreshRequest) -> AuthResponse:
    """
    Refresh access token using refresh token.

    This endpoint allows clients to obtain a new access token without
    re-authenticating, using a valid refresh token.

    Optionally rotates the refresh token for enhanced security.

    Args:
        request: Refresh token request

    Returns:
        AuthResponse with new tokens

    Raises:
        HTTPException 401: If refresh token is invalid or expired
        HTTPException 500: If token generation fails
    """
    logger.info("Token refresh attempt")

    # 1. Verify refresh token
    user_id = verify_refresh_token(request.refresh_token)
    if not user_id:
        logger.warning("Token refresh failed: invalid or expired refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Invalid or expired refresh token",
                    "type": "authentication_error",
                    "code": "invalid_refresh_token"
                }
            }
        )

    # 2. Check not revoked (already checked in verify_refresh_token)

    # 3. Get user data
    user = None
    for username, user_data in USERS_DB.items():
        if user_data["user_id"] == user_id:
            user = user_data
            break

    if not user:
        logger.error(f"User not found for refresh token: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "User not found",
                    "type": "authentication_error",
                    "code": "user_not_found"
                }
            }
        )

    # 4. Generate new access token
    try:
        jwt_manager = get_jwt_manager()
        access_token = jwt_manager.create_access_token(
            user_id=user["user_id"],
            client_id="lukhas-web",
            scopes=user["scopes"],
            tier=str(user.get("tier", 0)),
            permissions=user.get("permissions", [])
        )
    except Exception as e:
        logger.error(f"JWT generation failed during refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": "Token generation failed",
                    "type": "internal_error",
                    "code": "token_generation_failed"
                }
            }
        )

    # 5. Optionally rotate refresh token (security best practice)
    # For now, we'll issue the same refresh token
    # TODO: Implement refresh token rotation
    new_refresh_token = request.refresh_token

    logger.info(f"Token refresh successful for user: {user_id}")

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=3600,  # 1 hour
        user_id=user["user_id"],
        scopes=user["scopes"]
    )


@router.get(
    "/profile",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Get the profile of the currently authenticated user.",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "user_demo_001",
                        "username": "demo_user",
                        "email": "demo@lukhas.ai",
                        "scopes": ["read", "write"],
                        "tier": 1,
                        "permissions": ["user"],
                        "created_at": "2025-11-15T00:00:00"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "Authentication required",
                            "type": "authentication_error",
                            "code": "unauthorized"
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "User profile not found",
                            "type": "not_found_error",
                            "code": "user_not_found"
                        }
                    }
                }
            }
        }
    }
)
async def get_profile(user_data: Dict[str, Any] = Depends(get_current_user)) -> UserProfile:
    """
    Get current user profile.

    This endpoint returns the profile of the authenticated user.
    Authentication is required via Bearer token in the Authorization header.

    Args:
        user_data: Current user data from JWT token (injected by dependency)

    Returns:
        UserProfile with user information

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 404: If user profile not found
    """
    user_id = user_data.get("user_id")
    logger.info(f"Profile request for user: {user_id}")

    # 1. Extract user from auth token (already done by dependency)

    # 2. Fetch profile from database
    user = None
    username = None
    for uname, user_profile in USERS_DB.items():
        if user_profile["user_id"] == user_id:
            user = user_profile
            username = uname
            break

    if not user:
        logger.warning(f"User profile not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "message": "User profile not found",
                    "type": "not_found_error",
                    "code": "user_not_found"
                }
            }
        )

    # 3. Return profile
    logger.info(f"Profile retrieved for user: {user_id}")

    return UserProfile(
        user_id=user["user_id"],
        username=username,
        email=user.get("email"),
        scopes=user.get("scopes", []),
        tier=user.get("tier", 0),
        permissions=user.get("permissions", []),
        created_at=user.get("created_at", datetime.utcnow().isoformat())
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout and revoke all tokens for the current user.",
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Logout successful",
                        "revoked_tokens": 2
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing token",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "message": "Authentication required",
                            "type": "authentication_error",
                            "code": "unauthorized"
                        }
                    }
                }
            }
        }
    }
)
async def logout(
    request: Request,
    user_data: Dict[str, Any] = Depends(get_current_user)
) -> LogoutResponse:
    """
    Logout and revoke tokens.

    This endpoint:
    1. Revokes all refresh tokens for the user
    2. Adds the current access token to revocation list
    3. Returns confirmation

    Note: Clients should discard all tokens after logout.

    Args:
        request: FastAPI request object
        user_data: Current user data from JWT token (injected by dependency)

    Returns:
        LogoutResponse with confirmation

    Raises:
        HTTPException 401: If not authenticated
    """
    user_id = user_data.get("user_id")
    logger.info(f"Logout request for user: {user_id}")

    revoked_count = 0

    # 1. Revoke all refresh tokens for this user
    tokens_to_revoke = []
    for token, token_data in REFRESH_TOKENS.items():
        if token_data["user_id"] == user_id:
            tokens_to_revoke.append(token)

    for token in tokens_to_revoke:
        revoke_token(token)
        REFRESH_TOKENS.pop(token, None)
        revoked_count += 1

    # 2. Add access token to revocation list
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        access_token = auth_header[7:]
        revoke_token(access_token)
        revoked_count += 1

    # 3. Return success
    logger.info(f"Logout successful for user: {user_id}, revoked {revoked_count} tokens")

    return LogoutResponse(
        message="Logout successful",
        revoked_tokens=revoked_count
    )


# ============================================================================
# Health Check
# ============================================================================

@router.get(
    "/health",
    summary="Health check",
    description="Check the health status of the identity API.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "jwt_available": True,
                        "qrg_available": True,
                        "bcrypt_available": True,
                        "users_count": 1,
                        "active_refresh_tokens": 0
                    }
                }
            }
        }
    }
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns system status and availability of dependencies.

    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "jwt_available": JWT_AVAILABLE,
        "qrg_available": QRG_AVAILABLE,
        "bcrypt_available": BCRYPT_AVAILABLE,
        "users_count": len(USERS_DB),
        "active_refresh_tokens": len(REFRESH_TOKENS),
        "revoked_tokens": len(REVOKED_TOKENS)
    }


# Export router
__all__ = ["router", "authenticate", "refresh_token", "get_profile", "logout", "health_check"]
