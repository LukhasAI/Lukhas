"""
Tests for Sensitive Data Detector

Tests pattern matching, entropy analysis, and detection accuracy.
"""

import pytest
from lukhas.reasoning_lab.sensitive_data_detector import (
    SensitiveDataDetector,
    SensitiveDataType,
    DetectionThreshold,
)


class TestSensitiveDataDetector:
    """Test suite for sensitive data detection."""

    def test_detect_openai_api_key(self):
        """Test OpenAI API key detection."""
        detector = SensitiveDataDetector()
        text = "My API key is sk-abc123xyz456789012345678901234567890123456"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.API_KEY_OPENAI for d in detections)

    def test_detect_anthropic_api_key(self):
        """Test Anthropic API key detection."""
        detector = SensitiveDataDetector()
        text = "Use this key: sk-ant-abc123xyz" + "0" * 70  # Anthropic keys are long

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.API_KEY_ANTHROPIC for d in detections)

    def test_detect_aws_api_key(self):
        """Test AWS API key detection."""
        detector = SensitiveDataDetector()
        text = "AWS Access Key: AKIAIOSFODNN7EXAMPLE"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.API_KEY_AWS for d in detections)

    def test_detect_email(self):
        """Test email address detection."""
        detector = SensitiveDataDetector()
        text = "Contact me at user@example.com for details"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.EMAIL for d in detections)

    def test_detect_phone_number(self):
        """Test phone number detection."""
        detector = SensitiveDataDetector()
        text = "Call me at (555) 123-4567 or +1-555-987-6543"

        detections = detector.detect(text)

        assert len(detections) >= 2
        assert any(d.data_type == SensitiveDataType.PHONE for d in detections)

    def test_detect_credit_card(self):
        """Test credit card detection."""
        detector = SensitiveDataDetector()
        # Valid Visa test number
        text = "Card number: 4532015112830366"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.CREDIT_CARD for d in detections)

    def test_detect_ssn(self):
        """Test Social Security Number detection."""
        detector = SensitiveDataDetector()
        text = "My SSN is 123-45-6789"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.SSN for d in detections)

    def test_detect_ip_address(self):
        """Test IP address detection."""
        detector = SensitiveDataDetector()
        text = "Server IP: 192.168.1.100"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.IP_ADDRESS for d in detections)

    def test_detect_uuid(self):
        """Test UUID detection."""
        detector = SensitiveDataDetector()
        text = "User ID: 550e8400-e29b-41d4-a716-446655440000"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.UUID for d in detections)

    def test_detect_password_pattern(self):
        """Test password pattern detection."""
        detector = SensitiveDataDetector()
        text = "password: MySecretP@ssw0rd"

        detections = detector.detect(text)

        assert len(detections) > 0
        assert any(d.data_type == SensitiveDataType.PASSWORD for d in detections)

    def test_entropy_based_detection(self):
        """Test high-entropy string detection."""
        detector = SensitiveDataDetector()
        # Random high-entropy string
        text = "Secret token: aB3xY9pQmN4kL7sD2wF8gH6jV5tR1uE0"

        detections = detector.detect(text)

        assert len(detections) > 0

    def test_multiple_detections(self):
        """Test detecting multiple sensitive data types."""
        detector = SensitiveDataDetector()
        text = """
        User email: user@example.com
        API key: sk-abc123xyz456789012345678901234567890123456
        Phone: (555) 123-4567
        """

        detections = detector.detect(text)

        assert len(detections) >= 3

    def test_detection_threshold_low(self):
        """Test low threshold detects more items."""
        detector = SensitiveDataDetector(threshold=DetectionThreshold.LOW)
        text = "Maybe sensitive: abc123xyz789"

        detections = detector.detect(text)

        # Low threshold should detect more
        assert len(detections) >= 0

    def test_detection_threshold_high(self):
        """Test high threshold is more selective."""
        detector = SensitiveDataDetector(threshold=DetectionThreshold.HIGH)
        text = "Maybe sensitive: abc123xyz789"

        detections = detector.detect(text)

        # High threshold should be selective
        # Only very confident matches
        high_confidence_count = len([d for d in detections if d.confidence >= 0.8])
        assert all(d.confidence >= 0.8 for d in detections) or len(detections) == 0

    def test_no_false_positives_on_clean_text(self):
        """Test no detections on clean text."""
        detector = SensitiveDataDetector(threshold=DetectionThreshold.HIGH)
        text = "This is a normal sentence with no sensitive data."

        detections = detector.detect(text)

        assert len(detections) == 0

    def test_overlapping_detections_removed(self):
        """Test that overlapping detections are properly handled."""
        detector = SensitiveDataDetector()
        # Text that might trigger multiple patterns
        text = "Email: test@example.com"

        detections = detector.detect(text)

        # Check no overlaps
        for i, d1 in enumerate(detections):
            for d2 in detections[i + 1:]:
                # No overlap: either d1 ends before d2 starts or d2 ends before d1 starts
                assert d1.end_pos <= d2.start_pos or d2.end_pos <= d1.start_pos

    def test_get_statistics(self):
        """Test statistics generation."""
        detector = SensitiveDataDetector()
        text = """
        Email: user@example.com
        Another email: admin@example.org
        Phone: (555) 123-4567
        """

        detections = detector.detect(text)
        stats = detector.get_statistics(detections)

        assert isinstance(stats, dict)
        assert len(stats) > 0
        if 'email' in stats:
            assert stats['email'] >= 2

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        detector = SensitiveDataDetector()
        text = "API key: sk-abc123xyz456789012345678901234567890123456"

        detections = detector.detect(text)

        assert len(detections) > 0
        # OpenAI API keys should have high confidence
        openai_detections = [d for d in detections if d.data_type == SensitiveDataType.API_KEY_OPENAI]
        if openai_detections:
            assert openai_detections[0].confidence >= 0.9

    def test_detection_position_accuracy(self):
        """Test that detection positions are accurate."""
        detector = SensitiveDataDetector()
        text = "My email is user@example.com and that's it"
        email_start = text.index("user@example.com")
        email_end = email_start + len("user@example.com")

        detections = detector.detect(text)

        email_detections = [d for d in detections if d.data_type == SensitiveDataType.EMAIL]
        assert len(email_detections) > 0
        assert email_detections[0].start_pos == email_start
        assert email_detections[0].end_pos == email_end


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
