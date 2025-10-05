#!/usr/bin/env python3
"""Generate DOCUMENTATION_MAP.md and MODULE_INDEX.md from registry."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REG = Path("docs/_generated/MODULE_REGISTRY.json")
OUT_MAP = Path("docs/_generated/DOCUMENTATION_MAP.md")
OUT_IDX = Path("docs/_generated/MODULE_INDEX.md")


def main():
    if not REG.exists():
        print(f"❌ Registry not found: {REG}")
        print("   Run: python scripts/generate_module_registry.py")
        return 1

    reg = json.loads(REG.read_text())
    modules = sorted(reg["modules"], key=lambda m: m["name"])

    # Build documentation map table
    rows = []
    for m in modules:
        docs_count = len(m.get("docs", []))
        tests_count = len(m.get("tests", []))
        path = m.get("path", "")
        status = m.get("status", "unknown")
        api_count = m.get("api_count", 0)
        rows.append((m["name"], status, docs_count, tests_count, api_count, path))

    md_map = [
        "# Documentation Map",
        f"_Generated {datetime.now(timezone.utc).isoformat()}_",
        "",
        f"**Modules**: {len(modules)} | **Total Docs**: {sum(r[2] for r in rows)} | **Total Tests**: {sum(r[3] for r in rows)}",
        "",
        "| Module | Status | Docs | Tests | APIs | Path |",
        "|---|---|---:|---:|---:|---|",
    ]

    for name, status, dc, tc, ac, path in rows:
        md_map.append(f"| `{name}` | {status} | {dc} | {tc} | {ac} | `{path}` |")

    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    OUT_MAP.write_text("\n".join(md_map) + "\n", encoding="utf-8")

    # Build module index with links
    md_idx = [
        "# Module Index",
        f"_Generated {datetime.now(timezone.utc).isoformat()}_",
        "",
        "Navigate to module documentation:",
        "",
    ]

    # Group by constellation/domain if tagged
    by_constellation = {}
    uncategorized = []

    for m in modules:
        constellation = next(
            (t.split(":")[1] for t in m.get("tags", []) if t.startswith("constellation:")),
            None,
        )
        if constellation:
            by_constellation.setdefault(constellation, []).append(m)
        else:
            uncategorized.append(m)

    # Write categorized
    for const, mods in sorted(by_constellation.items()):
        md_idx.append(f"## {const.title()}")
        md_idx.append("")
        for m in sorted(mods, key=lambda x: x["name"]):
            readme = next(
                (p for p in m.get("docs", []) if p.endswith("README.md")), m.get("path")
            )
            desc = m.get("description", "")[:80]
            md_idx.append(f"- [{m['name']}]({readme}) — {desc}")
        md_idx.append("")

    # Write uncategorized
    if uncategorized:
        md_idx.append("## Other Modules")
        md_idx.append("")
        for m in sorted(uncategorized, key=lambda x: x["name"]):
            readme = next(
                (p for p in m.get("docs", []) if p.endswith("README.md")), m.get("path")
            )
            desc = m.get("description", "")[:80]
            md_idx.append(f"- [{m['name']}]({readme}) — {desc}")

    OUT_IDX.write_text("\n".join(md_idx) + "\n", encoding="utf-8")

    print("✅ Generated DOCUMENTATION_MAP.md")
    print(f"   Location: {OUT_MAP}")
    print("✅ Generated MODULE_INDEX.md")
    print(f"   Location: {OUT_IDX}")
    return 0


if __name__ == "__main__":
    exit(main())
