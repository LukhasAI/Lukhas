#!/usr/bin/env python3
"""
LUKHAS Pre-Launch Audit - Phase 8: Must-Keep Registry
Identifies critical files that must be preserved for system operation.
"""

import json
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

# Critical patterns
ENTRY_POINTS = ["main.py", "app.py", "serve.py", "__main__.py"]
CRITICAL_CONFIGS = ["pyproject.toml", "Makefile", "setup.py", "requirements.txt", "LICENSE"]
CRITICAL_DOCS = ["README.md", "CLAUDE.md", "claude.me"]

def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)

def find_entry_points():
    """Find application entry points."""
    entry_points = []

    for pattern in ENTRY_POINTS:
        for entry_file in ROOT_DIR.rglob(pattern):
            if should_exclude(entry_file):
                continue
            entry_points.append({
                "path": str(entry_file.relative_to(ROOT_DIR)),
                "category": "entry_point",
                "reason": f"Application entry point: {entry_file.name}",
                "priority": "critical"
            })

    return entry_points

def find_production_lane():
    """Find all production lane files."""
    production_files = []

    lukhas_dir = ROOT_DIR / "lukhas"
    if lukhas_dir.exists():
        for py_file in lukhas_dir.rglob("*.py"):
            if should_exclude(py_file):
                continue
            production_files.append({
                "path": str(py_file.relative_to(ROOT_DIR)),
                "category": "production_lane",
                "reason": "Production lane code",
                "priority": "critical"
            })

    return production_files

def find_core_integration():
    """Find core integration layer files."""
    core_files = []

    core_dir = ROOT_DIR / "core"
    if core_dir.exists():
        for py_file in core_dir.rglob("*.py"):
            if should_exclude(py_file):
                continue
            core_files.append({
                "path": str(py_file.relative_to(ROOT_DIR)),
                "category": "integration_lane",
                "reason": "Core integration layer",
                "priority": "high"
            })

    return core_files

def find_matriz_engine():
    """Find MATRIZ cognitive engine files."""
    matriz_files = []

    matriz_dir = ROOT_DIR / "matriz"
    if matriz_dir.exists():
        for py_file in matriz_dir.rglob("*.py"):
            if should_exclude(py_file):
                continue
            matriz_files.append({
                "path": str(py_file.relative_to(ROOT_DIR)),
                "category": "matriz_engine",
                "reason": "MATRIZ cognitive engine",
                "priority": "critical"
            })

    return matriz_files

def find_critical_configs():
    """Find critical configuration files."""
    critical_configs = []

    for config_name in CRITICAL_CONFIGS:
        config_file = ROOT_DIR / config_name
        if config_file.exists():
            critical_configs.append({
                "path": str(config_file.relative_to(ROOT_DIR)),
                "category": "critical_config",
                "reason": f"Critical configuration: {config_name}",
                "priority": "critical"
            })

    return critical_configs

def find_critical_docs():
    """Find critical documentation files."""
    critical_docs = []

    for doc_name in CRITICAL_DOCS:
        for doc_file in ROOT_DIR.rglob(doc_name):
            if should_exclude(doc_file):
                continue
            critical_docs.append({
                "path": str(doc_file.relative_to(ROOT_DIR)),
                "category": "critical_documentation",
                "reason": f"Critical documentation: {doc_name}",
                "priority": "high"
            })

    return critical_docs

def find_branding_assets():
    """Find branding assets for public launch."""
    branding_files = []

    branding_dir = ROOT_DIR / "branding"
    if branding_dir.exists():
        for file_path in branding_dir.rglob("*"):
            if file_path.is_file() and not should_exclude(file_path):
                branding_files.append({
                    "path": str(file_path.relative_to(ROOT_DIR)),
                    "category": "branding",
                    "reason": "Public launch branding",
                    "priority": "high"
                })

    return branding_files

def find_mcp_servers():
    """Find MCP server implementations."""
    mcp_files = []

    mcp_dir = ROOT_DIR / "mcp-servers"
    if mcp_dir.exists():
        for py_file in mcp_dir.rglob("*.py"):
            if should_exclude(py_file):
                continue
            mcp_files.append({
                "path": str(py_file.relative_to(ROOT_DIR)),
                "category": "mcp_servers",
                "reason": "MCP server implementation",
                "priority": "medium"
            })

    return mcp_files

