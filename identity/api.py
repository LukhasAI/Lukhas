"""
LUKHΛS Identity API
===================

Main API module that combines all identity endpoints.
Provides unified authentication and identity management.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

from fastapi import APIRouter
import logging

# Import all identity routers
from .registration import router as registration_router
from .login import router as login_router
from .verify import router as verify_router

logger = logging.getLogger(__name__)

# Create main identity router
identity_router = APIRouter(tags=["identity"])

# Include all sub-routers
# Note: They already have /identity prefix, so we include them without additional prefix
identity_router.include_router(registration_router)
identity_router.include_router(login_router)
identity_router.include_router(verify_router)

# Add root identity endpoint
@identity_router.get("/identity")
async def identity_info():
    """
    Get information about the LUKHΛS Identity System.
    
    Returns system information and available endpoints.
    """
    return {
        "system": "LUKHΛS Identity System (ΛiD)",
        "version": "1.0.0",
        "trinity_framework": {
            "⚛️": "Identity - Core authentication and tier management",
            "🧠": "Consciousness - User awareness and tracking",
            "🛡️": "Guardian - Security and consent protection"
        },
        "endpoints": {
            "registration": {
                "POST /identity/register": "Register new user",
                "GET /identity/register/check-email/{email}": "Check email availability",
                "GET /identity/register/tiers": "Get tier information"
            },
            "authentication": {
                "POST /identity/login": "Login with email/password or token",
                "POST /identity/logout": "Logout and invalidate token",
                "GET /identity/profile": "Get current user profile"
            },
            "verification": {
                "POST /identity/verify": "Verify token and get permissions",
                "GET /identity/verify/quick": "Quick token validation",
                "GET /identity/verify/permissions/{resource}": "Check resource access"
            }
        },
        "tiers": {
            "T1": "Observer - Basic access",
            "T2": "Participant - Content creation",
            "T3": "Contributor - Advanced features",
            "T4": "Architect - System design",
            "T5": "Guardian - Full Trinity access"
        },
        "demo_account": {
            "email": "reviewer@openai.com",
            "password": "demo_password",
            "tier": "T5",
            "note": "Pre-configured for OpenAI review"
        }
    }

# Export main router
__all__ = ["identity_router"]