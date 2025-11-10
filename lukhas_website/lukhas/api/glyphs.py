"""
LUKHAS GLYPH API Endpoints
===========================

Production API routes for GLYPH symbolic communication and binding.
All endpoints are feature-flag gated (LUKHAS_GLYPHS_ENABLED).

Endpoints:
- POST /api/v1/glyphs/encode - Encode a concept into a GLYPH
- POST /api/v1/glyphs/bind - Bind a GLYPH to a memory
- GET /api/v1/glyphs/bindings/{binding_id} - Retrieve binding
- POST /api/v1/glyphs/validate - Validate GLYPH data structure
- GET /api/v1/glyphs/stats - Get GLYPH subsystem statistics
"""
import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# Import wrapper module
try:
    from lukhas.glyphs import (
        is_enabled,
        encode_concept,
        bind_glyph,
        get_binding,
        validate_glyph,
        get_glyph_stats,
    )
    GLYPHS_WRAPPER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Glyphs wrapper unavailable: {e}")
    GLYPHS_WRAPPER_AVAILABLE = False


# Pydantic models for request/response validation
class GlyphEncodeRequest(BaseModel):
    """Request model for GLYPH encoding"""
    concept: str = Field(..., min_length=1, max_length=1000, description="Concept to encode")
    emotion: Optional[dict[str, float]] = Field(default=None, description="Emotional context (0.0-1.0)")
    modalities: Optional[list[str]] = Field(default=None, description="Symbol modalities")
    domains: Optional[list[str]] = Field(default=None, description="Symbol domains")
    source_module: Optional[str] = Field(default=None, max_length=100, description="Source module name")

    @validator('emotion')
    def validate_emotion(cls, v):
        if v is not None:
            for key, value in v.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Emotion value '{key}' must be numeric")
                if not (0.0 <= value <= 1.0):
                    raise ValueError(f"Emotion value '{key}' must be between 0.0 and 1.0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "concept": "morning_gratitude",
                "emotion": {"joy": 0.8, "calm": 0.6},
                "source_module": "daily_reflection"
            }
        }


class GlyphEncodeResponse(BaseModel):
    """Response model for GLYPH encoding"""
    success: bool
    symbol: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class GlyphBindRequest(BaseModel):
    """Request model for GLYPH binding"""
    glyph_data: dict[str, Any] = Field(..., description="GLYPH data to bind")
    memory_id: str = Field(..., min_length=1, max_length=100, description="Target memory identifier")
    user_id: Optional[str] = Field(default=None, max_length=100, description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "glyph_data": {
                    "concept": "important_insight",
                    "emotion": {"joy": 0.7}
                },
                "memory_id": "mem_abc123",
                "user_id": "user_xyz"
            }
        }


class GlyphBindResponse(BaseModel):
    """Response model for GLYPH binding"""
    success: bool
    binding_id: Optional[str] = None
    glyph_data: Optional[dict[str, Any]] = None
    memory_id: Optional[str] = None
    error: Optional[str] = None


class GlyphValidateRequest(BaseModel):
    """Request model for GLYPH validation"""
    glyph_data: dict[str, Any] = Field(..., description="GLYPH data to validate")


class GlyphValidateResponse(BaseModel):
    """Response model for GLYPH validation"""
    valid: bool
    error: Optional[str] = None


# Create router
router = APIRouter(
    prefix="/api/v1/glyphs",
    tags=["GLYPHs"],
)


