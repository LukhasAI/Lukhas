#!/usr/bin/env python3
"""
LUKHAS 2030 Guardian Governance Consolidation
Unified ethical oversight and governance
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def consolidate_guardian_governance() -> dict[str, Any]:
    """Consolidate guardian governance metadata into a unified registry.

    This first iteration performs a non-destructive consolidation by:
    - Scanning known governance/ethics source directories
    - Building a normalized registry of modules and paths
    - Emitting machine-readable `registry.json` and a human-readable report

    Returns a summary dict with counts to allow callers/tests to verify work.
    """

    print("🔧 Consolidating guardian_governance...")
    print("   Vision: Incorruptible guardian system")

    # Target directory (allow override for tests/ops)
    target_dir = Path(os.getenv("LUKHAS_GUARDIAN_TARGET_DIR", "guardian/governance"))
    target_dir.mkdir(parents=True, exist_ok=True)

    # Source roots to scan (best-effort if present)
    roots = [
        ("candidate_core_governance", Path("candidate/core/governance")),
        ("candidate_governance", Path("candidate/governance")),
        ("lukhas_governance", Path("lukhas/governance")),
        ("ethics", Path("ethics")),
    ]

    modules: list[dict[str, str]] = []
    for domain, root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if p.name == "__init__.py":
                continue
            modules.append(
                {
                    "domain": domain,
                    "path": str(p),
                    "name": p.stem,
                }
            )

    # Write registry.json
    registry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "module_count": len(modules),
        "modules": modules,
    }
    (target_dir / "registry.json").write_text(json.dumps(registry, indent=2))

    # Write consolidation report
    lines = [
        "# Guardian Governance Consolidation Report",
        "",
        f"Generated: {registry['timestamp_utc']}",
        f"Modules indexed: {registry['module_count']}",
        "",
        "## Sources:",
    ]
    for domain, root in roots:
        lines.append(f"- {domain}: {root}")
    lines += [
        "",
        "## Sample (first 10)",
    ]
    for item in modules[:10]:
        lines.append(f"- [{item['domain']}] {item['name']} -> {item['path']}")
    (target_dir / "CONSOLIDATION_REPORT.md").write_text("\n".join(lines))

    summary = {
        "target_dir": str(target_dir),
        "module_count": len(modules),
        "sources_scanned": len([r for _, r in roots if r.exists()]),
    }
    print("✅ guardian_governance consolidation complete!")
    return summary


if __name__ == "__main__":
    consolidate_guardian_governance()
