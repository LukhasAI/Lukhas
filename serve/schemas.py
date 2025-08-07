from typing import List, Dict, Any
from pydantic import BaseModel


class DreamRequest(BaseModel):
    symbols: List[str]


class DreamResponse(BaseModel):
    dream: str
    driftScore: float  # ΛTAG: driftScore
    affect_delta: float  # ΛTAG: affect_delta


class GlyphFeedbackRequest(BaseModel):
    driftScore: float  # ΛTAG: driftScore
    collapseHash: str  # ΛTAG: collapseHash


class GlyphFeedbackResponse(BaseModel):
    suggestions: List[str]


class TierAuthRequest(BaseModel):
    token: str


class TierAuthResponse(BaseModel):
    access_rights: List[str]
    tier: int


class PluginLoadRequest(BaseModel):
    symbols: List[str]


class PluginLoadResponse(BaseModel):
    status: str


class MemoryDumpResponse(BaseModel):
    folds: List[Dict[str, Any]]
    emotional_state: Dict[str, float]
