"""FastAPI routes exposing core Lukhas capabilities"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from config.config import TIER_PERMISSIONS
from .schemas import (
    DreamRequest,
    DreamResponse,
    GlyphFeedbackRequest,
    GlyphFeedbackResponse,
    TierAuthRequest,
    TierAuthResponse,
    PluginLoadRequest,
    PluginLoadResponse,
    MemoryDumpResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

TOKEN_TIER_MAP = {
    "symbolic-tier-1": 1,
    "symbolic-tier-3": 3,
    "symbolic-tier-5": 5,
}
# ΛLOCKED


def compute_drift_score(symbols: List[str]) -> float:
    """Compute drift score from symbols"""
    # TODO: integrate real drift computation
    return len(symbols) / 10.0


def compute_affect_delta(symbols: List[str]) -> float:
    """Compute affect delta from symbols"""
    # TODO: integrate affect delta engine
    return len(symbols) * 0.1


@router.post("/generate-dream/", response_model=DreamResponse)
async def generate_dream(req: DreamRequest) -> DreamResponse:
    """Generate a symbolic dream"""
    drift_score = compute_drift_score(req.symbols)
    # ΛTAG: driftScore
    affect_delta = compute_affect_delta(req.symbols)
    # ΛTAG: affect_delta
    logger.info(
        "Generating dream",
        extra={"driftScore": drift_score, "affect_delta": affect_delta},
    )
    # TODO: replace with real dream engine logic
    dream = " ".join(req.symbols[::-1])
    return DreamResponse(
        dream=dream, driftScore=drift_score, affect_delta=affect_delta
    )


@router.post("/glyph-feedback/", response_model=GlyphFeedbackResponse)
async def glyph_feedback(req: GlyphFeedbackRequest) -> GlyphFeedbackResponse:
    """Provide glyph adjustment suggestions"""
    # ΛTAG: driftScore
    # ΛTAG: collapseHash
    logger.info(
        "Glyph feedback request",
        extra={"driftScore": req.driftScore, "collapseHash": req.collapseHash},
    )
    # TODO: implement feedback algorithm
    suggestions = [
        f"Adjust symbol intensity by {req.driftScore}",
        "Re-align glyph sequence",
    ]
    return GlyphFeedbackResponse(suggestions=suggestions)


@router.post("/tier-auth/", response_model=TierAuthResponse)
async def tier_auth(req: TierAuthRequest) -> TierAuthResponse:
    """Resolve symbolic token to access rights"""
    tier = TOKEN_TIER_MAP.get(req.token)
    if tier is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    rights = TIER_PERMISSIONS.get(tier, [])
    return TierAuthResponse(access_rights=rights, tier=tier)


@router.post("/plugin-load/", response_model=PluginLoadResponse)
async def plugin_load(req: PluginLoadRequest) -> PluginLoadResponse:
    """Register plugin symbols"""
    logger.info("Loading plugins", extra={"plugins": req.symbols})
    # TODO: persist plugin registration
    return PluginLoadResponse(status="loaded")


@router.get("/memory-dump/", response_model=MemoryDumpResponse)
async def memory_dump() -> MemoryDumpResponse:
    """Export symbolic folds and emotional state"""
    folds = [{"id": "mem001", "content": "placeholder"}]
    affect_delta = 0.0
    # ΛTAG: affect_delta
    logger.info(
        "Memory dump", extra={"folds": len(folds), "affect_delta": affect_delta}
    )
    # TODO: connect to memory subsystem
    emotional_state = {"affect_delta": affect_delta}
    return MemoryDumpResponse(folds=folds, emotional_state=emotional_state)
