"""
LUKHΛS Registration System
==========================

User registration with symbolic consent tracking and tier assignment.
Implements GDPR-compliant registration flow with Trinity Framework integration.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import logging
import re
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator

from .user_db import user_db

logger = logging.getLogger(__name__)

# Create router for registration endpoints
router = APIRouter(prefix="/identity", tags=["identity", "registration"])

class RegistrationRequest(BaseModel):
    """Registration request with symbolic metadata."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    tier: Optional[str] = Field("T1", pattern="^T[1-5]$", description="Requested tier (T1-T5)")
    cultural_profile: Optional[str] = Field("universal", description="Cultural background")
    personality_type: Optional[str] = Field("balanced", description="Personality profile")
    consent: bool = Field(..., description="GDPR consent acknowledgment")

    @validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain letters")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain numbers")
        return v

    @validator('tier')
    def validate_tier_request(cls, v):
        """Validate tier request - new users typically start at T1."""
        if v not in ["T1", "T2", "T3", "T4", "T5"]:
            raise ValueError("Invalid tier. Must be T1-T5")
        # New users typically start at T1 unless special authorization
        if v not in ["T1", "T2"]:
            logger.warning(f"High tier {v} requested at registration")
        return v

class RegistrationResponse(BaseModel):
    """Registration response with symbolic identity."""
    success: bool
    message: str
    user_id: str
    lambda_id: str
    tier: str
    glyphs: List[str]
    token: str
    consent_logged: bool
    trinity_score: float

@router.post("/register", response_model=RegistrationResponse)
async def register_user(request: RegistrationRequest):
    """
    Register a new LUKHΛS user with symbolic identity.
    
    This endpoint:
    1. Validates registration data
    2. Creates user with tier assignment
    3. Generates Lambda ID and symbolic glyphs
    4. Logs GDPR consent with Trinity tracking
    5. Returns initial session token
    
    Trinity Integration:
    - ⚛️ Identity: Lambda ID generation
    - 🧠 Consciousness: Personality profiling
    - 🛡️ Guardian: Consent and tier validation
    """
    try:
        # Validate consent
        if not request.consent:
            raise HTTPException(
                status_code=400,
                detail="GDPR consent is required for registration"
            )

        # Check if user already exists
        existing_user = user_db.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists"
            )

        # Create user with symbolic initialization
        user_data = user_db.create_user(
            email=request.email,
            password=request.password,
            tier=request.tier,
            cultural_profile=request.cultural_profile,
            personality_type=request.personality_type
        )

        # Extract user ID
        user_id = request.email.split('@')[0].replace('.', '_').lower()

        # Log registration event
        logger.info(f"New user registered: {user_id} with tier {request.tier}")

        return RegistrationResponse(
            success=True,
            message=f"Welcome to LUKHΛS! Your identity has been created with {request.tier} access.",
            user_id=user_id,
            lambda_id=user_data["lambda_id"],
            tier=user_data["tier"],
            glyphs=user_data["glyphs"],
            token=user_data["token"],
            consent_logged=True,
            trinity_score=user_data["metadata"]["trinity_score"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/register/check-email/{email}")
async def check_email_availability(email: EmailStr):
    """
    Check if email is available for registration.
    
    Returns:
        - available: bool
        - message: str
    """
    try:
        existing_user = user_db.get_user_by_email(email)

        if existing_user:
            return {
                "available": False,
                "message": "Email already registered"
            }

        return {
            "available": True,
            "message": "Email available for registration"
        }

    except Exception as e:
        logger.error(f"Email check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error checking email availability"
        )

@router.get("/register/tiers")
async def get_available_tiers():
    """
    Get information about available tiers and their symbolic meanings.
    
    Returns tier information with associated glyphs and capabilities.
    """
    return {
        "tiers": {
            "T1": {
                "name": "Observer",
                "glyphs": ["⚛️"],
                "description": "Basic identity access",
                "capabilities": ["View public content", "Basic profile"],
                "trinity_score": 0.3
            },
            "T2": {
                "name": "Participant",
                "glyphs": ["⚛️", "🔐"],
                "description": "Secure participant access",
                "capabilities": ["Create content", "Join discussions", "Basic API access"],
                "trinity_score": 0.5
            },
            "T3": {
                "name": "Contributor",
                "glyphs": ["⚛️", "🔐", "🧠"],
                "description": "Consciousness-aware contributor",
                "capabilities": ["Advanced features", "Dream access", "Emotion tracking"],
                "trinity_score": 0.7
            },
            "T4": {
                "name": "Architect",
                "glyphs": ["⚛️", "🔐", "🧠", "🌍"],
                "description": "Cultural architect with global awareness",
                "capabilities": ["System design", "Cultural adaptation", "Advanced API"],
                "trinity_score": 0.9
            },
            "T5": {
                "name": "Guardian",
                "glyphs": ["🛡️", "⚛️", "🧠"],
                "description": "Full Trinity Framework access",
                "capabilities": ["All features", "Admin tools", "Guardian oversight"],
                "trinity_score": 1.0
            }
        },
        "default_tier": "T1",
        "upgrade_path": "Tiers can be upgraded through contribution and Guardian approval"
    }
