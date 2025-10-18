#!/usr/bin/env python3
"""
Telemetry Fixtures Generator for Matrix Contracts v2

Generates OpenTelemetry-compliant fixture files for testing semantic conventions
compliance. Creates realistic spans and metrics data that can be used for
deterministic telemetry smoke tests.

Usage:
    python3 tools/generate_telemetry_fixtures.py --module memory --output telemetry/
    python3 tools/generate_telemetry_fixtures.py --module identity --output telemetry/
"""

import argparse
import json
import pathlib
import time
import uuid
from typing import Any, Dict


def generate_trace_id() -> str:
    """Generate a valid OpenTelemetry trace ID (32 hex chars)."""
    return uuid.uuid4().hex + uuid.uuid4().hex[:16]


def generate_span_id() -> str:
    """Generate a valid OpenTelemetry span ID (16 hex chars)."""
    return uuid.uuid4().hex[:16]


def generate_spans_fixture(module: str) -> Dict[str, Any]:
    """Generate spans fixture for a module."""
    trace_id = generate_trace_id()
    current_nano = int(time.time() * 1_000_000_000)

    # Module-specific span configurations
    span_configs = {
        "memory": [
            {
                "name": "memory.recall",
                "attrs": {
                    "code.function": "recall",
                    "module": "memory",
                    "k": 10,
                    "query_length": 256
                },
                "duration_ms": 1000
            },
            {
                "name": "memory.store",
                "attrs": {
                    "code.function": "store",
                    "module": "memory",
                    "content_size": 1024
                },
                "duration_ms": 500
            },
            {
                "name": "memory.fold",
                "attrs": {
                    "code.function": "fold",
                    "module": "memory",
                    "fold_count": 3
                },
                "duration_ms": 100
            }
        ],
        "identity": [
            {
                "name": "identity.authenticate",
                "attrs": {
                    "code.function": "authenticate",
                    "module": "identity",
                    "auth.method": "webauthn",
                    "user.tier": "T3"
                },
                "duration_ms": 200
            },
            {
                "name": "identity.authorize",
                "attrs": {
                    "code.function": "authorize",
                    "module": "identity",
                    "resource.type": "api",
                    "permission.scope": "read"
                },
                "duration_ms": 50
            }
        ],
        "consciousness": [
            {
                "name": "consciousness.process",
                "attrs": {
                    "code.function": "process",
                    "module": "consciousness",
                    "awareness.level": 0.85,
                    "emergence.pattern": "coherent"
                },
                "duration_ms": 2000
            },
            {
                "name": "consciousness.dream",
                "attrs": {
                    "code.function": "dream",
                    "module": "consciousness",
                    "dream.state": "REM",
                    "symbol.count": 42
                },
                "duration_ms": 5000
            }
        ]
    }

    # Get spans for the module, or default generic spans
    spans_config = span_configs.get(module, [
        {
            "name": f"{module}.process",
            "attrs": {
                "code.function": "process",
                "module": module
            },
            "duration_ms": 1000
        }
    ])

    spans = []
    parent_span_id = None

    for i, config in enumerate(spans_config):
        span_id = generate_span_id()
        start_time = current_nano + (i * 1_000_000)  # 1ms apart
        end_time = start_time + (config["duration_ms"] * 1_000_000)

        # Add standard semconv version to all spans
        attrs = config["attrs"].copy()
        attrs["otel.semconv.version"] = "1.37.0"

        span = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "name": config["name"],
            "kind": "INTERNAL",
            "start_time_unix_nano": start_time,
            "end_time_unix_nano": end_time,
            "attributes": attrs,
            "status": {"code": "UNSET"},
            "events": []
        }

        spans.append(span)
        # First span becomes parent for subsequent spans
        if parent_span_id is None:
            parent_span_id = span_id

    return {"spans": spans}


