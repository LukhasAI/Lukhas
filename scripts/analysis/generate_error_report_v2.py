#!/usr/bin/env python3
"""
Module: generate_error_report_v2.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Generate comprehensive JSON report of all pytest collection errors with full tracebacks.
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
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--tb=long"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.stderr + "\n" + proc.stdout


def parse_pytest_output(output: str) -> list[dict[str, Any]]:
    """Parse pytest output to extract detailed error information."""
    errors = []
    lines = output.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for ERROR lines
        if line.startswith("ERROR"):
            # Extract test path
            match = re.match(r"ERROR\s+([^\s]+)(?:\s+-\s+(.*))?", line)
            if not match:
                i += 1
                continue

            test_path = match.group(1)
            inline_msg = match.group(2) or ""

            # Collect full error message from following lines
            full_message_lines = []
            if inline_msg:
                full_message_lines.append(inline_msg)

            # Look ahead for continuation lines (not starting with ERROR or ===)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.startswith("ERROR") or next_line.startswith("!!!!"):
                    break
                if next_line.startswith("==="):
                    break
                if next_line.strip():
                    full_message_lines.append(next_line)
                j += 1

            full_message = "\n".join(full_message_lines).strip()

            # Parse error details
            error_info = parse_error_details(test_path, full_message)
            errors.append(error_info)

            i = j
        else:
            i += 1

    return errors


def parse_error_details(test_path: str, full_message: str) -> dict[str, Any]:
    """Extract structured information from error message."""
    # Determine error type
    error_type = "UnknownError"
    error_class = None
    traceback_lines = []

    if "ModuleNotFoundError" in full_message:
        error_type = "ModuleNotFoundError"
        error_class = "ModuleNotFoundError"
    elif "ImportError" in full_message:
        error_type = "ImportError"
        error_class = "ImportError"
    elif "AttributeError" in full_message:
        error_type = "AttributeError"
        error_class = "AttributeError"
    elif "SyntaxError" in full_message:
        error_type = "SyntaxError"
        error_class = "SyntaxError"
    elif "ValueError" in full_message:
        error_type = "ValueError"
        error_class = "ValueError"
    elif "TypeError" in full_message:
        error_type = "TypeError"
        error_class = "TypeError"
    elif "Failed:" in full_message:
        error_type = "FailedAssertion"
    elif "Duplicated timeseries" in full_message:
        error_type = "DuplicatedTimeseries"

    # Extract specific details based on error type
    missing_module = None
    missing_symbol = None
    missing_attr = None
    source_file = None
    line_number = None

    if error_type == "ModuleNotFoundError":
        mod_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", full_message)
        if mod_match:
            missing_module = mod_match.group(1)

    if error_type == "ImportError":
        sym_match = re.search(r"cannot import name ['\"]([^'\"]+)['\"]", full_message)
        if sym_match:
            missing_symbol = sym_match.group(1)

        # Try to extract 'from' module
        from_match = re.search(r"from ['\"]([^'\"]+)['\"]", full_message)
        if from_match:
            source_file = from_match.group(1)

    if error_type == "AttributeError":
        attr_match = re.search(r"(?:has no attribute|attribute not found on) ['\"]([^'\"]+)['\"]", full_message)
        if attr_match:
            missing_attr = attr_match.group(1)

        # Extract object type
        obj_match = re.search(r"['\"]([^'\"]+)['\"] object", full_message)
        if obj_match:
            error_class = obj_match.group(1)

    # Extract file and line number from traceback-style messages
    file_line_match = re.search(r"File \"([^\"]+)\", line (\d+)", full_message)
    if file_line_match:
        source_file = file_line_match.group(1)
        line_number = int(file_line_match.group(2))

    # Extract traceback if present
    if "Traceback" in full_message:
        in_traceback = False
        for line in full_message.split("\n"):
            if "Traceback" in line:
                in_traceback = True
            if in_traceback and line.strip():
                traceback_lines.append(line)

    return {
        "test_path": test_path,
        "error_type": error_type,
        "error_class": error_class,
        "error_message": full_message[:500],  # First 500 chars
        "full_message": full_message,
        "missing_module": missing_module,
        "missing_symbol": missing_symbol,
        "missing_attribute": missing_attr,
        "source_file": source_file,
        "line_number": line_number,
        "traceback": "\n".join(traceback_lines) if traceback_lines else None,
    }


def categorize_errors(errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Categorize errors and extract patterns."""
    by_type = defaultdict(list)
    by_module = defaultdict(list)
    by_test_dir = defaultdict(list)
    by_error_class = defaultdict(list)

    for err in errors:
        by_type[err["error_type"]].append(err)

        if err["missing_module"]:
            by_module[err["missing_module"]].append(err)

        if err["error_class"]:
            by_error_class[err["error_class"]].append(err)

        path_parts = Path(err["test_path"]).parts
        if len(path_parts) >= 2:
            test_dir = path_parts[1]
            by_test_dir[test_dir].append(err)

    return {
        "by_type": {k: len(v) for k, v in by_type.items()},
        "by_module": {k: len(v) for k, v in by_module.items()},
        "by_test_dir": {k: len(v) for k, v in by_test_dir.items()},
        "by_error_class": {k: len(v) for k, v in by_error_class.items()},
        "type_details": {k: v for k, v in by_type.items()},
        "module_details": {k: v for k, v in by_module.items()},
    }


