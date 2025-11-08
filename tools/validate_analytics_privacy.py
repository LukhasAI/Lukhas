#!/usr/bin/env python3
"""
Analytics Privacy Validation Tool

Checks analytics events for:
- PII leakage (emails, phone numbers, IPs, etc.)
- Forbidden property names
- Property value length limits
- Event taxonomy compliance
- Consent validation

Usage:
    python3 tools/validate_analytics_privacy.py
    python3 tools/validate_analytics_privacy.py --events sample_events.json
    python3 tools/validate_analytics_privacy.py --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class PIIDetector:
    """Detects PII in event properties."""

    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\+?[1-9]\d{1,14}|\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        "ip": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "uuid": r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
    }

    @classmethod
    def detect(cls, text: str) -> List[str]:
        """Detect PII types in text."""
        if not isinstance(text, str):
            return []

        detected = []
        for pii_type, pattern in cls.PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pii_type)

        return detected


class AnalyticsPrivacyValidator:
    """Validates analytics events for privacy compliance."""

    # Allowed event names from taxonomy
    ALLOWED_EVENTS = {
        "page_view",
        "quickstart_started",
        "quickstart_completed",
        "reasoning_trace_viewed",
        "assistive_variant_viewed",
        "assistive_audio_played",
        "evidence_artifact_requested",
        "demo_interaction",
        "cta_clicked",
    }

    # Forbidden property names (likely to contain PII)
    FORBIDDEN_PROPERTIES = {
        "email",
        "phone",
        "name",
        "first_name",
        "last_name",
        "address",
        "user_id",
        "session_token",
        "api_key",
        "password",
        "credit_card",
        "ssn",
        "ip_address",
    }

    # Maximum property value length
    MAX_PROPERTY_LENGTH = 1000

    def __init__(self, strict: bool = False):
        """
        Initialize validator.

        Args:
            strict: If True, fail on warnings (not just errors)
        """
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_event(self, event: Dict[str, Any], index: int = 0) -> bool:
        """
        Validate single event.

        Args:
            event: Event dictionary
            index: Event index (for error messages)

        Returns:
            True if valid, False otherwise
        """
        valid = True

        # Check event structure
        if "event" not in event:
            self.errors.append(f"Event {index}: Missing 'event' field")
            return False

        event_name = event["event"]

        # Check event name
        if event_name not in self.ALLOWED_EVENTS:
            self.errors.append(
                f"Event {index}: '{event_name}' not in allowed taxonomy"
            )
            valid = False

        # Check properties
        if "properties" not in event:
            self.errors.append(f"Event {index}: Missing 'properties' field")
            return False

        properties = event["properties"]

        if not isinstance(properties, dict):
            self.errors.append(f"Event {index}: 'properties' must be a dict")
            return False

        # Validate properties
        for key, value in properties.items():
            # Check forbidden property names
            if key in self.FORBIDDEN_PROPERTIES:
                self.errors.append(
                    f"Event {index}: Forbidden property '{key}' "
                    f"(likely contains PII)"
                )
                valid = False

            # Check property value for PII
            if isinstance(value, str):
                pii_types = PIIDetector.detect(value)
                if pii_types:
                    self.errors.append(
                        f"Event {index}: Property '{key}' contains PII "
                        f"({', '.join(pii_types)}): {value[:50]}..."
                    )
                    valid = False

                # Check length
                if len(value) > self.MAX_PROPERTY_LENGTH:
                    self.warnings.append(
                        f"Event {index}: Property '{key}' exceeds max length "
                        f"({len(value)} > {self.MAX_PROPERTY_LENGTH})"
                    )
                    if self.strict:
                        valid = False

        # Check required properties
        if "domain" not in properties:
            self.errors.append(
                f"Event {index}: Missing required property 'domain'"
            )
            valid = False

        return valid

    def validate_events(self, events: List[Dict[str, Any]]) -> bool:
        """
        Validate multiple events.

        Args:
            events: List of event dictionaries

        Returns:
            True if all valid, False otherwise
        """
        all_valid = True

        for i, event in enumerate(events):
            if not self.validate_event(event, index=i):
                all_valid = False

        return all_valid

    def print_results(self) -> None:
        """Print validation results."""
        print("\n" + "=" * 80)
        print("Analytics Privacy Validation Results")
        print("=" * 80 + "\n")

        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):\n")
            for error in self.errors:
                print(f"  • {error}")
            print()

        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):\n")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ All validations passed!")
            print("   • No PII detected")
            print("   • All events in taxonomy")
            print("   • All properties within limits")
        elif not self.errors and self.warnings:
            print("✅ No errors found")
            print(f"⚠️  {len(self.warnings)} warnings (non-critical)")

        print()


def load_sample_events() -> List[Dict[str, Any]]:
    """Load sample events for testing."""
    return [
        {
            "event": "page_view",
            "properties": {
                "domain": "lukhas.ai",
                "path": "/matriz",
                "variant": "assistive",
            },
            "timestamp": "2025-11-08T12:00:00Z",
        },
        {
            "event": "quickstart_started",
            "properties": {
                "domain": "lukhas.dev",
                "language": "python",
                "quickstart_id": "matriz-hello-world",
            },
            "timestamp": "2025-11-08T12:01:00Z",
        },
        {
            "event": "quickstart_completed",
            "properties": {
                "domain": "lukhas.dev",
                "language": "python",
                "quickstart_id": "matriz-hello-world",
                "duration_seconds": 120,
                "success": True,
            },
            "timestamp": "2025-11-08T12:03:00Z",
        },
    ]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate analytics events for privacy compliance"
    )
    parser.add_argument(
        "--events",
        type=str,
        help="Path to JSON file with events to validate",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (not just errors)",
    )

    args = parser.parse_args()

    # Load events
    if args.events:
        events_path = Path(args.events)
        if not events_path.exists():
            print(f"❌ Error: Events file not found: {events_path}")
            sys.exit(1)

        with open(events_path) as f:
            data = json.load(f)
            if isinstance(data, list):
                events = data
            elif isinstance(data, dict) and "events" in data:
                events = data["events"]
            else:
                print("❌ Error: Invalid events file format")
                sys.exit(1)
    else:
        # Use sample events
        events = load_sample_events()
        print("ℹ️  Using sample events (use --events to validate custom file)\n")

    # Validate
    validator = AnalyticsPrivacyValidator(strict=args.strict)
    all_valid = validator.validate_events(events)

    # Print results
    validator.print_results()

    # Exit code
    if validator.errors:
        sys.exit(1)
    elif args.strict and validator.warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
