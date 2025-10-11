Perfect—here are **all the drop-in files** in one go. Copy them into your repo at the indicated paths and run the Make targets. This set gives you:

* Schema **v1.1.0** patcher (adds **Flow/Consciousness 🌊**, deprecates lanes, adds `security` & `events`, tightens nested objects, T1 gates)
* Canonical **Constellation** list + **aliases**
* **Manifest generator** (from your inventory → 100% coverage)
* **Validator** (warn or fail)
* **Badge** generator (manifest & context coverage SVGs)
* **Makefile** targets
* **GitHub Actions** workflow (warning-only at first)

---

### `scripts/star_canon.json`

```json
{
  "stars": [
    "⚛️ Anchor (Identity)",
    "✦ Trail (Memory)",
    "🔬 Horizon (Vision)",
    "🌱 Living (Bio)",
    "🌙 Drift (Dream)",
    "⚖️ North (Ethics)",
    "🛡️ Watch (Guardian)",
    "🔮 Oracle (Quantum)",
    "🌊 Flow (Consciousness)",
    "Supporting"
  ],
  "aliases": {
    "Anchor": "⚛️ Anchor (Identity)",
    "Identity": "⚛️ Anchor (Identity)",

    "Trail": "✦ Trail (Memory)",
    "Memory": "✦ Trail (Memory)",

    "Horizon": "🔬 Horizon (Vision)",
    "Vision": "🔬 Horizon (Vision)",

    "Living": "🌱 Living (Bio)",
    "Bio": "🌱 Living (Bio)",

    "Drift": "🌙 Drift (Dream)",
    "Dream": "🌙 Drift (Dream)",

    "North": "⚖️ North (Ethics)",
    "Ethics": "⚖️ North (Ethics)",

    "Watch": "🛡️ Watch (Guardian)",
    "Guardian": "🛡️ Watch (Guardian)",

    "Oracle": "🔮 Oracle (Quantum)",
    "Quantum": "🔮 Oracle (Quantum)",
    "🔮 Oracle (Quantum)": "🔮 Oracle (Quantum)",

    "Flow": "🌊 Flow (Consciousness)",
    "Consciousness": "🌊 Flow (Consciousness)",
    "🌊 Flow (Consciousness)": "🌊 Flow (Consciousness)"
  }
}
```

---

### `scripts/patch_schema_to_v1_1_0.py`

