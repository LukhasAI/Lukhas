#!/usr/bin/env python3
"""
Create missing lukhas_context.md files next to module.manifest.json using
manifest data and include proper YAML front-matter.

This avoids regenerating manifests while achieving high context coverage.
"""
from __future__ import annotations

import json
import pathlib
from typing import List

ROOT = pathlib.Path(__file__).resolve().parents[1]


def make_body(fqn: str, logger: str) -> str:
    return f"""
## What it does
_TODO: short description (2-3 sentences). Add links to demos, notebooks, or dashboards._

## Contracts
- **Publishes**: _e.g., `topic.name@v1`_
- **Subscribes**: _e.g., `topic.other@v1`_
- **Exports**: _e.g., `ClassName`, `function_name()`_

## Observability
- **Spans**: _otlp-span-name_
- **Metrics**: _counter.foo, histogram.bar_
- **Logging**: `{logger or fqn}: INFO`

## Security
- **Auth**: _OIDC|Token|None_
- **Data classification**: _public|internal|restricted|sensitive_
- **Policies**: _Guardian/North policy refs_

## Tests
- _Add paths under_ `tests/…`
- Coverage target (tier-driven): T1≥70% • T2≥50% • T3≥30% • T4=n/a
""".lstrip("\n")


def to_front_matter(module: str, star: str, tier: str, owner: str, matriz: list[str], colony: str, manifest_path: str) -> str:
    arr = ", ".join(matriz or [])
    fm = [
        "---",
        f"module: {module}",
        f"star: {star}",
        f"tier: {tier}",
        f"owner: {owner or 'unassigned'}",
        f"colony: {colony or ''}",
        f"manifest_path: {manifest_path}",
        f"matriz: [{arr}]" if arr else "matriz: []",
        "---",
        "",
    ]
    return "\n".join(fm)


def main():
    created = 0
    for mf in ROOT.rglob("module.manifest.json"):
        # Skip archived manifests
        if "/.archive/" in str(mf):
            continue
        ctx = mf.parent / "lukhas_context.md"
        if ctx.exists():
            continue
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        mod = m.get("module", {}) or {}
        meta = m.get("metadata", {}) or {}
        obs = m.get("observability", {}) or {}

        # Handle logging data which can be a dict or null
        logging_data = obs.get("logging")
        if isinstance(logging_data, dict):
            log = logging_data.get("logger_name") or mod.get("name") or "lukhas"
        else:
            log = mod.get("name") or "lukhas"

        star = (m.get("constellation_alignment", {}) or {}).get("primary_star") or "Supporting"
        tier = (m.get("testing", {}) or {}).get("quality_tier") or "T4_experimental"
        owner = (meta.get("owner") or "unassigned")
        nodes = (m.get("matriz_integration", {}) or {}).get("pipeline_nodes") or []
        colony = (mod.get("colony") or "")
        module_name = mod.get("name") or (mod.get("path") or mf.parent.name)

        text = to_front_matter(module_name, star, tier, owner, nodes, colony, str(mf))
        text += f"# {module_name}\n\n" + make_body(module_name, log)
        ctx.write_text(text, encoding="utf-8")
        print(f"[OK] Created context: {ctx}")
        created += 1

    print(f"Created: {created}")


if __name__ == "__main__":
    main()

