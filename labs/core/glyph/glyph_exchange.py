"""Glyph Exchange API for LUKHAS.

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

This module exposes FastAPI endpoints to export and import symbolic GLYPHs
and to receive compressed dream tags from external systems.
"""

from __future__ import annotations

import base64
import json
import logging
import zlib
from datetime import datetime, timezone
from typing import Any

from core.glyph.glyph_memory_integration import get_glyph_memory_system
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from symbolic.features.glyphs import GLYPH_MAP

logger = logging.getLogger("api.glyph_exchange")

router = APIRouter(prefix="/glyph", tags=["glyph"])


class GlyphImportItem(BaseModel):
    glyph: str = Field(..., description="Unicode glyph symbol")
    meaning: str | None = Field(None, description="Optional glyph meaning")


class GlyphImportRequest(BaseModel):
    glyphs: list[GlyphImportItem]
    user_id: str = Field(..., description="ID of importing system")


class CompressedDreamTagRequest(BaseModel):
    compressed_data: str = Field(..., description="Base64-encoded zlib-compressed dream tag payload")
    activate_glyphs: bool = Field(True, description="Whether to activate glyphs during processing")


class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    data: Any = Field(..., description="Response data")
    message: str | None = Field(None, description="Optional message")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


GlyphImportItem.model_rebuild()
GlyphImportRequest.model_rebuild()
CompressedDreamTagRequest.model_rebuild()
APIResponse.model_rebuild()


@router.get("/export", response_model=APIResponse)
async def export_glyphs(limit: int = 100) -> APIResponse:
    """Export registered glyphs and usage counts."""
    system = get_glyph_memory_system()
    glyph_counts: dict[str, int] = {g: len(folds) for g, folds in system.glyph_index.glyph_to_folds.items()}
    sorted_glyphs = sorted(glyph_counts.items(), key=lambda x: x[1], reverse=True)
    export_list = [{"glyph": g, "count": c, "meaning": GLYPH_MAP.get(g)} for g, c in sorted_glyphs[:limit]]
    return APIResponse(status="success", data=export_list, message="glyph_export")


@router.post("/import", response_model=APIResponse)
async def import_glyphs(request: GlyphImportRequest) -> APIResponse:
    """Import new glyphs into the system."""
    imported = []
    for item in request.glyphs:
        if item.glyph not in GLYPH_MAP and item.meaning:
            GLYPH_MAP[item.glyph] = item.meaning
            imported.append(item.glyph)
    msg = f"Imported {len(imported)} new glyphs" if imported else "No new glyphs"
    logger.info("Glyph import by %s: %s", request.user_id, imported)
    return APIResponse(status="success", data={"imported": imported}, message=msg)


@router.post("/dream-tags", response_model=APIResponse)
async def submit_compressed_dream_tags(
    request: CompressedDreamTagRequest,
) -> APIResponse:
    """Receive compressed dream tags and integrate them."""
    try:
        raw = base64.b64decode(request.compressed_data)
        payload_json = zlib.decompress(raw).decode()
        dream_data = json.loads(payload_json)
    except Exception as exc:
        logger.error("Failed to decode dream tags: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid compressed data")

    system = get_glyph_memory_system()
    result = system.dream_bridge.process_dream_state(dream_data, activate_glyphs=request.activate_glyphs)

    return APIResponse(status="success", data=result, message="dream_tags_processed")
