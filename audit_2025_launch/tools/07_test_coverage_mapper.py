#!/usr/bin/env python3
"""
LUKHAS Pre-Launch Audit - Phase 7: Test Coverage Mapping
Maps tests to source code and identifies coverage gaps.
"""

import ast
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_DATA_DIR = ROOT_DIR / "audit_2025_launch" / "data"
AUDIT_REPORTS_DIR = ROOT_DIR / "audit_2025_launch" / "reports"

EXCLUDE_PATTERNS = [
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".venv", "venv", "env",
    "dist", "build", "*.egg-info",
    "node_modules", ".git", ".vscode", ".idea",
]

def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)

def discover_test_files():
    """Discover all test files."""
    test_files = []
    tests_dir = ROOT_DIR / "tests"
    if tests_dir.exists():
        for test_file in tests_dir.rglob("*.py"):
            if not should_exclude(test_file):
                test_files.append(test_file)
    return test_files

def count_test_functions(test_file):
    """Count test functions in a file."""
    try:
        with open(test_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(test_file))
        test_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_count += 1
        return test_count
    except (OSError, ValueError):
        return 0

def extract_pytest_markers(test_file):
    """Extract pytest markers from test file."""
    markers = set()
    try:
        with open(test_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        marker_matches = re.findall(r'@pytest\.mark\.(\w+)', content)
        markers.update(marker_matches)
    except (OSError, UnicodeDecodeError):
        pass
    return sorted(markers)

def discover_source_files():
    """Discover all source Python files (non-test)."""
    source_files = []
    for py_file in ROOT_DIR.rglob("*.py"):
        if should_exclude(py_file):
            continue
        if "test_" in py_file.name or py_file.name.endswith("_test.py"):
            continue
        if "/tests/" in str(py_file):
            continue
        source_files.append(py_file)
    return source_files

def categorize_by_lane(files):
    """Categorize files by LUKHAS lane."""
    by_lane = {
        "production": [],
        "integration": [],
        "development": [],
        "engine": [],
        "other": []
    }
    for file_info in files:
        path = file_info if isinstance(file_info, str) else file_info.get("path", "")
        if path.startswith("lukhas/"):
            by_lane["production"].append(file_info)
        elif path.startswith("core/"):
            by_lane["integration"].append(file_info)
        elif path.startswith("candidate/"):
            by_lane["development"].append(file_info)
        elif path.startswith("matriz/"):
            by_lane["engine"].append(file_info)
        else:
            by_lane["other"].append(file_info)
    return by_lane

def generate_test_coverage_report():
    """Generate test coverage mapping report."""
    print("=" * 80)
    print("LUKHAS PRE-LAUNCH AUDIT - PHASE 7: TEST COVERAGE MAPPING")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    print("[1/3] Discovering test files...")
    test_files = discover_test_files()
    print(f"  Found {len(test_files)} test files")

    print("[2/3] Discovering source files...")
    source_files = discover_source_files()
    print(f"  Found {len(source_files)} source files")

    print("[3/3] Analyzing tests...")
    test_files_info = []
    for i, test_file in enumerate(test_files):
        if (i + 1) % 50 == 0:
            print(f"  Analyzed {i + 1}/{len(test_files)} test files...")
        rel_path = str(test_file.relative_to(ROOT_DIR))
        test_count = count_test_functions(test_file)
        markers = extract_pytest_markers(test_file)
        test_files_info.append({
            "path": rel_path,
            "test_count": test_count,
            "markers": markers,
            "size": test_file.stat().st_size
        })

    total_test_count = sum(t["test_count"] for t in test_files_info)

    # Basic untested identification
    source_files_info = [{"path": str(f.relative_to(ROOT_DIR))} for f in source_files]
    untested_by_lane = categorize_by_lane(source_files_info)

    coverage_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_test_files": len(test_files),
            "total_test_functions": total_test_count,
            "total_source_files": len(source_files),
            "note": "Simplified coverage - run pytest-cov for detailed coverage"
        },
        "test_files": test_files_info[:100],
        "source_files_by_lane": {
            lane: len(files) for lane, files in untested_by_lane.items()
        }
    }

    output_file = AUDIT_REPORTS_DIR / "test_coverage_map.json"
    with open(output_file, 'w') as f:
        json.dump(coverage_report, indent=2, fp=f)

    print("\n" + "=" * 80)
    print("TEST COVERAGE SUMMARY")
    print("=" * 80)
    print(f"\nTest Files: {len(test_files)}")
    print(f"Test Functions: {total_test_count}")
    print(f"Source Files: {len(source_files)}")
    print("\nSource Files by Lane:")
    for lane, files in untested_by_lane.items():
        print(f"  {lane}: {len(files)}")
    print(f"\n✓ Test coverage report saved to: {output_file}")
    print("=" * 80)

    return coverage_report

if __name__ == "__main__":
    generate_test_coverage_report()
