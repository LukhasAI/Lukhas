"""
Tests for Demo Mode

Tests session management, rate limiting, and sandboxing.
"""

import pytest
import time
from lukhas.reasoning_lab.demo_mode import DemoMode, DemoSession
from lukhas.reasoning_lab.redaction_engine import RedactionMode
from datetime import datetime, timedelta


class TestDemoMode:
    """Test suite for privacy-preserving demo mode."""

    def test_create_session(self):
        """Test session creation."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        assert session_id is not None
        assert len(session_id) > 0

    def test_session_info(self):
        """Test retrieving session information."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        info = demo.get_session_info(session_id)

        assert info is not None
        assert info['session_id'] == session_id
        assert 'created_at' in info
        assert 'expires_at' in info

    def test_demo_allowed_for_new_session(self):
        """Test demo is allowed for new sessions."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        assert demo.is_demo_allowed(session_id) is True

    def test_demo_not_allowed_for_invalid_session(self):
        """Test demo is blocked for invalid sessions."""
        demo = DemoMode()

        assert demo.is_demo_allowed("invalid_session_id") is False

    def test_rate_limiting(self):
        """Test rate limiting prevents abuse."""
        demo = DemoMode()

        # Create multiple sessions from same IP
        sessions = []
        for i in range(15):
            session_id = demo.create_session("192.168.1.1")
            if session_id:
                sessions.append(session_id)

        # Should be rate limited after MAX_TRACES_PER_SESSION
        assert len(sessions) <= demo.MAX_TRACES_PER_SESSION + 2

    def test_process_reasoning_trace(self):
        """Test processing reasoning trace with redaction."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        trace = "My reasoning with API key sk-abc123xyz456789012345678901234567890123456"

        result = demo.process_reasoning_trace(
            session_id,
            trace,
            RedactionMode.FULL
        )

        assert result['success'] is True
        assert 'trace' in result
        assert demo.WATERMARK in result['trace']
        assert 'sk-abc' not in result['trace']

    def test_watermark_added(self):
        """Test watermark is added to traces."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        result = demo.process_reasoning_trace(
            session_id,
            "Clean reasoning trace",
            RedactionMode.FULL
        )

        assert demo.WATERMARK in result['trace']

    def test_trace_count_limit(self):
        """Test trace count limit enforcement."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        # Process up to limit
        for i in range(demo.MAX_TRACES_PER_SESSION):
            result = demo.process_reasoning_trace(
                session_id,
                f"Trace {i}",
                RedactionMode.FULL
            )
            assert result['success'] is True

        # Next one should fail
        result = demo.process_reasoning_trace(
            session_id,
            "One more trace",
            RedactionMode.FULL
        )
        assert result['success'] is False

    def test_session_expiration(self):
        """Test sessions expire after TTL."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        # Manually expire session
        session = demo.sessions[session_id]
        session.expires_at = datetime.utcnow() - timedelta(hours=1)

        # Should not be allowed
        assert demo.is_demo_allowed(session_id) is False

    def test_expired_sessions_cleaned_up(self):
        """Test expired sessions are removed."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        # Expire session
        session = demo.sessions[session_id]
        session.expires_at = datetime.utcnow() - timedelta(hours=1)

        # Trigger cleanup
        demo._cleanup_expired_sessions()

        assert session_id not in demo.sessions

    def test_sandboxed_mode(self):
        """Test demo mode is sandboxed."""
        demo = DemoMode()

        assert demo.is_sandboxed() is True

    def test_disable_external_calls(self):
        """Test external calls can be disabled."""
        demo = DemoMode()
        demo.sandboxed = False

        demo.disable_external_calls()

        assert demo.is_sandboxed() is True

    def test_get_statistics(self):
        """Test statistics generation."""
        demo = DemoMode()
        session_id1 = demo.create_session("192.168.1.1")
        session_id2 = demo.create_session("192.168.1.2")

        stats = demo.get_statistics()

        assert 'active_sessions' in stats
        assert stats['active_sessions'] >= 2

    def test_detection_counts_reported(self):
        """Test detection counts are reported."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        trace = "Email: user@example.com, Phone: (555) 123-4567"

        result = demo.process_reasoning_trace(
            session_id,
            trace,
            RedactionMode.FULL
        )

        assert 'detections_count' in result
        assert result['detections_count'] > 0

    def test_session_traces_remaining_updated(self):
        """Test traces remaining count is updated."""
        demo = DemoMode()
        session_id = demo.create_session("192.168.1.1")

        result = demo.process_reasoning_trace(
            session_id,
            "First trace",
            RedactionMode.FULL
        )

        assert 'session_traces_remaining' in result
        assert result['session_traces_remaining'] == demo.MAX_TRACES_PER_SESSION - 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
