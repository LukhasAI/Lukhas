"""
LUKHAS Consent Fabric API
========================
FastAPI endpoints for consent management and capability tokens.
Implements metadata-first consent with escalation paths.

System-wide guardrails applied:
1. Canonical identity is ΛID = {namespace?}:{username}
2. Data minimization: metadata-only reads by default
3. Capability tokens: short-lived, least-privilege JWT with caveats
4. Everything has logs, audit trail, and revocation paths

ACK GUARDRAILS
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .service import (
    CapabilityToken,
    ConsentGrantRequest,
    ConsentLedgerEntry,
    ConsentRevokeRequest,
    ConsentService,
)


# Request/Response Models
class GrantConsentRequest(BaseModel):
    """API request model for granting consent"""
    lid: str = Field(..., description="Canonical ΛID")
    service: str = Field(..., description="Service name")
    scopes: list[str] = Field(..., description="Requested scopes")
    purpose: str = Field(..., description="Human-readable purpose")
    ttl_minutes: int = Field(60, ge=1, le=1440, description="Time-to-live (1-1440 minutes)")
    resource_pattern: Optional[str] = Field(None, description="Optional resource filter")


class GrantConsentResponse(BaseModel):
    """API response model for consent grant"""
    grant_id: str
    capability_token: CapabilityToken
    message: str = "Consent granted successfully"


class RevokeConsentRequest(BaseModel):
    """API request model for revoking consent"""
    lid: str = Field(..., description="Canonical ΛID")
    grant_id: Optional[str] = Field(None, description="Specific grant ID")
    service: Optional[str] = Field(None, description="Service filter")
    scopes: Optional[list[str]] = Field(None, description="Scope filters")
    reason: str = Field("User requested", description="Revocation reason")


class RevokeConsentResponse(BaseModel):
    """API response model for consent revocation"""
    revoked_count: int
    message: str


class LedgerResponse(BaseModel):
    """API response model for consent ledger"""
    lid: str
    entries: list[ConsentLedgerEntry]
    total_entries: int


class EscalateRequest(BaseModel):
    """API request model for content escalation"""
    lid: str = Field(..., description="Canonical ΛID")
    service: str = Field(..., description="Service name")
    resource_id: str = Field(..., description="Specific resource ID")
    purpose: str = Field(..., description="Purpose for content access")
    ttl_minutes: int = Field(30, ge=1, le=30, description="TTL for content access (max 30 min)")


class EscalateResponse(BaseModel):
    """API response model for content escalation"""
    capability_token: CapabilityToken
    message: str = "Content access granted"


class VerifyTokenRequest(BaseModel):
    """API request model for token verification"""
    token: str = Field(..., description="Capability token to verify")
    required_scopes: list[str] = Field(..., description="Required scopes")
    resource_id: Optional[str] = Field(None, description="Specific resource ID")


class VerifyTokenResponse(BaseModel):
    """API response model for token verification"""
    valid: bool
    claims: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ConsentStatsResponse(BaseModel):
    """API response model for consent statistics"""
    total_active_grants: int
    total_services: int
    recent_activity: dict[str, int]
    performance_stats: dict[str, float]


# Global consent service instance
consent_service: Optional[ConsentService] = None


async def get_consent_service() -> ConsentService:
    """Dependency to get consent service instance"""
    global consent_service
    if consent_service is None:
        consent_service = ConsentService()
        await consent_service.initialize()
    return consent_service


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    # Check for forwarded IP headers (for reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct connection IP
    return request.client.host if request.client else "unknown"


def get_client_context(request: Request) -> dict[str, Any]:
    """Extract client context from request"""
    return {
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "referer": request.headers.get("Referer"),
        "accept_language": request.headers.get("Accept-Language"),
        "session_id": request.headers.get("X-Session-ID"),
        "client_fingerprint": request.headers.get("X-Client-Fingerprint")
    }


# FastAPI Router
router = APIRouter(prefix="/consent", tags=["Consent Management"])


@router.post("/grant", response_model=GrantConsentResponse)
async def grant_consent(
    request_data: GrantConsentRequest,
    request: Request,
    service: ConsentService = Depends(get_consent_service)
):
    """
    Grant consent for service access with capability token issuance.

    Implements metadata-first consent:
    - Metadata scopes (*.headers, *.list.metadata) get longer TTL
    - Content scopes (*.read.content, *.write) get shorter TTL
    - Admin scopes (*.delete, *.share) get very short TTL

    Returns capability token (macaroon) with caveats for verification.
    """
    try:
        # Convert to service request
        service_request = ConsentGrantRequest(
            lid=request_data.lid,
            service=request_data.service,
            scopes=request_data.scopes,
            purpose=request_data.purpose,
            ttl_minutes=request_data.ttl_minutes,
            resource_pattern=request_data.resource_pattern
        )

        # Grant consent
        grant_id, capability_token = await service.grant_consent(
            service_request,
            client_ip=get_client_ip(request),
            client_context=get_client_context(request)
        )

        return GrantConsentResponse(
            grant_id=grant_id,
            capability_token=capability_token
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grant failed: {str(e)}")


@router.post("/revoke", response_model=RevokeConsentResponse)
async def revoke_consent(
    request_data: RevokeConsentRequest,
    request: Request,
    service: ConsentService = Depends(get_consent_service)
):
    """
    Revoke consent grants and invalidate associated tokens.

    Can revoke by:
    - Specific grant_id
    - All grants for a service
    - All grants matching specific scopes
    - All grants for a user (if no filters provided)
    """
    try:
        # Convert to service request
        service_request = ConsentRevokeRequest(
            lid=request_data.lid,
            grant_id=request_data.grant_id,
            service=request_data.service,
            scopes=request_data.scopes,
            reason=request_data.reason
        )

        # Revoke consent
        revoked_count = await service.revoke_consent(
            service_request,
            client_ip=get_client_ip(request)
        )

        message = f"Successfully revoked {revoked_count} consent grant(s)"
        if revoked_count == 0:
            message = "No matching consent grants found to revoke"

        return RevokeConsentResponse(
            revoked_count=revoked_count,
            message=message
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revoke failed: {str(e)}")


@router.get("/ledger", response_model=LedgerResponse)
async def get_consent_ledger(
    lid: str,
    service: Optional[str] = None,
    active_only: bool = True,
    consent_service: ConsentService = Depends(get_consent_service)
):
    """
    Get human-readable consent ledger for Studio UI.

    Returns all consent grants with:
    - Service and scope details
    - Grant timing and usage statistics
    - Active capability token count
    - Revocation paths

    Used by LUKHAS Studio Connections page.
    """
    try:
        entries = await consent_service.get_consent_ledger(lid, service, active_only)

        return LedgerResponse(
            lid=lid,
            entries=entries,
            total_entries=len(entries)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger retrieval failed: {str(e)}")


@router.post("/escalate", response_model=EscalateResponse)
async def escalate_to_content(
    request_data: EscalateRequest,
    request: Request,
    service: ConsentService = Depends(get_consent_service)
):
    """
    Escalate from metadata-only to content access for specific resource.

    Creates narrow, short-lived capability for content access:
    - Max 30 minutes TTL
    - Specific resource ID only
    - Audit trail with escalation reason

    Used when user clicks on email thread, file, etc. in Studio.
    """
    try:
        capability_token = await service.escalate_to_content(
            lid=request_data.lid,
            service=request_data.service,
            resource_id=request_data.resource_id,
            purpose=request_data.purpose,
            ttl_minutes=request_data.ttl_minutes
        )

        return EscalateResponse(capability_token=capability_token)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Escalation failed: {str(e)}")


@router.post("/verify", response_model=VerifyTokenResponse)
async def verify_capability_token(
    request_data: VerifyTokenRequest,
    service: ConsentService = Depends(get_consent_service)
):
    """
    Verify capability token and check caveats.

    Used by service adapters to validate tokens before API access:
    - Checks macaroon signature and caveats
    - Validates scope permissions
    - Ensures token not expired/revoked
    - Records usage for audit trail

    Returns claims if valid, error if invalid.
    """
    try:
        claims = await service.verify_capability_token(
            token=request_data.token,
            required_scopes=request_data.required_scopes,
            resource_id=request_data.resource_id
        )

        return VerifyTokenResponse(
            valid=True,
            claims=claims
        )

    except Exception as e:
        return VerifyTokenResponse(
            valid=False,
            error=str(e)
        )


@router.get("/stats", response_model=ConsentStatsResponse)
async def get_consent_statistics(
    service: ConsentService = Depends(get_consent_service)
):
    """
    Get consent system statistics for monitoring and dashboards.

    Returns:
    - Active grant counts
    - Service usage statistics
    - Recent activity metrics
    - Performance statistics
    """
    try:
        # This would normally query the database for stats
        # For now, return mock data
        return ConsentStatsResponse(
            total_active_grants=42,
            total_services=6,
            recent_activity={
                "grants_last_24h": 15,
                "revokes_last_24h": 3,
                "token_verifications_last_24h": 148
            },
            performance_stats={
                "avg_grant_time_ms": 25.4,
                "p95_grant_time_ms": 45.2,
                "avg_verify_time_ms": 8.1,
                "p95_verify_time_ms": 15.8
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.post("/cleanup")
async def cleanup_expired_grants(
    service: ConsentService = Depends(get_consent_service)
):
    """
    Clean up expired grants and tokens.

    Admin endpoint for maintenance:
    - Updates expired grants to 'expired' status
    - Updates expired tokens to 'expired' status
    - Returns counts of cleaned up items
    """
    try:
        result = await service.cleanup_expired()

        return JSONResponse({
            "message": "Cleanup completed successfully",
            "expired_grants": result["expired_grants"],
            "expired_tokens": result["expired_tokens"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


# Health check and system info
@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "service": "LUKHAS Consent Fabric",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/info")
async def system_info():
    """System information endpoint"""
    return {
        "service": "LUKHAS Consent Fabric",
        "description": "Capability-based consent management with macaroon tokens",
        "features": [
            "Metadata-first consent",
            "Content escalation",
            "Macaroon capability tokens",
            "Comprehensive audit trails",
            "Revocation paths"
        ],
        "guardrails": [
            "No raw PII as usernames",
            "Short-lived least-privilege tokens",
            "Data minimization by default",
            "Complete audit trail"
        ],
        "endpoints": {
            "grant": "POST /consent/grant - Grant consent and issue token",
            "revoke": "POST /consent/revoke - Revoke consent and invalidate tokens",
            "ledger": "GET /consent/ledger - Get user's consent ledger",
            "escalate": "POST /consent/escalate - Escalate to content access",
            "verify": "POST /consent/verify - Verify capability token"
        }
    }


# Startup and shutdown event handlers
@router.on_event("startup")
async def startup_event():
    """Initialize consent service on startup"""
    global consent_service
    if consent_service is None:
        consent_service = ConsentService()
        await consent_service.initialize()
        print("🔐 LUKHAS Consent Fabric initialized")


@router.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global consent_service
    if consent_service:
        await consent_service.close()
        print("🔐 LUKHAS Consent Fabric shutdown")


# Example usage
async def demonstrate_consent_api():
    """Demonstrate consent API functionality"""
    print("🔗 LUKHAS Consent API Demonstration")
    print("=" * 40)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    # Create test app
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Test grant consent
    print("📝 Testing consent grant...")
    grant_response = client.post("/consent/grant", json={
        "lid": "gonzo",
        "service": "gmail",
        "scopes": ["email.read.headers"],
        "purpose": "Unified inbox display",
        "ttl_minutes": 120
    })
    print(f"Status: {grant_response.status_code}")
    if grant_response.status_code == 200:
        grant_data = grant_response.json()
        print(f"Grant ID: {grant_data['grant_id']}")

    # Test get ledger
    print("\n📋 Testing consent ledger...")
    ledger_response = client.get("/consent/ledger?lid=gonzo")
    print(f"Status: {ledger_response.status_code}")
    if ledger_response.status_code == 200:
        ledger_data = ledger_response.json()
        print(f"Total entries: {ledger_data['total_entries']}")

    # Test system info
    print("\n📊 Testing system info...")
    info_response = client.get("/consent/info")
    print(f"Status: {info_response.status_code}")
    if info_response.status_code == 200:
        info_data = info_response.json()
        print(f"Service: {info_data['service']}")

    print("\n✅ Consent API demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_consent_api())
