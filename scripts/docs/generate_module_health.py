#!/usr/bin/env python3
"""
Generate module structure health report.

Cross-references:
- module.manifest.json files
- docs/ directories
- tests/ directories
- MODULE_REGISTRY.json

Outputs:
- artifacts/module_structure_report.json (machine-readable)
- docs/_generated/MODULE_INDEX.md (human-readable index)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

ART = Path("artifacts")
ART.mkdir(exist_ok=True, parents=True)

DOCS_GEN = Path("docs/_generated")
DOCS_GEN.mkdir(exist_ok=True, parents=True)


def find_modules_with_manifests() -> List[Path]:
    """Find all module.manifest.json files."""
    manifests = []
    root = Path(".")

    for manifest_path in root.rglob("module.manifest.json"):
        # Exclude common directories
        if any(x in manifest_path.parts for x in [".venv", "node_modules", "__pycache__", ".git"]):
            continue
        manifests.append(manifest_path.parent)

    return manifests


def assess_module_health(module_dir: Path) -> Dict:
    """Assess health of a single module."""
    manifest_path = module_dir / "module.manifest.json"
    docs_dir = module_dir / "docs"
    tests_dir = module_dir / "tests"

    # Load manifest
    manifest = None
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception as e:
            print(f"⚠️  Error reading manifest {manifest_path}: {e}", file=sys.stderr)

    # Count docs
    doc_count = 0
    if docs_dir.exists():
        doc_count = len(list(docs_dir.rglob("*.md")))

    # Count tests
    test_count = 0
    if tests_dir.exists():
        test_count = len(list(tests_dir.rglob("test_*.py")))

    # Has conftest.py?
    has_conftest = (tests_dir / "conftest.py").exists() if tests_dir.exists() else False

    # Calculate health score (0-100)
    score = 0

    # Manifest exists (20 pts)
    if manifest:
        score += 20

    # Has docs (30 pts)
    if doc_count > 0:
        score += 30

    # Has tests (30 pts)
    if test_count > 0:
        score += 30

    # Has conftest (10 pts)
    if has_conftest:
        score += 10

    # Has claude.me or lukhas_context.md (10 pts bonus)
    if (module_dir / "claude.me").exists() or (module_dir / "lukhas_context.md").exists():
        score += 10

    return {
        "module": module_dir.name,
        "path": str(module_dir),
        "has_manifest": manifest is not None,
        "has_docs": docs_dir.exists(),
        "doc_count": doc_count,
        "has_tests": tests_dir.exists(),
        "test_count": test_count,
        "has_conftest": has_conftest,
        "health_score": min(100, score),  # Cap at 100
        "manifest": manifest.get("name") if manifest else None,
    }


def generate_module_index(health_data: List[Dict]) -> str:
    """Generate human-readable module index."""
    lines = []
    lines.append("# LUKHAS Module Index")
    lines.append("")
    lines.append("Auto-generated module structure health report.")
    lines.append("")

    # Sort by health score (descending)
    sorted_modules = sorted(health_data, key=lambda x: (-x["health_score"], x["module"]))

    # Summary stats
    total = len(sorted_modules)
    with_docs = sum(1 for m in sorted_modules if m["has_docs"])
    with_tests = sum(1 for m in sorted_modules if m["has_tests"])
    avg_score = sum(m["health_score"] for m in sorted_modules) / total if total > 0 else 0

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total modules: {total}")
    lines.append(f"- With documentation: {with_docs} ({with_docs/total*100:.1f}%)")
    lines.append(f"- With tests: {with_tests} ({with_tests/total*100:.1f}%)")
    lines.append(f"- Average health score: {avg_score:.1f}/100")
    lines.append("")

    # Module table
    lines.append("## Modules")
    lines.append("")
    lines.append("| Module | Health | Docs | Tests | Conftest | Path |")
    lines.append("|--------|--------|------|-------|----------|------|")

    for module in sorted_modules:
        health_emoji = "🟢" if module["health_score"] >= 80 else "🟡" if module["health_score"] >= 50 else "🔴"
        docs_emoji = "✅" if module["has_docs"] else "❌"
        tests_emoji = "✅" if module["has_tests"] else "❌"
        conftest_emoji = "✅" if module["has_conftest"] else "❌"

        lines.append(
            f"| {module['module']} | {health_emoji} {module['health_score']}/100 | "
            f"{docs_emoji} {module['doc_count']} | {tests_emoji} {module['test_count']} | "
            f"{conftest_emoji} | `{module['path']}` |"
        )

    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("- 🟢 Healthy (≥80), 🟡 Moderate (50-79), 🔴 Needs Attention (<50)")
    lines.append("- Health score = Manifest (20) + Docs (30) + Tests (30) + Conftest (10) + Context (10)")

    return "\n".join(lines)


def main():
    print("🔍 Finding modules with manifests...")

    modules = find_modules_with_manifests()
    print(f"📊 Found {len(modules)} modules")

    print("\n🏥 Assessing module health...")
    health_data = []

    for module_dir in modules:
        health = assess_module_health(module_dir)
        health_data.append(health)

        emoji = "🟢" if health["health_score"] >= 80 else "🟡" if health["health_score"] >= 50 else "🔴"
        print(f"  {emoji} {health['module']}: {health['health_score']}/100 (docs: {health['doc_count']}, tests: {health['test_count']})")

    # Write JSON report
    report_path = ART / "module_structure_report.json"
    report_path.write_text(json.dumps({
        "modules": health_data,
        "summary": {
            "total": len(health_data),
            "with_docs": sum(1 for m in health_data if m["has_docs"]),
            "with_tests": sum(1 for m in health_data if m["has_tests"]),
            "avg_health": sum(m["health_score"] for m in health_data) / len(health_data) if health_data else 0
        }
    }, indent=2))
    print(f"\n✅ Wrote {report_path}")

    # Write human-readable index
    index_path = DOCS_GEN / "MODULE_INDEX.md"
    index_path.write_text(generate_module_index(health_data))
    print(f"✅ Wrote {index_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())