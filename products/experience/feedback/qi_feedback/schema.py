# path: qi/feedback/schema.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, validator
from qi.safety.constants import ALLOWED_STYLES, MAX_THRESHOLD_SHIFT


class FeedbackContext(BaseModel):
    """Context information for the feedback."""

    task: str = Field(..., description="Task type (e.g., summarize, classify)")
    jurisdiction: str = Field(..., description="Jurisdiction (e.g., eu, us, global)")
    policy_pack: str = Field(..., description="Policy pack version")
    model_version: str = Field(..., description="Model version")


class FeedbackData(BaseModel):
    """User feedback data."""

    satisfaction: float = Field(..., ge=0.0, le=1.0, description="Satisfaction score 0-1")
    issues: list[str] = Field(default_factory=list, description="List of issue types")
    note_hash: str | None = Field(None, description="HMAC hash of user note")


class ProposedTuning(BaseModel):
    """Proposed tuning parameters."""

    style: str | None = Field(None, description="Proposed style")
    threshold_delta: float | None = Field(None, description="Threshold adjustment")

    @validator("style")
    def validate_style(cls, v):
        if v and v not in ALLOWED_STYLES:
            raise ValueError(f"Style must be one of {ALLOWED_STYLES}")
        return v

    @validator("threshold_delta")
    def validate_threshold(cls, v):
        if v is not None and abs(v) > MAX_THRESHOLD_SHIFT:
            raise ValueError(f"Threshold delta must be within ±{MAX_THRESHOLD_SHIFT}")
        return v


class FeedbackConstraints(BaseModel):
    """Safety constraints for the feedback."""

    ethics_bound: bool = Field(True, description="Ethics boundary enforced")
    compliance_bound: bool = Field(True, description="Compliance boundary enforced")


class FeedbackAttestation(BaseModel):
    """Cryptographic attestation."""

    alg: str = Field(..., description="Algorithm (dilithium3, ed25519)")
    sig: str = Field(..., description="Signature")
    content_hash: str = Field(..., description="SHA3-512 hash of content")
    pubkey_id: str | None = Field(None, description="Public key identifier")


class FeedbackCard(BaseModel):
    """Complete feedback card schema."""

    fc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=datetime.utcnow)
    user_hash: str = Field(..., description="HMAC SHA3-512 of user ID")
    session_hash: str = Field(..., description="HMAC SHA3-512 of session ID")
    context: FeedbackContext
    feedback: FeedbackData
    proposed_tuning: ProposedTuning | None = None
    constraints: FeedbackConstraints = Field(default_factory=FeedbackConstraints)
    attestation: FeedbackAttestation | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class PolicySafePatch(BaseModel):
    """Policy-safe configuration patch."""

    style: str | None = Field(None, description="Style adjustment")
    threshold_delta: float | None = Field(None, description="Threshold adjustment")
    explain_depth: int | None = Field(None, ge=1, le=5, description="Explanation depth")

    @validator("style")
    def validate_style(cls, v):
        if v and v not in ALLOWED_STYLES:
            raise ValueError(f"Style must be one of {ALLOWED_STYLES}")
        return v

    @validator("threshold_delta")
    def validate_threshold(cls, v):
        if v is not None and abs(v) > MAX_THRESHOLD_SHIFT:
            raise ValueError(f"Threshold delta must be within ±{MAX_THRESHOLD_SHIFT}")
        return v


class ChangeProposal(BaseModel):
    """Change proposal for HITL approval queue."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: str = Field(..., description="Author of the proposal")
    target_file: str = Field(..., description="Target configuration file")
    patch: dict[str, Any] = Field(..., description="Configuration patch to apply")
    risk: Literal["low", "medium", "high"] = Field("low")
    ttl_sec: int = Field(3600, description="Time to live in seconds")
    status: Literal["pending", "approved", "rejected", "applied"] = Field("pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    feedback_ref: str | None = Field(None, description="Reference to feedback card")
    cluster_id: str | None = Field(None, description="Reference to feedback cluster")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class FeedbackCluster(BaseModel):
    """Clustered feedback for batch processing."""

    cluster_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task: str = Field(..., description="Task type")
    jurisdiction: str = Field(..., description="Jurisdiction")
    feedback_ids: list[str] = Field(..., description="List of feedback card IDs")
    sat_mean: float = Field(..., description="Mean satisfaction score")
    sat_var: float = Field(..., description="Satisfaction variance")
    n_samples: int = Field(..., description="Number of samples")
    common_issues: list[str] = Field(default_factory=list, description="Common issues")
    drift_delta: float | None = Field(None, description="Observed drift from baseline")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}
