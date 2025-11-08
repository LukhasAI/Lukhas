"""
Sensitive Data Detector

Detects sensitive data in text using pattern-based detection and entropy analysis.
Supports API keys, passwords, PII, credit cards, and other secret formats.
"""

import re
import math
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum


class SensitiveDataType(Enum):
    """Types of sensitive data that can be detected."""
    API_KEY_AWS = "aws_api_key"
    API_KEY_OPENAI = "openai_api_key"
    API_KEY_ANTHROPIC = "anthropic_api_key"
    API_KEY_GOOGLE = "google_api_key"
    PASSWORD = "password"
    EMAIL = "email"
    PHONE = "phone_number"
    CREDIT_CARD = "credit_card"
    SSN = "social_security_number"
    IP_ADDRESS = "ip_address"
    UUID = "uuid"
    SECRET_BASE64 = "secret_base64"
    SECRET_HEX = "secret_hex"
    GENERIC_SECRET = "generic_secret"


class DetectionThreshold(Enum):
    """Detection sensitivity thresholds."""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8


@dataclass
class Detection:
    """Represents a single detection of sensitive data."""
    data_type: SensitiveDataType
    start_pos: int
    end_pos: int
    confidence: float
    matched_text: str


class SensitiveDataDetector:
    """
    Detects sensitive data in text using pattern matching and entropy analysis.

    Examples:
        >>> detector = SensitiveDataDetector()
        >>> text = "My API key is sk-abc123xyz"
        >>> detections = detector.detect(text)
        >>> len(detections) > 0
        True
    """

    # Regex patterns for different sensitive data types
    PATTERNS: Dict[SensitiveDataType, List[str]] = {
        SensitiveDataType.API_KEY_AWS: [
            r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',  # AWS Access Key
            r'\b[A-Za-z0-9/+=]{40}\b',  # AWS Secret Key
        ],
        SensitiveDataType.API_KEY_OPENAI: [
            r'\bsk-[A-Za-z0-9]{48}\b',  # OpenAI API Key
        ],
        SensitiveDataType.API_KEY_ANTHROPIC: [
            r'\bsk-ant-[A-Za-z0-9\-]{95,}\b',  # Anthropic API Key
        ],
        SensitiveDataType.API_KEY_GOOGLE: [
            r'\bAIza[0-9A-Za-z\-_]{35}\b',  # Google API Key
        ],
        SensitiveDataType.EMAIL: [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        SensitiveDataType.PHONE: [
            r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',  # US format
            r'\+\d{1,3}\s?\d{1,14}\b',  # International format
        ],
        SensitiveDataType.CREDIT_CARD: [
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b',
        ],
        SensitiveDataType.SSN: [
            r'\b\d{3}-\d{2}-\d{4}\b',  # XXX-XX-XXXX format
            r'\b\d{9}\b',  # XXXXXXXXX format (9 digits)
        ],
        SensitiveDataType.IP_ADDRESS: [
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IPv4
            r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',  # IPv6
        ],
        SensitiveDataType.UUID: [
            r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b',
        ],
        SensitiveDataType.SECRET_BASE64: [
            r'\b(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?(?=\s|$)',
        ],
        SensitiveDataType.SECRET_HEX: [
            r'\b[0-9a-fA-F]{32,128}\b',  # 32-128 char hex strings
        ],
        SensitiveDataType.PASSWORD: [
            r'(?:password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']+)["\']?',
            r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']?([^\s"\']+)["\']?',
            r'(?:secret|token)\s*[:=]\s*["\']?([^\s"\']+)["\']?',
        ],
    }

    def __init__(self, threshold: DetectionThreshold = DetectionThreshold.MEDIUM):
        """
        Initialize detector with specified sensitivity threshold.

        Args:
            threshold: Detection sensitivity (LOW, MEDIUM, HIGH)
        """
        self.threshold = threshold
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[SensitiveDataType, List[re.Pattern]]:
        """Compile all regex patterns for efficient matching."""
        compiled = {}
        for data_type, patterns in self.PATTERNS.items():
            compiled[data_type] = [re.compile(p, re.IGNORECASE) for p in patterns]
        return compiled

    def detect(self, text: str) -> List[Detection]:
        """
        Detect sensitive data in text.

        Args:
            text: Text to scan for sensitive data

        Returns:
            List of Detection objects with type, position, and confidence
        """
        detections = []

        # Pattern-based detection
        for data_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    confidence = self._calculate_confidence(
                        match.group(0), data_type
                    )
                    if confidence >= self.threshold.value:
                        detections.append(Detection(
                            data_type=data_type,
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=confidence,
                            matched_text=match.group(0)
                        ))

        # Entropy-based detection for unknown secrets
        entropy_detections = self._detect_high_entropy_strings(text)
        detections.extend(entropy_detections)

        # Remove overlapping detections (keep higher confidence)
        detections = self._remove_overlaps(detections)

        return sorted(detections, key=lambda d: d.start_pos)

    def _calculate_confidence(self, text: str, data_type: SensitiveDataType) -> float:
        """
        Calculate confidence score for a match.

        Args:
            text: Matched text
            data_type: Type of sensitive data

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from pattern match
        confidence = 0.7

        # Boost for strong indicators
        if data_type in [
            SensitiveDataType.API_KEY_AWS,
            SensitiveDataType.API_KEY_OPENAI,
            SensitiveDataType.API_KEY_ANTHROPIC,
        ]:
            confidence = 0.95  # Very specific patterns

        # Entropy-based boost
        entropy = self._calculate_entropy(text)
        if entropy > 4.0:
            confidence = min(1.0, confidence + 0.1)

        # Length-based adjustment
        if len(text) > 20:
            confidence = min(1.0, confidence + 0.05)

        return confidence

    def _calculate_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy of text.

        Higher entropy suggests more randomness (potential secret).

        Args:
            text: Text to analyze

        Returns:
            Entropy value (0.0 = no entropy, higher = more random)
        """
        if not text:
            return 0.0

        # Count character frequencies
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
        entropy = 0.0
        text_len = len(text)
        for count in freq.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)

        return entropy

    def _detect_high_entropy_strings(self, text: str) -> List[Detection]:
        """
        Detect high-entropy strings that might be secrets.

        Args:
            text: Text to analyze

        Returns:
            List of detections for high-entropy strings
        """
        detections = []

        # Find potential secret strings (20+ chars, no spaces)
        pattern = re.compile(r'\b[A-Za-z0-9\-_+/=]{20,}\b')

        for match in pattern.finditer(text):
            matched_text = match.group(0)
            entropy = self._calculate_entropy(matched_text)

            # High entropy suggests randomness (potential secret)
            if entropy > 4.5:
                confidence = min(0.9, entropy / 5.5)
                if confidence >= self.threshold.value:
                    detections.append(Detection(
                        data_type=SensitiveDataType.GENERIC_SECRET,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        matched_text=matched_text
                    ))

        return detections

    def _remove_overlaps(self, detections: List[Detection]) -> List[Detection]:
        """
        Remove overlapping detections, keeping higher confidence ones.

        Args:
            detections: List of detections

        Returns:
            Filtered list without overlaps
        """
        if not detections:
            return []

        # Sort by confidence (descending) then by position
        sorted_detections = sorted(
            detections,
            key=lambda d: (-d.confidence, d.start_pos)
        )

        result = []
        used_ranges = []

        for detection in sorted_detections:
            # Check if this detection overlaps with any kept detection
            overlaps = False
            for used_start, used_end in used_ranges:
                if not (detection.end_pos <= used_start or detection.start_pos >= used_end):
                    overlaps = True
                    break

            if not overlaps:
                result.append(detection)
                used_ranges.append((detection.start_pos, detection.end_pos))

        return result

    def get_statistics(self, detections: List[Detection]) -> Dict[str, int]:
        """
        Get statistics about detections.

        Args:
            detections: List of detections

        Returns:
            Dictionary with detection counts by type
        """
        stats = {}
        for detection in detections:
            type_name = detection.data_type.value
            stats[type_name] = stats.get(type_name, 0) + 1
        return stats
