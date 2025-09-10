"""
Pydantic models for trace API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TraceResponse(BaseModel):
    """Response model for a single trace entry."""

    trace_id: str = Field(..., description="Unique trace identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp when trace was created")
    unix_time: float = Field(..., description="Unix timestamp for efficient sorting")
    level: int = Field(..., description="Trace level (0-7)")
    level_name: str = Field(..., description="Human-readable trace level name")
    message: str = Field(..., description="Main trace message")
    source_component: str = Field(..., description="Component that generated the trace")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional structured data")
    emotional: Optional[Dict[str, float]] = Field(None, description="Emotional valence data")
    ethical_score: Optional[float] = Field(None, description="Ethical evaluation score (0-1)")


class ExecutionTraceResponse(BaseModel):
    """Enhanced response model for execution trace entries with full context."""

    trace_id: str = Field(..., description="Unique trace identifier")
    timestamp: str = Field(..., description="ISO 8601 timestamp when trace was created")
    unix_time: float = Field(..., description="Unix timestamp for efficient sorting")
    level: int = Field(..., description="Trace level (0-7)")
    level_name: str = Field(..., description="Human-readable trace level name")
    message: str = Field(..., description="Main trace message")
    source_component: str = Field(..., description="Component that generated the trace")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional structured data")
    emotional: Optional[Dict[str, float]] = Field(None, description="Emotional valence data")
    ethical_score: Optional[float] = Field(None, description="Ethical evaluation score (0-1)")

    # Additional execution context fields
    execution_context: Optional[Dict[str, Any]] = Field(None, description="Execution environment context")
    performance_metrics: Optional[Dict[str, float]] = Field(None, description="Performance timing and resource usage")
    related_traces: Optional[List[str]] = Field(None, description="IDs of related traces in the execution chain")


class TraceNotFoundResponse(BaseModel):
    """Response model for trace not found errors."""

    error: str = Field("trace_not_found", description="Error type")
    message: str = Field(..., description="Human-readable error message")
    trace_id: str = Field(..., description="The trace ID that was not found")


class TraceErrorResponse(BaseModel):
    """Response model for general trace API errors."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")


class TraceValidationErrorResponse(BaseModel):
    """Response model for validation errors."""

    error: str = Field("validation_error", description="Error type")
    message: str = Field(..., description="Human-readable error message")
    field: str = Field(..., description="Field that failed validation")
    value: str = Field(..., description="Invalid value provided")
