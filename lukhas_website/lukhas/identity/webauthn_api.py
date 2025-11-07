#!/usr/bin/env python3
"""
LUKHAS I.4 WebAuthn/Passkeys - API Endpoints
Production Schema v1.0.0

REST API for WebAuthn/FIDO2 operations with comprehensive
authentication tiers and device management.

Constellation Framework: Identity ⚛️ API layer
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from opentelemetry import trace
from prometheus_client import Counter, Histogram
from pydantic import BaseModel, Field

from .auth_service import verify_token
from .rate_limiting import RateLimitType, get_rate_limiter
from .webauthn_production import AuthenticatorTier, AuthenticatorType, get_webauthn_manager

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
security = HTTPBearer()

# Prometheus metrics
webauthn_api_requests_total = Counter(
    'lukhas_webauthn_api_requests_total',
    'Total WebAuthn API requests',
    ['endpoint', 'status']
)

webauthn_api_latency_seconds = Histogram(
    'lukhas_webauthn_api_latency_seconds',
    'WebAuthn API latency',
    ['endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

router = APIRouter(prefix="/webauthn", tags=["webauthn"])


class RegistrationBeginRequest(BaseModel):
    """WebAuthn registration begin request"""
    username: str = Field(..., description="Username")
    display_name: str = Field(..., description="Display name")
    tier: str = Field(default="T4", description="Authentication tier (T3, T4, T5)")
    authenticator_attachment: str | None = Field(default=None, description="platform, cross-platform, or None")
    resident_key: bool = Field(default=True, description="Require resident key")
    device_name: str | None = Field(default=None, description="Device name for identification")


class RegistrationFinishRequest(BaseModel):
    """WebAuthn registration finish request"""
    challenge_id: str = Field(..., description="Challenge ID from begin request")
    credential: Dict[str, Any] = Field(..., description="WebAuthn credential response")
    device_name: str | None = Field(default=None, description="Device name for identification")


class AuthenticationBeginRequest(BaseModel):
    """WebAuthn authentication begin request"""
    user_id: str | None = Field(default=None, description="User ID (optional for usernameless)")
    tier: str = Field(default="T4", description="Required authentication tier")
    timeout: int = Field(default=300000, description="Timeout in milliseconds")


class AuthenticationFinishRequest(BaseModel):
    """WebAuthn authentication finish request"""
    challenge_id: str = Field(..., description="Challenge ID from begin request")
    credential: Dict[str, Any] = Field(..., description="WebAuthn authentication response")


class WebAuthnCredentialResponse(BaseModel):
    """WebAuthn credential response"""
    id: str
    device_name: str | None
    authenticator_type: str
    tier: str
    status: str
    created_at: str
    last_used: str | None
    biometric_enrolled: bool
    backup_eligible: bool


class WebAuthnStatusResponse(BaseModel):
    """WebAuthn system status"""
    available: bool
    registered_credentials: int
    supported_tiers: List[str]
    supported_authenticator_types: List[str]


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L100"}
    """Verify authentication token"""
    try:
        token = credentials.credentials
        payload = await verify_token(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def registration_rate_limit(request: Request):
    """Rate limiting dependency for WebAuthn registration endpoints"""
    client_ip = await get_client_ip(request)
    rate_limiter = get_rate_limiter()

    allowed, metadata = await rate_limiter.check_rate_limit(
        client_ip, RateLimitType.WEBAUTHN_REGISTRATION
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=metadata,
            headers={"Retry-After": str(metadata.get("retry_after", 60))}
        )

    return metadata


async def authentication_rate_limit(request: Request):
    """Rate limiting dependency for WebAuthn authentication endpoints"""
    client_ip = await get_client_ip(request)
    rate_limiter = get_rate_limiter()

    allowed, metadata = await rate_limiter.check_rate_limit(
        client_ip, RateLimitType.WEBAUTHN_AUTHENTICATION
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=metadata,
            headers={"Retry-After": str(metadata.get("retry_after", 60))}
        )

    return metadata


@router.post("/register/begin")
async def begin_registration(
    request: RegistrationBeginRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L168"}
    rate_limit_check: Dict[str, Any] = Depends(registration_rate_limit)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L169"}
):
    """Begin WebAuthn credential registration"""

    with tracer.start_span("webauthn_api.begin_registration") as span:
        span.set_attribute("user_id", current_user.get("sub", "unknown"))
        span.set_attribute("tier", request.tier)
        span.set_attribute("authenticator_attachment", request.authenticator_attachment or "any")

        start_time = time.time()

        try:
            # Validate tier
            try:
                tier = AuthenticatorTier(request.tier)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid tier: {request.tier}. Must be T3, T4, or T5"
                )

            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # Begin registration
            options = await webauthn_manager.begin_registration(
                user_id=current_user["sub"],
                username=request.username,
                display_name=request.display_name,
                tier=tier,
                authenticator_attachment=request.authenticator_attachment,
                resident_key=request.resident_key
            )

            # Record metrics
            latency = time.time() - start_time
            webauthn_api_requests_total.labels(
                endpoint="begin_registration",
                status="success"
            ).inc()

            webauthn_api_latency_seconds.labels(
                endpoint="begin_registration"
            ).observe(latency)

            span.set_attribute("challenge_id", options.get("_challenge_id", "unknown"))
            span.set_attribute("latency", latency)

            return options

        except HTTPException:
            webauthn_api_requests_total.labels(
                endpoint="begin_registration",
                status="client_error"
            ).inc()
            raise
        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="begin_registration",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn registration begin failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to begin WebAuthn registration"
            )


@router.post("/register/finish")
async def finish_registration(
    request: RegistrationFinishRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L244"}
    rate_limit_check: Dict[str, Any] = Depends(registration_rate_limit)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L245"}
):
    """Complete WebAuthn credential registration"""

    with tracer.start_span("webauthn_api.finish_registration") as span:
        span.set_attribute("user_id", current_user.get("sub", "unknown"))
        span.set_attribute("challenge_id", request.challenge_id)

        start_time = time.time()

        try:
            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # Complete registration
            credential = await webauthn_manager.finish_registration(
                challenge_id=request.challenge_id,
                credential_data=request.credential,
                device_name=request.device_name
            )

            # Record metrics
            latency = time.time() - start_time
            webauthn_api_requests_total.labels(
                endpoint="finish_registration",
                status="success"
            ).inc()

            webauthn_api_latency_seconds.labels(
                endpoint="finish_registration"
            ).observe(latency)

            span.set_attribute("credential_id", credential.credential_id)
            span.set_attribute("authenticator_type", credential.authenticator_type.value)
            span.set_attribute("tier", credential.tier.value)
            span.set_attribute("latency", latency)

            return WebAuthnCredentialResponse(
                id=credential.credential_id,
                device_name=credential.device_name,
                authenticator_type=credential.authenticator_type.value,
                tier=credential.tier.value,
                status=credential.status.value,
                created_at=credential.created_at.isoformat(),
                last_used=credential.last_used.isoformat() if credential.last_used else None,
                biometric_enrolled=credential.biometric_enrolled,
                backup_eligible=credential.backup_eligible
            )

        except HTTPException:
            webauthn_api_requests_total.labels(
                endpoint="finish_registration",
                status="client_error"
            ).inc()
            raise
        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="finish_registration",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn registration finish failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete WebAuthn registration"
            )


@router.post("/authenticate/begin")
async def begin_authentication(
    request: AuthenticationBeginRequest,
    rate_limit_check: Dict[str, Any] = Depends(authentication_rate_limit)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L319"}
):
    """Begin WebAuthn authentication"""

    with tracer.start_span("webauthn_api.begin_authentication") as span:
        span.set_attribute("user_id", request.user_id or "usernameless")
        span.set_attribute("tier", request.tier)

        start_time = time.time()

        try:
            # Validate tier
            try:
                tier = AuthenticatorTier(request.tier)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid tier: {request.tier}. Must be T3, T4, or T5"
                )

            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # Begin authentication
            options = await webauthn_manager.begin_authentication(
                user_id=request.user_id,
                tier=tier,
                timeout=request.timeout
            )

            # Record metrics
            latency = time.time() - start_time
            webauthn_api_requests_total.labels(
                endpoint="begin_authentication",
                status="success"
            ).inc()

            webauthn_api_latency_seconds.labels(
                endpoint="begin_authentication"
            ).observe(latency)

            span.set_attribute("challenge_id", options.get("_challenge_id", "unknown"))
            span.set_attribute("allowed_credentials", len(options.get("allowCredentials", [])))
            span.set_attribute("latency", latency)

            return options

        except HTTPException:
            webauthn_api_requests_total.labels(
                endpoint="begin_authentication",
                status="client_error"
            ).inc()
            raise
        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="begin_authentication",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn authentication begin failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to begin WebAuthn authentication"
            )


@router.post("/authenticate/finish")
async def finish_authentication(
    request: AuthenticationFinishRequest,
    rate_limit_check: Dict[str, Any] = Depends(authentication_rate_limit)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L391"}
):
    """Complete WebAuthn authentication"""

    with tracer.start_span("webauthn_api.finish_authentication") as span:
        span.set_attribute("challenge_id", request.challenge_id)

        start_time = time.time()

        try:
            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # Complete authentication
            credential, verification_result = await webauthn_manager.finish_authentication(
                challenge_id=request.challenge_id,
                credential_data=request.credential
            )

            # Record metrics
            latency = time.time() - start_time
            webauthn_api_requests_total.labels(
                endpoint="finish_authentication",
                status="success"
            ).inc()

            webauthn_api_latency_seconds.labels(
                endpoint="finish_authentication"
            ).observe(latency)

            span.set_attribute("credential_id", credential.credential_id)
            span.set_attribute("authenticator_type", credential.authenticator_type.value)
            span.set_attribute("tier", credential.tier.value)
            span.set_attribute("verified", verification_result["verified"])
            span.set_attribute("latency", latency)

            # Return authentication result
            return {
                "verified": verification_result["verified"],
                "user_id": credential.user_id,
                "credential_id": credential.credential_id,
                "authenticator_type": credential.authenticator_type.value,
                "tier": credential.tier.value,
                "device_name": credential.device_name,
                "biometric_enrolled": credential.biometric_enrolled,
                "sign_count": verification_result["sign_count"],
                "backup_eligible": verification_result.get("backup_eligible", False),
                "backup_state": verification_result.get("backup_state", False)
            }

        except HTTPException:
            webauthn_api_requests_total.labels(
                endpoint="finish_authentication",
                status="client_error"
            ).inc()
            raise
        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="finish_authentication",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn authentication finish failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete WebAuthn authentication"
            )


@router.get("/credentials", response_model=List[WebAuthnCredentialResponse])
async def list_credentials(current_user: Dict[str, Any] = Depends(get_current_user)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L464"}
    """List all WebAuthn credentials for the current user"""

    with tracer.start_span("webauthn_api.list_credentials") as span:
        span.set_attribute("user_id", current_user.get("sub", "unknown"))

        start_time = time.time()

        try:
            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # List user credentials
            credentials = await webauthn_manager.list_user_credentials(current_user["sub"])

            # Record metrics
            latency = time.time() - start_time
            webauthn_api_requests_total.labels(
                endpoint="list_credentials",
                status="success"
            ).inc()

            webauthn_api_latency_seconds.labels(
                endpoint="list_credentials"
            ).observe(latency)

            span.set_attribute("credential_count", len(credentials))
            span.set_attribute("latency", latency)

            return [
                WebAuthnCredentialResponse(
                    id=cred["id"],
                    device_name=cred["device_name"],
                    authenticator_type=cred["authenticator_type"],
                    tier=cred["tier"],
                    status=cred["status"],
                    created_at=cred["created_at"],
                    last_used=cred["last_used"],
                    biometric_enrolled=cred["biometric_enrolled"],
                    backup_eligible=cred["backup_eligible"]
                )
                for cred in credentials
            ]

        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="list_credentials",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn credential listing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list WebAuthn credentials"
            )


@router.delete("/credentials/{credential_id}")
async def revoke_credential(
    credential_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L527"}
):
    """Revoke a WebAuthn credential"""

    with tracer.start_span("webauthn_api.revoke_credential") as span:
        span.set_attribute("user_id", current_user.get("sub", "unknown"))
        span.set_attribute("credential_id", credential_id)

        start_time = time.time()

        try:
            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # Verify credential belongs to user
            credential = await webauthn_manager.credential_store.get_credential(credential_id)
            if not credential or credential.user_id != current_user["sub"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Credential not found"
                )

            # Revoke credential
            success = await webauthn_manager.revoke_credential(credential_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Credential not found"
                )

            # Record metrics
            latency = time.time() - start_time
            webauthn_api_requests_total.labels(
                endpoint="revoke_credential",
                status="success"
            ).inc()

            webauthn_api_latency_seconds.labels(
                endpoint="revoke_credential"
            ).observe(latency)

            span.set_attribute("latency", latency)

            return {"message": "Credential revoked successfully"}

        except HTTPException:
            webauthn_api_requests_total.labels(
                endpoint="revoke_credential",
                status="client_error"
            ).inc()
            raise
        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="revoke_credential",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn credential revocation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke WebAuthn credential"
            )


@router.get("/status", response_model=WebAuthnStatusResponse)
async def get_webauthn_status(current_user: Dict[str, Any] = Depends(get_current_user)):  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_identity_webauthn_api_py_L596"}
    """Get WebAuthn system status for the current user"""

    with tracer.start_span("webauthn_api.status") as span:
        span.set_attribute("user_id", current_user.get("sub", "unknown"))

        try:
            # Get WebAuthn manager
            webauthn_manager = get_webauthn_manager()

            # Get user credentials count
            credentials = await webauthn_manager.credential_store.get_credentials(current_user["sub"])
            active_credentials = [c for c in credentials if c.status.value == "active"]

            webauthn_api_requests_total.labels(
                endpoint="status",
                status="success"
            ).inc()

            return WebAuthnStatusResponse(
                available=True,  # WebAuthn is available
                registered_credentials=len(active_credentials),
                supported_tiers=[tier.value for tier in AuthenticatorTier],
                supported_authenticator_types=[auth_type.value for auth_type in AuthenticatorType]
            )

        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="status",
                status="server_error"
            ).inc()

            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            logger.error(f"WebAuthn status check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get WebAuthn status"
            )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for WebAuthn service"""

    with tracer.start_span("webauthn_api.health_check"):
        try:
            # Basic health check - verify WebAuthn manager can be initialized
            get_webauthn_manager()

            webauthn_api_requests_total.labels(
                endpoint="health_check",
                status="success"
            ).inc()

            return {
                "status": "healthy",
                "webauthn_available": True,
                "timestamp": time.time()
            }

        except Exception as e:
            webauthn_api_requests_total.labels(
                endpoint="health_check",
                status="server_error"
            ).inc()

            logger.error(f"WebAuthn health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="WebAuthn service unhealthy"
            )
