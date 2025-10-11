#!/usr/bin/env python3
"""
Generate module manifests (+ optional lukhas_context.md)
from docs/audits/COMPLETE_MODULE_INVENTORY.json

Usage:
  python scripts/generate_module_manifests.py \
    --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
    --out manifests \
    --schema schemas/matriz_module_compliance.schema.json \
    --star-canon scripts/star_canon.json \
    --write-context
"""
import argparse, json, os, re, sys, pathlib, datetime
from typing import Dict, Any, List, Optional

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

STAR_DEFAULT = "Supporting"

STAR_HINTS = [
    (r"/consciousness/|/awareness/|/dream/|/oneiric/|/creativity/", "🌊 Flow (Consciousness)"),
    (r"/memory/|/rag/|/embeddings/|/kg/", "✦ Trail (Memory)"),
    (r"/oidc/|/auth/|/identity/|/tenancy/", "⚛️ Anchor (Identity)"),
    (r"/guardian|/ethic", "🛡️ Watch (Guardian)"),  # bias to Watch; refine manually for North if policy-only
    (r"/vision/|/visualization/|/dashboard/|/ui/", "🔬 Horizon (Vision)"),
    (r"/bio/", "🌱 Living (Bio)"),
    (r"/quantum_|/qi_", "🔮 Oracle (Quantum)")
]

COLONY_HINTS = [
    (r"/api/|/bridge/", "actuation"),
    (r"/consciousness/|/dream|/planning|/simulation", "simulation"),
    (r"/memory/|/rag/|/embedding|/kg/", "memory"),
    (r"/ethic|/guardian", "ethics"),
    (r"/vision|/ui|/dashboard|/visualization", "interface"),
    (r"/perception|/asr|/vision_model", "perception"),
]

def guess_star(path: str, inv_star: Optional[str], star_canon: Dict[str, Any]) -> str:
    aliases = star_canon.get("aliases", {})
    stars = set(star_canon.get("stars", []))
    # Inventory-proposed star (normalize via aliases)
    if inv_star:
        norm = aliases.get(inv_star, inv_star)
        if norm in stars:
            return norm
    # Heuristics from path
    for pattern, star in STAR_HINTS:
        if re.search(pattern, path):
            return star
    return STAR_DEFAULT

def guess_colony(path: str) -> Optional[str]:
    for pattern, colony in COLONY_HINTS:
        if re.search(pattern, path):
            return colony
    if "/api/" in path:
        return "actuation"
    return None

def map_priority_to_quality_tier(priority: str) -> str:
    p = (priority or "").lower()
    if p == "critical":
        return "T1_critical"
    if p == "high":
        return "T2_important"
    if p == "medium":
        return "T3_standard"
    return "T4_experimental"

def detect_has_tests(module_path: str) -> (bool, List[str]):
    # Check common test locations
    candidates = [
        ROOT / "tests" / module_path,
        ROOT / module_path / "tests"
    ]
    found = []
    for c in candidates:
        if c.exists():
            for py in c.rglob("test_*.py"):
                rel = py.relative_to(ROOT).as_posix()
                found.append(rel)
    return (len(found) > 0, found)

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def make_context_md(fqn: str, star: str, pipeline_nodes: List[str], colony: Optional[str], exports=None, contracts=None, logger=None) -> str:
    pn = ", ".join(pipeline_nodes or [])
    return f"""# {fqn}

**Star**: {star}
**MATRIZ Nodes**: {pn}
**Colony**: {colony or "-"}

## What it does
_TODO: short description (2–3 sentences). Add links to demos, notebooks, or dashboards._

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
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="docs/audits/COMPLETE_MODULE_INVENTORY.json")
    ap.add_argument("--out", default="manifests")
    ap.add_argument("--schema", default=None)
    ap.add_argument("--star-canon", default=str(HERE / "star_canon.json"))
    ap.add_argument("--write-context", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    inv = json.load(open(args.inventory, "r", encoding="utf-8"))
    star_canon = json.load(open(args.star_canon, "r", encoding="utf-8"))

    items = inv.get("inventory", [])
    if args.limit:
        items = items[:args.limit]

    total = 0
    wrote = 0
    for it in items:
        total += 1
        module_name = it.get("module_name")
        path = it.get("path")  # repo-relative
        lane = it.get("lane")
        inv_star = it.get("constellation_star")
        matriz_node = (it.get("matriz_node") or "supporting").lower()
        priority = it.get("priority") or "low"

        star = guess_star("/"+(path or ""), inv_star, star_canon)
        colony = guess_colony("/"+(path or ""))

        quality_tier = map_priority_to_quality_tier(priority)
        has_tests, test_paths = detect_has_tests(path or "")

        manifest = {
            "schema_version": "1.1.0",
            "module": {
                "name": module_name,
                "path": path,
                "type": it.get("type", "package"),
                "colony": colony,
                "lane": lane  # legacy, allowed but deprecated
            },
            "matriz_integration": {
                "status": "partial",
                "pipeline_nodes": [matriz_node],
                "cognitive_function": ""
            },
            "constellation_alignment": {
                "primary_star": star,
                "star_aliases": [],
                "trinity_aspects": []
            },
            "capabilities": [],
            "dependencies": {"internal": [], "external": [], "circular_dependencies": []},
            "exports": {"classes": [], "functions": [], "constants": []},
            "testing": {
                "has_tests": has_tests,
                "test_paths": test_paths,
                "quality_tier": quality_tier
            },
            "observability": {
                "spans": [],
                "metrics": [],
                "logging": {"logger_name": (module_name or path or "").replace("/", ".") or "lukhas", "default_level": "INFO"},
                "events": {"publishes": [], "subscribes": []}
            },
            "security": {
                "requires_auth": False,
                "data_classification": "internal",
                "secrets_used": [],
                "network_calls": False,
                "sandboxed": True,
                "policies": []
            },
            "metadata": {
                "created": now_iso(),
                "last_updated": now_iso(),
                "manifest_generated": True,
                "owner": "unassigned",
                "documentation_url": "",
                "tags": []
            }
        }

        out_dir = ROOT / args.out / (path or module_name or "unknown")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "module.manifest.json"
        out_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        wrote += 1

        if args.write_context:
            ctx = make_context_md(module_name or path, star, manifest["matriz_integration"]["pipeline_nodes"], colony,
                                  exports=None, contracts=None, logger=manifest["observability"]["logging"]["logger_name"])
            (out_dir / "lukhas_context.md").write_text(ctx, encoding="utf-8")

    print(f"DONE: wrote {wrote}/{total} manifests to {args.out}")

if __name__ == "__main__":
    main()
