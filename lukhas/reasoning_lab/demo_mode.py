"""
Privacy-Preserving Demo Mode

Provides sandboxed execution environment for public demonstrations with:
- Auto-enabled redaction
- No external API calls
- Ephemeral session storage
- Rate limiting
"""

import time
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

from .sensitive_data_detector import SensitiveDataDetector, DetectionThreshold
from .redaction_engine import RedactionEngine, RedactionMode


@dataclass
class DemoSession:
    """Represents a demo session."""
    session_id: str
    created_at: datetime
    ip_address: str
    trace_count: int = 0
    expires_at: datetime = field(init=False)

    def __post_init__(self):
        # Sessions expire after 1 hour
        self.expires_at = self.created_at + timedelta(hours=1)

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def can_create_trace(self, limit: int = 10) -> bool:
        """Check if session can create more traces."""
        return self.trace_count < limit and not self.is_expired()


class DemoMode:
    """
    Privacy-preserving demo mode with safety controls.

    Features:
    - Auto-enabled redaction (paranoid mode)
    - Sandboxed execution (no external API calls)
    - Ephemeral session storage (1 hour TTL)
    - Rate limiting (10 traces per IP per hour)
    - Watermark on reasoning traces

    Examples:
        >>> demo = DemoMode()
        >>> session_id = demo.create_session("192.168.1.1")
        >>> demo.is_demo_allowed(session_id)
        True
    """

    WATERMARK = "⚠️ Demo Mode - Not for Production Use"
    MAX_TRACES_PER_SESSION = 10
    SESSION_TTL_HOURS = 1
    RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

    def __init__(self):
        """Initialize demo mode."""
        self.sessions: Dict[str, DemoSession] = {}
        self.rate_limiter: Dict[str, list] = defaultdict(list)
        self.detector = SensitiveDataDetector(
            threshold=DetectionThreshold.HIGH
        )
        self.redactor = RedactionEngine(audit_logging=True)
        self.logger = logging.getLogger(__name__)
        self.sandboxed = True  # Disable external API calls

    def create_session(self, ip_address: str) -> Optional[str]:
        """
        Create a new demo session.

        Args:
            ip_address: Client IP address

        Returns:
            Session ID if allowed, None if rate limited
        """
        # Check rate limiting
        if not self._check_rate_limit(ip_address):
            self.logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return None

        # Clean up expired sessions
        self._cleanup_expired_sessions()

        # Create new session
        session_id = self._generate_session_id(ip_address)
        session = DemoSession(
            session_id=session_id,
            created_at=datetime.utcnow(),
            ip_address=ip_address
        )

        self.sessions[session_id] = session
        self.logger.info(f"Created demo session: {session_id}")

        return session_id

    def is_demo_allowed(self, session_id: str) -> bool:
        """
        Check if demo is allowed for session.

        Args:
            session_id: Session ID

        Returns:
            True if demo allowed, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        if session.is_expired():
            self._remove_session(session_id)
            return False

        return session.can_create_trace(self.MAX_TRACES_PER_SESSION)

    def process_reasoning_trace(
        self,
        session_id: str,
        trace_text: str,
        redaction_mode: RedactionMode = RedactionMode.FULL
    ) -> Dict[str, Any]:
        """
        Process reasoning trace in demo mode.

        Args:
            session_id: Session ID
            trace_text: Reasoning trace text
            redaction_mode: Redaction mode (default: FULL)

        Returns:
            Dictionary with redacted trace and metadata
        """
        # Verify session
        if not self.is_demo_allowed(session_id):
            return {
                'success': False,
                'error': 'Session expired or rate limited',
                'trace': None
            }

        # Detect sensitive data
        detections = self.detector.detect(trace_text)

        # Redact sensitive data
        redacted_trace = self.redactor.redact(
            trace_text,
            detections,
            redaction_mode
        )

        # Add watermark
        redacted_trace = f"{self.WATERMARK}\n\n{redacted_trace}"

        # Update session
        session = self.sessions[session_id]
        session.trace_count += 1

        # Log processing
        self.logger.info(
            f"Processed trace for session {session_id}: "
            f"{len(detections)} detections, mode={redaction_mode.value}"
        )

        return {
            'success': True,
            'trace': redacted_trace,
            'detections_count': len(detections),
            'session_traces_remaining': self.MAX_TRACES_PER_SESSION - session.trace_count,
            'session_expires_at': session.expires_at.isoformat(),
            'watermark': self.WATERMARK
        }

    def _check_rate_limit(self, ip_address: str) -> bool:
        """
        Check if IP address is rate limited.

        Args:
            ip_address: Client IP address

        Returns:
            True if allowed, False if rate limited
        """
        current_time = time.time()
        window_start = current_time - self.RATE_LIMIT_WINDOW

        # Clean old timestamps
        self.rate_limiter[ip_address] = [
            ts for ts in self.rate_limiter[ip_address]
            if ts > window_start
        ]

        # Check limit
        if len(self.rate_limiter[ip_address]) >= self.MAX_TRACES_PER_SESSION:
            return False

        # Record this request
        self.rate_limiter[ip_address].append(current_time)
        return True

    def _cleanup_expired_sessions(self):
        """Remove expired sessions to free memory."""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]

        for session_id in expired:
            self._remove_session(session_id)

    def _remove_session(self, session_id: str):
        """
        Remove session and clean up resources.

        Args:
            session_id: Session ID to remove
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Removed session: {session_id}")

    def _generate_session_id(self, ip_address: str) -> str:
        """
        Generate unique session ID.

        Args:
            ip_address: Client IP address

        Returns:
            Session ID
        """
        import hashlib
        timestamp = str(time.time())
        data = f"{ip_address}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            Session info dictionary or None
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'trace_count': session.trace_count,
            'traces_remaining': self.MAX_TRACES_PER_SESSION - session.trace_count,
            'is_expired': session.is_expired()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get demo mode statistics.

        Returns:
            Statistics dictionary
        """
        active_sessions = sum(
            1 for s in self.sessions.values()
            if not s.is_expired()
        )

        return {
            'active_sessions': active_sessions,
            'total_sessions': len(self.sessions),
            'redactor_stats': self.redactor.get_statistics(),
            'rate_limited_ips': len([
                ips for ips in self.rate_limiter.values()
                if len(ips) >= self.MAX_TRACES_PER_SESSION
            ])
        }

    def is_sandboxed(self) -> bool:
        """Check if demo mode is sandboxed (no external API calls)."""
        return self.sandboxed

    def disable_external_calls(self):
        """Disable external API calls (safety measure)."""
        self.sandboxed = True
        self.logger.info("External API calls disabled (sandboxed mode)")
