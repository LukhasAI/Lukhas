#!/usr/bin/env python3
"""T4/0.01% Validation Checkpoint

Comprehensive pre-sprint validation that runs all quality checks:
1. Module registry generation and validation
2. Meta-registry fusion
3. Coverage ledger consistency
4. Benchmark ledger consistency
5. Documentation quality checks
6. Test infrastructure smoke tests

Usage:
    python scripts/validate_t4_checkpoint.py [--strict]

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class CheckResult(NamedTuple):
    """Result of a validation check."""
    name: str
    passed: bool
    message: str


def run_check(name: str, cmd: list[str], cwd: Path | None = None) -> CheckResult:
    """Run a validation check command."""
    print(f"\n🔍 {name}")
    print(f"   Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print(f"   ✅ PASSED")
            return CheckResult(name, True, result.stdout)
        else:
            print(f"   ❌ FAILED")
            print(f"   Error: {result.stderr}")
            return CheckResult(name, False, result.stderr)

    except Exception as e:
        print(f"   ❌ FAILED (exception)")
        print(f"   Error: {e}")
        return CheckResult(name, False, str(e))


def run_python_script(name: str, script_path: str) -> CheckResult:
    """Run a Python script check."""
    return run_check(name, [sys.executable, script_path])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run comprehensive T4/0.01% validation checkpoint"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail fast on first error (default: run all checks)"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("T4/0.01% VALIDATION CHECKPOINT")
    print("=" * 80)

    checks: list[CheckResult] = []

    # Check 1: Module Registry Generation
    checks.append(run_python_script(
        "Module Registry Generation",
        "scripts/generate_module_registry.py"
    ))
    if args.strict and not checks[-1].passed:
        return 1

    # Check 2: Meta-Registry Fusion
    checks.append(run_python_script(
        "Meta-Registry Fusion",
        "scripts/generate_meta_registry.py"
    ))
    if args.strict and not checks[-1].passed:
        return 1

    # Check 3: Documentation Map Generation
    checks.append(run_python_script(
        "Documentation Map Generation",
        "scripts/generate_documentation_map.py"
    ))
    if args.strict and not checks[-1].passed:
        return 1

    # Check 4: Ledger Consistency (if in git repo)
    git_dir = Path(".git")
    if git_dir.exists():
        checks.append(run_python_script(
            "Ledger Consistency Check",
            "scripts/ci/ledger_consistency.py"
        ))
        if args.strict and not checks[-1].passed:
            return 1
    else:
        print("\nℹ️  Skipping ledger consistency check (not a git repository)")

    # Check 5: Coverage Trend Analytics (if ledger exists)
    coverage_ledger = Path("manifests/.ledger/coverage.ndjson")
    if coverage_ledger.exists() and coverage_ledger.stat().st_size > 0:
        checks.append(run_python_script(
            "Coverage Trend Analytics",
            "scripts/analytics/coverage_trend.py"
        ))
        if args.strict and not checks[-1].passed:
            return 1
    else:
        print("\nℹ️  Skipping coverage trends (no coverage data)")

    # Check 6: Benchmark Trend Analytics (if ledger exists)
    bench_ledger = Path("manifests/.ledger/bench.ndjson")
    if bench_ledger.exists() and bench_ledger.stat().st_size > 0:
        checks.append(run_python_script(
            "Benchmark Trend Analytics",
            "scripts/analytics/bench_trend.py"
        ))
        if args.strict and not checks[-1].passed:
            return 1
    else:
        print("\nℹ️  Skipping benchmark trends (no benchmark data)")

    # Check 7: Validate MODULE_REGISTRY.json exists and is valid JSON
    registry_path = Path("docs/_generated/MODULE_REGISTRY.json")
    if registry_path.exists():
        try:
            import json
            data = json.loads(registry_path.read_text())
            module_count = data.get("module_count", 0)
            checks.append(CheckResult(
                "MODULE_REGISTRY.json Validation",
                True,
                f"Valid JSON with {module_count} modules"
            ))
            print(f"\n🔍 MODULE_REGISTRY.json Validation")
            print(f"   ✅ PASSED ({module_count} modules)")
        except Exception as e:
            checks.append(CheckResult(
                "MODULE_REGISTRY.json Validation",
                False,
                str(e)
            ))
            print(f"\n🔍 MODULE_REGISTRY.json Validation")
            print(f"   ❌ FAILED: {e}")
            if args.strict:
                return 1
    else:
        checks.append(CheckResult(
            "MODULE_REGISTRY.json Validation",
            False,
            "Registry file not found"
        ))
        print(f"\n🔍 MODULE_REGISTRY.json Validation")
        print(f"   ❌ FAILED: Registry file not found")
        if args.strict:
            return 1

    # Check 8: Validate META_REGISTRY.json exists and is valid JSON
    meta_registry_path = Path("docs/_generated/META_REGISTRY.json")
    if meta_registry_path.exists():
        try:
            import json
            data = json.loads(meta_registry_path.read_text())
            module_count = data.get("module_count", 0)
            avg_health = data.get("summary", {}).get("avg_health_score", 0)
            checks.append(CheckResult(
                "META_REGISTRY.json Validation",
                True,
                f"Valid JSON with {module_count} modules, avg health {avg_health}/100"
            ))
            print(f"\n🔍 META_REGISTRY.json Validation")
            print(f"   ✅ PASSED ({module_count} modules, avg health {avg_health}/100)")
        except Exception as e:
            checks.append(CheckResult(
                "META_REGISTRY.json Validation",
                False,
                str(e)
            ))
            print(f"\n🔍 META_REGISTRY.json Validation")
            print(f"   ❌ FAILED: {e}")
            if args.strict:
                return 1
    else:
        checks.append(CheckResult(
            "META_REGISTRY.json Validation",
            False,
            "Meta-registry file not found"
        ))
        print(f"\n🔍 META_REGISTRY.json Validation")
        print(f"   ❌ FAILED: Meta-registry file not found")
        if args.strict:
            return 1

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for check in checks if check.passed)
    failed = sum(1 for check in checks if not check.passed)

    print(f"\n✅ Passed: {passed}/{len(checks)}")
    print(f"❌ Failed: {failed}/{len(checks)}")

    if failed > 0:
        print("\nFailed checks:")
        for check in checks:
            if not check.passed:
                print(f"  - {check.name}")

    print("\n" + "=" * 80)

    if failed == 0:
        print("✅ ALL CHECKS PASSED - Ready for sprint")
        print("=" * 80)
        return 0
    else:
        print("❌ VALIDATION FAILED - Fix issues before proceeding")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
