# path: qi/glyphs/signer_service.py
"""
LUKHAS AI GLYPH Signer Service

Production-ready FastAPI microservice for creating cryptographic seals.
Designed for deployment behind KMS/HSM for key management.
"""
from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .seal import GlyphSigner, HSMSigner, policy_fingerprint_from_files


# Request/Response Models
class SealRequest(BaseModel):
    """Request to create a GLYPH seal"""
    content_hash: str = Field(..., description="SHA3-512 hash of content (hex)")
    media_type: str = Field(..., description="MIME type of content")
    issuer: str = Field(..., description="Issuer ID (lukhas://org/<tenant>)")
    model_id: str = Field(..., description="Model identifier")
    policy_fingerprint: str | None = Field(None, description="Policy fingerprint (auto-computed if not provided)")
    jurisdiction: str = Field("global", description="Jurisdiction")
    proof_bundle: str = Field(..., description="URL to proof bundle")
    ttl_days: int = Field(365, description="Seal validity in days", ge=1, le=3650)
    calib_ref: dict[str, float] | None = Field(None, description="Calibration reference")
    prev: str | None = Field(None, description="Previous seal ID for chaining")

class SealResponse(BaseModel):
    """Response containing created seal"""
    seal: dict[str, Any]
    signature: dict[str, Any]
    compact: str = Field(..., description="Base64 compact representation for QR codes")
    qr_data: str = Field(..., description="QR-ready data")
    public_key: str = Field(..., description="Base64 public key for verification")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: float
    key_id: str
    capabilities: list[str]

class JWKSResponse(BaseModel):
    """JWKS endpoint response"""
    keys: list[dict[str, Any]]

# Configuration
SIGNER_CONFIG = {
    "issuer_whitelist": os.environ.get("GLYPH_ISSUER_WHITELIST", "lukhas://org/lukhas-ai").split(","),
    "require_auth": os.environ.get("GLYPH_REQUIRE_AUTH", "false").lower() == "true",
    "auth_token": os.environ.get("GLYPH_AUTH_TOKEN"),
    "hsm_config": {
        "enabled": os.environ.get("GLYPH_HSM_ENABLED", "false").lower() == "true",
        "key_id": os.environ.get("GLYPH_HSM_KEY_ID", "prod-hsm-001"),
        "provider": os.environ.get("GLYPH_HSM_PROVIDER", "aws-kms")
    },
    "policy_root": os.environ.get("GLYPH_POLICY_ROOT", "qi/safety/policy_packs/global"),
    "policy_overlays": os.environ.get("GLYPH_POLICY_OVERLAYS", "qi/risk")
}

# Global signer instance
_signer: GlyphSigner | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize signer on startup"""
    global _signer

    if SIGNER_CONFIG["hsm_config"]["enabled"]:
        _signer = HSMSigner(SIGNER_CONFIG["hsm_config"])
    else:
        _signer = GlyphSigner(key_id="dev-key-001")

    yield

    # Cleanup if needed
    _signer = None

# FastAPI app
app = FastAPI(
    title="LUKHAS AI GLYPH Signer Service",
    description="Cryptographic seal creation for AI artifacts",
    version="0.1.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer(auto_error=False)

async def verify_auth(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify authentication token if required"""
    if not SIGNER_CONFIG["require_auth"]:
        return True

    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    expected_token = SIGNER_CONFIG["auth_token"]
    if not expected_token or credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    return True

def validate_issuer(issuer: str) -> bool:
    """Validate issuer against whitelist"""
    whitelist = SIGNER_CONFIG["issuer_whitelist"]
    return any(issuer.startswith(allowed) for allowed in whitelist)

# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global _signer

    capabilities = ["seal_creation", "ed25519_signing"]
    if SIGNER_CONFIG["hsm_config"]["enabled"]:
        capabilities.append("hsm_signing")

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=time.time(),
        key_id=_signer.key_id if _signer else "none",
        capabilities=capabilities
    )

