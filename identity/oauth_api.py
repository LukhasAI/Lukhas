"""
OAuth Federation API Endpoints
==============================
FastAPI endpoints for OAuth login flows and enterprise user management.
"""

from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field

from .oauth_federation import oauth_federation, OAuthProvider, EnterpriseConfig
from .identity_core import AccessTier

router = APIRouter(prefix="/identity/oauth", tags=["OAuth & Enterprise"])


# Request/Response Models
class OAuthLoginRequest(BaseModel):
    """Request model for initiating OAuth login."""
    provider: str = Field(..., description="OAuth provider (apple, google, github, etc.)")
    redirect_uri: str = Field(..., description="Callback URI after OAuth")
    mobile_app: bool = Field(False, description="Whether this is from mobile app")


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback."""
    provider: str
    code: str
    state: Optional[str] = None
    redirect_uri: str


class EnterpriseUserRequest(BaseModel):
    """Request for enterprise user operations."""
    organization_id: str
    user_email: EmailStr
    custom_user_id: Optional[str] = None
    tier: Optional[str] = "T2"


class AccountLinkRequest(BaseModel):
    """Request to link OAuth accounts."""
    primary_user_id: str
    secondary_provider: str
    secondary_code: str
    redirect_uri: str


class OAuthLoginResponse(BaseModel):
    """Response with OAuth login URL."""
    provider: str
    authorization_url: str
    state: str
    expires_in: int = 3600  # 1 hour


class LoginSuccessResponse(BaseModel):
    """Successful login response."""
    success: bool = True
    user_id: str
    display_name: str
    email: str
    token: str
    tier: str
    glyphs: list
    provider: str
    organization: Optional[str] = None
    is_new_user: bool
    federated: bool = True
    message: Optional[str] = None


# OAuth Login Flow Endpoints

@router.post("/login", response_model=OAuthLoginResponse)
async def initiate_oauth_login(request: OAuthLoginRequest):
    """
    Initiate OAuth login flow.
    
    Returns authorization URL that user should be redirected to.
    
    Supported providers:
    - apple: Apple Sign-In  
    - google: Google OAuth 2.0
    - github: GitHub OAuth
    - microsoft: Microsoft OAuth
    - linkedin: LinkedIn OAuth
    - discord: Discord OAuth
    
    Example:
    ```json
    {
        "provider": "google",
        "redirect_uri": "https://yourapp.com/oauth/callback",
        "mobile_app": false
    }
    ```
    """
    try:
        provider = OAuthProvider(request.provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {request.provider}"
        )
    
    try:
        # Generate state for CSRF protection
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Generate OAuth authorization URL
        auth_url = oauth_federation.generate_oauth_url(
            provider=provider,
            redirect_uri=request.redirect_uri,
            state=state
        )
        
        return OAuthLoginResponse(
            provider=request.provider.lower(),
            authorization_url=auth_url,
            state=state
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )


@router.get("/login/{provider}")
async def oauth_login_redirect(
    provider: str,
    redirect_uri: str = Query(..., description="Callback URI"),
    mobile: bool = Query(False, description="Mobile app flow")
):
    """
    Direct OAuth login redirect (GET endpoint for easy linking).
    
    Usage: 
    - Web: <a href="/identity/oauth/login/google?redirect_uri=...">Login with Google</a>
    - Mobile: Handle the redirect URL in your app
    """
    try:
        provider_enum = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    auth_url = oauth_federation.generate_oauth_url(
        provider=provider_enum,
        redirect_uri=redirect_uri
    )
    
    return RedirectResponse(url=auth_url)


@router.post("/callback", response_model=LoginSuccessResponse)
async def oauth_callback(request: OAuthCallbackRequest):
    """
    Handle OAuth callback after user authorization.
    
    This endpoint processes the authorization code and creates/links LUKHAS account.
    
    Flow:
    1. User authorizes on OAuth provider
    2. Provider redirects to your callback with code
    3. Your app calls this endpoint with the code
    4. Returns LUKHAS token and user info
    
    Example:
    ```json
    {
        "provider": "google",
        "code": "authorization_code_from_provider",
        "redirect_uri": "https://yourapp.com/oauth/callback"
    }
    ```
    """
    try:
        provider = OAuthProvider(request.provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {request.provider}"
        )
    
    # Handle OAuth callback
    result = await oauth_federation.handle_oauth_callback(
        provider=provider,
        code=request.code,
        redirect_uri=request.redirect_uri,
        state=request.state
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )
    
    return LoginSuccessResponse(**result)


@router.get("/callback/{provider}")
async def oauth_callback_get(
    provider: str,
    code: str = Query(...),
    state: Optional[str] = Query(None),
    request: Request = None
):
    """
    Handle OAuth callback via GET (for providers that use GET redirects).
    
    This is typically called automatically by the OAuth provider.
    Returns redirect to frontend with token or error.
    """
    try:
        provider_enum = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    # Get redirect URI from referrer or default
    redirect_uri = str(request.url_for("oauth_callback_get", provider=provider))
    
    result = await oauth_federation.handle_oauth_callback(
        provider=provider_enum,
        code=code,
        redirect_uri=redirect_uri,
        state=state
    )
    
    if result["success"]:
        # In production, redirect to your frontend with token
        frontend_url = f"https://yourapp.com/auth/success?token={result['token']}&user_id={result['user_id']}"
        return RedirectResponse(url=frontend_url)
    else:
        # Redirect to error page
        error_url = f"https://yourapp.com/auth/error?error={result['error']}"
        return RedirectResponse(url=error_url)


# Enterprise/Institutional Management

@router.get("/organizations")
async def get_organizations():
    """
    Get list of supported organizations for enterprise/institutional login.
    
    Returns all configured enterprise domains and their settings.
    """
    orgs = oauth_federation.get_organization_configs()
    
    return {
        "organizations": [
            {
                "id": org_id,
                "display_name": config.display_name,
                "domain_pattern": config.domain_pattern,
                "user_id_format": config.user_id_format,
                "default_tier": config.default_tier.value,
                "auto_verify": config.auto_verify,
                "sso_required": config.sso_required
            }
            for org_id, config in orgs.items()
        ],
        "total": len(orgs)
    }


@router.post("/organizations/{org_id}/users")
async def create_enterprise_user(org_id: str, request: EnterpriseUserRequest):
    """
    Create enterprise user with organization prefix.
    
    This is typically called by enterprise admin or automated provisioning.
    Creates user with format: org_id-username
    
    Example:
    ```json
    {
        "organization_id": "acme",
        "user_email": "john.doe@acme.com", 
        "custom_user_id": "johndoe",
        "tier": "T3"
    }
    ```
    
    Result: User ID "acme-johndoe" with tier T3
    """
    if org_id != request.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL organization ID must match request organization ID"
        )
    
    # Get organization config
    org_configs = oauth_federation.get_organization_configs()
    if org_id not in org_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found"
        )
    
    org_config = org_configs[org_id]
    
    # Validate email domain
    email_domain = request.user_email.split("@")[1].lower()
    org_domain = org_config.domain_pattern.replace("*.", "")
    
    if not email_domain.endswith(org_domain):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email domain {email_domain} does not match organization domain {org_domain}"
        )
    
    # Generate user ID
    if request.custom_user_id:
        username = request.custom_user_id
    else:
        username = str(request.user_email).split("@")[0].replace(".", "_").lower()
    
    user_id = org_config.user_id_format.format(
        org_id=org_id,
        username=username
    )
    
    # Create user
    tier = AccessTier(request.tier) if request.tier else org_config.default_tier
    
    metadata = {
        "email": str(request.user_email),
        "organization_id": org_id,
        "enterprise_user": True,
        "auto_verified": org_config.auto_verify,
        "created_via": "enterprise_api"
    }
    
    token = oauth_federation.identity_core.create_token(user_id, tier, metadata)
    glyphs = oauth_federation.identity_core.generate_identity_glyph(user_id)
    
    return {
        "success": True,
        "user_id": user_id,
        "email": str(request.user_email),
        "organization": org_id,
        "tier": tier.value,
        "token": token,
        "glyphs": glyphs,
        "auto_verified": org_config.auto_verify,
        "message": f"Enterprise user created for {org_config.display_name}"
    }


# Account Linking

@router.post("/link-account")
async def link_oauth_account(request: AccountLinkRequest):
    """
    Link additional OAuth provider to existing LUKHAS account.
    
    Allows users to sign in with multiple providers (Google + Apple, etc.)
    
    Example: User has Google account, wants to add Apple Sign-In
    ```json
    {
        "primary_user_id": "john_doe",
        "secondary_provider": "apple", 
        "secondary_code": "apple_auth_code",
        "redirect_uri": "https://yourapp.com/oauth/callback"
    }
    ```
    """
    try:
        secondary_provider = OAuthProvider(request.secondary_provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {request.secondary_provider}"
        )
    
    # Validate primary user exists
    primary_user = oauth_federation.get_user_info(request.primary_user_id)
    if not primary_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Primary user not found"
        )
    
    # Process secondary OAuth
    secondary_result = await oauth_federation.handle_oauth_callback(
        provider=secondary_provider,
        code=request.secondary_code,
        redirect_uri=request.redirect_uri
    )
    
    if not secondary_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Secondary OAuth failed: {secondary_result['error']}"
        )
    
    # Link accounts
    link_success = oauth_federation.link_accounts(
        primary_user_id=request.primary_user_id,
        secondary_provider=secondary_provider,
        secondary_user_id=secondary_result["user_id"]
    )
    
    if not link_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link accounts"
        )
    
    return {
        "success": True,
        "primary_user_id": request.primary_user_id,
        "linked_provider": request.secondary_provider,
        "message": f"Successfully linked {request.secondary_provider} account"
    }


# User Info and Management

@router.get("/user/{user_id}")
async def get_federated_user_info(user_id: str):
    """Get federated user information and linked accounts."""
    
    user = oauth_federation.get_user_info(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user.lukhas_user_id,
        "email": user.email,
        "display_name": user.display_name,
        "provider": user.provider.value,
        "organization": user.organization_id,
        "is_temporary": user.is_temporary,
        "verified": user.verified,
        "linked_accounts": user.linked_accounts,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }


# Admin/Debug Endpoints

@router.get("/providers")
async def get_oauth_providers():
    """Get list of configured OAuth providers."""
    
    providers = []
    for provider, config in oauth_federation.providers.items():
        providers.append({
            "provider": provider.value,
            "enabled": config.enabled,
            "scopes": config.scopes,
            "authorization_url": config.authorization_url
        })
    
    return {
        "providers": providers,
        "total": len(providers)
    }


@router.post("/cleanup-temp-users")
async def cleanup_temporary_users():
    """Admin endpoint to clean up expired temporary users."""
    
    oauth_federation.cleanup_temporary_users()
    
    return {
        "success": True,
        "message": "Temporary users cleaned up"
    }


# Health Check

@router.get("/health")
async def oauth_health_check():
    """Health check for OAuth federation system."""
    
    return {
        "status": "healthy",
        "providers_configured": len(oauth_federation.providers),
        "organizations_configured": len(oauth_federation.enterprises),
        "federated_users": len(oauth_federation.federated_users),
        "temporary_users": len(oauth_federation.temp_users)
    }