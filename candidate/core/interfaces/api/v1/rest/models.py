from __future__ import annotations

import time
from datetime import datetime
from enum import Enum
from typing import Any

import streamlit as st
from pydantic import BaseModel, Field, field_validator


class ProcessingMode(str, Enum):
    SYMBOLIC = "symbolic"
    CAUSAL = "causal"
    HYBRID = "hybrid"


class ProcessRequest(BaseModel):
    """Main processing request model."""

    input_text: str = Field(..., min_length=1, max_length=10000)
    mode: ProcessingMode = ProcessingMode.HYBRID
    context: dict[str, Any] | None = None
    options: dict[str, Any] | None = None

    @field_validator("input_text")
    def validate_input(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Input text cannot be empty")
        return v


class SymbolicState(BaseModel):
    """Symbolic state representation."""

    glyphs: list[str]
    resonance: float = Field(..., ge=0.0, le=1.0)
    drift_score: float = Field(..., ge=0.0, le=1.0)
    entropy: float = Field(..., ge=0.0, le=1.0)


class ProcessResponse(BaseModel):
    """Processing response model."""

    request_id: str
    timestamp: datetime
    result: dict[str, Any]
    symbolic_state: SymbolicState | None = None
    metadata: dict[str, Any] = {}
    processing_time_ms: float


class HealthStatus(BaseModel):
    """System health status."""

    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    version: str
    uptime_seconds: float
    components: dict[str, bool]


class MetricsResponse(BaseModel):
    """System metrics."""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    drift_metrics: dict[str, float]
    request_count: int
    average_response_time_ms: float


class CapabilityAnnouncement(BaseModel):
    """Agent capability announcement payload."""

    agent_id: str
    capability: dict[str, Any]


class TaskAnnouncement(BaseModel):
    """Task announcement payload."""

    agent_id: str
    task: dict[str, Any]
