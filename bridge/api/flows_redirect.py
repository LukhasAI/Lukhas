"""
Authentication Flow Redirector
==============================

Redirects legacy authentication endpoints to the new LUKHΛS Identity System.
Maintains backward compatibility while using the new ΛiD implementation.
"""

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import logging

logger = logging.getLogger(__name__)

# Create router for legacy auth endpoints
legacy_auth_router = APIRouter(prefix="/api/v2/auth", tags=["legacy-auth"])

@legacy_auth_router.post("/register")
async def legacy_register(request: Request):
    """
    Legacy registration endpoint - redirects to new identity system.
    
    This endpoint is maintained for backward compatibility.
    New integrations should use /identity/register directly.
    """
    logger.info("Legacy /api/v2/auth/register called - redirecting to /identity/register")
    
    # Get request body
    try:
        body = await request.json()
    except:
        body = {}
    
    # Return redirect information
    return JSONResponse(
        status_code=301,
        content={
            "message": "This endpoint has moved. Please use /identity/register",
            "new_endpoint": "/identity/register",
            "method": "POST",
            "deprecated": True,
            "migration_guide": "https://docs.lukhas.ai/identity/migration"
        },
        headers={
            "Location": "/identity/register",
            "X-Deprecated": "true",
            "X-New-Endpoint": "/identity/register"
        }
    )

@legacy_auth_router.post("/login")
async def legacy_login(request: Request):
    """
    Legacy login endpoint - redirects to new identity system.
    
    This endpoint is maintained for backward compatibility.
    New integrations should use /identity/login directly.
    """
    logger.info("Legacy /api/v2/auth/login called - redirecting to /identity/login")
    
    return JSONResponse(
        status_code=301,
        content={
            "message": "This endpoint has moved. Please use /identity/login",
            "new_endpoint": "/identity/login",
            "method": "POST",
            "deprecated": True,
            "migration_guide": "https://docs.lukhas.ai/identity/migration"
        },
        headers={
            "Location": "/identity/login",
            "X-Deprecated": "true",
            "X-New-Endpoint": "/identity/login"
        }
    )

@legacy_auth_router.post("/logout")
async def legacy_logout(request: Request):
    """
    Legacy logout endpoint - redirects to new identity system.
    """
    logger.info("Legacy /api/v2/auth/logout called - redirecting to /identity/logout")
    
    return JSONResponse(
        status_code=301,
        content={
            "message": "This endpoint has moved. Please use /identity/logout",
            "new_endpoint": "/identity/logout",
            "method": "POST",
            "deprecated": True
        },
        headers={
            "Location": "/identity/logout",
            "X-Deprecated": "true",
            "X-New-Endpoint": "/identity/logout"
        }
    )

@legacy_auth_router.post("/token/verify")
async def legacy_verify(request: Request):
    """
    Legacy token verification endpoint - redirects to new identity system.
    """
    logger.info("Legacy /api/v2/auth/token/verify called - redirecting to /identity/verify")
    
    return JSONResponse(
        status_code=301,
        content={
            "message": "This endpoint has moved. Please use /identity/verify",
            "new_endpoint": "/identity/verify",
            "method": "POST",
            "deprecated": True
        },
        headers={
            "Location": "/identity/verify",
            "X-Deprecated": "true",
            "X-New-Endpoint": "/identity/verify"
        }
    )

@legacy_auth_router.get("/")
async def legacy_auth_info():
    """
    Information about the legacy auth endpoints.
    """
    return {
        "status": "deprecated",
        "message": "These endpoints have been moved to the LUKHΛS Identity System",
        "migration": {
            "/api/v2/auth/register": "/identity/register",
            "/api/v2/auth/login": "/identity/login",
            "/api/v2/auth/logout": "/identity/logout",
            "/api/v2/auth/token/verify": "/identity/verify"
        },
        "documentation": "https://docs.lukhas.ai/identity",
        "identity_system": "/identity"
    }