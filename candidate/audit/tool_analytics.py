"""Tool Usage Analytics & Incident Tracking ⚛️🛡️
Tracks actual tool invocations and blocks disallowed attempts.
"""

import hashlib
import json
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from lukhas.flags import get_flags

# Storage paths
AUDIT_DIR = Path(".lukhas_audit")
INCIDENTS_FILE = AUDIT_DIR / "tool_incidents.jsonl"
AUDIT_DIR.mkdir(exist_ok=True)
INCIDENTS_FILE.touch(exist_ok=True)

# Thread safety
_INCIDENT_LOCK = threading.Lock()


@dataclass
class ToolCall:
    """Represents a single tool invocation"""

    tool_name: str
    arguments: dict[str, Any]
    start_time: float
    end_time: Optional[float] = None
    status: str = "pending"  # pending, success, failed, blocked
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None

    def complete(self, status: str, result: Any = None, error: str = None):
        """Mark tool call as complete"""
        self.end_time = time.time()
        self.duration_ms = int((self.end_time - self.start_time) * 1000)
        self.status = status
        self.result = result
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "timestamp": self.start_time,
        }


@dataclass
class ToolIncident:
    """Represents a blocked tool attempt"""

    audit_id: str
    attempted_tool: str
    allowed_tools: list[str]
    prompt_hash: str
    timestamp: float
    action_taken: str = "blocked_and_tightened"
    severity: str = "high"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ToolAnalytics:
    """Tracks tool usage and security incidents"""

    def __init__(self):
        self.active_calls: dict[str, ToolCall] = {}
        self.completed_calls: list[ToolCall] = []
        self.incidents: list[ToolIncident] = []

    def start_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Record the start of a tool invocation"""
        # Check if analytics is disabled via flag
        if not get_flags().get("tool_analytics", True):
            # Return a dummy ID but don't track
            return f"tool_{uuid.uuid4().hex[:8]}"

        call_id = f"tool_{uuid.uuid4().hex[:8]}"
        self.active_calls[call_id] = ToolCall(
            tool_name=tool_name, arguments=arguments, start_time=time.time()
        )
        return call_id

    def complete_tool_call(
        self,
        call_id: str,
        status: str = "success",
        result: Any = None,
        error: str = None,
    ):
        """Record completion of a tool invocation"""
        # Check if analytics is disabled via flag
        if not get_flags().get("tool_analytics", True):
            # No-op if analytics is disabled
            return

        if call_id in self.active_calls:
            call = self.active_calls.pop(call_id)
            call.complete(status, result, error)
            self.completed_calls.append(call)

    def record_blocked_attempt(
        self,
        audit_id: str,
        attempted_tool: str,
        allowed_tools: list[str],
        prompt: str,
    ) -> ToolIncident:
        """Record a blocked tool attempt as security incident"""
        # Hash the prompt for privacy
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

        incident = ToolIncident(
            audit_id=audit_id,
            attempted_tool=attempted_tool,
            allowed_tools=allowed_tools,
            prompt_hash=prompt_hash,
            timestamp=time.time(),
        )

        self.incidents.append(incident)

        # Only persist to file if analytics is enabled
        if get_flags().get("tool_analytics", True):
            with _INCIDENT_LOCK:
                write_incident(incident)

        return incident

    def get_analytics_summary(self) -> dict[str, Any]:
        """Get summary of tool usage analytics"""
        all_calls = self.completed_calls + list(self.active_calls.values())

        # Calculate statistics
        tool_counts = {}
        total_duration = 0
        failed_count = 0

        for call in all_calls:
            tool_counts[call.tool_name] = tool_counts.get(call.tool_name, 0) + 1
            if call.duration_ms:
                total_duration += call.duration_ms
            if call.status == "failed":
                failed_count += 1

        return {
            "total_calls": len(all_calls),
            "active_calls": len(self.active_calls),
            "completed_calls": len(self.completed_calls),
            "tool_distribution": tool_counts,
            "total_duration_ms": total_duration,
            "average_duration_ms": (total_duration // len(all_calls) if all_calls else 0),
            "failed_calls": failed_count,
            "incidents_count": len(self.incidents),
            "tools_used": list(tool_counts.keys()),
            "recent_incidents": [inc.to_dict() for inc in self.incidents[-5:]],
        }

    def get_calls_for_audit(self) -> list[dict[str, Any]]:
        """Get tool calls formatted for audit bundle"""
        return [call.to_dict() for call in self.completed_calls]


def write_incident(incident: ToolIncident):
    """Write incident to persistent storage"""
    line = json.dumps(incident.to_dict(), ensure_ascii=False)
    with INCIDENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_incidents(limit: int = 100) -> list[dict[str, Any]]:
    """Read recent incidents from storage"""
    incidents = []
    try:
        with INCIDENTS_FILE.open("r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
            for line in lines:
                try:
                    incidents.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return incidents


def check_tool_allowlist(requested_tool: str, allowlist: list[str]) -> bool:
    """Check if a tool is in the allowlist"""
    return requested_tool in allowlist


def enforce_tool_governance(
    requested_tools: list[str],
    allowlist: list[str],
    audit_id: str,
    prompt: str,
    analytics: ToolAnalytics,
) -> tuple[list[str], list[ToolIncident]]:
    """
    Enforce tool governance by filtering requested tools through allowlist.
    Returns (allowed_tools, incidents)
    """
    allowed = []
    incidents = []

    for tool in requested_tools:
        if check_tool_allowlist(tool, allowlist):
            allowed.append(tool)
        else:
            # Record security incident
            incident = analytics.record_blocked_attempt(
                audit_id=audit_id,
                attempted_tool=tool,
                allowed_tools=allowlist,
                prompt=prompt,
            )
            incidents.append(incident)

    return allowed, incidents


# Global analytics instance
_global_analytics = ToolAnalytics()


def get_analytics() -> ToolAnalytics:
    """Get the global analytics instance"""
    return _global_analytics
