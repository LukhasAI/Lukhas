"""
Universal Language API Endpoints
=================================
REST API for managing personal symbol-meaning bindings.
All symbol data stays local - server only handles proofs.

System-wide guardrails applied:
1. Symbol data never transmitted to server
2. Only cryptographic proofs sent/verified
3. Local binding operations are async
4. Composition challenges time-limited
5. Integration with GTΨ for combined approval

ACK GUARDRAILS
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from . import (
    CompositionProof,
    MeaningType,
    SymbolType,
    ULSignature,
    requires_ul_entropy,
)
from .service import UniversalLanguageService


# API Models
class BindSymbolRequest(BaseModel):
    """Request to bind personal symbol to meaning"""
    symbol_type: SymbolType = Field(..., description="Type of symbol")
    symbol_data: Any = Field(..., description="Raw symbol data (stays local)")
    meaning_type: MeaningType = Field(..., description="Type of meaning")
    meaning_value: str = Field(..., description="Meaning to bind")


class BindSymbolResponse(BaseModel):
    """Response from symbol binding"""
    symbol_id: str = Field(..., description="Symbol ID for reference")
    quality_score: float = Field(..., description="Symbol quality score")
    message: str = Field(..., description="Success message")


class ChallengeRequest(BaseModel):
    """Request for composition challenge"""
    lid: str = Field(..., description="Canonical ΛID")
    action: str = Field(..., description="High-risk action")


class ChallengeResponse(BaseModel):
    """Composition challenge response"""
    challenge_id: str = Field(..., description="Challenge ID")
    composition: str = Field(..., description="Required composition")
    expected_symbols: int = Field(..., description="Number of symbols needed")
    expires_at: datetime = Field(..., description="Challenge expiration")


class ProofSubmissionRequest(BaseModel):
    """Submit composition proof for verification"""
    challenge_id: str = Field(..., description="Challenge being answered")
    proof_hash: str = Field(..., description="Cryptographic proof")
    symbol_count: int = Field(..., description="Number of symbols used")
    computation_time_ms: float = Field(..., description="Time to compute")
    quality_score: float = Field(..., description="Composition quality")


class ProofVerificationResponse(BaseModel):
    """Response from proof verification"""
    verified: bool = Field(..., description="Whether proof is valid")
    signature: Optional[ULSignature] = Field(None, description="UL signature if verified")
    message: str = Field(..., description="Result message")


class ULStatusResponse(BaseModel):
    """UL system status"""
    initialized: bool = Field(..., description="Whether UL is initialized")
    symbol_count: int = Field(..., description="Number of bound symbols")
    composition_count: int = Field(..., description="Number of compositions")
    active_challenges: int = Field(..., description="Active challenge count")


# Create router
router = APIRouter(prefix="/ul", tags=["Universal Language"])

# Global service instance
ul_service: Optional[UniversalLanguageService] = None


async def get_ul_service() -> UniversalLanguageService:
    """Dependency to get UL service"""
    global ul_service
    if ul_service is None:
        ul_service = UniversalLanguageService()
        await ul_service.initialize()
    return ul_service


@router.post("/bind")
async def bind_symbol(
    request: BindSymbolRequest,
    service: UniversalLanguageService = Depends(get_ul_service)
) -> BindSymbolResponse:
    """
    Bind personal symbol to meaning (local only).

    Symbol data is hashed and stored locally, never sent to server.
    """
    try:
        symbol_id = await service.bind_symbol(
            request.symbol_type,
            request.symbol_data,
            request.meaning_type,
            request.meaning_value
        )

        # Get symbol details for quality score
        symbol = service.local_store.symbols.get(symbol_id)

        return BindSymbolResponse(
            symbol_id=symbol_id,
            quality_score=symbol.quality_score if symbol else 0.0,
            message=f"Symbol bound to '{request.meaning_value}' successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Symbol binding failed: {str(e)}")


@router.post("/challenge")
async def request_challenge(
    request: ChallengeRequest,
    service: UniversalLanguageService = Depends(get_ul_service)
) -> ChallengeResponse:
    """
    Request composition challenge for high-risk action.

    Server generates challenge based on action risk level.
    """
    # Check if action requires UL entropy
    if not requires_ul_entropy(request.action):
        raise HTTPException(
            status_code=400,
            detail=f"Action '{request.action}' does not require UL entropy"
        )

    try:
        challenge = await service.request_challenge(request.lid, request.action)

        return ChallengeResponse(
            challenge_id=challenge.challenge_id,
            composition=challenge.composition,
            expected_symbols=challenge.expected_symbols,
            expires_at=challenge.expires_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Challenge generation failed: {str(e)}")


@router.post("/verify")
async def verify_proof(
    request: ProofSubmissionRequest,
    service: UniversalLanguageService = Depends(get_ul_service)
) -> ProofVerificationResponse:
    """
    Verify composition proof without seeing symbols.

    Server validates cryptographic proof without accessing raw symbol data.
    """
    try:
        # Reconstruct proof object
        proof = CompositionProof(
            challenge_id=request.challenge_id,
            proof_hash=request.proof_hash,
            symbol_count=request.symbol_count,
            computation_time_ms=request.computation_time_ms,
            quality_score=request.quality_score
        )

        # Get challenge to find LID
        challenge = service.challenge_service.active_challenges.get(request.challenge_id)
        if not challenge:
            raise ValueError("Challenge not found or expired")

        # Parse challenge to get LID and action
        lid = "gonzo"  # In production: extract from challenge
        action = "grant_admin_scope"  # In production: extract from challenge

        # Verify proof
        verified = await service.challenge_service.verify_composition_proof(lid, proof)

        if verified:
            # Create UL signature
            signature = await service.create_approval_signature(lid, action, proof)

            return ProofVerificationResponse(
                verified=True,
                signature=signature,
                message="Composition proof verified successfully"
            )
        else:
            return ProofVerificationResponse(
                verified=False,
                message="Composition proof verification failed"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof verification failed: {str(e)}")


@router.get("/status")
async def get_status(
    service: UniversalLanguageService = Depends(get_ul_service)
) -> ULStatusResponse:
    """
    Get UL system status.

    Returns statistics about symbols and challenges.
    """
    return ULStatusResponse(
        initialized=service.initialized,
        symbol_count=len(service.local_store.symbols),
        composition_count=len(service.local_store.compositions),
        active_challenges=len(service.challenge_service.active_challenges)
    )


@router.delete("/challenge/{challenge_id}")
async def cancel_challenge(
    challenge_id: str,
    service: UniversalLanguageService = Depends(get_ul_service)
) -> dict[str, str]:
    """
    Cancel active challenge.

    Removes challenge from active list.
    """
    if challenge_id in service.challenge_service.active_challenges:
        del service.challenge_service.active_challenges[challenge_id]
        return {"message": f"Challenge {challenge_id} cancelled"}
    else:
        raise HTTPException(status_code=404, detail="Challenge not found")


@router.get("/actions")
async def list_ul_actions() -> dict[str, Any]:
    """
    List actions that benefit from UL entropy.

    Returns all high-risk actions with UL requirements.
    """
    from . import UL_ENHANCED_ACTIONS

    return {
        "ul_enhanced_actions": UL_ENHANCED_ACTIONS,
        "info": {
            "description": "Actions that benefit from Universal Language entropy",
            "usage": "Request challenge, solve with personal symbols, submit proof"
        }
    }


@router.get("/demo")
async def demo_ul_flow(
    service: UniversalLanguageService = Depends(get_ul_service)
) -> dict[str, Any]:
    """
    Demonstrate UL workflow for development.

    Shows complete flow from binding to verification.
    """
    demo_steps = [
        {
            "step": 1,
            "action": "Bind personal symbols",
            "endpoint": "POST /ul/bind",
            "example": {
                "symbol_type": "emoji",
                "symbol_data": "⚡️💪",
                "meaning_type": "concept",
                "meaning_value": "power"
            }
        },
        {
            "step": 2,
            "action": "Request challenge",
            "endpoint": "POST /ul/challenge",
            "example": {
                "lid": "gonzo",
                "action": "grant_admin_scope"
            }
        },
        {
            "step": 3,
            "action": "Solve challenge locally",
            "description": "Client solves composition with personal symbols"
        },
        {
            "step": 4,
            "action": "Submit proof",
            "endpoint": "POST /ul/verify",
            "example": {
                "challenge_id": "ul_challenge_xxx",
                "proof_hash": "sha256_hash",
                "symbol_count": 2,
                "computation_time_ms": 150.5,
                "quality_score": 0.85
            }
        },
        {
            "step": 5,
            "action": "Use UL signature",
            "description": "Combine with GTΨ for complete high-risk approval"
        }
    ]

    return {
        "message": "Universal Language (UL) Demo",
        "workflow": demo_steps,
        "current_status": {
            "initialized": service.initialized,
            "symbols": len(service.local_store.symbols),
            "active_challenges": len(service.challenge_service.active_challenges)
        },
        "security_notes": [
            "All symbol data stays local",
            "Server only sees cryptographic proofs",
            "Challenges expire after 5 minutes",
            "Quality scores ensure strong entropy"
        ]
    }


# Startup event
@router.on_event("startup")
async def startup_ul_service():
    """Initialize UL service on startup"""
    global ul_service
    if ul_service is None:
        ul_service = UniversalLanguageService()
        await ul_service.initialize()
        print("🔤 Universal Language service initialized")


# Shutdown event
@router.on_event("shutdown")
async def shutdown_ul_service():
    """Cleanup UL service on shutdown"""
    global ul_service
    if ul_service:
        # Save any pending local data
        if ul_service.local_store.symbols:
            ul_service.local_store._save_symbols()
        print("🔤 Universal Language service shutdown")