@app.get("/.well-known/jwks.json", response_model=JWKSResponse)
async def get_jwks():
    """JWKS endpoint for public key distribution"""
    global _signer

    if not _signer:
        raise HTTPException(status_code=503, detail="Signer not initialized")

    # Create JWK for current key
    public_key_b64 = _signer.get_public_key()

    jwk = {
        "kty": "OKP",  # Octet Key Pair
        "crv": "Ed25519",
        "use": "sig",
        "kid": _signer.key_id,
        "x": public_key_b64,
        "alg": "EdDSA"
    }

    return JWKSResponse(keys=[jwk])

@app.post("/seal", response_model=SealResponse)
async def create_seal(
    request: SealRequest,
    _: bool = Depends(verify_auth)
):
    """
    Create a cryptographic GLYPH seal.

    This endpoint creates a cryptographically sealed attestation for an AI artifact.
    The content hash should be pre-computed by the client to avoid transmitting
    sensitive content to the signing service.
    """
    global _signer

    if not _signer:
        raise HTTPException(status_code=503, detail="Signer service not available")

    # Validate issuer
    if not validate_issuer(request.issuer):
        raise HTTPException(
            status_code=403,
            detail=f"Issuer not authorized: {request.issuer}"
        )

    # Validate content hash format
    if not request.content_hash.startswith("sha3-512:"):
        raise HTTPException(
            status_code=400,
            detail="content_hash must be SHA3-512 in format 'sha3-512:<hex>'"
        )

    try:
        # Compute policy fingerprint if not provided
        policy_fp = request.policy_fingerprint
        if not policy_fp:
            policy_fp = policy_fingerprint_from_files(
                SIGNER_CONFIG["policy_root"],
                SIGNER_CONFIG["policy_overlays"]
            )

        # Create mock content bytes from hash for signing
        # In practice, the signer service never sees the original content
        content_hash_hex = request.content_hash.split(":", 1)[1]
        mock_content = bytes.fromhex(content_hash_hex)

        # Create seal using signer
        result = _signer.create_seal(
            content_bytes=mock_content,  # This is just the hash, not real content
            media_type=request.media_type,
            issuer=request.issuer,
            model_id=request.model_id,
            policy_fingerprint=policy_fp,
            jurisdiction=request.jurisdiction,
            proof_bundle=request.proof_bundle,
            ttl_days=request.ttl_days,
            calib_ref=request.calib_ref,
            prev=request.prev
        )

        # Override the content_hash in the seal with the provided one
        # (since we used mock content for signing)
        result["seal"]["content_hash"] = request.content_hash

        return SealResponse(
            seal=result["seal"],
            signature=result["signature"],
            compact=result["compact"],
            qr_data=result["compact"],  # Same as compact for now
            public_key=_signer.get_public_key()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seal creation failed: {str(e)}")

@app.post("/seal/batch")
async def create_seal_batch(
    requests: list[SealRequest],
    _: bool = Depends(verify_auth)
):
    """Create multiple seals in a batch operation"""
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="Batch size limited to 100 seals")

    results = []
    errors = []

    for i, request in enumerate(requests):
        try:
            result = await create_seal(request, _)
            results.append({"index": i, "seal": result})
        except HTTPException as e:
            errors.append({"index": i, "error": e.detail, "status": e.status_code})
        except Exception as e:
            errors.append({"index": i, "error": str(e), "status": 500})

    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

@app.get("/policy/fingerprint")
async def get_policy_fingerprint():
    """Get current policy fingerprint"""
    try:
        fingerprint = policy_fingerprint_from_files(
            SIGNER_CONFIG["policy_root"],
            SIGNER_CONFIG["policy_overlays"]
        )
        return {
            "policy_fingerprint": fingerprint,
            "policy_root": SIGNER_CONFIG["policy_root"],
            "policy_overlays": SIGNER_CONFIG["policy_overlays"],
            "computed_at": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy fingerprint computation failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "LUKHAS AI GLYPH Signer",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "jwks": "/.well-known/jwks.json",
            "seal": "/seal",
            "batch": "/seal/batch",
            "policy": "/policy/fingerprint"
        },
        "documentation": "/docs"
    }

# For development/testing
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("GLYPH_PORT", "8080"))
    host = os.environ.get("GLYPH_HOST", "127.0.0.1")

    uvicorn.run(
        "qi.glyphs.signer_service:app",
        host=host,
        port=port,
        reload=bool(os.environ.get("GLYPH_DEBUG"))
    )