def find_active_tests():
    """Find active test files (smoke, tier1)."""
    active_tests = []

    # Smoke tests
    smoke_dir = ROOT_DIR / "tests" / "smoke"
    if smoke_dir.exists():
        for test_file in smoke_dir.rglob("*.py"):
            if should_exclude(test_file):
                continue
            active_tests.append({
                "path": str(test_file.relative_to(ROOT_DIR)),
                "category": "active_tests",
                "reason": "Smoke test",
                "priority": "high"
            })

    # Tier1 tests (if marked)
    tests_dir = ROOT_DIR / "tests"
    if tests_dir.exists():
        for test_file in tests_dir.rglob("test_*.py"):
            if should_exclude(test_file):
                continue
            # Check if marked as tier1
            try:
                with open(test_file, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '@pytest.mark.tier1' in content:
                        active_tests.append({
                            "path": str(test_file.relative_to(ROOT_DIR)),
                            "category": "active_tests",
                            "reason": "Tier1 test",
                            "priority": "high"
                        })
            except OSError:
                pass

    return active_tests

def generate_must_keep_report():
    """Generate must-keep registry report."""
    print("=" * 80)
    print("LUKHAS PRE-LAUNCH AUDIT - PHASE 8: MUST-KEEP REGISTRY")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    all_must_keep = []

    print("[1/9] Finding entry points...")
    entry_points = find_entry_points()
    all_must_keep.extend(entry_points)
    print(f"  Found {len(entry_points)} entry points")

    print("[2/9] Finding production lane files...")
    production = find_production_lane()
    all_must_keep.extend(production)
    print(f"  Found {len(production)} production files")

    print("[3/9] Finding core integration files...")
    core = find_core_integration()
    all_must_keep.extend(core)
    print(f"  Found {len(core)} core files")

    print("[4/9] Finding MATRIZ engine files...")
    matriz = find_matriz_engine()
    all_must_keep.extend(matriz)
    print(f"  Found {len(matriz)} MATRIZ files")

    print("[5/9] Finding critical configs...")
    configs = find_critical_configs()
    all_must_keep.extend(configs)
    print(f"  Found {len(configs)} critical configs")

    print("[6/9] Finding critical documentation...")
    docs = find_critical_docs()
    all_must_keep.extend(docs)
    print(f"  Found {len(docs)} critical docs")

    print("[7/9] Finding branding assets...")
    branding = find_branding_assets()
    all_must_keep.extend(branding)
    print(f"  Found {len(branding)} branding files")

    print("[8/9] Finding MCP servers...")
    mcp = find_mcp_servers()
    all_must_keep.extend(mcp)
    print(f"  Found {len(mcp)} MCP files")

    print("[9/9] Finding active tests...")
    tests = find_active_tests()
    all_must_keep.extend(tests)
    print(f"  Found {len(tests)} active tests")

    # Categorize by category
    by_category = defaultdict(list)
    for item in all_must_keep:
        by_category[item["category"]].append(item)

    # Categorize by priority
    by_priority = defaultdict(list)
    for item in all_must_keep:
        by_priority[item["priority"]].append(item)

    # Compile report
    must_keep_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_must_keep": len(all_must_keep),
            "by_category": {
                cat: len(items) for cat, items in by_category.items()
            },
            "by_priority": {
                pri: len(items) for pri, items in by_priority.items()
            }
        },
        "files": all_must_keep,
        "by_category": {
            cat: items for cat, items in by_category.items()
        }
    }

    # Save report
    output_file = AUDIT_REPORTS_DIR / "must_keep_registry.json"
    with open(output_file, 'w') as f:
        json.dump(must_keep_report, indent=2, fp=f)

    # Print summary
    print("\n" + "=" * 80)
    print("MUST-KEEP REGISTRY SUMMARY")
    print("=" * 80)
    print(f"\nTotal Must-Keep Files: {len(all_must_keep)}")

    print("\nBy Category:")
    for cat, items in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {cat}: {len(items)}")

    print("\nBy Priority:")
    for pri, items in sorted(by_priority.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {pri}: {len(items)}")

    print(f"\n✓ Must-keep registry saved to: {output_file}")
    print("=" * 80)

    return must_keep_report

if __name__ == "__main__":
    generate_must_keep_report()
