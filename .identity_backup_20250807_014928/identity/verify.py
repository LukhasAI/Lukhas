"""
LUKHΛS Token Verification System
================================

Token validation and user verification for secure access control.
Implements stateless verification with Trinity Framework validation.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .user_db import user_db

logger = logging.getLogger(__name__)

# Create router for verification endpoints
router = APIRouter(prefix="/identity", tags=["identity", "verification"])

# Security scheme
security = HTTPBearer()


class VerifyResponse(BaseModel):
    """Token verification response."""

    valid: bool
    user_id: str
    email: str
    tier: str
    lambda_id: str
    glyphs: List[str]
    trinity_score: float
    permissions: Dict[str, bool]
    expires_at: Optional[str] = None


class TierPermissions(BaseModel):
    """Tier-based permissions."""

    can_view_public: bool = True
    can_create_content: bool = False
    can_access_api: bool = False
    can_use_consciousness: bool = False
    can_use_emotion: bool = False
    can_use_dream: bool = False
    can_use_quantum: bool = False
    can_access_guardian: bool = False
    can_admin: bool = False


def get_tier_permissions(tier: str) -> Dict[str, bool]:
    """
    Get permissions based on tier level.

    Implements hierarchical permission model aligned with Trinity Framework.
    """
    permissions = {
        "T1": {
            "can_view_public": True,
            "can_create_content": False,
            "can_access_api": False,
            "can_use_consciousness": False,
            "can_use_emotion": False,
            "can_use_dream": False,
            "can_use_quantum": False,
            "can_access_guardian": False,
            "can_admin": False,
        },
        "T2": {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": False,
            "can_use_emotion": False,
            "can_use_dream": False,
            "can_use_quantum": False,
            "can_access_guardian": False,
            "can_admin": False,
        },
        "T3": {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": True,
            "can_use_emotion": True,
            "can_use_dream": True,
            "can_use_quantum": False,
            "can_access_guardian": False,
            "can_admin": False,
        },
        "T4": {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": True,
            "can_use_emotion": True,
            "can_use_dream": True,
            "can_use_quantum": True,
            "can_access_guardian": False,
            "can_admin": False,
        },
        "T5": {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": True,
            "can_use_emotion": True,
            "can_use_dream": True,
            "can_use_quantum": True,
            "can_access_guardian": True,
            "can_admin": True,
        },
    }

    return permissions.get(tier, permissions["T1"])


@router.post("/verify", response_model=VerifyResponse)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify authentication token and return user permissions.

    This endpoint:
    1. Validates the provided bearer token
    2. Returns user information and tier
    3. Provides permission matrix based on tier
    4. Tracks verification for audit trail

    Used by middleware and services to validate access.
    """
    try:
        token = credentials.credentials

        # Verify token
        user_data = user_db.verify_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Extract user ID
        user_id = user_data["email"].split("@")[0].replace(".", "_").lower()

        # Get tier permissions
        permissions = get_tier_permissions(user_data["tier"])

        # Log verification
        logger.debug(f"Token verified for user {user_id} with tier {user_data['tier']}")

        return VerifyResponse(
            valid=True,
            user_id=user_id,
            email=user_data["email"],
            tier=user_data["tier"],
            lambda_id=user_data["lambda_id"],
            glyphs=user_data["glyphs"],
            trinity_score=user_data["metadata"]["trinity_score"],
            permissions=permissions,
            expires_at=None,  # Tokens don't expire in this implementation
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/verify/quick")
async def quick_verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Quick token verification for performance-critical checks.

    Returns minimal information for fast validation.
    """
    try:
        token = credentials.credentials

        # Verify token
        user_data = user_db.verify_token(token)
        if not user_data:
            return {"valid": False}

        return {
            "valid": True,
            "tier": user_data["tier"],
            "trinity_active": user_data["metadata"]["trinity_score"] >= 0.7,
        }

    except Exception as e:
        logger.error(f"Quick verify error: {str(e)}")
        return {"valid": False}


@router.get("/verify/permissions/{resource}")
async def verify_resource_access(
    resource: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify if user has access to a specific resource.

    Resources:
    - consciousness: Consciousness module access
    - emotion: Emotion processing access
    - dream: Dream engine access
    - quantum: Quantum processing access
    - guardian: Guardian system access
    - admin: Administrative functions

    Returns:
        - allowed: bool
        - reason: str
    """
    try:
        token = credentials.credentials

        # Verify token
        user_data = user_db.verify_token(token)
        if not user_data:
            return {"allowed": False, "reason": "Invalid token"}

        # Get permissions
        permissions = get_tier_permissions(user_data["tier"])

        # Map resource to permission
        resource_map = {
            "consciousness": "can_use_consciousness",
            "emotion": "can_use_emotion",
            "dream": "can_use_dream",
            "quantum": "can_use_quantum",
            "guardian": "can_access_guardian",
            "admin": "can_admin",
            "api": "can_access_api",
            "content": "can_create_content",
        }

        permission_key = resource_map.get(resource.lower())
        if not permission_key:
            return {"allowed": False, "reason": f"Unknown resource: {resource}"}

        allowed = permissions.get(permission_key, False)

        if allowed:
            return {
                "allowed": True,
                "reason": f"Access granted with {user_data['tier']} tier",
            }
        else:
            return {
                "allowed": False,
                "reason": f"Resource '{resource}' requires higher tier than {user_data['tier']}",
            }

    except Exception as e:
        logger.error(f"Resource verification error: {str(e)}")
        return {"allowed": False, "reason": f"Verification error: {str(e)}"}
