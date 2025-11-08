"""
LUKHAS Identity API Endpoints for Tiered Authentication
======================================================

Comprehensive FastAPI endpoints for the LUKHAS tiered authentication system (T1-T5).
Provides RESTful API for authentication flows, credential management, and security monitoring.

Features:
- Complete T1-T5 authentication endpoints
- WebAuthn credential registration and authentication
- Biometric enrollment and verification
- Session management and tier elevation
- Security monitoring and audit trails
- Guardian system integration
- Performance monitoring (<100ms p95 latency)
- OpenAPI 3.0 documentation
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Import LUKHAS tiered authentication components
try:
    from ..governance.guardian_system import GuardianSystem
    from ..identity.biometrics import (
        BiometricAttestation,  # TODO: ..identity.biometrics.Biometri...
        BiometricModality,
        MockBiometricProvider,
        create_mock_biometric_provider,
    )
    from ..identity.tiers import (
        AuthContext,
        AuthResult,
        SecurityPolicy,
        Tier,
        TieredAuthenticator,
        create_tiered_authenticator,
    )
    from ..identity.webauthn_enhanced import (
        EnhancedWebAuthnService,
        create_enhanced_webauthn_service,
    )
    IDENTITY_SYSTEM_AVAILABLE = True
except ImportError:
    IDENTITY_SYSTEM_AVAILABLE = False
    structlog.get_logger(__name__).warning("Identity system components not available")

logger = structlog.get_logger(__name__)

# Security handler
security = HTTPBearer(auto_error=False)

# Pydantic models for API requests/responses

class TierAuthenticationRequest(BaseModel):
    """Base authentication request."""

    tier: Tier = Field(..., description="Authentication tier (T1-T5)")
    correlation_id: str | None = Field(None, description="Request correlation ID")

    # T2+ credentials
    username: str | None = Field(None, description="Username for T2+ authentication")
    password: str | None = Field(None, description="Password for T2 authentication")

    # T3+ credentials
    totp_token: str | None = Field(None, description="TOTP token for T3 authentication")

    # T4+ credentials
    webauthn_response: dict[str, Any] | None = Field(None, description="WebAuthn response for T4")
    webauthn_challenge_id: str | None = Field(None, description="Issued WebAuthn challenge identifier")

    # T5 credentials
    biometric_attestation: dict[str, Any] | None = Field(None, description="Biometric attestation for T5")

    # Session context
    existing_tier: Tier | None = Field(None, description="Current authenticated tier")
    session_id: str | None = Field(None, description="Existing session ID")
    nonce: str | None = Field(None, description="Anti-replay nonce")


class AuthenticationResponse(BaseModel):
    """Authentication response."""

    success: bool = Field(..., description="Authentication success status")
    tier: Tier = Field(..., description="Achieved authentication tier")

    # Success fields
    user_id: str | None = Field(None, description="Authenticated user ID")
    session_id: str | None = Field(None, description="Session identifier")
    jwt_token: str | None = Field(None, description="JWT authentication token")
    expires_at: datetime | None = Field(None, description="Token expiration time")
    tier_elevation_path: str | None = Field(None, description="Tier elevation path")

    # Metadata
    correlation_id: str | None = Field(None, description="Request correlation ID")
    auth_time: datetime = Field(..., description="Authentication timestamp")
    duration_ms: float = Field(..., description="Authentication duration in milliseconds")
    guardian_validated: bool = Field(False, description="Guardian system validation status")

    # Error fields
    error_code: str | None = Field(None, description="Error code for failed authentication")
    error_message: str | None = Field(None, description="Human-readable error message")


class WebAuthnChallengeRequest(BaseModel):
    """WebAuthn challenge generation request."""

    user_id: str = Field(..., description="User identifier")
    correlation_id: str | None = Field(None, description="Request correlation ID")


class WebAuthnChallengeResponse(BaseModel):
    """WebAuthn challenge response."""

    challenge_id: str = Field(..., description="Challenge identifier")
    options: dict[str, Any] = Field(..., description="WebAuthn challenge options")
    expires_at: datetime = Field(..., description="Challenge expiration time")


class WebAuthnVerificationRequest(BaseModel):
    """WebAuthn verification request."""

    challenge_id: str = Field(..., description="Challenge identifier")
    webauthn_response: dict[str, Any] = Field(..., description="WebAuthn authentication response")
    correlation_id: str | None = Field(None, description="Request correlation ID")


class WebAuthnVerificationResponse(BaseModel):
    """WebAuthn verification response."""

    success: bool = Field(..., description="Verification success status")
    credential_id: str | None = Field(None, description="Verified credential ID")
    user_id: str | None = Field(None, description="Verified user ID")

    # Security metadata
    signature_valid: bool = Field(False, description="Signature validation status")
    user_verified: bool = Field(False, description="User verification status")

    # Performance metadata
    verification_time_ms: float = Field(..., description="Verification duration")

    # Error metadata
    error_code: str | None = Field(None, description="Error code")
    error_message: str | None = Field(None, description="Error message")


class BiometricEnrollmentRequest(BaseModel):
    """Biometric enrollment request."""

    user_id: str = Field(..., description="User identifier")
    modality: str = Field(..., description="Biometric modality (fingerprint, face, iris, etc.)")
    sample_data: str = Field(..., description="Base64-encoded biometric sample")
    device_info: dict[str, Any] | None = Field(None, description="Capture device information")


class BiometricEnrollmentResponse(BaseModel):
    """Biometric enrollment response."""

    success: bool = Field(..., description="Enrollment success status")
    template_id: str | None = Field(None, description="Generated template ID")
    error_message: str | None = Field(None, description="Error message if failed")


class BiometricAuthenticationRequest(BaseModel):
    """Biometric authentication request."""

    user_id: str = Field(..., description="User identifier")
    modality: str = Field(..., description="Biometric modality")
    sample_data: str = Field(..., description="Base64-encoded biometric sample")
    nonce: str = Field(..., description="Anti-replay nonce")
    device_info: dict[str, Any] | None = Field(None, description="Capture device information")


class BiometricAuthenticationResponse(BaseModel):
    """Biometric authentication response."""

    success: bool = Field(..., description="Authentication success status")
    attestation: dict[str, Any] = Field(..., description="Biometric attestation data")
    processing_time_ms: float = Field(..., description="Processing duration")


class SessionStatusResponse(BaseModel):
    """Session status response."""

    authenticated: bool = Field(..., description="Session authentication status")
    tier: Tier | None = Field(None, description="Current authentication tier")
    user_id: str | None = Field(None, description="Authenticated user ID")
    session_id: str | None = Field(None, description="Session identifier")
    expires_at: datetime | None = Field(None, description="Session expiration time")
    created_at: datetime | None = Field(None, description="Session creation time")


class SystemMetricsResponse(BaseModel):
    """System performance metrics response."""

    authentication_metrics: dict[str, Any] = Field(..., description="Authentication performance metrics")
    webauthn_metrics: dict[str, Any] = Field(..., description="WebAuthn performance metrics")
    biometric_metrics: dict[str, Any] = Field(..., description="Biometric performance metrics")
    system_status: dict[str, Any] = Field(..., description="Overall system status")


# Router initialization
router = APIRouter(
    prefix="/identity",
    tags=["identity", "authentication"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient privileges"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)

# Global services (initialized on startup)
authenticator: TieredAuthenticator | None = None
webauthn_service: EnhancedWebAuthnService | None = None
biometric_provider: MockBiometricProvider | None = None
guardian: GuardianSystem | None = None


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str | None:
    """Extract user agent from request."""
    return request.headers.get("User-Agent")


async def create_auth_context(
    request: Request,
    auth_request: TierAuthenticationRequest
) -> AuthContext:
    """Create authentication context from request."""
    return AuthContext(
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        correlation_id=auth_request.correlation_id,
        username=auth_request.username,
        password=auth_request.password,
        totp_token=auth_request.totp_token,
        webauthn_response=auth_request.webauthn_response,
        biometric_attestation=auth_request.biometric_attestation,
        existing_tier=auth_request.existing_tier,
        session_id=auth_request.session_id,
        nonce=auth_request.nonce,
        challenge_data=(
            {"challenge_id": auth_request.webauthn_challenge_id}
            if auth_request.webauthn_challenge_id
            else None
        )
    )


def convert_auth_result(result: AuthResult) -> AuthenticationResponse:
    """Convert AuthResult to API response."""
    return AuthenticationResponse(
        success=result.ok,
        tier=result.tier,
        user_id=result.user_id,
        session_id=result.session_id,
        jwt_token=result.jwt_token,
        expires_at=result.expires_at,
        tier_elevation_path=result.tier_elevation_path,
        correlation_id=result.correlation_id,
        auth_time=result.auth_time,
        duration_ms=result.duration_ms or 0.0,
        guardian_validated=result.guardian_validated,
        error_code=None if result.ok else "AUTHENTICATION_FAILED",
        error_message=None if result.ok else result.reason
    )


# Startup event to initialize services
@router.on_event("startup")
async def initialize_services():
    """Initialize identity services on startup."""
    global authenticator, webauthn_service, biometric_provider, guardian

    try:
        if IDENTITY_SYSTEM_AVAILABLE:
            # Initialize Guardian system
            guardian = GuardianSystem()

            # Initialize authentication services
            authenticator = create_tiered_authenticator(
                security_policy=SecurityPolicy(),
                guardian_system=guardian
            )

            webauthn_service = create_enhanced_webauthn_service(
                guardian_system=guardian
            )

            biometric_provider = create_mock_biometric_provider(
                guardian_system=guardian
            )

            logger.info("Identity services initialized successfully")
        else:
            logger.warning("Identity services unavailable - using mock responses")

    except Exception as e:
        logger.error("Failed to initialize identity services", error=str(e))


# Authentication endpoints

@router.post("/authenticate", response_model=AuthenticationResponse)
async def authenticate(
    auth_request: TierAuthenticationRequest,
    request: Request
) -> AuthenticationResponse:
    """
    Authenticate user using tiered authentication system.

    Supports all authentication tiers (T1-T5) with progressive enhancement:
    - T1: Public access (no credentials required)
    - T2: Password authentication (username + password)
    - T3: Multi-factor authentication (T2 + TOTP)
    - T4: Hardware security keys (T3 + WebAuthn)
    - T5: Biometric authentication (T4 + biometric attestation)
    """
    start_time = time.perf_counter()

    try:
        if not authenticator:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

        # Create authentication context
        auth_context = await create_auth_context(request, auth_request)

        # Route to appropriate tier authentication method
        if auth_request.tier == "T1":
            result = await authenticator.authenticate_T1(auth_context)
        elif auth_request.tier == "T2":
            result = await authenticator.authenticate_T2(auth_context)
        elif auth_request.tier == "T3":
            result = await authenticator.authenticate_T3(auth_context)
        elif auth_request.tier == "T4":
            result = await authenticator.authenticate_T4(auth_context)
        elif auth_request.tier == "T5":
            result = await authenticator.authenticate_T5(auth_context)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid authentication tier: {auth_request.tier}"
            )

        # Convert result to API response
        response = convert_auth_result(result)

        # Log authentication attempt
        logger.info("Authentication attempt completed",
                   tier=auth_request.tier, success=result.ok,
                   user_id=result.user_id, duration_ms=response.duration_ms)

        # Return appropriate HTTP status
        if not result.ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response.dict()
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error("Authentication endpoint error",
                    tier=auth_request.tier, error=str(e), duration_ms=duration_ms)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error"
        )


# WebAuthn endpoints

@router.post("/webauthn/challenge", response_model=WebAuthnChallengeResponse)
async def generate_webauthn_challenge(
    challenge_request: WebAuthnChallengeRequest,
    request: Request
) -> WebAuthnChallengeResponse:
    """
    Generate WebAuthn authentication challenge for T4 authentication.

    Creates a cryptographically secure challenge for WebAuthn/FIDO2 authentication
    with anti-replay protection and Guardian integration.
    """
    try:
        if authenticator and getattr(authenticator, "webauthn", None):
            challenge_data = await authenticator.generate_webauthn_challenge(
                username=challenge_request.user_id,
                correlation_id=challenge_request.correlation_id,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
            )
        elif webauthn_service:
            challenge_data = await webauthn_service.generate_authentication_challenge(
                user_id=challenge_request.user_id,
                correlation_id=challenge_request.correlation_id or "",
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WebAuthn service unavailable"
            )

        return WebAuthnChallengeResponse(
            challenge_id=challenge_data["challenge_id"],
            options=challenge_data["options"],
            expires_at=datetime.fromisoformat(challenge_data["expires_at"])
        )

    except Exception as e:
        logger.error("WebAuthn challenge generation failed",
                    user_id=challenge_request.user_id, error=str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate WebAuthn challenge"
        )


@router.post("/webauthn/verify", response_model=WebAuthnVerificationResponse)
async def verify_webauthn_response(
    verification_request: WebAuthnVerificationRequest,
    request: Request
) -> WebAuthnVerificationResponse:
    """
    Verify WebAuthn authentication response for T4 authentication.

    Validates WebAuthn response including signature verification, challenge validation,
    and user verification requirements for T4 tier authentication.
    """
    try:
        if authenticator and getattr(authenticator, "webauthn", None):
            service = authenticator.webauthn
        else:
            service = webauthn_service

        if not service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WebAuthn service unavailable"
            )

        result = await service.verify_authentication_response(  # type: ignore[call-arg]
            challenge_id=verification_request.challenge_id,
            webauthn_response=verification_request.webauthn_response,
            correlation_id=verification_request.correlation_id or "",
            ip_address=get_client_ip(request)
        )

        response = WebAuthnVerificationResponse(
            success=result.success,
            credential_id=result.credential_id,
            user_id=result.user_id,
            signature_valid=result.signature_valid,
            user_verified=result.user_verified,
            verification_time_ms=result.verification_time_ms,
            error_code=result.error_code,
            error_message=result.error_message
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response.dict()
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("WebAuthn verification failed",
                    challenge_id=verification_request.challenge_id, error=str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebAuthn verification error"
        )


# Biometric endpoints

@router.post("/biometric/enroll", response_model=BiometricEnrollmentResponse)
async def enroll_biometric(
    enrollment_request: BiometricEnrollmentRequest,
    request: Request
) -> BiometricEnrollmentResponse:
    """
    Enroll biometric template for T5 authentication.

    Registers a biometric template for the specified user and modality.
    Supports fingerprint, face, iris, and other biometric modalities.
    """
    try:
        if not biometric_provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Biometric service unavailable"
            )

        # Parse modality
        try:
            modality = BiometricModality(enrollment_request.modality.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid biometric modality: {enrollment_request.modality}"
            )

        # Enroll biometric template
        success, result = await biometric_provider.enroll_biometric(
            user_id=enrollment_request.user_id,
            modality=modality,
            sample_data=enrollment_request.sample_data,
            device_info=enrollment_request.device_info
        )

        if success:
            return BiometricEnrollmentResponse(
                success=True,
                template_id=result
            )
        else:
            return BiometricEnrollmentResponse(
                success=False,
                error_message=result
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Biometric enrollment failed",
                    user_id=enrollment_request.user_id, error=str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Biometric enrollment error"
        )


@router.post("/biometric/authenticate", response_model=BiometricAuthenticationResponse)
async def authenticate_biometric(
    auth_request: BiometricAuthenticationRequest,
    request: Request
) -> BiometricAuthenticationResponse:
    """
    Authenticate using biometric sample for T5 authentication.

    Performs biometric authentication using enrolled templates with anti-spoofing
    detection and liveness verification.
    """
    try:
        if not biometric_provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Biometric service unavailable"
            )

        # Parse modality
        try:
            modality = BiometricModality(auth_request.modality.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid biometric modality: {auth_request.modality}"
            )

        # Authenticate biometric sample
        attestation = await biometric_provider.authenticate_biometric(
            user_id=auth_request.user_id,
            sample_data=auth_request.sample_data,
            modality=modality,
            nonce=auth_request.nonce,
            device_info=auth_request.device_info
        )

        response = BiometricAuthenticationResponse(
            success=attestation.authenticated,
            attestation=attestation.to_dict(),
            processing_time_ms=attestation.processing_time_ms
        )

        if not attestation.authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=response.dict()
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Biometric authentication failed",
                    user_id=auth_request.user_id, error=str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Biometric authentication error"
        )


# Session management endpoints

@router.get("/session/status", response_model=SessionStatusResponse)
async def get_session_status(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_api_identity_py_L638"}
) -> SessionStatusResponse:
    """
    Get current session authentication status.

    Returns the current authentication tier and session metadata for the requesting user.
    """
    try:
        # Mock session status (in production, validate JWT token)
        if credentials and credentials.credentials:
            # Parse JWT token and extract session info
            # This is a mock implementation
            return SessionStatusResponse(
                authenticated=True,
                tier="T2",
                user_id="test_user",
                session_id="session_123",
                expires_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
        else:
            return SessionStatusResponse(
                authenticated=False
            )

    except Exception as e:
        logger.error("Session status check failed", error=str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session status check error"
        )


@router.post("/session/elevate")
async def elevate_session_tier(
    auth_request: TierAuthenticationRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security)  # TODO[T4-ISSUE]: {"code":"B008","ticket":"GH-1031","owner":"matriz-team","status":"accepted","reason":"FastAPI dependency injection - Depends() in route parameters is required pattern","estimate":"0h","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_lukhas_website_lukhas_api_identity_py_L676"}
) -> AuthenticationResponse:
    """
    Elevate current session to higher authentication tier.

    Allows upgrading from lower tier (e.g., T2) to higher tier (e.g., T4) within
    the same session for accessing privileged resources.
    """
    # Delegate to main authenticate endpoint
    return await authenticate(auth_request, request)


# Monitoring and metrics endpoints

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics() -> SystemMetricsResponse:
    """
    Get system performance metrics and status.

    Returns performance metrics for authentication, WebAuthn, and biometric services
    including latency percentiles, success rates, and system health indicators.
    """
    try:
        auth_metrics = {}
        webauthn_metrics = {}
        biometric_metrics = {}

        if authenticator:
            # In production, implement performance metrics collection
            auth_metrics = {
                "total_authentications": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0
            }

        if webauthn_service:
            webauthn_metrics = webauthn_service.get_performance_metrics()

        if biometric_provider:
            biometric_metrics = biometric_provider.get_performance_metrics()

        system_status = {
            "authenticator_available": authenticator is not None,
            "webauthn_available": webauthn_service is not None,
            "biometric_available": biometric_provider is not None,
            "guardian_available": guardian is not None,
            "overall_health": "healthy"
        }

        return SystemMetricsResponse(
            authentication_metrics=auth_metrics,
            webauthn_metrics=webauthn_metrics,
            biometric_metrics=biometric_metrics,
            system_status=system_status
        )

    except Exception as e:
        logger.error("Metrics retrieval failed", error=str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics retrieval error"
        )


# Health check endpoint

@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for service monitoring.

    Returns basic health status and service availability information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "authenticator": authenticator is not None,
            "webauthn": webauthn_service is not None,
            "biometric": biometric_provider is not None,
            "guardian": guardian is not None
        }
    }
