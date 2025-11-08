"""
Tests for Redaction Engine

Tests all redaction modes and audit logging.
"""

import pytest
import tempfile
import json
from lukhas.reasoning_lab.sensitive_data_detector import (
    SensitiveDataDetector,
    Detection,
    SensitiveDataType,
)
from lukhas.reasoning_lab.redaction_engine import (
    RedactionEngine,
    RedactionMode,
)


class TestRedactionEngine:
    """Test suite for redaction engine."""

    def test_full_redaction(self):
        """Test full redaction mode."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine()

        text = "My API key is sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)

        redacted = engine.redact(text, detections, RedactionMode.FULL)

        assert "sk-abc" not in redacted
        assert "REDACTED" in redacted

    def test_partial_redaction(self):
        """Test partial redaction mode."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine()

        text = "My API key is sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)

        redacted = engine.redact(text, detections, RedactionMode.PARTIAL)

        # Should show first/last chars
        assert "..." in redacted

    def test_hash_redaction(self):
        """Test hash redaction mode."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine()

        text = "My API key is sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)

        redacted = engine.redact(text, detections, RedactionMode.HASH)

        assert "hash:" in redacted

    def test_blur_redaction(self):
        """Test blur redaction mode."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine()

        text = "My API key is sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)

        redacted = engine.redact(text, detections, RedactionMode.BLUR)

        assert "*" in redacted

    def test_multiple_redactions(self):
        """Test redacting multiple sensitive items."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine()

        text = "Email: user@example.com, Phone: (555) 123-4567"
        detections = detector.detect(text)

        redacted = engine.redact(text, detections, RedactionMode.FULL)

        # Both should be redacted
        assert "user@example.com" not in redacted
        assert "(555) 123-4567" not in redacted
        assert "REDACTED" in redacted

    def test_no_redaction_without_detections(self):
        """Test that clean text is not modified."""
        engine = RedactionEngine()
        text = "This is clean text with no sensitive data."

        redacted = engine.redact(text, [], RedactionMode.FULL)

        assert redacted == text

    def test_audit_logging_enabled(self):
        """Test audit logging records redactions."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine(audit_logging=True)

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)

        engine.redact(text, detections, RedactionMode.FULL)

        audit_log = engine.get_audit_log()
        assert len(audit_log) > 0

    def test_audit_logging_disabled(self):
        """Test audit logging can be disabled."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine(audit_logging=False)

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)

        engine.redact(text, detections, RedactionMode.FULL)

        audit_log = engine.get_audit_log()
        assert len(audit_log) == 0

    def test_export_audit_log(self):
        """Test exporting audit log to file."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine(audit_logging=True)

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)
        engine.redact(text, detections, RedactionMode.FULL)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name

        engine.export_audit_log(filepath)

        with open(filepath, 'r') as f:
            data = json.load(f)

        assert len(data) > 0
        assert 'timestamp' in data[0]

    def test_reverse_redaction_unauthorized(self):
        """Test reverse redaction fails without authorization."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine(audit_logging=True)

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)
        engine.redact(text, detections, RedactionMode.FULL)

        # Try to reverse without authorization
        result = engine.reverse_redaction("some_hash", authorized=False)

        assert result is None

    def test_get_statistics(self):
        """Test statistics generation."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine(audit_logging=True)

        text = """
        Email: user@example.com
        Phone: (555) 123-4567
        API key: sk-abc123xyz456789012345678901234567890123456
        """
        detections = detector.detect(text)
        engine.redact(text, detections, RedactionMode.FULL)

        stats = engine.get_statistics()

        assert stats['total_redactions'] > 0
        assert 'by_type' in stats
        assert 'by_mode' in stats

    def test_clear_audit_log(self):
        """Test clearing audit log."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine(audit_logging=True)

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = detector.detect(text)
        engine.redact(text, detections, RedactionMode.FULL)

        assert len(engine.get_audit_log()) > 0

        engine.clear_audit_log()

        assert len(engine.get_audit_log()) == 0

    def test_redaction_preserves_text_structure(self):
        """Test that redaction preserves overall text structure."""
        detector = SensitiveDataDetector()
        engine = RedactionEngine()

        text = "Before email: user@example.com After"
        detections = detector.detect(text)

        redacted = engine.redact(text, detections, RedactionMode.FULL)

        assert redacted.startswith("Before email:")
        assert redacted.endswith("After")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
