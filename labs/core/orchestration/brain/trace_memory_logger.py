"""
#ΛTRACE
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: trace_memoria_logger.py
Advanced: trace_memoria_logger.py
Integration Date: 2025-05-31T07:55:27.785635
"""

from datetime import timezone

"""
TRACE MEMORY LOGGER
-------------------
Specialized logger for LUKHAS AI system that handles trace memory logging and persistence.
This module creates a system for encoding, storing, and retrieving memory traces with
emotional valence, ethical evaluations, and temporal context.

Author: LUKHAS AI Team
Date: May 8, 2025
Version: 1.0.0
"""

import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Configure standard logger
logger = logging.getLogger(__name__)


class TraceMemoryLogger:
    """
    TraceMemoryLogger handles the creation, storage, and retrieval of memory traces
    in the LUKHAS AI system. It supports various log levels, encryption, and
    structured memory formats with metadata.
    """

    # Trace log levels with symbolic meaning

    class TraceLevel:
        SYSTEM = 0  # System-level events
        CORE = 1  # Core component events
        SYMBOLIC = 2  # Symbolic reasoning events
        EMOTIONAL = 3  # Emotional processing events
        ETHICAL = 4  # Ethical deliberations
        INTERACTION = 5  # User interactions
        DREAM = 6  # Dream-state processing
        REFLECTION = 7  # Self-reflection events

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the TraceMemoriaLogger with configuration.

        Args:
            config: Configuration dictionary with settings
        """
        self.config = config or {}

        # Set default log directory
        self.base_log_dir = self.config.get("log_dir", "trace_logs")

        # Ensure log directories exist
        self._ensure_log_directories()

        # Initialize lock for thread safety
        self.log_lock = threading.Lock()

        # Cache for recent memory traces
        self.recent_traces = []
        self.recent_traces_limit = self.config.get("recent_traces_limit", 100)

        logger.info(f"TraceMemoryLogger initialized with base directory: {self.base_log_dir}")

    def _ensure_log_directories(self):
        """Create necessary log directories if they don't exist."""
        # Base log directory
        Path(self.base_log_dir).mkdir(parents=True, exist_ok=True)

        # Specialized log directories
        for dir_name in [
            "system",
            "core",
            "symbolic",
            "emotional",
            "ethical",
            "interaction",
            "dream",
            "reflection",
        ]:
            Path(os.path.join(self.base_log_dir, dir_name)).mkdir(exist_ok=True)

    def log_trace(
        self,
        level: int,
        message: str,
        metadata: Optional[dict[str, Any]] = None,
        emotional_valence: Optional[dict[str, float]] = None,
        ethical_score: Optional[float] = None,
        tags: Optional[list[str]] = None,
        source_component: Optional[str] = None,
    ) -> str:
        """
        Log a memory trace with metadata and context.

        Args:
            level: Trace level (use TraceLevel constants)
            message: The main trace message
            metadata: Additional structured data
            emotional_valence: Emotional values associated with trace
            ethical_score: Ethical evaluation score (0-1)
            tags: List of tags for categorizing the trace
            source_component: Component that generated the trace

        Returns:
            trace_id: Unique ID for the trace
        """
        # Generate unique ID for trace
        trace_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"

        # Build trace entry
        trace = {
            "trace_id": trace_id,
            "timestamp": timestamp,
            "unix_time": time.time(),
            "level": level,
            "level_name": self._level_to_name(level),
            "message": message,
            "source_component": source_component or "unknown",
            "tags": tags or [],
        }

        # Add optional fields if provided
        if metadata:
            trace["metadata"] = metadata

        if emotional_valence:
            trace["emotional"] = emotional_valence

        if ethical_score is not None:
            trace["ethical_score"] = ethical_score

        # Write to appropriate log file
        self._write_trace(trace)

        # Cache recent trace
        self._cache_trace(trace)

        return trace_id

    def _level_to_name(self, level: int) -> str:
        """Convert trace level to string name."""
        level_names = {
            self.TraceLevel.SYSTEM: "SYSTEM",
            self.TraceLevel.CORE: "CORE",
            self.TraceLevel.SYMBOLIC: "SYMBOLIC",
            self.TraceLevel.EMOTIONAL: "EMOTIONAL",
            self.TraceLevel.ETHICAL: "ETHICAL",
            self.TraceLevel.INTERACTION: "INTERACTION",
            self.TraceLevel.DREAM: "DREAM",
            self.TraceLevel.REFLECTION: "REFLECTION",
        }
        return level_names.get(level, "UNKNOWN")

    def _write_trace(self, trace: dict[str, Any]):
        """Write trace to appropriate log file based on level."""
        level = trace.get("level", 0)
        level_name = self._level_to_name(level).lower()

        # Determine log file path
        log_file = os.path.join(self.base_log_dir, level_name, f"trace_{level_name}.jsonl")

        # Write to file with thread safety
        with self.log_lock, open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace) + "\n")

        # Always write to all_traces log
        all_traces_log = os.path.join(self.base_log_dir, "all_traces.jsonl")
        with self.log_lock, open(all_traces_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace) + "\n")

    def _cache_trace(self, trace: dict[str, Any]):
        """Cache recent trace in memory."""
        self.recent_traces.append(trace)
        # Trim if exceeding limit
        while len(self.recent_traces) > self.recent_traces_limit:
            self.recent_traces.pop(0)

    def get_recent_traces(
        self,
        limit: int = 10,
        level: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent memory traces from cache.

        Args:
            limit: Maximum number of traces to return
            level: Filter by trace level
            tag: Filter by specific tag

        Returns:
            List of trace entries
        """
        filtered = self.recent_traces

        # Apply filters
        if level is not None:
            filtered = [t for t in filtered if t.get("level") == level]

        if tag is not None:
            filtered = [t for t in filtered if tag in t.get("tags", [])]

        # Return most recent traces first
        return sorted(filtered, key=lambda t: t["unix_time"], reverse=True)[:limit]

    def read_traces(
        self,
        level: Optional[int] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100,
        tags: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """
        Read traces from log files based on filters.

        Args:
            level: Filter by trace level
            start_time: Filter by start time (unix timestamp)
            end_time: Filter by end time (unix timestamp)
            limit: Maximum number of traces to return
            tags: Filter by one or more tags

        Returns:
            List of trace entries
        """
        # Determine which log file to read from
        if level is not None:
            level_name = self._level_to_name(level).lower()
            log_file = os.path.join(self.base_log_dir, level_name, f"trace_{level_name}.jsonl")
            if not os.path.exists(log_file):
                return []
            files_to_read = [log_file]
        else:
            # Read from all_traces log
            log_file = os.path.join(self.base_log_dir, "all_traces.jsonl")
            if not os.path.exists(log_file):
                return []
            files_to_read = [log_file]

        traces = []
        for file_path in files_to_read:
            try:
                with open(file_path, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue

                        trace = json.loads(line)

                        # Apply time filters
                        trace_time = trace.get("unix_time", 0)
                        if start_time and trace_time < start_time:
                            continue
                        if end_time and trace_time > end_time:
                            continue

                        # Apply tag filters
                        if tags and not any(tag in trace.get("tags", []) for tag in tags):
                            continue

                        traces.append(trace)

                        if len(traces) >= limit:
                            break
            except Exception as e:
                logger.error(f"Error reading traces from {file_path}: {e}")

        # Return most recent traces first
        return sorted(traces, key=lambda t: t["unix_time"], reverse=True)[:limit]

    def log_system_event(self, message: str, **kwargs) -> str:
        """Convenience method to log system events."""
        return self.log_trace(self.TraceLevel.SYSTEM, message, **kwargs)

    def log_core_event(self, message: str, **kwargs) -> str:
        """Convenience method to log core events."""
        return self.log_trace(self.TraceLevel.CORE, message, **kwargs)

    def log_symbolic(self, message: str, **kwargs) -> str:
        """Convenience method to log symbolic processing."""
        return self.log_trace(self.TraceLevel.SYMBOLIC, message, **kwargs)

    def log_emotional(self, message: str, emotional_valence: dict[str, float], **kwargs) -> str:
        """Convenience method to log emotional processing."""
        kwargs["emotional_valence"] = emotional_valence
        return self.log_trace(self.TraceLevel.EMOTIONAL, message, **kwargs)

    def log_ethical(self, message: str, ethical_score: float, **kwargs) -> str:
        """Convenience method to log ethical deliberations."""
        kwargs["ethical_score"] = ethical_score
        return self.log_trace(self.TraceLevel.ETHICAL, message, **kwargs)

    def log_interaction(self, message: str, **kwargs) -> str:
        """Convenience method to log user interactions."""
        return self.log_trace(self.TraceLevel.INTERACTION, message, **kwargs)

    def log_dream(self, message: str, **kwargs) -> str:
        """Convenience method to log dream processing."""
        return self.log_trace(self.TraceLevel.DREAM, message, **kwargs)

    def log_reflection(self, message: str, **kwargs) -> str:
        """Convenience method to log self-reflection."""
        return self.log_trace(self.TraceLevel.REFLECTION, message, **kwargs)

    def get_trace_by_id(self, trace_id: str) -> Optional[dict[str, Any]]:
        """
        Find a trace by its unique ID.

        Args:
            trace_id: The unique trace ID to search for

        Returns:
            Trace entry if found, None otherwise
        """
        # First check in-memory cache
        for trace in self.recent_traces:
            if trace.get("trace_id") == trace_id:
                return trace

        # If not found, check log files
        all_traces_log = os.path.join(self.base_log_dir, "all_traces.jsonl")
        if not os.path.exists(all_traces_log):
            return None

        try:
            with open(all_traces_log, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    trace = json.loads(line)
                    if trace.get("trace_id") == trace_id:
                        return trace
        except Exception as e:
            logger.error(f"Error searching for trace {trace_id}: {e}")

        return None

    def close(self):
        """Perform cleanup operations before shutdown."""
        logger.info("TraceMemoryLogger shutting down")
        # Any cleanup operations would go here
        # For example, ensuring all logs are flushed


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Create logger instance
    trace_logger = TraceMemoryLogger()

    # Log various types of traces
    trace_logger.log_system_event("System initialized", metadata={"version": "1.0.0"})

    trace_logger.log_emotional(
        "Processing user sentiment",
        emotional_valence={"joy": 0.7, "trust": 0.8},
        metadata={"user_input": "I'm feeling great today!"},
    )

    trace_logger.log_ethical(
        "Evaluating content policy",
        ethical_score=0.9,
        metadata={"content_type": "user_query"},
    )

    # Retrieve recent traces
    recent = trace_logger.get_recent_traces(limit=5)
    print(f"Recent traces: {len(recent)}")
    for trace in recent:
        print(f"{trace['level_name']}: {trace['message']}")
