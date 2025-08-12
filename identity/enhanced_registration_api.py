"""
Enhanced Registration API Endpoints
===================================
API endpoints for custom user ID registration and username management.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from .enhanced_registration import enhanced_registration

router = APIRouter(prefix="/identity/register", tags=["Enhanced Registration"])


# Request/Response Models
class CustomRegistrationRequest(BaseModel):
    """Request model for custom user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    custom_user_id: Optional[str] = Field(None, description="Preferred user ID (optional)")
    display_name: Optional[str] = Field(None, description="Display name for UI (optional)")
    requested_tier: Optional[str] = Field("T2", description="Requested tier (T1-T5)")


class UsernameCheckRequest(BaseModel):
    """Request model for username availability check."""
    user_id: str = Field(..., min_length=3, max_length=30, description="Desired user ID")


class SuggestionRequest(BaseModel):
    """Request model for username suggestions."""
    email: EmailStr = Field(..., description="Email to generate suggestions from")


class RegistrationResponse(BaseModel):
    """Response model for user registration."""
    success: bool
    message: str
    user_id: Optional[str] = None
    display_name: Optional[str] = None
    token: Optional[str] = None
    tier: Optional[str] = None
    glyphs: Optional[list] = None
    custom_id_used: Optional[bool] = None
    error: Optional[str] = None
    suggestions: Optional[list] = None
    fallback_user_id: Optional[str] = None


class AvailabilityResponse(BaseModel):
    """Response model for username availability."""
    user_id: str
    available: bool
    message: str
    suggestions: Optional[list] = None


class SuggestionResponse(BaseModel):
    """Response model for username suggestions."""
    email: str
    suggestions: list
    default: Optional[str] = None
    message: str


# API Endpoints

@router.post("/enhanced", response_model=RegistrationResponse)
async def register_with_custom_id(request: CustomRegistrationRequest):
    """
    Register a new user with optional custom user ID.
    
    Features:
    - Choose your own user ID (username)
    - Fallback to email-derived ID if custom ID unavailable
    - Username validation and suggestions
    - Display name support
    - Tier selection
    
    Example:
    ```json
    {
        "email": "john.doe@example.com",
        "password": "SecurePass123!",
        "custom_user_id": "johndoe",
        "display_name": "John Doe",
        "requested_tier": "T2"
    }
    ```
    """
    try:
        result = enhanced_registration.register_user_enhanced(
            email=str(request.email),
            password=request.password,
            requested_tier=request.requested_tier,
            custom_user_id=request.custom_user_id,
            display_name=request.display_name
        )

        return RegistrationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/check-username", response_model=AvailabilityResponse)
async def check_username_availability(request: UsernameCheckRequest):
    """
    Check if a username (user ID) is available.
    
    Returns availability status and suggestions if unavailable.
    
    Example:
    ```json
    {
        "user_id": "johndoe"
    }
    ```
    
    Response:
    ```json
    {
        "user_id": "johndoe",
        "available": false,
        "message": "User ID 'johndoe' is already taken",
        "suggestions": ["johndoe1", "johndoe2024", "johndoe_42"]
    }
    ```
    """
    try:
        result = enhanced_registration.check_user_id_availability(request.user_id)
        return AvailabilityResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Username check failed: {str(e)}"
        )


@router.post("/suggest-usernames", response_model=SuggestionResponse)
async def get_username_suggestions(request: SuggestionRequest):
    """
    Get username suggestions based on email address.
    
    Generates multiple username options from the email address.
    
    Example:
    ```json
    {
        "email": "john.doe@example.com"
    }
    ```
    
    Response:
    ```json
    {
        "email": "john.doe@example.com",
        "suggestions": ["john_doe", "johndoe", "john", "john_doe1", "john_doe2024"],
        "default": "john_doe",
        "message": "Generated 5 suggestions from email"
    }
    ```
    """
    try:
        result = enhanced_registration.get_user_id_suggestions(str(request.email))
        return SuggestionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Suggestion generation failed: {str(e)}"
        )


@router.get("/username-rules")
async def get_username_rules():
    """
    Get the rules and requirements for choosing a username.
    
    Returns validation rules, reserved words, and formatting requirements.
    """
    return {
        "rules": {
            "length": {
                "minimum": 3,
                "maximum": 30,
                "description": "Username must be 3-30 characters long"
            },
            "characters": {
                "allowed": "letters, numbers, underscore (_), hyphen (-)",
                "forbidden": "spaces, special characters (except _ and -)",
                "must_start_with": "letter",
                "description": "Must start with a letter, contain only alphanumeric, underscore, or hyphen"
            },
            "case": {
                "rule": "case insensitive",
                "description": "Usernames are converted to lowercase"
            }
        },
        "reserved_usernames": [
            "admin", "root", "system", "api", "www", "mail", "ftp",
            "test", "guest", "anonymous", "user", "support", "help",
            "lukhas", "lambda", "trinity", "guardian", "consciousness",
            "quantum", "dream", "emotion", "governance"
        ],
        "tips": [
            "Keep it memorable and easy to type",
            "Avoid numbers at the end if possible",
            "Consider using underscore to separate words",
            "Your display name can be different and more formal",
            "Username cannot be changed after registration"
        ],
        "examples": {
            "good": ["johndoe", "alice_smith", "dev-guru", "quantum_alice"],
            "bad": ["john..doe", "123user", "admin", "a", "this-is-way-too-long-for-a-username"]
        }
    }


@router.get("/demo-usernames")
async def get_demo_usernames():
    """
    Get sample usernames for demonstration and testing.
    
    Useful for UI examples and testing flows.
    """
    return {
        "available_examples": [
            "demo_user", "test_explorer", "luke_reviewer", "ai_enthusiast",
            "quantum_dev", "consciousness_fan", "guardian_tester"
        ],
        "taken_examples": [
            "admin", "root", "john", "alice", "test123", "demo_user"
        ],
        "tier_examples": {
            "T1": ["observer_1", "viewer_demo"],
            "T2": ["creator_joe", "builder_alice"],
            "T3": ["advanced_user", "consciousness_dev"],
            "T4": ["quantum_alice", "architect_bob"],
            "T5": ["guardian_admin", "trinity_master"]
        },
        "note": "These are examples only. Actual availability may vary."
    }


# Backward compatibility endpoint
@router.post("/legacy", response_model=RegistrationResponse)
async def register_legacy_mode(
    email: EmailStr,
    password: str,
    requested_tier: Optional[str] = "T2"
):
    """
    Legacy registration mode (email-derived user ID only).
    
    Maintains backward compatibility with existing registration flow.
    User ID will be automatically generated from email address.
    """
    try:
        result = enhanced_registration.register_user_enhanced(
            email=str(email),
            password=password,
            requested_tier=requested_tier,
            custom_user_id=None  # Force email-derived ID
        )

        return RegistrationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Legacy registration failed: {str(e)}"
        )
