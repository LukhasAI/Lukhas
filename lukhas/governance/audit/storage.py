"""Audit log storage backends with retention and rotation."""

# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for audit storage
# estimate: 15min | priority: high | dependencies: none

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from collections import deque
from threading import Lock
from typing import Any, Optional

from lukhas.governance.audit.events import AuditEvent, AuditEventType

# Import config for type hints
if False:
    from lukhas.governance.audit.config import AuditConfig

logger = logging.getLogger(__name__)


class AuditStorage(ABC):
    """Abstract base class for audit log storage backends."""

    @abstractmethod
    def store_event(self, event: AuditEvent) -> None:
        """Store an audit event.

        Args:
            event: Audit event to store
        """
        pass

    @abstractmethod
    def get_events(
        self,
        user_id: Optional[str] = None,
        event_types: Optional[list[AuditEventType]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 1000,
    ) -> list[AuditEvent]:
        """Query audit events with filters.

        Args:
            user_id: Filter by user ID
            event_types: Filter by event types
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            success: Filter by success status
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        pass

    @abstractmethod
    def cleanup_old_events(self, cutoff_time: float) -> int:
        """Remove audit events older than cutoff time.

        Args:
            cutoff_time: Unix timestamp cutoff (remove events before this)

        Returns:
            Number of events removed
        """
        pass

    @abstractmethod
    def get_statistics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> dict[str, Any]:
        """Get audit log statistics.

        Args:
            start_time: Start timestamp for statistics
            end_time: End timestamp for statistics

        Returns:
            Dictionary with audit statistics
        """
        pass


class InMemoryAuditStorage(AuditStorage):
    """In-memory audit log storage for testing and development.

    Thread-safe in-memory storage with automatic size limits and cleanup.

    Attributes:
        config: Audit configuration
        events: Deque of audit events (bounded by max_events)
        max_events: Maximum number of events to store (default 10,000)
    """

    def __init__(self, config: "AuditConfig", max_events: int = 10000):
        """Initialize in-memory storage.

        Args:
            config: Audit configuration
            max_events: Maximum number of events to store
        """
        self.config = config
        self.max_events = max_events
        self._events: deque[AuditEvent] = deque(maxlen=max_events)
        self._lock = Lock()

    def store_event(self, event: AuditEvent) -> None:
        """Store an audit event in memory.

        Args:
            event: Audit event to store
        """
        with self._lock:
            self._events.append(event)

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_types: Optional[list[AuditEventType]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 1000,
    ) -> list[AuditEvent]:
        """Query audit events with filters.

        Args:
            user_id: Filter by user ID
            event_types: Filter by event types
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            success: Filter by success status
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        with self._lock:
            results = []

            for event in reversed(self._events):  # Most recent first
                # Apply filters
                if user_id and event.user_id != user_id:
                    continue

                if event_types and event.event_type not in event_types:
                    continue

                if start_time and event.timestamp < start_time:
                    continue

                if end_time and event.timestamp > end_time:
                    continue

                if resource_type and event.resource_type != resource_type:
                    continue

                if resource_id and event.resource_id != resource_id:
                    continue

                if success is not None and event.success != success:
                    continue

                results.append(event)

                if len(results) >= limit:
                    break

            return results

    def cleanup_old_events(self, cutoff_time: float) -> int:
        """Remove audit events older than cutoff time.

        Args:
            cutoff_time: Unix timestamp cutoff (remove events before this)

        Returns:
            Number of events removed
        """
        with self._lock:
            original_count = len(self._events)

            # Filter events, keeping only those after cutoff
            self._events = deque(
                (event for event in self._events if event.timestamp >= cutoff_time),
                maxlen=self.max_events
            )

            removed_count = original_count - len(self._events)
            return removed_count

    def get_statistics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> dict[str, Any]:
        """Get audit log statistics.

        Args:
            start_time: Start timestamp for statistics
            end_time: End timestamp for statistics

        Returns:
            Dictionary with audit statistics
        """
        with self._lock:
            total_events = len(self._events)

            # Filter by time range
            events = self._events
            if start_time or end_time:
                events = [
                    event for event in self._events
                    if (not start_time or event.timestamp >= start_time)
                    and (not end_time or event.timestamp <= end_time)
                ]

            # Count by event type
            event_type_counts: Dict[str, int] = {}
            success_count = 0
            failure_count = 0

            for event in events:
                event_type_counts[event.event_type.value] = event_type_counts.get(event.event_type.value, 0) + 1

                if event.success:
                    success_count += 1
                else:
                    failure_count += 1

            return {
                "total_events": total_events,
                "filtered_events": len(events),
                "event_type_counts": event_type_counts,
                "success_count": success_count,
                "failure_count": failure_count,
                "success_rate": success_count / len(events) if events else 0.0,
                "storage_type": "in_memory",
                "max_events": self.max_events,
            }


class FileAuditStorage(AuditStorage):
    """File-based audit log storage with rotation and retention.

    Stores audit events as JSON Lines (one JSON object per line) for efficient
    appending and streaming. Implements automatic file rotation and retention.

    Thread-safe with file locking for concurrent writes.

    Attributes:
        config: Audit configuration
        log_file: Path to audit log file
    """

    def __init__(self, config: "AuditConfig"):
        """Initialize file-based storage.

        Args:
            config: Audit configuration
        """
        self.config = config
        self.log_file = config.log_file_path
        self._lock = Lock()

        if not self.log_file:
            raise ValueError("log_file_path is required for FileAuditStorage")

        # Ensure parent directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create log file if it doesn't exist
        if not self.log_file.exists():
            self.log_file.touch()

    def store_event(self, event: AuditEvent) -> None:
        """Store an audit event to file.

        Args:
            event: Audit event to store
        """
        with self._lock:
            try:
                # Check if rotation is needed
                self._rotate_if_needed()

                # Append event as JSON line
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(event.to_json() + "\n")

            except Exception as e:
                logger.error(f"Failed to store audit event: {e}")

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_types: Optional[list[AuditEventType]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 1000,
    ) -> list[AuditEvent]:
        """Query audit events with filters.

        Args:
            user_id: Filter by user ID
            event_types: Filter by event types
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            success: Filter by success status
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        with self._lock:
            results = []

            try:
                # Read file in reverse order (most recent first)
                lines = self._read_file_reversed()

                for line in lines:
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)
                        event = self._dict_to_event(data)

                        # Apply filters
                        if user_id and event.user_id != user_id:
                            continue

                        if event_types and event.event_type not in event_types:
                            continue

                        if start_time and event.timestamp < start_time:
                            continue

                        if end_time and event.timestamp > end_time:
                            continue

                        if resource_type and event.resource_type != resource_type:
                            continue

                        if resource_id and event.resource_id != resource_id:
                            continue

                        if success is not None and event.success != success:
                            continue

                        results.append(event)

                        if len(results) >= limit:
                            break

                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Failed to parse audit log line: {e}")
                        continue

            except Exception as e:
                logger.error(f"Failed to read audit events: {e}")

            return results

    def cleanup_old_events(self, cutoff_time: float) -> int:
        """Remove audit events older than cutoff time.

        Args:
            cutoff_time: Unix timestamp cutoff (remove events before this)

        Returns:
            Number of events removed
        """
        with self._lock:
            try:
                if not self.log_file.exists():
                    return 0

                # Read all events
                temp_file = self.log_file.with_suffix(".tmp")
                removed_count = 0
                kept_count = 0

                with open(self.log_file, encoding="utf-8") as infile:
                    with open(temp_file, "w", encoding="utf-8") as outfile:
                        for line in infile:
                            if not line.strip():
                                continue

                            try:
                                data = json.loads(line)
                                timestamp = data.get("timestamp", 0)

                                if timestamp >= cutoff_time:
                                    outfile.write(line)
                                    kept_count += 1
                                else:
                                    removed_count += 1

                            except (json.JSONDecodeError, KeyError):
                                # Keep malformed lines
                                outfile.write(line)
                                kept_count += 1

                # Replace original file with filtered file
                temp_file.replace(self.log_file)

                logger.info(f"Cleaned up {removed_count} old audit events, kept {kept_count}")
                return removed_count

            except Exception as e:
                logger.error(f"Failed to cleanup old events: {e}")
                return 0

    def get_statistics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> dict[str, Any]:
        """Get audit log statistics.

        Args:
            start_time: Start timestamp for statistics
            end_time: End timestamp for statistics

        Returns:
            Dictionary with audit statistics
        """
        with self._lock:
            try:
                if not self.log_file.exists():
                    return {
                        "total_events": 0,
                        "filtered_events": 0,
                        "event_type_counts": {},
                        "success_count": 0,
                        "failure_count": 0,
                        "success_rate": 0.0,
                        "storage_type": "file",
                        "log_file": str(self.log_file),
                        "file_size_bytes": 0,
                    }

                total_events = 0
                filtered_events = 0
                event_type_counts: Dict[str, int] = {}
                success_count = 0
                failure_count = 0

                with open(self.log_file, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue

                        try:
                            data = json.loads(line)
                            total_events += 1

                            timestamp = data.get("timestamp", 0)

                            # Filter by time range
                            if start_time and timestamp < start_time:
                                continue
                            if end_time and timestamp > end_time:
                                continue

                            filtered_events += 1

                            # Count by event type
                            event_type = data.get("event_type", "unknown")
                            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

                            # Count success/failure
                            if data.get("success", True):
                                success_count += 1
                            else:
                                failure_count += 1

                        except (json.JSONDecodeError, KeyError):
                            continue

                file_size = os.path.getsize(self.log_file)

                return {
                    "total_events": total_events,
                    "filtered_events": filtered_events,
                    "event_type_counts": event_type_counts,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "success_rate": success_count / filtered_events if filtered_events else 0.0,
                    "storage_type": "file",
                    "log_file": str(self.log_file),
                    "file_size_bytes": file_size,
                    "file_size_mb": file_size / (1024 * 1024),
                }

            except Exception as e:
                logger.error(f"Failed to get statistics: {e}")
                return {
                    "total_events": 0,
                    "error": str(e),
                }

    def _rotate_if_needed(self) -> None:
        """Rotate log file if it exceeds max size."""
        if not self.log_file.exists():
            return

        file_size_mb = os.path.getsize(self.log_file) / (1024 * 1024)

        if file_size_mb >= self.config.max_file_size_mb:
            self._rotate_log_file()

    def _rotate_log_file(self) -> None:
        """Rotate log file by renaming with timestamp."""
        try:
            timestamp = int(time.time())
            backup_file = self.log_file.with_suffix(f".{timestamp}.jsonl")

            # Rename current file
            self.log_file.rename(backup_file)

            # Create new empty file
            self.log_file.touch()

            logger.info(f"Rotated audit log to {backup_file}")

            # Clean up old backups
            self._cleanup_old_backups()

        except Exception as e:
            logger.error(f"Failed to rotate log file: {e}")

    def _cleanup_old_backups(self) -> None:
        """Remove old backup files beyond max_backup_count."""
        try:
            backup_pattern = f"{self.log_file.stem}.*.jsonl"
            backup_files = sorted(
                self.log_file.parent.glob(backup_pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            # Keep only max_backup_count newest backups
            for backup_file in backup_files[self.config.max_backup_count:]:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file}")

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

    def _read_file_reversed(self) -> list[str]:
        """Read file lines in reverse order (most recent first).

        Returns:
            List of lines in reverse order
        """
        if not self.log_file.exists():
            return []

        with open(self.log_file, encoding="utf-8") as f:
            lines = f.readlines()

        return list(reversed(lines))

    def _dict_to_event(self, data: dict[str, Any]) -> AuditEvent:
        """Convert dictionary to AuditEvent.

        Args:
            data: Dictionary representation of audit event

        Returns:
            AuditEvent instance
        """
        # Convert event_type string back to enum
        event_type_str = data.get("event_type", "data.read")
        event_type = AuditEventType(event_type_str)

        return AuditEvent(
            event_id=data.get("event_id", ""),
            timestamp=data.get("timestamp", 0),
            event_type=event_type,
            user_id=data.get("user_id"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            resource_type=data.get("resource_type"),
            resource_id=data.get("resource_id"),
            action=data.get("action", ""),
            success=data.get("success", True),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )
