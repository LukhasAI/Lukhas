"""
Redaction Engine

Redacts sensitive data from text with multiple redaction modes.
Supports full, partial, hash, and blur redaction with audit logging.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

from .sensitive_data_detector import Detection, SensitiveDataType


class RedactionMode(Enum):
    """Redaction modes with different privacy levels."""
    FULL = "full"  # Replace with [REDACTED-{TYPE}]
    PARTIAL = "partial"  # Show first/last 4 chars
    HASH = "hash"  # Show SHA-256 hash prefix
    BLUR = "blur"  # Show placeholder length


@dataclass
class RedactionRecord:
    """Record of a redaction operation for audit logging."""
    timestamp: str
    data_type: str
    redaction_mode: str
    original_length: int
    hash_value: str
    position: int


class RedactionEngine:
    """
    Redacts sensitive data with configurable modes and audit logging.

    Examples:
        >>> from sensitive_data_detector import SensitiveDataDetector
        >>> detector = SensitiveDataDetector()
        >>> engine = RedactionEngine()
        >>> text = "My API key is sk-abc123xyz"
        >>> detections = detector.detect(text)
        >>> redacted = engine.redact(text, detections, RedactionMode.FULL)
        >>> "REDACTED" in redacted
        True
    """

    def __init__(self, audit_logging: bool = True):
        """
        Initialize redaction engine.

        Args:
            audit_logging: Enable audit logging of redactions
        """
        self.audit_logging = audit_logging
        self.redaction_log: List[RedactionRecord] = []
        self.redaction_mapping: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)

    def redact(
        self,
        text: str,
        detections: List[Detection],
        mode: RedactionMode = RedactionMode.FULL,
    ) -> str:
        """
        Redact sensitive data from text.

        Args:
            text: Original text with sensitive data
            detections: List of detections from SensitiveDataDetector
            mode: Redaction mode to use

        Returns:
            Redacted text with sensitive data removed/masked
        """
        if not detections:
            return text

        # Sort detections by position (reverse to maintain indices)
        sorted_detections = sorted(
            detections,
            key=lambda d: d.start_pos,
            reverse=True
        )

        redacted_text = text
        for detection in sorted_detections:
            original = detection.matched_text
            redacted = self._apply_redaction(original, detection, mode)

            # Replace in text
            redacted_text = (
                redacted_text[:detection.start_pos] +
                redacted +
                redacted_text[detection.end_pos:]
            )

            # Audit logging
            if self.audit_logging:
                self._log_redaction(detection, mode, original)

        return redacted_text

    def _apply_redaction(
        self,
        text: str,
        detection: Detection,
        mode: RedactionMode
    ) -> str:
        """
        Apply redaction based on mode.

        Args:
            text: Text to redact
            detection: Detection information
            mode: Redaction mode

        Returns:
            Redacted version of text
        """
        if mode == RedactionMode.FULL:
            return self._redact_full(detection.data_type)

        elif mode == RedactionMode.PARTIAL:
            return self._redact_partial(text)

        elif mode == RedactionMode.HASH:
            return self._redact_hash(text)

        elif mode == RedactionMode.BLUR:
            return self._redact_blur(text)

        return text

    def _redact_full(self, data_type: SensitiveDataType) -> str:
        """
        Full redaction: Replace with [REDACTED-{TYPE}].

        Args:
            data_type: Type of sensitive data

        Returns:
            Redacted placeholder
        """
        type_name = data_type.value.upper().replace("_", "-")
        return f"[REDACTED-{type_name}]"

    def _redact_partial(self, text: str) -> str:
        """
        Partial redaction: Show first/last 4 chars.

        Args:
            text: Original text

        Returns:
            Partially redacted text (e.g., "sk-a...xyz")
        """
        if len(text) <= 8:
            return "*" * len(text)

        first_4 = text[:4]
        last_3 = text[-3:]
        return f"{first_4}...{last_3}"

    def _redact_hash(self, text: str) -> str:
        """
        Hash redaction: Show SHA-256 hash prefix.

        Args:
            text: Original text

        Returns:
            Hash-based redaction (e.g., "hash:a1b2c3...")
        """
        hash_value = hashlib.sha256(text.encode()).hexdigest()
        return f"hash:{hash_value[:8]}..."

    def _redact_blur(self, text: str) -> str:
        """
        Blur redaction: Show placeholder length.

        Args:
            text: Original text

        Returns:
            Blurred text with same length (e.g., "****-****-****")
        """
        # Create pattern with dashes every 4 chars for readability
        result = []
        for i, char in enumerate(text):
            if char.isalnum():
                result.append('*')
            else:
                result.append(char)  # Preserve special chars
        return ''.join(result)

    def _log_redaction(
        self,
        detection: Detection,
        mode: RedactionMode,
        original_text: str
    ):
        """
        Log redaction operation for audit trail.

        Args:
            detection: Detection information
            mode: Redaction mode used
            original_text: Original text (hashed for security)
        """
        hash_value = hashlib.sha256(original_text.encode()).hexdigest()

        record = RedactionRecord(
            timestamp=datetime.utcnow().isoformat(),
            data_type=detection.data_type.value,
            redaction_mode=mode.value,
            original_length=len(original_text),
            hash_value=hash_value,
            position=detection.start_pos
        )

        self.redaction_log.append(record)

        # Store reversible mapping (for authorized users only)
        self.redaction_mapping[hash_value] = original_text

        self.logger.info(
            f"Redacted {detection.data_type.value} at position "
            f"{detection.start_pos} using {mode.value} mode"
        )

    def get_audit_log(self) -> List[Dict]:
        """
        Get audit log of all redactions.

        Returns:
            List of redaction records as dictionaries
        """
        return [asdict(record) for record in self.redaction_log]

    def export_audit_log(self, filepath: str):
        """
        Export audit log to JSON file.

        Args:
            filepath: Path to export file
        """
        with open(filepath, 'w') as f:
            json.dump(self.get_audit_log(), f, indent=2)

    def reverse_redaction(self, hash_value: str, authorized: bool = False) -> Optional[str]:
        """
        Reverse redaction for authorized users.

        Args:
            hash_value: Hash of redacted text
            authorized: Whether user is authorized to reverse

        Returns:
            Original text if authorized, None otherwise
        """
        if not authorized:
            self.logger.warning("Unauthorized attempt to reverse redaction")
            return None

        return self.redaction_mapping.get(hash_value)

    def clear_audit_log(self):
        """Clear audit log and redaction mapping (use with caution)."""
        self.redaction_log.clear()
        self.redaction_mapping.clear()
        self.logger.info("Audit log and redaction mapping cleared")

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about redactions.

        Returns:
            Dictionary with redaction counts by type and mode
        """
        stats = {
            'total_redactions': len(self.redaction_log),
            'by_type': {},
            'by_mode': {}
        }

        for record in self.redaction_log:
            # Count by type
            data_type = record.data_type
            stats['by_type'][data_type] = stats['by_type'].get(data_type, 0) + 1

            # Count by mode
            mode = record.redaction_mode
            stats['by_mode'][mode] = stats['by_mode'].get(mode, 0) + 1

        return stats