def generate_metrics_fixture(module: str) -> Dict[str, Any]:
    """Generate metrics fixture for a module."""

    # Module-specific metric configurations
    metric_configs = {
        "memory": [
            {
                "name": "memory.latency",
                "description": "end-to-end latency for memory operations",
                "unit": "s",
                "type": "histogram",
                "data_points": [
                    {
                        "attributes": {"operation": "recall"},
                        "count": 100,
                        "sum": 12.3,
                        "bounds": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
                        "bucket_counts": [10, 30, 40, 15, 4, 1]
                    }
                ]
            },
            {
                "name": "memory.recall.results",
                "description": "number of recall results returned",
                "unit": "1",
                "type": "gauge",
                "data_points": [
                    {"attributes": {"k": 10}, "value": 8}
                ]
            },
            {
                "name": "memory.cascade.prevented",
                "description": "count of cascades prevented",
                "unit": "1",
                "type": "counter",
                "data_points": [
                    {"attributes": {}, "value": 42}
                ]
            }
        ],
        "identity": [
            {
                "name": "identity.auth.latency",
                "description": "authentication latency",
                "unit": "s",
                "type": "histogram",
                "data_points": [
                    {
                        "attributes": {"method": "webauthn"},
                        "count": 50,
                        "sum": 2.5,
                        "bounds": [0.01, 0.05, 0.1, 0.2, 0.5],
                        "bucket_counts": [5, 15, 20, 8, 2]
                    }
                ]
            },
            {
                "name": "identity.sessions.active",
                "description": "active user sessions",
                "unit": "1",
                "type": "gauge",
                "data_points": [
                    {"attributes": {}, "value": 127}
                ]
            }
        ],
        "consciousness": [
            {
                "name": "consciousness.awareness.level",
                "description": "current awareness level",
                "unit": "1",
                "type": "gauge",
                "data_points": [
                    {"attributes": {"pattern": "coherent"}, "value": 0.85}
                ]
            },
            {
                "name": "consciousness.dreams.generated",
                "description": "dreams generated count",
                "unit": "1",
                "type": "counter",
                "data_points": [
                    {"attributes": {"state": "REM"}, "value": 15}
                ]
            }
        ]
    }

    # Get metrics for the module, or default generic metrics
    metrics_config = metric_configs.get(module, [
        {
            "name": f"lukhas.{module}.operations",
            "description": f"operations performed by {module}",
            "unit": "1",
            "type": "counter",
            "data_points": [
                {"attributes": {}, "value": 100}
            ]
        }
    ])

    return {"metrics": metrics_config}


def write_fixture_file(data: Dict[str, Any], output_path: pathlib.Path) -> None:
    """Write fixture data to JSON file with pretty formatting."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=False)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate telemetry fixtures for Matrix contracts")
    parser.add_argument(
        "--module",
        required=True,
        help="Module name (e.g., memory, identity, consciousness)"
    )
    parser.add_argument(
        "--output",
        default="telemetry/",
        help="Output directory for fixtures (default: telemetry/)"
    )
    parser.add_argument(
        "--spans-only",
        action="store_true",
        help="Generate only spans fixture"
    )
    parser.add_argument(
        "--metrics-only",
        action="store_true",
        help="Generate only metrics fixture"
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔧 Generating telemetry fixtures for module: {args.module}")
    print(f"📁 Output directory: {output_dir}")

    # Generate spans fixture
    if not args.metrics_only:
        spans_data = generate_spans_fixture(args.module)
        spans_file = output_dir / f"{args.module}_spans.json"
        write_fixture_file(spans_data, spans_file)
        print(f"✅ Generated spans fixture: {spans_file}")

    # Generate metrics fixture
    if not args.spans_only:
        metrics_data = generate_metrics_fixture(args.module)
        metrics_file = output_dir / f"{args.module}_metrics.json"
        write_fixture_file(metrics_data, metrics_file)
        print(f"✅ Generated metrics fixture: {metrics_file}")

    print(f"🎉 Telemetry fixtures generated for {args.module}")
    print("\nNext steps:")
    print(f"1. Review generated fixtures in {output_dir}")
    print(f"2. Create telemetry smoke test: tests/test_telemetry_{args.module}.py")
    print(f"3. Run tests: make telemetry-test MODULE={args.module}")


if __name__ == "__main__":
    main()
