#!/usr/bin/env python3
"""
LUKHAS OIDC API Endpoints - FastAPI Implementation

OpenID Connect 1.0 and OAuth2 API endpoints.
Implements discovery, authorization, token, and userinfo endpoints.

T4/0.01% Excellence: Production-ready API with comprehensive validation and monitoring.
"""

from __future__ import annotations
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Form, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from opentelemetry import trace
from prometheus_client import Counter

from ..identity.oidc.provider import get_oidc_provider, OIDCProvider
from ..identity.tiers import get_tiered_auth_system

tracer = trace.get_tracer(__name__)
security = HTTPBearer(auto_error=False)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs): return self
    def inc(self, amount=1): pass

try:
    oidc_api_requests_total = Counter(
        'lukhas_oidc_api_requests_total',
        'Total OIDC API requests',
        ['endpoint', 'method', 'status']
    )
except ValueError:
    oidc_api_requests_total = MockMetric()

# Create router
router = APIRouter(prefix="/oauth2", tags=["OIDC", "OAuth2"])

# Helper function to get current user from session/token
async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current authenticated user from session or token."""
    # In production, this would integrate with session management
    # For now, we'll simulate authentication status
    user_id = request.session.get("user_id") if hasattr(request, "session") else None
    auth_tier = request.session.get("auth_tier") if hasattr(request, "session") else None

    if user_id:
        return {
            "user_id": user_id,
            "authenticated": True,
            "auth_tier": auth_tier
        }
    return {"authenticated": False}


@router.get("/.well-known/openid-configuration")
async def openid_configuration(
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    OpenID Connect Discovery 1.0 endpoint.

    Returns the OpenID Provider Configuration Information.
    """
    with tracer.start_span("api.oidc.discovery") as span:
        try:
            config = provider.get_discovery_document()

            oidc_api_requests_total.labels(
                endpoint="discovery",
                method="GET",
                status="200"
            ).inc()

            span.set_attribute("oidc.issuer", config.get("issuer"))
            return config

        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="discovery",
                method="GET",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/.well-known/jwks.json")
