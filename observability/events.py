"""
Structured event logging for LUKHAS MATRIZ.

Provides unified event schema for tracing, debugging, and observability.
Events are emitted as JSON Lines for easy ingestion by log aggregators.
"""

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class EventType(str, Enum):
    """Standard event types following OpenAI-ish taxonomy."""

    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    TOOL_CALLED = "tool.called"
    TOOL_RESULT = "tool.result"
    MODEL_REQUEST = "model.request"
    MODEL_RESPONSE = "model.response"
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"


@dataclass
class RunEvent:
    """
    Base event for all LUKHAS operations.

    Follows structured logging best practices with consistent fields
    across all event types.
    """

    event_type: str
    run_id: str
    timestamp: float = field(default_factory=time.time)
    step_id: str = ""
    model: str = ""
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = asdict(self)
        # Add ISO timestamp for human readability
        data["timestamp_iso"] = datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat()
        return json.dumps(data, ensure_ascii=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class EventLogger:
    """
    JSON Lines event logger with automatic file rotation.

    Writes events to runlogs/ directory with daily rotation.
    """

    def __init__(self, base_path: str = "runlogs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._current_file: Optional[Path] = None
        self._current_date: Optional[str] = None

    def _get_log_file(self) -> Path:
        """Get current log file path with daily rotation."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if date_str != self._current_date:
            self._current_date = date_str
            self._current_file = self.base_path / f"events_{date_str}.jsonl"
        return self._current_file

    def log(self, event: RunEvent) -> None:
        """Write event to log file."""
        log_file = self._get_log_file()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(event.to_json() + "\n")

    def log_dict(self, event_data: dict[str, Any]) -> None:
        """Log from dictionary (convenience method)."""
        event = RunEvent(
            event_type=event_data.get("event_type", "unknown"),
            run_id=event_data.get("run_id", ""),
            step_id=event_data.get("step_id", ""),
            model=event_data.get("model", ""),
            latency_ms=event_data.get("latency_ms", 0.0),
            metadata=event_data.get("metadata", {}),
        )
        self.log(event)


# Global event logger instance
_global_logger: Optional[EventLogger] = None


def get_event_logger() -> EventLogger:
    """Get or create global event logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = EventLogger()
    return _global_logger


def log_event(
    event_type: str,
    run_id: str,
    step_id: str = "",
    model: str = "",
    latency_ms: float = 0.0,
    **metadata,
) -> None:
    """
    Convenience function to log an event.

    Example:
        log_event(
            EventType.RUN_STARTED,
            run_id="req_abc123",
            model="lukhas-matriz",
            input_length=42
        )
    """
    event = RunEvent(
        event_type=event_type,
        run_id=run_id,
        step_id=step_id,
        model=model,
        latency_ms=latency_ms,
        metadata=metadata,
    )
    get_event_logger().log(event)


def generate_run_id() -> str:
    """Generate a unique run ID."""
    return f"run_{uuid.uuid4().hex[:12]}"


def generate_step_id(run_id: str, step_num: int) -> str:
    """Generate a step ID within a run."""
    return f"{run_id}_step_{step_num}"
