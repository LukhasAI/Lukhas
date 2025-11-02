"""
Audit trail data models for LUKHAS decision traces.
All models are Pydantic for validation and JSON serialization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DecisionTrace(BaseModel):
    """Complete decision trace with timing and outcome metadata."""

    trace_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    input_hash: str
    started_at: float
    finished_at: float
    latency_ms: int
    final_outcome: Dict[str, Any]
    confidence: float = 0.0
    policy_version: str = "v1"
    git_sha: str = "unknown"


class TraceSpan(BaseModel):
    """Individual operation span within a trace."""

    span_id: str
    trace_id: str
    module: str  # e.g., "Intent" | "Memory" | "Ethics" | "Action"
    operation: str  # e.g., "analyze" | "retrieve" | "guard" | "execute"
    parent_span_id: Optional[str] = None
    ts_start: float
    ts_end: float
    status: str = "OK"
    error: Optional[str] = None


class EvidenceLink(BaseModel):
    """Link to evidence source with consent metadata."""

    span_id: str
    source_type: str  # "qrg" | "glymps" | "memory" | "api" | "doc"
    uri_or_key: str
    sha256: str
    excerpt: Optional[str] = None
    consent_scope: str = "default"  # per ΛID policy
    pii_tags: List[str] = Field(default_factory=list)
    redacted: bool = False


class GovernanceEvent(BaseModel):
    """Governance decision event for audit trail."""

    event_id: str
    trace_id: str
    rule_id: str
    decision: str  # ALLOW | DENY | REDACT | WARN
    justification: str
    feature_flags_snapshot: Dict[str, Any] = Field(default_factory=dict)


class FeedbackEvent(BaseModel):
    """User feedback event linked to trace."""

    feedback_id: str
    trace_id: str
    rating_0_10: int
    text: str
    labels: Dict[str, float] = Field(default_factory=dict)  # taxonomy → weight
    sentiment: Optional[str] = None
    followup_state: Dict[str, Any] = Field(default_factory=dict)