async def jwks_json(
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    JSON Web Key Set (JWKS) endpoint.

    Returns the public keys for token verification.
    """
    with tracer.start_span("api.oidc.jwks") as span:
        try:
            jwks = provider.get_jwks()

            oidc_api_requests_total.labels(
                endpoint="jwks",
                method="GET",
                status="200"
            ).inc()

            span.set_attribute("oidc.key_count", len(jwks.get("keys", [])))
            return jwks

        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="jwks",
                method="GET",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/authorize")
async def authorize(
    request: Request,
    provider: OIDCProvider = Depends(get_oidc_provider)
):
    """
    OAuth2 Authorization endpoint.

    Handles authorization requests from OAuth2 clients.
    """
    with tracer.start_span("api.oidc.authorize") as span:
        try:
            # Get query parameters
            params = dict(request.query_params)
            client_id = params.get("client_id", "unknown")

            # Get current user authentication status
            user_info = await get_current_user(request)

            # Handle authorization request
            result = provider.handle_authorization_request(
                params=params,
                user_authenticated=user_info.get("authenticated", False),
                user_id=user_info.get("user_id"),
                authentication_tier=user_info.get("auth_tier")
            )

            span.set_attribute("oidc.client_id", client_id)
            span.set_attribute("oidc.action", result.get("action", "unknown"))

            if result.get("action") == "redirect":
                oidc_api_requests_total.labels(
                    endpoint="authorize",
                    method="GET",
                    status="302"
                ).inc()
                return RedirectResponse(url=result["redirect_url"], status_code=302)

            elif result.get("action") == "authenticate":
                oidc_api_requests_total.labels(
                    endpoint="authorize",
                    method="GET",
                    status="302"
                ).inc()
                # Redirect to login with original parameters
                return RedirectResponse(url=result["login_url"], status_code=302)

            elif result.get("action") == "consent":
                oidc_api_requests_total.labels(
                    endpoint="authorize",
                    method="GET",
                    status="200"
                ).inc()
                # Return consent page information
                return JSONResponse(content={
                    "action": "consent_required",
                    "client": result["client"],
                    "scopes": result["scopes"],
                    "consent_url": result["consent_url"]
                })

            else:
                # Error response
                error = result.get("error", "server_error")
                oidc_api_requests_total.labels(
                    endpoint="authorize",
                    method="GET",
                    status="400"
                ).inc()

                if "redirect_url" in result:
                    return RedirectResponse(url=result["redirect_url"], status_code=302)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": error,
                            "error_description": result.get("error_description", "Authorization request failed")
                        }
                    )

        except HTTPException:
            raise
        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="authorize",
                method="GET",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/token")
async def token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    OAuth2 Token endpoint.

    Exchanges authorization codes for tokens or refreshes access tokens.
    """
    with tracer.start_span("api.oidc.token") as span:
        try:
            # Build form data dictionary
            form_data = {
                "grant_type": grant_type,
                "client_id": client_id,
            }

            # Add optional parameters
            if code: form_data["code"] = code
            if redirect_uri: form_data["redirect_uri"] = redirect_uri
            if code_verifier: form_data["code_verifier"] = code_verifier
            if refresh_token: form_data["refresh_token"] = refresh_token
            if client_secret: form_data["client_secret"] = client_secret

            # Handle token request
            result = provider.handle_token_request(form_data)

            span.set_attribute("oidc.client_id", client_id)
            span.set_attribute("oidc.grant_type", grant_type)

            if "error" in result:
                oidc_api_requests_total.labels(
                    endpoint="token",
                    method="POST",
                    status="400"
                ).inc()
                span.set_attribute("oidc.error", result["error"])
                raise HTTPException(
                    status_code=400,
                    detail=result
                )
            else:
                oidc_api_requests_total.labels(
                    endpoint="token",
                    method="POST",
                    status="200"
                ).inc()
                span.set_attribute("oidc.tokens_issued", len([k for k in result.keys() if "token" in k]))
                return result

        except HTTPException:
            raise
        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="token",
                method="POST",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/userinfo")
@router.post("/userinfo")
async def userinfo(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    OpenID Connect UserInfo endpoint.

    Returns user information for the provided access token.
    """
    with tracer.start_span("api.oidc.userinfo") as span:
        try:
            # Extract access token from Authorization header
            access_token = None

            if credentials and credentials.credentials:
                access_token = credentials.credentials
            elif authorization and authorization.startswith("Bearer "):
                access_token = authorization[7:]  # Remove "Bearer " prefix

            if not access_token:
                oidc_api_requests_total.labels(
                    endpoint="userinfo",
                    method="GET",
                    status="401"
                ).inc()
                raise HTTPException(
                    status_code=401,
                    detail={"error": "invalid_token", "error_description": "Missing or invalid access token"}
                )

            # Get user information
            userinfo_data = provider.handle_userinfo_request(access_token)

            oidc_api_requests_total.labels(
                endpoint="userinfo",
                method="GET",
                status="200"
            ).inc()

            span.set_attribute("oidc.subject", userinfo_data.get("sub"))
            return userinfo_data

        except HTTPException:
            raise
        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="userinfo",
                method="GET",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/revoke")
async def revoke_token(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    OAuth2 Token Revocation endpoint (RFC 7009).

    Revokes access tokens or refresh tokens.
    """
    with tracer.start_span("api.oidc.revoke") as span:
        try:
            # Authenticate client
            client = provider.client_registry.authenticate_client(client_id, client_secret)
            if not client:
                oidc_api_requests_total.labels(
                    endpoint="revoke",
                    method="POST",
                    status="401"
                ).inc()
                raise HTTPException(
                    status_code=401,
                    detail={"error": "invalid_client", "error_description": "Client authentication failed"}
                )

            # Revoke token
            success = provider.token_manager.revoke_token(token, token_type_hint)

            oidc_api_requests_total.labels(
                endpoint="revoke",
                method="POST",
                status="200"
            ).inc()

            span.set_attribute("oidc.client_id", client_id)
            span.set_attribute("oidc.token_revoked", success)

            # RFC 7009: Always return 200 regardless of token validity
            return {"revoked": success}

        except HTTPException:
            raise
        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="revoke",
                method="POST",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/introspect")
async def introspect_token(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    OAuth2 Token Introspection endpoint (RFC 7662).

    Returns metadata about a token.
    """
    with tracer.start_span("api.oidc.introspect") as span:
        try:
            # Authenticate client
            client = provider.client_registry.authenticate_client(client_id, client_secret)
            if not client:
                oidc_api_requests_total.labels(
                    endpoint="introspect",
                    method="POST",
                    status="401"
                ).inc()
                raise HTTPException(
                    status_code=401,
                    detail={"error": "invalid_client", "error_description": "Client authentication failed"}
                )

            # Introspect token
            introspection_result = provider.token_manager.introspect_token(token)

            oidc_api_requests_total.labels(
                endpoint="introspect",
                method="POST",
                status="200"
            ).inc()

            span.set_attribute("oidc.client_id", client_id)
            span.set_attribute("oidc.token_active", introspection_result.get("active", False))

            return introspection_result

        except HTTPException:
            raise
        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="introspect",
                method="POST",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


# Additional endpoints for debugging and administration

@router.get("/clients", include_in_schema=False)
async def list_clients(
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    List registered OAuth2 clients (admin endpoint).

    For debugging and administration purposes.
    """
    with tracer.start_span("api.oidc.list_clients"):
        try:
            clients = provider.client_registry.list_clients()

            return {
                "clients": [
                    {
                        "client_id": client.client_id,
                        "client_name": client.client_name,
                        "client_type": client.client_type.value,
                        "application_type": client.application_type.value,
                        "is_active": client.is_active,
                        "created_at": client.created_at,
                        "last_used_at": client.last_used_at
                    }
                    for client in clients
                ],
                "total": len(clients)
            }

        except Exception as e:
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", include_in_schema=False)
async def provider_stats(
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    Get OIDC provider statistics (admin endpoint).

    For monitoring and debugging purposes.
    """
    with tracer.start_span("api.oidc.stats"):
        try:
            token_stats = provider.token_manager.get_stats()
            client_count = len(provider.client_registry.list_clients())

            return {
                "clients": {
                    "total_registered": client_count,
                    "active_clients": len(provider.client_registry.list_clients(active_only=True))
                },
                "tokens": token_stats,
                "provider": {
                    "issuer": provider.issuer
                }
            }

        except Exception as e:
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")


# Integration with LUKHAS authentication system

@router.post("/authenticate")
async def authenticate_with_tier(
    username: str = Form(...),
    password: str = Form(...),
    tier: str = Form("T2"),
    totp_code: Optional[str] = Form(None),
    webauthn_response: Optional[str] = Form(None),
    provider: OIDCProvider = Depends(get_oidc_provider)
) -> Dict[str, Any]:
    """
    Authenticate user with LUKHAS tiered authentication.

    This endpoint integrates OIDC with the I.2 Tiered Authentication system.
    """
    with tracer.start_span("api.oidc.authenticate_tier") as span:
        try:
            # Get tiered authentication system
            auth_system = get_tiered_auth_system()

            # Prepare authentication request
            auth_request = {
                "username": username,
                "password": password,
                "tier": tier
            }

            if totp_code:
                auth_request["totp_code"] = totp_code

            if webauthn_response:
                auth_request["webauthn_response"] = json.loads(webauthn_response)

            # Perform tiered authentication
            auth_result = await auth_system.authenticate_tier(tier, auth_request)

            if auth_result.success:
                oidc_api_requests_total.labels(
                    endpoint="authenticate",
                    method="POST",
                    status="200"
                ).inc()

                span.set_attribute("oidc.auth_tier", tier)
                span.set_attribute("oidc.user_id", auth_result.user_id)

                return {
                    "authenticated": True,
                    "user_id": auth_result.user_id,
                    "tier": tier,
                    "token": auth_result.token,
                    "permissions": auth_result.claims.get("permissions", [])
                }
            else:
                oidc_api_requests_total.labels(
                    endpoint="authenticate",
                    method="POST",
                    status="401"
                ).inc()

                span.set_attribute("oidc.auth_failed", True)

                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "authentication_failed",
                        "error_description": auth_result.error_message or "Authentication failed"
                    }
                )

        except HTTPException:
            raise
        except Exception as e:
            oidc_api_requests_total.labels(
                endpoint="authenticate",
                method="POST",
                status="500"
            ).inc()
            span.set_attribute("error", str(e))
            raise HTTPException(status_code=500, detail="Internal server error")