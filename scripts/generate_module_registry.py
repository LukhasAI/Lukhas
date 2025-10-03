#!/usr/bin/env python3
"""
T4/0.01% Module Registry Generator
===================================

Single source of truth for all modules in the LUKHAS codebase.
All tools read from this registry for sync order, health, and locations.

Inputs:
  - All module.manifest.json files
  - Filesystem structure (docs/, tests/ directories)
  - MQI scores (if available)

Output:
  - docs/_generated/MODULE_REGISTRY.json

Guarantees:
  - Deterministic output (sorted by module name)
  - Full path resolution (absolute paths converted to relative)
  - Health metrics from manifests
  - Notion page ID tracking (populated by sync)

Usage:
  python scripts/generate_module_registry.py
  python scripts/generate_module_registry.py --verbose
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "_generated" / "MODULE_REGISTRY.json"


def find_manifests(root: Path) -> List[Path]:
    """Find all module manifests, excluding build artifacts"""
    manifests = [
        m for m in root.rglob("module.manifest.json")
        if not any(part in m.parts for part in ["node_modules", ".venv", "dist", "__pycache__"])
    ]
    return sorted(manifests)


def relative_path(path: Path, root: Path) -> str:
    """Convert absolute path to relative from root"""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def extract_module_info(manifest_path: Path, root: Path, verbose: bool = False) -> Dict[str, Any]:
    """Extract module information from manifest and filesystem"""
    try:
        data = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        if verbose:
            print(f"❌ {manifest_path.parent.name}: invalid JSON: {e}", file=sys.stderr)
        return None

    module_dir = manifest_path.parent
    module_name = data.get("module", module_dir.name)

    # Find docs
    docs_dir = module_dir / "docs"
    docs = []
    if docs_dir.exists() and docs_dir.is_dir():
        docs = sorted([
            relative_path(p, root)
            for p in docs_dir.rglob("*.md")
        ])

    # Find tests
    tests_dir = module_dir / "tests"
    tests = []
    if tests_dir.exists() and tests_dir.is_dir():
        tests = sorted([
            relative_path(p, root)
            for p in tests_dir.rglob("*.py")
        ])

    # Extract health metrics
    testing = data.get("testing", {}) or {}
    performance = data.get("performance", {}) or {}
    observed = performance.get("observed", {}) or {}

    health = {
        "mqi": 0,  # Will be populated by mqi_gate.py if run
        "coverage": testing.get("coverage_observed"),
        "observed_at": observed.get("observed_at")
    }

    # Clean up None values
    health = {k: v for k, v in health.items() if v is not None}

    module_info = {
        "name": module_name,
        "path": relative_path(module_dir, root),
        "manifest": relative_path(manifest_path, root),
        "docs": docs,
        "tests": tests,
        "tags": data.get("tags", []),
        "health": health,
        "notion_page_id": None  # Populated by notion_sync.py
    }

    return module_info


def generate_registry(root: Path, verbose: bool = False) -> Dict[str, Any]:
    """Generate complete module registry"""
    manifests = find_manifests(root)

    if verbose:
        print(f"🔍 Found {len(manifests)} manifests")

    modules = []
    for manifest_path in manifests:
        info = extract_module_info(manifest_path, root, verbose)
        if info:
            modules.append(info)
            if verbose:
                print(f"✅ {info['name']}: {len(info['docs'])} docs, {len(info['tests'])} tests")

    # Sort by module name for determinism
    modules.sort(key=lambda m: m["name"])

    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "module_count": len(modules),
        "modules": modules
    }

    return registry


def main():
    ap = argparse.ArgumentParser(
        description="Generate MODULE_REGISTRY.json from manifests and filesystem"
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress"
    )
    args = ap.parse_args()

    # Generate registry
    registry = generate_registry(ROOT, args.verbose)

    # Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    OUTPUT.write_text(content)

    print(f"✅ MODULE_REGISTRY.json ({registry['module_count']} modules)")
    print(f"   Location: {OUTPUT.relative_to(ROOT)}")

    # Summary statistics
    total_docs = sum(len(m["docs"]) for m in registry["modules"])
    total_tests = sum(len(m["tests"]) for m in registry["modules"])

    print(f"   Total docs: {total_docs}")
    print(f"   Total tests: {total_tests}")

    sys.exit(0)


if __name__ == "__main__":
    main()
