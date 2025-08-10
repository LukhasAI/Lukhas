"""
LUKHΛS Login System
===================

Secure login with token generation and symbolic tracking.
Implements multi-factor authentication readiness with Trinity validation.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from .user_db import user_db

logger = logging.getLogger(__name__)

# Create router for login endpoints
router = APIRouter(prefix="/identity", tags=["identity", "authentication"])

# Security scheme for token authentication
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request with flexible authentication."""

    email: Optional[EmailStr] = Field(None, description="Email address")
    token: Optional[str] = Field(None, description="Existing session token")
    password: Optional[str] = Field(None, description="User password")

    class Config:
        schema_extra = {
            "example": {"email": "reviewer@openai.com", "password": "demo_password"}
        }


class LoginResponse(BaseModel):
    """Login response with symbolic metadata."""

    success: bool
    message: str
    token: str
    tier: str
    lambda_id: str
    glyphs: List[str]
    allowed_routes: List[str]
    metadata: Dict[str, Any]
    trinity_active: bool


class UserProfile(BaseModel):
    """User profile response."""

    email: str
    lambda_id: str
    tier: str
    glyphs: List[str]
    trinity_score: float
    drift_score: float
    cultural_profile: str
    personality_type: str
    created_at: str
    last_login: Optional[str]
    login_count: int


def get_allowed_routes(tier: str) -> List[str]:
    """
    Get allowed routes based on user tier.

    Implements tier-based access control for LUKHΛS systems.
    """
    base_routes = [
        "/identity/profile",
        "/identity/logout",
        "/api/health",
        "/api/status",
    ]

    tier_routes = {
        "T1": base_routes + ["/api/public/*", "/dashboard/view"],
        "T2": base_routes
        + ["/api/public/*", "/dashboard/*", "/api/content/create", "/api/basic/*"],
        "T3": base_routes
        + ["/api/*", "/dashboard/*", "/consciousness/*", "/emotion/*", "/dream/view"],
        "T4": base_routes
        + [
            "/api/*",
            "/dashboard/*",
            "/consciousness/*",
            "/emotion/*",
            "/dream/*",
            "/quantum/*",
            "/orchestration/*",
        ],
        "T5": base_routes + ["/*"],  # Full access
    }

    return tier_routes.get(tier, base_routes)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and generate session token.

    Supports multiple authentication methods:
    1. Email + Password (standard)
    2. Token (session continuation)
    3. Future: Biometric, MFA, Quantum keys

    Trinity Integration:
    - ⚛️ Identity: Token generation and validation
    - 🧠 Consciousness: User state tracking
    - 🛡️ Guardian: Security validation
    """
    try:
        user_data = None

        # Method 1: Token-based authentication
        if request.token:
            user_data = user_db.verify_token(request.token)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            # Token is valid, return existing session
            return LoginResponse(
                success=True,
                message="Session continued with existing token",
                token=request.token,
                tier=user_data["tier"],
                lambda_id=user_data["lambda_id"],
                glyphs=user_data["glyphs"],
                allowed_routes=get_allowed_routes(user_data["tier"]),
                metadata={
                    "cultural_profile": user_data["metadata"]["cultural_profile"],
                    "personality_type": user_data["metadata"]["personality_type"],
                    "trinity_score": user_data["metadata"]["trinity_score"],
                    "drift_score": user_data["metadata"]["drift_score"],
                },
                trinity_active=user_data["metadata"]["trinity_score"] >= 0.7,
            )

        # Method 2: Email + Password authentication
        if request.email and request.password:
            user_data = user_db.authenticate_user(request.email, request.password)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Successful authentication
            logger.info(f"User {request.email} logged in with tier {user_data['tier']}")

            return LoginResponse(
                success=True,
                message=f"Welcome back! Logged in with {user_data['tier']} access",
                token=user_data["token"],
                tier=user_data["tier"],
                lambda_id=user_data["lambda_id"],
                glyphs=user_data["glyphs"],
                allowed_routes=get_allowed_routes(user_data["tier"]),
                metadata={
                    "cultural_profile": user_data["metadata"]["cultural_profile"],
                    "personality_type": user_data["metadata"]["personality_type"],
                    "trinity_score": user_data["metadata"]["trinity_score"],
                    "drift_score": user_data["metadata"]["drift_score"],
                    "login_count": user_data["metadata"]["login_count"],
                },
                trinity_active=user_data["metadata"]["trinity_score"] >= 0.7,
            )

        # No valid authentication method provided
        raise HTTPException(
            status_code=400, detail="Please provide either email+password or token"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate session token.

    Removes token from active sessions and logs the action.
    """
    try:
        token = credentials.credentials

        # Verify token exists
        user_data = user_db.verify_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Invalidate token
        success = user_db.invalidate_token(token)

        if success:
            logger.info(f"User {user_data['email']} logged out")
            return {
                "success": True,
                "message": "Logged out successfully",
                "glyphs": ["🔒", "👋"],  # Locked + Goodbye
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to invalidate token")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")


@router.get("/profile", response_model=UserProfile)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user's profile.

    Returns user information based on authenticated token.
    """
    try:
        token = credentials.credentials

        # Verify token and get user
        user_data = user_db.verify_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return UserProfile(
            email=user_data["email"],
            lambda_id=user_data["lambda_id"],
            tier=user_data["tier"],
            glyphs=user_data["glyphs"],
            trinity_score=user_data["metadata"]["trinity_score"],
            drift_score=user_data["metadata"]["drift_score"],
            cultural_profile=user_data["metadata"]["cultural_profile"],
            personality_type=user_data["metadata"]["personality_type"],
            created_at=user_data["created_at"],
            last_login=user_data["metadata"].get("last_login"),
            login_count=user_data["metadata"].get("login_count", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch profile: {str(e)}"
        )
