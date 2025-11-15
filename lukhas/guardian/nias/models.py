"""NIAS audit event data models.

Defines the schema for NIAS audit events written to the JSONL event stream.
Events capture request/response metadata, timing, identity, and optional
drift scores for security analytics and compliance reporting.

Performance:
    Event serialization: <0.1ms per event (Pydantic model_dump_json)
    File write: <1ms (buffered async I/O)

Privacy:
    - No request/response bodies stored (only metadata)
    - PII limited to caller identity (ΛiD, tenant, org header)
    - Configurable field filtering via environment variables
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NIASAuditEvent(BaseModel):
    """Single audit event for a request/response pair.

    Attributes:
        ts: Event timestamp (UTC)
        trace_id: Unique request trace ID (from X-Trace-Id or X-Request-Id header)
        route: Request path (e.g., "/v1/models")
        method: HTTP method (GET, POST, etc.)
        status_code: Response status code (200, 401, 500, etc.)
        duration_ms: Request processing duration in milliseconds
        caller: Caller identity (ΛiD, tenant ID, or Organization header)
        drift_score: Optional drift detection score (0.0-1.0, higher = more drift)
        request_meta: Request metadata (content-type, accept, etc.)
        response_meta: Response metadata (rate limits, cache status, etc.)
        notes: Optional human-readable notes or error details

    Example Event:
        {
            "ts": "2025-11-13T17:45:23.123456",
            "trace_id": "abc123def456",
            "route": "/v1/chat/completions",
            "method": "POST",
            "status_code": 200,
            "duration_ms": 1234.56,
            "caller": "org-xyz",
            "drift_score": 0.12,
            "request_meta": {"content_type": "application/json"},
            "response_meta": {"ratelimit": {"limit": "60", "remaining": "59"}},
            "notes": null
        }
    """

    ts: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp in UTC"
    )

    trace_id: Optional[str] = Field(
        default=None,
        description="Unique request trace ID for correlation"
    )

    route: str = Field(
        ...,
        description="Request path (e.g., /v1/models)"
    )

    method: str = Field(
        ...,
        description="HTTP method (GET, POST, PUT, DELETE, etc.)"
    )

    status_code: int = Field(
        ...,
        description="HTTP response status code"
    )

    duration_ms: float = Field(
        ...,
        description="Request processing duration in milliseconds"
    )

    caller: Optional[str] = Field(
        default=None,
        description="Caller identity: ΛiD, tenant ID, or OpenAI-Organization header"
    )

    drift_score: Optional[float] = Field(
        default=None,
        description="Optional drift detection score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    request_meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Request metadata (content-type, accept, user-agent, etc.)"
    )

    response_meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="Response metadata (rate limits, cache status, etc.)"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes or error details"
    )

    class Config:
        """Pydantic model configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        # Allow extra fields for future extensibility
        extra = "allow"


# Convenience type alias for clarity
AuditEvent = NIASAuditEvent
