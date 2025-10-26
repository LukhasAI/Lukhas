#!/usr/bin/env python3
"""
Generate missing module.lane.yaml files from manifests/module.manifest.json.

For each `manifests/**/module.manifest.json`, derive the module directory
relative to the repository root (or `labs/`), and if the module's
`module.lane.yaml` does not exist, create a minimal, validator-compliant
YAML with required fields.

Lane mapping:
    - "candidate" → candidate
    - "integration" → integration
    - "production" | "lukhas" → production
    - anything else → candidate (default)

SLO defaults (p95_ms): {tick: 100, reflect: 200, decide: 300, e2e: 500}

Usage:
    python scripts/phase4_generate_lane_yaml.py \
      --manifests manifests \
      --prefer-labs  # try labs/<module_path> first

"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import yaml

LANE_MAP = {
    "candidate": "candidate",
    "integration": "integration",
    "production": "production",
    "lukhas": "production",
}

SLO_DEFAULT = {"tick": 100, "reflect": 200, "decide": 300, "e2e": 500}
INFRA_MODULES = {"core", "governance", "security", "observability", "api"}
CRITICAL_MODULES = {"identity", "memory", "consciousness", "governance"}


def lane_from_json(raw: Optional[str]) -> str:
    raw = (raw or "").strip().lower()
    return LANE_MAP.get(raw, "candidate")


def resolve_module_path(manifest_path: Path, prefer_labs: bool) -> Optional[Path]:
    rel = manifest_path.parent
    # rel is manifests/<parts>/; we need <parts> as module path
    try:
        module_rel = rel.relative_to(Path("manifests"))
    except Exception:
        return None
    # Two candidates: <module_rel>, labs/<module_rel>
    candidate = Path(module_rel)
    labs_candidate = Path("labs") / module_rel
    if prefer_labs and labs_candidate.exists():
        return labs_candidate
    if candidate.exists():
        return candidate
    if labs_candidate.exists():
        return labs_candidate
    return None


def build_yaml(doc: dict) -> dict:
    module = doc.get("module", {})
    metadata = doc.get("metadata", {})
    name = module.get("name") or module.get("path") or "unknown"
    lane = lane_from_json(module.get("lane"))
    # If name carries a top-level module (last segment), apply overrides
    base_name = str(module.get("path") or name).split("/")[-1]
    if base_name in INFRA_MODULES and lane == "candidate":
        lane = "integration"
    if base_name in CRITICAL_MODULES and lane == "candidate":
        lane = "integration"
    owner = metadata.get("owner") or "unassigned"
    return {
        "name": name,
        "lane": lane,
        "owner": owner,
        "description": metadata.get("description", ""),
        "slo": {"p95_ms": dict(SLO_DEFAULT)},
        "gates": [],
        "artifacts": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate missing lane YAMLs")
    ap.add_argument("--manifests", default="manifests", help="Path to manifests directory")
    ap.add_argument("--prefer-labs", action="store_true", help="Prefer labs/<module> as output root")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing module.lane.yaml when present")
    args = ap.parse_args()

    base = Path(args.manifests)
    if not base.exists():
        print(f"Manifests directory not found: {base}")
        return 1

    created = 0
    scanned = 0
    for p in base.rglob("module.manifest.json"):
        scanned += 1
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        target_dir = resolve_module_path(p, prefer_labs=args.prefer_labs)
        if not target_dir:
            continue
        lane_file = target_dir / "module.lane.yaml"
        if lane_file.exists() and not args.overwrite:
            continue
        data = build_yaml(doc)
        lane_file.parent.mkdir(parents=True, exist_ok=True)
        lane_file.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        created += 1
        print(f"+ {lane_file}")

    print(f"✅ Created {created} lane YAMLs (scanned {scanned} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
