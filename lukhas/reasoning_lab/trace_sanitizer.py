"""
Reasoning Trace Sanitizer

Sanitizes reasoning traces before storage with configurable retention policies
and export capabilities for debugging.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from .sensitive_data_detector import SensitiveDataDetector, DetectionThreshold
from .redaction_engine import RedactionEngine, RedactionMode


class RetentionPolicy(Enum):
    """Retention policies for reasoning traces."""
    DEMO = 7  # 7 days for demo sessions
    AUTHENTICATED = 30  # 30 days for authenticated users
    ENTERPRISE = 90  # 90 days for enterprise customers


@dataclass
class SanitizedTrace:
    """Represents a sanitized reasoning trace."""
    trace_id: str
    original_length: int
    sanitized_content: str
    detections_count: int
    created_at: str
    expires_at: str
    retention_policy: str
    metadata: Dict[str, Any]


class TraceSanitizer:
    """
    Sanitizes reasoning traces before storage.

    Features:
    - Sensitive data detection and removal
    - Configurable retention policies
    - Safe export for debugging
    - Automatic expiration

    Examples:
        >>> sanitizer = TraceSanitizer()
        >>> trace = "My reasoning with API key sk-abc123"
        >>> result = sanitizer.sanitize(trace, policy=RetentionPolicy.DEMO)
        >>> "REDACTED" in result.sanitized_content
        True
    """

    def __init__(self):
        """Initialize trace sanitizer."""
        self.detector = SensitiveDataDetector(
            threshold=DetectionThreshold.MEDIUM
        )
        self.redactor = RedactionEngine(audit_logging=True)
        self.traces: Dict[str, SanitizedTrace] = {}
        self.logger = logging.getLogger(__name__)

    def sanitize(
        self,
        trace_content: str,
        trace_id: str,
        policy: RetentionPolicy = RetentionPolicy.DEMO,
        redaction_mode: RedactionMode = RedactionMode.FULL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SanitizedTrace:
        """
        Sanitize reasoning trace.

        Args:
            trace_content: Original trace content
            trace_id: Unique trace identifier
            policy: Retention policy
            redaction_mode: Redaction mode to use
            metadata: Optional metadata

        Returns:
            SanitizedTrace object
        """
        # Detect sensitive data
        detections = self.detector.detect(trace_content)

        # Redact sensitive data
        sanitized_content = self.redactor.redact(
            trace_content,
            detections,
            redaction_mode
        )

        # Calculate expiration
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(days=policy.value)

        # Create sanitized trace
        sanitized_trace = SanitizedTrace(
            trace_id=trace_id,
            original_length=len(trace_content),
            sanitized_content=sanitized_content,
            detections_count=len(detections),
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat(),
            retention_policy=policy.name,
            metadata=metadata or {}
        )

        # Store trace
        self.traces[trace_id] = sanitized_trace

        self.logger.info(
            f"Sanitized trace {trace_id}: {len(detections)} detections, "
            f"policy={policy.name}, expires={expires_at.isoformat()}"
        )

        return sanitized_trace

    def get_trace(self, trace_id: str) -> Optional[SanitizedTrace]:
        """
        Retrieve sanitized trace.

        Args:
            trace_id: Trace identifier

        Returns:
            SanitizedTrace if found and not expired, None otherwise
        """
        trace = self.traces.get(trace_id)
        if not trace:
            return None

        # Check expiration
        if self._is_expired(trace):
            self._remove_trace(trace_id)
            return None

        return trace

    def remove_sensitive_from_logs(self, log_content: str) -> str:
        """
        Remove sensitive data from log content.

        Args:
            log_content: Log content to sanitize

        Returns:
            Sanitized log content
        """
        detections = self.detector.detect(log_content)
        return self.redactor.redact(
            log_content,
            detections,
            RedactionMode.FULL
        )

    def export_trace(
        self,
        trace_id: str,
        format: str = "json"
    ) -> Optional[str]:
        """
        Export sanitized trace for debugging.

        Args:
            trace_id: Trace identifier
            format: Export format (json, txt)

        Returns:
            Exported content as string, None if not found
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        if format == "json":
            return json.dumps(asdict(trace), indent=2)
        elif format == "txt":
            return trace.sanitized_content
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_all_traces(self, filepath: str, format: str = "json"):
        """
        Export all sanitized traces to file.

        Args:
            filepath: Output file path
            format: Export format (json)
        """
        # Clean expired traces first
        self.cleanup_expired_traces()

        traces_data = [asdict(trace) for trace in self.traces.values()]

        with open(filepath, 'w') as f:
            if format == "json":
                json.dump(traces_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")

        self.logger.info(f"Exported {len(traces_data)} traces to {filepath}")

    def cleanup_expired_traces(self) -> int:
        """
        Remove expired traces.

        Returns:
            Number of traces removed
        """
        expired = [
            trace_id for trace_id, trace in self.traces.items()
            if self._is_expired(trace)
        ]

        for trace_id in expired:
            self._remove_trace(trace_id)

        if expired:
            self.logger.info(f"Cleaned up {len(expired)} expired traces")

        return len(expired)

    def update_retention_policy(
        self,
        trace_id: str,
        new_policy: RetentionPolicy
    ) -> bool:
        """
        Update retention policy for a trace.

        Args:
            trace_id: Trace identifier
            new_policy: New retention policy

        Returns:
            True if updated, False if trace not found
        """
        trace = self.traces.get(trace_id)
        if not trace:
            return False

        # Recalculate expiration
        created_at = datetime.fromisoformat(trace.created_at)
        new_expires_at = created_at + timedelta(days=new_policy.value)

        trace.expires_at = new_expires_at.isoformat()
        trace.retention_policy = new_policy.name

        self.logger.info(
            f"Updated retention policy for trace {trace_id}: "
            f"{new_policy.name} (expires {new_expires_at.isoformat()})"
        )

        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get sanitizer statistics.

        Returns:
            Statistics dictionary
        """
        # Clean expired first
        self.cleanup_expired_traces()

        stats = {
            'total_traces': len(self.traces),
            'by_policy': {},
            'total_detections': 0,
            'redactor_stats': self.redactor.get_statistics()
        }

        for trace in self.traces.values():
            policy = trace.retention_policy
            stats['by_policy'][policy] = stats['by_policy'].get(policy, 0) + 1
            stats['total_detections'] += trace.detections_count

        return stats

    def _is_expired(self, trace: SanitizedTrace) -> bool:
        """Check if trace is expired."""
        expires_at = datetime.fromisoformat(trace.expires_at)
        return datetime.utcnow() > expires_at

    def _remove_trace(self, trace_id: str):
        """Remove trace from storage."""
        if trace_id in self.traces:
            del self.traces[trace_id]
            self.logger.debug(f"Removed trace: {trace_id}")

    def get_trace_metadata(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace metadata without content.

        Args:
            trace_id: Trace identifier

        Returns:
            Metadata dictionary or None
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        return {
            'trace_id': trace.trace_id,
            'original_length': trace.original_length,
            'detections_count': trace.detections_count,
            'created_at': trace.created_at,
            'expires_at': trace.expires_at,
            'retention_policy': trace.retention_policy,
            'metadata': trace.metadata
        }
