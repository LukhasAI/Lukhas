#!/usr/bin/env python3
"""
Pre-commit hook: Telemetry Semantic Conventions Validation

Validates telemetry fixtures have required OpenTelemetry semantic convention
attributes before commit. Ensures semconv compliance is maintained.
"""

import json
import sys
from typing import List


def validate_telemetry_fixture(fixture_path: str) -> list[str]:
    """Validate telemetry fixture has required semconv attributes."""
    errors = []

    try:
        with open(fixture_path) as f:
            fixture_data = json.load(f)

        # Required attributes per OpenTelemetry semconv v1.37.0
        required_span_attrs = {
            "code.function",
            "module",
            "otel.semconv.version"
        }

        # Check spans
        spans = fixture_data.get("spans", [])
        for i, span in enumerate(spans):
            span_attrs = set(span.get("attributes", {}).keys())
            missing_attrs = required_span_attrs - span_attrs

            if missing_attrs:
                errors.append(f"Span {i} missing required attributes: {', '.join(missing_attrs)}")

            # Check semconv version is correct
            semconv_version = span.get("attributes", {}).get("otel.semconv.version")
            if semconv_version != "1.37.0":
                errors.append(f"Span {i} has incorrect semconv version: {semconv_version} (expected: 1.37.0)")

        # Check metrics (less strict requirements)
        metrics = fixture_data.get("metrics", [])
        for i, metric in enumerate(metrics):
            if not metric.get("name", "").startswith("lukhas."):
                errors.append(f"Metric {i} name doesn't follow lukhas.* convention: {metric.get('name')}")

            if "unit" not in metric:
                errors.append(f"Metric {i} missing required 'unit' field")

            if "type" not in metric:
                errors.append(f"Metric {i} missing required 'type' field")

        # Check fixture has at least spans or metrics
        if not spans and not metrics:
            errors.append("Fixture contains no spans or metrics")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
    except FileNotFoundError as e:
        errors.append(f"File not found: {e}")
    except Exception as e:
        errors.append(f"Validation error: {e}")

    return errors


def main():
    """Main pre-commit hook entry point."""
    if len(sys.argv) < 2:
        print("Usage: pre_commit_telemetry_check.py <fixture_file> [<fixture_file>...]", file=sys.stderr)
        sys.exit(1)

    fixture_files = sys.argv[1:]
    total_errors = 0

    print(f"📡 Validating {len(fixture_files)} telemetry fixture(s)...")

    for fixture_path in fixture_files:
        errors = validate_telemetry_fixture(fixture_path)

        if errors:
            print(f"❌ {fixture_path}:")
            for error in errors:
                print(f"   {error}")
            total_errors += len(errors)
        else:
            print(f"✅ {fixture_path}")

    if total_errors > 0:
        print(f"\n❌ Found {total_errors} telemetry validation error(s)")
        print("Fix these errors before committing to maintain OpenTelemetry semconv compliance")
        sys.exit(1)
    else:
        print("\n✅ All telemetry fixtures comply with semconv requirements")


if __name__ == "__main__":
    main()
