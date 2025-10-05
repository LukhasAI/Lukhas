#!/usr/bin/env python3
"""
LUKHAS Performance Validation Script
T4/0.01% Excellence Standard Enforcement

Validates performance metrics from test artifacts against defined SLOs.
Fails CI pipeline if performance targets are not met.
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class PerformanceValidator:
    """Validates performance artifacts against SLO targets"""

    def __init__(self):
        self.targets = {
            "orchestration_routing_latency": {
                "p95_ms": 250,  # Target: <250ms
                "description": "O.2 Orchestration routing latency"
            },
            "webauthn_registration_latency": {
                "p95_ms": 100,  # Target: <100ms
                "description": "I.4 WebAuthn registration latency"
            },
            "webauthn_authentication_latency": {
                "p95_ms": 100,  # Target: <100ms
                "description": "I.4 WebAuthn authentication latency"
            }
        }

    def validate_artifact(self, artifact_path: str) -> Dict[str, Any]:
        """Validate a single performance artifact"""
        try:
            with open(artifact_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load artifact: {e}",
                "artifact": artifact_path
            }

        test_name = data.get("test")
        if not test_name or test_name not in self.targets:
            return {
                "status": "skipped",
                "message": f"Unknown test type: {test_name}",
                "artifact": artifact_path
            }

        target = self.targets[test_name]
        metrics = data.get("metrics", {})

        # Validate P95 latency
        actual_p95 = metrics.get("p95_ms")
        target_p95 = target["p95_ms"]

        if actual_p95 is None:
            return {
                "status": "error",
                "message": "P95 metric missing from artifact",
                "artifact": artifact_path,
                "test": test_name
            }

        passed = actual_p95 <= target_p95

        result = {
            "status": "pass" if passed else "fail",
            "test": test_name,
            "description": target["description"],
            "artifact": artifact_path,
            "metrics": {
                "actual_p95_ms": actual_p95,
                "target_p95_ms": target_p95,
                "margin_ms": target_p95 - actual_p95,
                "samples": metrics.get("samples", 0),
                "failed_samples": metrics.get("failed_samples", 0),
                "p50_ms": metrics.get("p50_ms"),
                "p99_ms": metrics.get("p99_ms")
            },
            "timestamp": data.get("timestamp"),
            "passed": passed
        }

        if not passed:
            result["message"] = f"P95 latency {actual_p95:.1f}ms exceeds target {target_p95}ms"
        else:
            margin = target_p95 - actual_p95
            result["message"] = f"P95 latency {actual_p95:.1f}ms (margin: {margin:.1f}ms)"

        return result

    def validate_directory(self, artifact_dir: str) -> Dict[str, Any]:
        """Validate all performance artifacts in a directory"""
        if not os.path.exists(artifact_dir):
            return {
                "status": "error",
                "message": f"Artifact directory not found: {artifact_dir}",
                "results": []
            }

        # Find performance artifacts
        patterns = [
            f"{artifact_dir}/perf_*.json",
            f"{artifact_dir}/**/perf_*.json"
        ]

        artifacts = []
        for pattern in patterns:
            artifacts.extend(glob.glob(pattern, recursive=True))

        if not artifacts:
            return {
                "status": "warning",
                "message": f"No performance artifacts found in {artifact_dir}",
                "results": []
            }

        results = []
        for artifact_path in sorted(artifacts):
            result = self.validate_artifact(artifact_path)
            results.append(result)

        # Calculate summary
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "pass")
        failed = sum(1 for r in results if r["status"] == "fail")
        errors = sum(1 for r in results if r["status"] == "error")

        overall_status = "pass"
        if failed > 0:
            overall_status = "fail"
        elif errors > 0:
            overall_status = "error"
        elif passed == 0:
            overall_status = "warning"

        return {
            "status": overall_status,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors
            },
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def generate_report(self, validation_result: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate human-readable performance report"""
        status = validation_result["status"]
        summary = validation_result.get("summary", {})
        results = validation_result.get("results", [])

        # Status emoji
        status_emoji = {
            "pass": "✅",
            "fail": "❌",
            "error": "⚠️",
            "warning": "🟡"
        }.get(status, "❓")

        report_lines = [
            "=" * 80,
            "🚀 LUKHAS Performance Validation Report",
            "=" * 80,
            "",
            f"Overall Status: {status_emoji} {status.upper()}",
            f"Validation Time: {validation_result.get('timestamp', 'unknown')}",
            "",
        ]

        if summary:
            report_lines.extend([
                "📊 Summary:",
                f"  Total Tests: {summary.get('total', 0)}",
                f"  ✅ Passed: {summary.get('passed', 0)}",
                f"  ❌ Failed: {summary.get('failed', 0)}",
                f"  ⚠️  Errors: {summary.get('errors', 0)}",
                "",
            ])

        # Detailed results
        if results:
            report_lines.extend([
                "📋 Detailed Results:",
                "-" * 40,
                ""
            ])

            for result in results:
                test_status = result.get("status", "unknown")
                test_emoji = {
                    "pass": "✅",
                    "fail": "❌",
                    "error": "⚠️",
                    "skipped": "⏭️"
                }.get(test_status, "❓")

                test_name = result.get("test", "unknown")
                description = result.get("description", "")
                message = result.get("message", "")

                report_lines.extend([
                    f"{test_emoji} {test_name}",
                    f"   {description}",
                    f"   {message}",
                ])

                metrics = result.get("metrics", {})
                if metrics:
                    p95 = metrics.get("actual_p95_ms")
                    target = metrics.get("target_p95_ms")
                    samples = metrics.get("samples", 0)

                    if p95 is not None and target is not None:
                        percentage = (p95 / target) * 100
                        report_lines.append(f"   P95: {p95:.1f}ms / {target}ms ({percentage:.1f}%) | Samples: {samples}")

                    if metrics.get("failed_samples", 0) > 0:
                        report_lines.append(f"   ⚠️ Failed samples: {metrics['failed_samples']}")

                report_lines.append("")

        # Performance targets reference
        report_lines.extend([
            "🎯 Performance Targets:",
            "-" * 40,
            ""
        ])

        for test_name, target in self.targets.items():
            description = target["description"]
            p95_target = target["p95_ms"]
            report_lines.append(f"• {description}: P95 < {p95_target}ms")

        report_lines.extend([
            "",
            "=" * 80,
            ""
        ])

        report_text = "\n".join(report_lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)

        return report_text


def main():
    """Main validation script entry point"""
    parser = argparse.ArgumentParser(description="Validate LUKHAS performance artifacts")
    parser.add_argument("artifact_dir", help="Directory containing performance artifacts")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--fail-fast", action="store_true", help="Exit on first failure")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    validator = PerformanceValidator()

    print("🔍 Validating LUKHAS performance artifacts...")
    print(f"📁 Artifact directory: {args.artifact_dir}")

    # Run validation
    result = validator.validate_directory(args.artifact_dir)

    if args.json:
        # JSON output
        json_output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
        else:
            print(json_output)
    else:
        # Human-readable report
        report = validator.generate_report(result, args.output)
        if not args.output:
            print(report)

    # Handle exit codes
    status = result["status"]
    if status == "fail":
        print("💥 Performance validation FAILED!")
        print("Some performance targets were not met.")

        if args.fail_fast:
            print("Exiting due to --fail-fast flag.")

        sys.exit(1)
    elif status == "error":
        print("⚠️  Performance validation encountered errors!")
        sys.exit(2)
    elif status == "warning":
        print("🟡 Performance validation completed with warnings.")
        sys.exit(0)
    else:
        print("🎉 All performance targets met!")
        sys.exit(0)


if __name__ == "__main__":
    main()
