"""Lightweight JSONL audit sink."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import os


class JSONLAuditSink:
    """Append audit events as JSONL to rotating file."""

    def __init__(
        self,
        log_dir: str = "./audit_logs",
        max_file_size_mb: int = 100,
        file_prefix: str = "audit"
    ):
        """
        Initialize JSONL audit sink.

        Args:
            log_dir: Directory for audit logs
            max_file_size_mb: Max file size before rotation (MB)
            file_prefix: Prefix for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.file_prefix = file_prefix
        self.current_file: Optional[Path] = None
        self.current_handle: Optional[Any] = None

    def _get_current_file(self) -> Path:
        """Get current log file, rotating if needed."""
        if self.current_file and self.current_file.exists():
            if self.current_file.stat().st_size < self.max_file_size_bytes:
                return self.current_file

        # Need new file (first time or rotation)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        new_file = self.log_dir / f"{self.file_prefix}_{timestamp}.jsonl"
        self.current_file = new_file

        # Close old handle if exists
        if self.current_handle:
            self.current_handle.close()
        self.current_handle = None

        return new_file

    def append(self, event: Dict[str, Any]) -> None:
        """
        Append audit event to JSONL file.

        Args:
            event: Event dictionary to log
        """
        file_path = self._get_current_file()

        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat()

        # Append as single JSONL line
        with open(file_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def close(self) -> None:
        """Close the current file handle."""
        if self.current_handle:
            self.current_handle.close()
            self.current_handle = None


if __name__ == "__main__":
    print("=== JSONL Audit Sink Demo ===\n")

    sink = JSONLAuditSink(log_dir="./test_audit", max_file_size_mb=1)

    # Log some events
    events = [
        {"event_type": "guardian_veto", "reason": "UNSAFE_CONTENT", "user": "user_1"},
        {"event_type": "login", "user": "user_2", "success": True},
        {"event_type": "data_access", "resource": "/api/data", "user": "user_1"},
    ]

    for event in events:
        sink.append(event)
        print(f"Logged: {event['event_type']}")

    sink.close()
    print(f"\nLogs written to: {sink.log_dir}")