def extract_actionable_insights(categorized: dict[str, Any]) -> list[dict[str, str]]:
    """Extract actionable insights with recommendations."""
    insights = []

    # Top module offenders
    top_modules = sorted(
        categorized["by_module"].items(),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    if top_modules:
        insights.append({
            "type": "missing_modules",
            "severity": "high",
            "message": f"Top missing modules: {', '.join(f'{m} ({c})' for m, c in top_modules[:5])}",
            "recommendation": "Create bridge modules using bridge_from_candidates() pattern",
        })

    # Error class distribution
    error_classes = categorized["by_error_class"]
    if "_SixMetaPathImporter" in error_classes:
        count = error_classes["_SixMetaPathImporter"]
        insights.append({
            "type": "sys_path_issue",
            "severity": "critical",
            "message": f"{count} _SixMetaPathImporter errors detected",
            "recommendation": "Check conftest.py sys.path configuration and import hooks",
        })

    # Test directory patterns
    test_dirs = categorized["by_test_dir"]
    if test_dirs:
        worst_dir = max(test_dirs.items(), key=lambda x: x[1])
        insights.append({
            "type": "test_directory",
            "severity": "medium",
            "message": f"Most affected: tests/{worst_dir[0]} ({worst_dir[1]} errors)",
            "recommendation": f"Focus bridge creation on modules used by tests/{worst_dir[0]}",
        })

    # Error type distribution
    error_types = categorized["by_type"]
    if error_types.get("ModuleNotFoundError", 0) > 0:
        insights.append({
            "type": "module_structure",
            "severity": "high",
            "message": f"{error_types['ModuleNotFoundError']} missing module errors",
            "recommendation": "Run analyzer script to identify bridge targets",
        })

    return insights


def generate_report() -> dict[str, Any]:
    """Generate comprehensive error report."""
    print("🔍 Collecting pytest errors with full tracebacks...")
    raw_output = run_pytest_collection()

    print("📊 Parsing error messages...")
    errors = parse_pytest_output(raw_output)

    print(f"✅ Parsed {len(errors)} detailed errors")

    print("🏷️  Categorizing errors...")
    categorized = categorize_errors(errors)

    print("💡 Extracting actionable insights...")
    insights = extract_actionable_insights(categorized)

    # Build final report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors),
            "pytest_command": "pytest --collect-only -q --tb=long",
            "repo_path": str(Path.cwd()),
            "phase": "Phase 9 Complete",
            "baseline": "204 errors",
            "current": f"{len(errors)} errors",
            "reduction_percentage": f"{((204 - len(errors)) / 204 * 100):.1f}%",
        },
        "summary": {
            "total_errors": len(errors),
            "error_types": categorized["by_type"],
            "error_classes": categorized["by_error_class"],
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
            "error_classes": sorted(
                categorized["by_error_class"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        },
        "actionable_insights": insights,
        "detailed_errors": errors,
        "examples_by_type": {
            k: [
                {
                    "test_path": e["test_path"],
                    "error_class": e["error_class"],
                    "message": e["error_message"],
                    "missing_module": e["missing_module"],
                    "missing_symbol": e["missing_symbol"],
                    "missing_attribute": e["missing_attribute"],
                }
                for e in v[:5]  # Top 5 examples per type
            ]
            for k, v in categorized["type_details"].items()
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
    print(f"  Reduction from baseline: {report['metadata']['reduction_percentage']}")
    print(f"  Unique missing modules: {report['summary']['unique_missing_modules']}")

    print(f"\n💡 Actionable Insights ({len(report['actionable_insights'])}):")
    for insight in report["actionable_insights"]:
        severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(insight["severity"], "ℹ️")
        print(f"  {severity_icon} [{insight['type']}] {insight['message']}")
        print(f"     → {insight['recommendation']}")

    if report["top_offenders"]["missing_modules"]:
        print(f"\n🔝 Top 5 Missing Modules:")
        for mod, count in report["top_offenders"]["missing_modules"][:5]:
            print(f"  • {mod}: {count} tests")

    print(f"\n📋 Error Type Distribution:")
    for err_type, count in report["top_offenders"]["error_types"]:
        print(f"  • {err_type}: {count}")


if __name__ == "__main__":
    main()
