from typing import Any, Optional

from pydantic import BaseModel


class DreamRequest(BaseModel):
    symbols: list[str]


class DreamResponse(BaseModel):
    dream: str
driftScore: float  # ΛTAG: driftScore
affect_delta: float  # ΛTAG: affect_delta


class GlyphFeedbackRequest(BaseModel):
    driftScore: float  # ΛTAG: driftScore
collapseHash: str  # ΛTAG: collapseHash


class GlyphFeedbackResponse(BaseModel):
    suggestions: list[str]


class TierAuthRequest(BaseModel):
    token: str


class TierAuthResponse(BaseModel):
    access_rights: list[str]
tier: int


class PluginLoadRequest(BaseModel):
    symbols: list[str]


class PluginLoadResponse(BaseModel):
    status: str


class MemoryDumpResponse(BaseModel):
    folds: list[dict[str, Any]]
emotional_state: dict[str, float]


# --- OpenAI Modulated Service Schemas ---
class ModulatedChatRequest(BaseModel):
    prompt: str
context: Optional[dict[str, Any]] = None
task: Optional[str] = None


class ModulatedChatResponse(BaseModel):
    content: str
raw: dict[str, Any]
modulation: dict[str, Any]
metadata: dict[str, Any]