```python
#!/usr/bin/env python3
"""
Patch schemas/matriz_module_compliance.schema.json → v1.1.0

- Add "🌊 Flow (Consciousness)" to constellation enum
- Deprecate module.lane (optional); add module.colony
- Tighten nested objects with additionalProperties: false
- Extend logging levels; add observability.events
- Add top-level "security" block
- Add T1_critical gates via if/then
- Bump version field to 1.1.0 (schema metadata)
"""
import json, sys, copy, datetime, pathlib

SCHEMA_PATH = pathlib.Path("schemas/matriz_module_compliance.schema.json")

def ensure_ap_false(node):
    if isinstance(node, dict) and node.get("type") == "object":
        node.setdefault("additionalProperties", False)
    return node

def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SCHEMA_PATH
    schema = json.loads(path.read_text(encoding="utf-8"))

    # --- bump version metadata if present ---
    if "version" in schema:
        schema["version"] = "1.1.0"
    # keep $id if present

    props = schema.setdefault("properties", {})

    # --- MODULE: add colony, deprecate lane, adjust required ---
    module = props.get("module", {})
    module_props = module.setdefault("properties", {})
    req = module.setdefault("required", [])
    if "lane" in req:
        req = [r for r in req if r != "lane"]
        module["required"] = req
    module_props.setdefault("colony", {
        "type": "string",
        "description": "Flat capability domain (replaces legacy 'lane')."
    })
    if "lane" in module_props:
        lane_desc = module_props["lane"].get("description", "")
        if "DEPRECATED" not in lane_desc:
            module_props["lane"]["description"] = (lane_desc + " (DEPRECATED: use 'colony')").strip()
    ensure_ap_false(module)
    props["module"] = module

    # --- CONSTELLATION: add Flow star, add star_aliases ---
    ca = props.get("constellation_alignment", {})
    ca_props = ca.setdefault("properties", {})
    primary = ca_props.get("primary_star", {})
    enum = primary.get("enum", [])
    flow = "🌊 Flow (Consciousness)"
    if flow not in enum:
        enum.append(flow)
        primary["enum"] = enum
    ca_props.setdefault("star_aliases", {
        "type":"array", "items":{"type":"string"},
        "description":"Optional aliases that map to canonical star name"
    })
    ensure_ap_false(ca)
    props["constellation_alignment"] = ca

    # --- OBSERVABILITY: extend logging levels; add events; tighten ---
    obs = props.get("observability", {})
    obs_props = obs.setdefault("properties", {})
    logging = obs_props.setdefault("logging", {"type":"object","properties":{}})
    log_props = logging.setdefault("properties", {})
    levels = set(log_props.get("default_level", {}).get("enum", ["DEBUG","INFO","WARNING","ERROR"]))
    levels.update(["TRACE","CRITICAL"])
    log_props["default_level"] = {"type":"string","enum":sorted(levels)}
    ensure_ap_false(logging)
    obs_props["logging"] = logging

    obs_props.setdefault("events", {
        "type":"object",
        "properties": {
            "publishes":{"type":"array","items":{"type":"string","pattern":"^[a-z0-9_.:-]+@v\\d+$"}},
            "subscribes":{"type":"array","items":{"type":"string","pattern":"^[a-z0-9_.:-]+@v\\d+$"}}
        }
    })
    ensure_ap_false(obs)
    props["observability"] = obs

    # --- SECURITY: add top-level block if missing ---
    props.setdefault("security", {
        "type":"object",
        "properties":{
            "requires_auth":{"type":"boolean"},
            "data_classification":{"type":"string","enum":["public","internal","restricted","sensitive"]},
            "secrets_used":{"type":"array","items":{"type":"string"}},
            "network_calls":{"type":"boolean"},
            "sandboxed":{"type":"boolean"},
            "policies":{"type":"array","items":{"type":"string"}}
        }
    })

    # --- Tighten nested objects globally where known ---
    for key in ["module","matriz_integration","constellation_alignment","dependencies",
                "exports","testing","observability","metadata","security"]:
        if key in props:
            ensure_ap_false(props[key])

    # --- Add T1_critical gates via if/then ---
    gates = {
        "if": {
            "properties": {
                "testing": {
                    "properties": {
                        "quality_tier": {"const":"T1_critical"}
                    }
                }
            }
        },
        "then": {
            "properties": {
                "testing": {
                    "required": ["has_tests","test_paths"],
                    "properties": {
                        "has_tests":{"const": True},
                        "test_paths":{"type":"array","minItems":1}
                    }
                },
                "metadata": {
                    "required": ["owner"],
                    "properties": {"owner":{"type":"string","minLength":1}}
                },
                "observability": {
                    "properties": {
                        "spans":{"type":"array","minItems":1},
                        "metrics":{"type":"array","minItems":1},
                        "logging":{"type":"object","required":["logger_name","default_level"]}
                    }
                }
            }
        }
    }
    allOf = list(schema.get("allOf", []))
    allOf.append(gates)
    schema["allOf"] = allOf

    # --- write back ---
    text = json.dumps(schema, indent=4, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")
    print("Patched →", path, "at", datetime.datetime.utcnow().isoformat()+"Z")

if __name__ == "__main__":
    main()
```

---

### `scripts/generate_module_manifests.py`

```python
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
```

---

### `scripts/validate_manifests.py`

```python
#!/usr/bin/env python3
"""
Validate all module.manifest.json files against schema.
Usage:
  python scripts/validate_manifests.py --schema schemas/matriz_module_compliance.schema.json [--root .] [--warn-only]
"""
import argparse, json, pathlib, sys
from jsonschema import Draft7Validator

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--warn-only", action="store_true")
    args = ap.parse_args()

    schema = json.load(open(args.schema, "r", encoding="utf-8"))
    validator = Draft7Validator(schema)

    root = pathlib.Path(args.root)
    files = list(root.rglob("module.manifest.json"))
    failures = 0

    for f in sorted(files):
        data = json.load(open(f, "r", encoding="utf-8"))
        errs = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errs:
            failures += 1
            print(f"[FAIL] {f}")
            for e in errs[:10]:
                loc = "$." + ".".join([str(p) for p in e.path])
                print("  -", e.message, " @ ", loc)
        else:
            print(f"[OK]   {f}")

    print(f"\nChecked {len(files)} files; failures: {failures}")
    if failures and not args.warn_only:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

### `scripts/generate_badges.py`

```python
#!/usr/bin/env python3
"""
Generate simple SVG badges for manifest and context coverage.

Usage:
  python scripts/generate_badges.py \
    --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
    --manifests-root manifests \
    --out docs/audits
"""
import argparse, json, pathlib

