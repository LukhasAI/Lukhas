#!/usr/bin/env python3
"""
Reasoning Lab Safety Compliance Validator

Validates that reasoning lab safety controls meet compliance requirements:
- Detection accuracy >= 95%
- All 4 redaction modes functional
- Demo mode properly sandboxed
- Audit logging working
- Documentation complete
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lukhas.reasoning_lab.sensitive_data_detector import (
    SensitiveDataDetector,
    SensitiveDataType,
    DetectionThreshold,
)
from lukhas.reasoning_lab.redaction_engine import RedactionEngine, RedactionMode
from lukhas.reasoning_lab.demo_mode import DemoMode


class ValidationResult:
    """Result of a validation check."""

    def __init__(self, name: str, passed: bool, message: str):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status}: {self.name}\n   {self.message}"


class SafetyValidator:
    """Validates reasoning lab safety controls compliance."""

    def __init__(self):
        self.results: List[ValidationResult] = []
        self.detector = SensitiveDataDetector()
        self.redactor = RedactionEngine(audit_logging=True)
        self.demo = DemoMode()

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating Reasoning Lab Safety Controls\n")

        # Detection accuracy
        self.validate_detection_accuracy()

        # Redaction modes
        self.validate_redaction_modes()

        # Demo mode
        self.validate_demo_mode()

        # Audit logging
        self.validate_audit_logging()

        # Documentation
        self.validate_documentation()

        # Print results
        print("\n📊 Validation Results:\n")
        for result in self.results:
            print(result)

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        print(f"\n{'='*60}")
        print(f"Total: {passed}/{total} checks passed ({(passed/total)*100:.1f}%)")
        print(f"{'='*60}\n")

        return all(r.passed for r in self.results)

    def validate_detection_accuracy(self):
        """Validate detection accuracy >= 95%."""
        print("📌 Testing detection accuracy...")

        test_cases = [
            ("sk-abc123xyz456789012345678901234567890123456", SensitiveDataType.API_KEY_OPENAI),
            ("sk-ant-" + "x" * 90, SensitiveDataType.API_KEY_ANTHROPIC),
            ("AKIAIOSFODNN7EXAMPLE", SensitiveDataType.API_KEY_AWS),
            ("user@example.com", SensitiveDataType.EMAIL),
            ("(555) 123-4567", SensitiveDataType.PHONE),
            ("4532015112830366", SensitiveDataType.CREDIT_CARD),
            ("123-45-6789", SensitiveDataType.SSN),
        ]

        detected = 0
        for text, expected_type in test_cases:
            detections = self.detector.detect(text)
            if any(d.data_type == expected_type for d in detections):
                detected += 1

        accuracy = (detected / len(test_cases)) * 100

        self.results.append(ValidationResult(
            "Detection Accuracy",
            accuracy >= 95.0,
            f"Detected {detected}/{len(test_cases)} test cases ({accuracy:.1f}%)"
        ))

    def validate_redaction_modes(self):
        """Validate all 4 redaction modes work."""
        print("📌 Testing redaction modes...")

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = self.detector.detect(text)

        modes = [
            (RedactionMode.FULL, "[REDACTED"),
            (RedactionMode.PARTIAL, "..."),
            (RedactionMode.HASH, "hash:"),
            (RedactionMode.BLUR, "*"),
        ]

        all_passed = True
        for mode, expected_marker in modes:
            redacted = self.redactor.redact(text, detections, mode)

            if expected_marker not in redacted:
                all_passed = False
                self.results.append(ValidationResult(
                    f"Redaction Mode: {mode.value}",
                    False,
                    f"Expected marker '{expected_marker}' not found in output"
                ))
            else:
                self.results.append(ValidationResult(
                    f"Redaction Mode: {mode.value}",
                    True,
                    f"Mode working correctly (marker: '{expected_marker}')"
                ))

    def validate_demo_mode(self):
        """Validate demo mode is properly sandboxed."""
        print("📌 Testing demo mode...")

        # Test session creation
        session_id = self.demo.create_session("192.168.1.1")
        session_created = session_id is not None

        self.results.append(ValidationResult(
            "Demo Mode: Session Creation",
            session_created,
            "Session created successfully" if session_created else "Failed to create session"
        ))

        if not session_created:
            return

        # Test watermark
        result = self.demo.process_reasoning_trace(
            session_id,
            "Test trace",
            RedactionMode.FULL
        )

        watermark_present = self.demo.WATERMARK in result.get('trace', '')

        self.results.append(ValidationResult(
            "Demo Mode: Watermark",
            watermark_present,
            "Watermark added to traces" if watermark_present else "Watermark missing"
        ))

        # Test sandboxing
        sandboxed = self.demo.is_sandboxed()

        self.results.append(ValidationResult(
            "Demo Mode: Sandboxing",
            sandboxed,
            "Demo mode is sandboxed (no external calls)" if sandboxed else "WARNING: Not sandboxed"
        ))

        # Test rate limiting
        # Try to exceed limit
        for i in range(self.demo.MAX_TRACES_PER_SESSION + 5):
            result = self.demo.process_reasoning_trace(
                session_id,
                f"Trace {i}",
                RedactionMode.FULL
            )

        # Last one should fail
        final_result = self.demo.process_reasoning_trace(
            session_id,
            "Final trace",
            RedactionMode.FULL
        )

        rate_limited = not final_result['success']

        self.results.append(ValidationResult(
            "Demo Mode: Rate Limiting",
            rate_limited,
            f"Rate limit enforced ({self.demo.MAX_TRACES_PER_SESSION} traces)" if rate_limited
            else "WARNING: Rate limiting not working"
        ))

    def validate_audit_logging(self):
        """Validate audit logging is working."""
        print("📌 Testing audit logging...")

        text = "API key: sk-abc123xyz456789012345678901234567890123456"
        detections = self.detector.detect(text)

        # Clear any existing logs
        self.redactor.clear_audit_log()

        # Perform redaction
        self.redactor.redact(text, detections, RedactionMode.FULL)

        # Check audit log
        audit_log = self.redactor.get_audit_log()
        log_created = len(audit_log) > 0

        self.results.append(ValidationResult(
            "Audit Logging: Recording",
            log_created,
            f"Audit log contains {len(audit_log)} entries" if log_created
            else "No audit log entries created"
        ))

        if log_created:
            # Validate log structure
            first_entry = audit_log[0]
            has_required_fields = all(
                field in first_entry
                for field in ['timestamp', 'data_type', 'redaction_mode', 'hash_value']
            )

            self.results.append(ValidationResult(
                "Audit Logging: Structure",
                has_required_fields,
                "Audit log has all required fields" if has_required_fields
                else "Audit log missing required fields"
            ))

    def validate_documentation(self):
        """Validate documentation completeness."""
        print("📌 Checking documentation...")

        docs_dir = Path(__file__).parent.parent / "docs" / "reasoning_lab"
        safety_doc = docs_dir / "SAFETY_CONTROLS.md"

        doc_exists = safety_doc.exists()

        self.results.append(ValidationResult(
            "Documentation: Existence",
            doc_exists,
            f"Found at {safety_doc}" if doc_exists else f"Missing: {safety_doc}"
        ))

        if doc_exists:
            content = safety_doc.read_text()

            # Check for key sections
            required_sections = [
                "## Overview",
                "## How Redaction Works",
                "## Demo Mode Usage",
                "## Privacy Guarantees",
                "## Troubleshooting",
            ]

            all_sections_present = all(section in content for section in required_sections)

            self.results.append(ValidationResult(
                "Documentation: Completeness",
                all_sections_present,
                f"All {len(required_sections)} required sections present"
                if all_sections_present else "Missing required sections"
            ))


def main():
    """Run validation."""
    validator = SafetyValidator()
    success = validator.run_all_validations()

    if success:
        print("✅ All validation checks passed!")
        print("🔒 Reasoning Lab safety controls are compliant")
        return 0
    else:
        print("❌ Some validation checks failed")
        print("⚠️  Please fix the issues above before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
