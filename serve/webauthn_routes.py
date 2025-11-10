"""Minimal WebAuthn API endpoints backed by the core adapter stub."""

from __future__ import annotations

from core.identity.adapters import webauthn_adapter
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

# ΛTAG: webauthn_routes

router = APIRouter()


class ChallengeRequest(BaseModel):
    """Request payload for starting a WebAuthn challenge."""

    user_id: str = Field(..., min_length=1, description="Canonical user identifier")
    rp_id: str = Field(..., min_length=1, description="Relying party identifier")
    origin: str = Field(..., min_length=1, description="Origin expected by the client")

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class VerifyRequest(BaseModel):
    """Request payload for verifying a WebAuthn response."""

    response: dict[str, object] = Field(..., description="Client-provided assertion payload")
    expected_challenge: str | None = Field(
        default=None,
        description="Optional challenge to enforce deterministic matching",
    )

    model_config = ConfigDict(extra="forbid")


@router.post("/id/webauthn/challenge")
async def create_challenge(payload: ChallengeRequest) -> dict[str, object]:
    """Generate deterministic PublicKeyCredentialRequestOptions."""

    try:
        options = webauthn_adapter.start_challenge(
            user_id=payload.user_id,
            rp_id=payload.rp_id,
            origin=payload.origin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return options


@router.post("/id/webauthn/verify")
async def verify_response(payload: VerifyRequest) -> dict[str, object]:
    """Verify a deterministic WebAuthn response."""

    try:
        result = webauthn_adapter.verify_response(
            response=dict(payload.response),
            expected_challenge=payload.expected_challenge,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # ΛTAG: webauthn_routes_result
    return {
        "ok": bool(result.get("ok")),
        "user_verified": bool(result.get("user_verified")),
    }
