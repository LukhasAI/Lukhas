#!/usr/bin/env python3
"""
Generate comprehensive JSON report of all pytest collection errors.
Categorizes errors by type, extracts root causes, and provides actionable insights.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def run_pytest_collection() -> str:
    """Run pytest --collect-only and capture all output."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.stderr + "\n" + proc.stdout


def parse_error_line(line: str) -> dict[str, Any] | None:
    """Parse a single ERROR line from pytest output."""
    # Match: ERROR tests/path/to/test.py - ErrorType: message
    # Or:    ERROR tests/path/to/test.py
    match = re.match(r"ERROR\s+([^\s]+)(?:\s+-\s+(.*))?", line)
    if not match:
        return None

    test_path = match.group(1)
    error_msg = match.group(2) or ""

    # Extract error type
    error_type = "UnknownError"
    if "ModuleNotFoundError" in error_msg:
        error_type = "ModuleNotFoundError"
    elif "ImportError" in error_msg:
        error_type = "ImportError"
    elif "AttributeError" in error_msg:
        error_type = "AttributeError"
    elif "SyntaxError" in error_msg:
        error_type = "SyntaxError"
    elif "ValueError" in error_msg:
        error_type = "ValueError"
    elif "TypeError" in error_msg:
        error_type = "TypeError"
    elif "Failed:" in error_msg:
        error_type = "FailedAssertion"
    elif "Duplicated timeseries" in error_msg:
        error_type = "DuplicatedTimeseries"

    # Extract missing module name for ModuleNotFoundError
    missing_module = None
    if error_type == "ModuleNotFoundError":
        mod_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_msg)
        if mod_match:
            missing_module = mod_match.group(1)

    # Extract missing symbol for ImportError
    missing_symbol = None
    if error_type == "ImportError":
        sym_match = re.search(r"cannot import name ['\"]([^'\"]+)['\"]", error_msg)
        if sym_match:
            missing_symbol = sym_match.group(1)

    # Extract attribute for AttributeError
    missing_attr = None
    if error_type == "AttributeError":
        attr_match = re.search(r"object has no attribute ['\"]([^'\"]+)['\"]", error_msg)
        if attr_match:
            missing_attr = attr_match.group(1)

    return {
        "test_path": test_path,
        "error_type": error_type,
        "error_message": error_msg,
        "missing_module": missing_module,
        "missing_symbol": missing_symbol,
        "missing_attribute": missing_attr,
    }


def categorize_errors(errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Categorize errors by type and extract patterns."""
    by_type = defaultdict(list)
    by_module = defaultdict(list)
    by_test_dir = defaultdict(list)

    for err in errors:
        # Group by error type
        by_type[err["error_type"]].append(err)

        # Group by missing module
        if err["missing_module"]:
            by_module[err["missing_module"]].append(err)

        # Group by test directory
        path_parts = Path(err["test_path"]).parts
        if len(path_parts) >= 2:
            test_dir = path_parts[1]  # tests/unit -> unit
            by_test_dir[test_dir].append(err)

    return {
        "by_type": {k: len(v) for k, v in by_type.items()},
        "by_module": {k: len(v) for k, v in by_module.items()},
        "by_test_dir": {k: len(v) for k, v in by_test_dir.items()},
        "type_details": {k: v for k, v in by_type.items()},
        "module_details": {k: v for k, v in by_module.items()},
    }


def extract_actionable_insights(categorized: dict[str, Any]) -> list[str]:
    """Extract actionable insights from categorized errors."""
    insights = []

    # Top module offenders
    top_modules = sorted(
        categorized["by_module"].items(),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    if top_modules:
        insights.append(
            f"Top missing modules: {', '.join(f'{m} ({c} tests)' for m, c in top_modules[:5])}"
        )

    # Error type distribution
    error_types = categorized["by_type"]
    if "AttributeError" in error_types and error_types["AttributeError"] > 10:
        insights.append(
            f"High AttributeError count ({error_types['AttributeError']}) suggests "
            "sys.path or import hook issues"
        )

    if "ModuleNotFoundError" in error_types:
        insights.append(
            f"{error_types['ModuleNotFoundError']} ModuleNotFoundError cases - "
            "likely need additional bridges or package structure fixes"
        )

    # Test directory patterns
    test_dirs = categorized["by_test_dir"]
    if test_dirs:
        worst_dir = max(test_dirs.items(), key=lambda x: x[1])
        insights.append(
            f"Most affected test directory: tests/{worst_dir[0]} ({worst_dir[1]} errors)"
        )

    return insights


def generate_report() -> dict[str, Any]:
    """Generate comprehensive error report."""
    print("🔍 Collecting pytest errors...")
    raw_output = run_pytest_collection()

    print("📊 Parsing error messages...")
    error_lines = [line for line in raw_output.split("\n") if line.startswith("ERROR")]

    errors = []
    for line in error_lines:
        parsed = parse_error_line(line)
        if parsed:
            errors.append(parsed)

    print(f"✅ Parsed {len(errors)} errors")

    print("🏷️  Categorizing errors...")
    categorized = categorize_errors(errors)

    print("💡 Extracting insights...")
    insights = extract_actionable_insights(categorized)

    # Build final report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors),
            "pytest_command": "pytest --collect-only -q",
            "repo_path": str(Path.cwd()),
        },
        "summary": {
            "total_errors": len(errors),
            "error_types": categorized["by_type"],
            "affected_test_directories": categorized["by_test_dir"],
            "unique_missing_modules": len(categorized["by_module"]),
        },
        "top_offenders": {
            "missing_modules": sorted(
                categorized["by_module"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:20],
            "error_types": sorted(
                categorized["by_type"].items(),
                key=lambda x: x[1],
                reverse=True,
            ),
        },
        "insights": insights,
        "detailed_errors": errors,
        "categorized": {
            "by_error_type": {
                k: [
                    {
                        "test_path": e["test_path"],
                        "message": e["error_message"][:200],  # truncate long msgs
                    }
                    for e in v[:10]  # limit to 10 examples per type
                ]
                for k, v in categorized["type_details"].items()
            },
            "by_missing_module": {
                k: [e["test_path"] for e in v[:10]]
                for k, v in categorized["module_details"].items()
            },
        },
    }

    return report


def main():
    """Main entry point."""
    report = generate_report()

    # Save to file
    output_path = Path("artifacts/pytest_collection_errors_detailed.json")
    output_path.parent.mkdir(exist_ok=True)

    with output_path.open("w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {output_path}")
    print(f"\n📊 Summary:")
    print(f"  Total errors: {report['metadata']['total_errors']}")
    print(f"  Unique missing modules: {report['summary']['unique_missing_modules']}")
    print(f"\n💡 Top Insights:")
    for insight in report["insights"]:
        print(f"  • {insight}")

    print(f"\n🔝 Top 5 Missing Modules:")
    for mod, count in report["top_offenders"]["missing_modules"][:5]:
        print(f"  • {mod}: {count} tests")


if __name__ == "__main__":
    main()