def badge_svg(label, value, color):
    # ultra-simple badge
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="220" height="20">
  <linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
  <mask id="a"><rect width="220" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#a)">
    <rect width="120" height="20" fill="#555"/>
    <rect x="120" width="100" height="20" fill="{color}"/>
    <rect width="220" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="60" y="14">{label}</text>
    <text x="170" y="14">{value}</text>
  </g>
</svg>
"""

def pct_color(p):
    if p >= 90: return "#4c1"
    if p >= 70: return "#97CA00"
    if p >= 50: return "#dfb317"
    if p >= 30: return "#fe7d37"
    return "#e05d44"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--manifests-root", default="manifests")
    ap.add_argument("--out", default="docs/audits")
    args = ap.parse_args()

    inv = json.load(open(args.inventory, "r", encoding="utf-8"))
    total = int(inv.get("statistics", {}).get("total_modules", len(inv.get("inventory", [])) or 0))
    out_dir = pathlib.Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)

    # Manifest coverage
    manifests = list(pathlib.Path(args.manifests_root).rglob("module.manifest.json"))
    m_pct = round(100.0 * (len(manifests) / max(1, total)), 1)
    (out_dir / "manifest_coverage.svg").write_text(badge_svg("manifests", f"{m_pct}%", pct_color(m_pct)), encoding="utf-8")

    # Context coverage
    contexts = list(pathlib.Path(args.manifests_root).rglob("lukhas_context.md"))
    c_pct = round(100.0 * (len(contexts) / max(1, total)), 1)
    (out_dir / "context_coverage.svg").write_text(badge_svg("context", f"{c_pct}%", pct_color(c_pct)), encoding="utf-8")

    print(f"Badges → {out_dir}/manifest_coverage.svg, {out_dir}/context_coverage.svg")

if __name__ == "__main__":
    main()
```

---

### `Makefile`

```make
PY := python3

.PHONY: init patch-schema manifests validate badges all

init:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install jsonschema

patch-schema:
	$(PY) scripts/patch_schema_to_v1_1_0.py schemas/matriz_module_compliance.schema.json

manifests:
	$(PY) scripts/generate_module_manifests.py \
		--inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
		--out manifests \
		--star-canon scripts/star_canon.json \
		--write-context

validate:
	$(PY) scripts/validate_manifests.py \
		--schema schemas/matriz_module_compliance.schema.json \
		--root .

badges:
	$(PY) scripts/generate_badges.py \
		--inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
		--manifests-root manifests \
		--out docs/audits

all: patch-schema manifests validate badges
```

---

### `.github/workflows/manifest-validate.yml`

```yaml
name: manifest-validate

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          python -m pip install jsonschema

      - name: Patch schema to v1.1.0
        run: |
          if [ -f scripts/patch_schema_to_v1_1_0.py ]; then
            python scripts/patch_schema_to_v1_1_0.py schemas/matriz_module_compliance.schema.json
          fi

      - name: Validate manifests (warning-only)
        run: |
          python scripts/validate_manifests.py \
            --schema schemas/matriz_module_compliance.schema.json \
            --root . \
            --warn-only

      - name: Build badges
        run: |
          python scripts/generate_badges.py \
            --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
            --manifests-root manifests \
            --out docs/audits || true

      - name: Upload badges as artifact
        uses: actions/upload-artifact@v4
        with:
          name: audit-badges
          path: docs/audits/*.svg
          if-no-files-found: ignore
```

---

## Quick start (run locally)

```bash
make init
make patch-schema
make manifests
make validate
make badges
```

**What you’ll see**

* `schemas/matriz_module_compliance.schema.json` patched to **v1.1.0**
* `manifests/**/module.manifest.json` for **all ~780 modules**
* `manifests/**/lukhas_context.md` scaffolds for each (editable)
* `docs/audits/manifest_coverage.svg` & `context_coverage.svg`
* CI workflow validates (warning-only) on PRs/commits

---