@router.post("/encode", response_model=GlyphEncodeResponse, status_code=status.HTTP_200_OK)
async def encode_glyph_concept(request: GlyphEncodeRequest) -> GlyphEncodeResponse:
    """
    Encode a concept into a Universal Symbol GLYPH.

    Requires: LUKHAS_GLYPHS_ENABLED=1

    Returns symbol data with modalities and domains.
    """
    if not GLYPHS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPHs wrapper module unavailable"
        )

    if not is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPH subsystem not enabled. Set LUKHAS_GLYPHS_ENABLED=1"
        )

    try:
        symbol = encode_concept(
            concept=request.concept,
            emotion=request.emotion,
            modalities=set(request.modalities) if request.modalities else None,
            domains=set(request.domains) if request.domains else None,
            source_module=request.source_module
        )

        if symbol is None:
            return GlyphEncodeResponse(
                success=False,
                error="Failed to encode concept"
            )

        return GlyphEncodeResponse(
            success=True,
            symbol=symbol
        )

    except Exception as e:
        logger.error(f"Error encoding GLYPH: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GLYPH encoding failed: {str(e)}"
        )


@router.post("/bind", response_model=GlyphBindResponse, status_code=status.HTTP_201_CREATED)
async def bind_glyph_to_memory(
    request: GlyphBindRequest,
    authorization: Optional[str] = Header(default=None, description="Bearer token")
) -> GlyphBindResponse:
    """
    Bind a GLYPH to a memory with authorization and safety checks.

    Requires: LUKHAS_GLYPHS_ENABLED=1
    Authorization: Optional Bearer token in Authorization header

    Returns binding_id for later retrieval.
    """
    if not GLYPHS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPHs wrapper module unavailable"
        )

    if not is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPH subsystem not enabled. Set LUKHAS_GLYPHS_ENABLED=1"
        )

    # Validate GLYPH data first
    is_valid, error_msg = validate_glyph(request.glyph_data)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GLYPH data: {error_msg}"
        )

    # Extract token from Authorization header if present
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    try:
        result = bind_glyph(
            glyph_data=request.glyph_data,
            memory_id=request.memory_id,
            user_id=request.user_id,
            token=token
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Binding failed")
            )

        return GlyphBindResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error binding GLYPH: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GLYPH binding failed: {str(e)}"
        )


@router.get("/bindings/{binding_id}", status_code=status.HTTP_200_OK)
async def get_glyph_binding(binding_id: str) -> dict[str, Any]:
    """
    Retrieve a GLYPH binding by its ID.

    Requires: LUKHAS_GLYPHS_ENABLED=1

    Returns binding data if found, 404 otherwise.
    """
    if not GLYPHS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPHs wrapper module unavailable"
        )

    if not is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPH subsystem not enabled. Set LUKHAS_GLYPHS_ENABLED=1"
        )

    try:
        binding = get_binding(binding_id)

        if binding is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Binding not found: {binding_id}"
            )

        return binding

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving binding {binding_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve binding: {str(e)}"
        )


@router.post("/validate", response_model=GlyphValidateResponse, status_code=status.HTTP_200_OK)
async def validate_glyph_data(request: GlyphValidateRequest) -> GlyphValidateResponse:
    """
    Validate GLYPH data structure and content.

    Does NOT require LUKHAS_GLYPHS_ENABLED (validation always available).

    Returns validation result and error message if invalid.
    """
    try:
        is_valid, error_msg = validate_glyph(request.glyph_data)

        return GlyphValidateResponse(
            valid=is_valid,
            error=error_msg
        )

    except Exception as e:
        logger.error(f"Error validating GLYPH: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats() -> dict[str, Any]:
    """
    Get GLYPH subsystem statistics.

    Requires: LUKHAS_GLYPHS_ENABLED=1

    Returns stats including glyphs created, symbols translated, etc.
    """
    if not GLYPHS_WRAPPER_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPHs wrapper module unavailable"
        )

    if not is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GLYPH subsystem not enabled. Set LUKHAS_GLYPHS_ENABLED=1"
        )

    try:
        stats = get_glyph_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting GLYPH stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for GLYPHs subsystem.

    Returns subsystem status and feature flags.
    """
    return {
        "service": "glyphs",
        "wrapper_available": GLYPHS_WRAPPER_AVAILABLE,
        "enabled": is_enabled() if GLYPHS_WRAPPER_AVAILABLE else False,
        "version": "0.1.0-alpha"
    }
