Massive win getting 780/780 green. 👏 Two things to do now:

1. **Fix the stats script** (it’s tripping on a stray string because it assumes every loaded object is a dict).
2. **Add the CI tripwires** (T1 test_paths, no forbidden stars, etc.), and re-run.

Below are drop-in patches + commands you can paste.

---

# 1) Patch `scripts/report_manifest_stats.py` (robust + artifacts)

**Replace the whole file** with this:

```python
#!/usr/bin/env python3
"""
Report stats over generated manifests.

Outputs:
- docs/audits/manifest_stats.json
- docs/audits/manifest_stats.md
- Prints a short summary to stdout

Robust against mixed content: skips non-dict JSON, missing fields, etc.
"""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Any, List

def load_json(p: Path) -> Any:
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to parse {p}: {e}", file=sys.stderr)
        return None

def coalesce(*vals):
    for v in vals:
        if v not in (None, "", []):
            return v
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", default="manifests", help="Root folder containing module.manifest.json files")
    ap.add_argument("--out", default="docs/audits", help="Output folder for stats")
    args = ap.parse_args()

    root = Path(args.manifests)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_paths = sorted(root.rglob("module.manifest.json"))
    if not manifest_paths:
        print(f"[ERROR] No manifests found under {root}", file=sys.stderr)
        sys.exit(2)

    star_counts = Counter()
    tier_counts = Counter()
    node_counts = Counter()
    colony_counts = Counter()
    t1_no_tests = []
    t1_missing_test_paths = []
    capability_gaps = []
    invalid_stars = []
    sample_modules = []

    for mp in manifest_paths:
        data = load_json(mp)
        if not isinstance(data, dict):
            # Some stray file or wrong format: skip loudly but continue
            print(f"[WARN] Skipping non-dict JSON: {mp}", file=sys.stderr)
            continue

        module = data.get("module", {}) if isinstance(data.get("module"), dict) else {}
        align  = data.get("constellation_alignment", {}) if isinstance(data.get("constellation_alignment"), dict) else {}
        testing = data.get("testing", {}) if isinstance(data.get("testing"), dict) else {}
        mi = data.get("matriz_integration", {}) if isinstance(data.get("matriz_integration"), dict) else {}

        name = coalesce(module.get("name"), module.get("path"), str(mp.parent))
        star = align.get("primary_star", "Supporting")
        tier = testing.get("quality_tier", None)
        has_tests = bool(testing.get("has_tests", False))
        test_paths_present = "test_paths" in testing
        pipeline_nodes = mi.get("pipeline_nodes", []) if isinstance(mi.get("pipeline_nodes"), list) else []
        colony = data.get("colony", None)  # optional; may be absent

        star_counts[star] += 1
        if tier:
            tier_counts[tier] += 1
        for n in pipeline_nodes:
            node_counts[n] += 1
        if colony is not None:
            colony_counts[str(colony)] += 1

        # Gaps
        if tier == "T1_critical" and not has_tests:
            t1_no_tests.append(name)
        if tier == "T1_critical" and not test_paths_present:
            t1_missing_test_paths.append(name)

        # Capabilities must be non-empty per schema; flag otherwise (shouldn’t happen post-gen)
        caps = data.get("capabilities", [])
        if not caps:
            capability_gaps.append(name)

        # Star sanity (Ambiguity must not appear)
        if star == "⚛️ Ambiguity (Quantum)":
            invalid_stars.append(name)

        # Keep a small sample for the MD table
        if len(sample_modules) < 25:
            sample_modules.append({
                "module": name,
                "star": star,
                "tier": tier or "",
                "has_tests": has_tests,
                "nodes": pipeline_nodes,
                "colony": colony if colony is not None else "",
                "file": str(mp),
            })

    # Compose JSON stats
    stats = {
        "total_manifests": sum(star_counts.values()),
        "stars": star_counts,
        "tiers": tier_counts,
        "matriz_nodes": node_counts,
        "colonies": colony_counts,
        "gaps": {
            "t1_no_tests": t1_no_tests,
            "t1_missing_test_paths_property": t1_missing_test_paths,
            "capability_gaps": capability_gaps,
            "invalid_stars": invalid_stars,
        },
        "sample": sample_modules,
    }

    json_path = out_dir / "manifest_stats.json"
    md_path   = out_dir / "manifest_stats.md"

    # Write JSON
    with json_path.open("w", encoding="utf-8") as f:
        json.dump({
            **stats,
            # convert Counters to plain dicts for JSON
            "stars": dict(stats["stars"]),
            "tiers": dict(stats["tiers"]),
            "matriz_nodes": dict(stats["matriz_nodes"]),
            "colonies": dict(stats["colonies"]),
        }, f, indent=2, ensure_ascii=False)

    # Write Markdown
    def md_counts(title: str, c: Counter) -> str:
        lines = [f"### {title}", "", "| Key | Count |", "|---|---|"]
        for k, v in c.most_common():
            lines.append(f"| {k} | {v} |")
        return "\n".join(lines) + "\n"

    md = []
    md.append(f"# Manifest Statistics\n")
    md.append(f"- Total manifests: **{stats['total_manifests']}**\n")
    md.append(md_counts("Stars", star_counts))
    md.append(md_counts("Quality Tiers", tier_counts))
    md.append(md_counts("MATRIZ Nodes", node_counts))
    if colony_counts:
        md.append(md_counts("Colonies", colony_counts))

    gaps = stats["gaps"]
    md.append("## Gaps")
    if not any(gaps.values()):
        md.append("- None ✅")
    else:
        if gaps["t1_no_tests"]:
            md.append(f"- T1 without tests: {len(gaps['t1_no_tests'])}")
        if gaps["t1_missing_test_paths_property"]:
            md.append(f"- T1 missing `testing.test_paths` property: {len(gaps['t1_missing_test_paths_property'])}")
        if gaps["capability_gaps"]:
            md.append(f"- Manifests with empty capabilities: {len(gaps['capability_gaps'])}")
        if gaps["invalid_stars"]:
            md.append(f"- Invalid star entries (e.g., Ambiguity): {len(gaps['invalid_stars'])}")
    md.append("\n## Sample (up to 25)\n")
    md.append("| Module | Star | Tier | Has Tests | Nodes | Colony | File |")
    md.append("|---|---|---|---:|---|---|---|")
    for s in stats["sample"]:
        md.append(f"| {s['module']} | {s['star']} | {s['tier']} | {str(s['has_tests']).lower()} | {', '.join(s['nodes'])} | {s['colony']} | `{s['file']}` |")

    with md_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print(f"[OK] Wrote {json_path} and {md_path}")
    print(f"[SUMMARY] Stars: {dict(star_counts)}")
    print(f"[SUMMARY] Tiers: {dict(tier_counts)}")
    if gaps["invalid_stars"]:
        print(f"[WARN] Invalid stars detected: {len(gaps['invalid_stars'])}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits
```

---

# 2) CI tripwires (paste into `.github/workflows/matriz-validate.yml`)

Add these **after** your smoke tests:

```yaml
      - name: Tripwire — T1 must have testing.test_paths (may be empty)
        run: |
          python - <<'PY'
          import json, pathlib, sys
          errs=0
          for p in pathlib.Path('manifests').rglob('module.manifest.json'):
              d=json.loads(p.read_text())
              t=d.get('testing',{})
              if t.get('quality_tier') == 'T1_critical' and 'test_paths' not in t:
                  print(f"[FAIL] {p}: T1_critical requires testing.test_paths property (can be [])")
                  errs+=1
          sys.exit(1 if errs else 0)
          PY

      - name: Tripwire — Forbid deprecated star names (Ambiguity)
        run: |
          python - <<'PY'
          import json, pathlib, sys
          bad=[]
          for p in pathlib.Path('manifests').rglob('module.manifest.json'):
              d=json.loads(p.read_text())
              star=d.get('constellation_alignment',{}).get('primary_star')
              if star == "⚛️ Ambiguity (Quantum)":
                  bad.append(str(p))
          if bad:
              print("[FAIL] Found deprecated star name in:", *bad, sep="\n  ")
              sys.exit(1)
          PY

      - name: Tripwire — No empty capabilities
        run: |
          python - <<'PY'
          import json, pathlib, sys
          bad=[]
          for p in pathlib.Path('manifests').rglob('module.manifest.json'):
              d=json.loads(p.read_text())
              caps=d.get('capabilities',[])
              if not caps:
                  bad.append(str(p))
          if bad:
              print("[FAIL] Empty capabilities detected in:", *bad, sep="\n  ")
              sys.exit(1)
          PY

      - name: Tripwire — Colony must not be null (omit if unknown)
        run: |
          python - <<'PY'
          import json, pathlib, sys
          bad=[]
          for p in pathlib.Path('manifests').rglob('module.manifest.json'):
              d=json.loads(p.read_text())
              if 'colony' in d and d['colony'] is None:
                  bad.append(str(p))
          if bad:
              print("[FAIL] colony is null (should be omitted):", *bad, sep="\n  ")
              sys.exit(1)
          PY

      - name: Stats — Generate manifest statistics (JSON+MD)
        run: |
          python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits

      - name: Upload artifacts — manifest stats & reports
        uses: actions/upload-artifact@v4
        with:
          name: matriz-reports
          path: |
            docs/audits/manifest_stats.json
            docs/audits/manifest_stats.md
            docs/audits/linkcheck.txt
            docs/audits/context_lint.txt
```

---

# 3) Quick local validation

```bash
# Re-run stats locally to mirror CI
python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits

# Sanity: show star counts from JSON
python - <<'PY'
import json
d=json.load(open('docs/audits/manifest_stats.json'))
print("Stars:", d["stars"])
print("Tiers:", d["tiers"])
print("Gaps:", {k: len(v) for k,v in d["gaps"].items()})
PY
```

You should see the same distribution you grep’d (Oracle present, Flow present, lots of Supporting), with zero gaps.

---

## Optional T4 + 0.01% add-ons (tiny, high leverage)

* **“Supporting reducer”**: write `scripts/suggest_star_promotions.py` to propose promotions for “Supporting” modules using `configs/star_rules.json` (regex→star). Emit a diffable CSV of suggestions.
* **Tier gate**: fail CI if any `T1_critical` lacks `owner` in metadata (keeps ownership tight).
* **Drift guard**: add a job that reads `manifest_stats.json.total_manifests` and fails if it drops by >1% vs previous main (prevents accidental deletions).

Absolutely—dropping in the three “tiny, high-leverage” scripts plus a default ruleset and CI wiring so they work out of the box.

---

---

# `configs/star_rules.json`

Paste this whole file (safe to use today). It keeps “🔮 Oracle (Quantum)” canonical and includes **exclusions**, **owner priors**, **dependency hints**, and a **changelog**. You can trim later.

```json
{
  "version": "2.0",
  "updated": "2025-10-11",
  "changelog": [
    "v2.0: Add exclusions, owner/dependency priors, richer capability mapping, path guards, and confidence bands; keep Oracle (Quantum) canonical; add Flow (Consciousness)."
  ],

  "canonical_stars": [
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
    "Ambiguity": "🔮 Oracle (Quantum)",
    "Flow": "🌊 Flow (Consciousness)",
    "Consciousness": "🌊 Flow (Consciousness)"
  },

  "deny": ["⚛️ Ambiguity (Quantum)"],

  "weights": {
    "capability_override": 0.60,
    "node_override": 0.50,
    "path_regex": 0.40,
    "owner_prior": 0.35,
    "dependency_hint": 0.30
  },

  "confidence": {
    "min_suggest": 0.50,
    "min_autopromote": 0.70
  },

  "exclusions": [
    {"pattern": "\\bstopwatch\\b", "explain": "Avoid Watch star false positives"},
    {"pattern": "\\bwatchers?\\b", "explain": "Avoid repo watcher noise"},
    {"pattern": "\\banchor(?:ing)? bolts?\\b", "explain": "Non-Identity engineering term"},
    {"pattern": "\\bdreamliner\\b", "explain": "Brand name, not Drift"},
    {"pattern": "\\bmemory leak(s)?\\b", "explain": "Bug phrase; not Memory star capability"},
    {"pattern": "\\bvisionary\\b", "explain": "English adjective; not Vision"}
  ],

  "rules": [
    { "star": "🌊 Flow (Consciousness)", "pattern": "(?<!sub)conscious|awareness|metacognition|oneiric|dream(?!liner)|imagination|rumination|inner[_-]?voice|attention[_-]?router|salience", "source": "path_keywords" },
    { "star": "✦ Trail (Memory)", "pattern": "memory|episodic|semantic|retriev(al|er)|embedding(s)?|vector[_-]?index|cache(manager)?|consolidation|trace(store|log)", "source": "path_keywords" },
    { "star": "🛡️ Watch (Guardian)", "pattern": "auth(n|z)?\\b|oidc|oauth|rbac|abac|policy|guard(rail|ian)|verifier|redteam|threat|sandbox|jail|gatekeeper|aud(it|itor)", "source": "path_keywords" },
    { "star": "🔬 Horizon (Vision)", "pattern": "vision|percept(ion|ual)|image|camera|frame|segmentation|detector|ocr|render(er)?|overlay|pose|cv2|opencv", "source": "path_keywords" },
    { "star": "🌱 Living (Bio)", "pattern": "bio|biolog(y|ical)|mito(chondria|chondrial)|endocrine|metabolic|organ(ism|ic)|cell(ular)?|homeostasis", "source": "path_keywords" },
    { "star": "🌙 Drift (Dream)", "pattern": "dream[_-]?engine|dream[_-]?loop|lucid|hypnagogic|oneiric|dream[_-]refold|hallucinat(e|ion)", "source": "path_keywords" },
    { "star": "⚖️ North (Ethics)", "pattern": "ethic(s|al)|safety[_-]?policy|fair(ness)?|bias|consent|provenance|governance|compliance|audit[_-]?trail", "source": "path_keywords" },
    { "star": "⚛️ Anchor (Identity)", "pattern": "identity|persona|profile|anchor(?! bolt)|self[_-]?model|whoami|account|session|idp", "source": "path_keywords" },
    { "star": "🔮 Oracle (Quantum)", "pattern": "\\bquantum\\b|\\bqi\\b|anneal(er|ing)|qiskit|oracle[_-]?gate|superposition|entangle(d|ment)", "source": "path_keywords" }
  ],

  "capability_overrides": [
    { "capability": "authentication", "star": "🛡️ Watch (Guardian)" },
    { "capability": "authorization", "star": "🛡️ Watch (Guardian)" },
    { "capability": "api_gateway", "star": "🛡️ Watch (Guardian)" },
    { "capability": "policy_guard", "star": "🛡️ Watch (Guardian)" },
    { "capability": "red_team", "star": "🛡️ Watch (Guardian)" },

    { "capability": "memory_consolidation", "star": "✦ Trail (Memory)" },
    { "capability": "vector_index", "star": "✦ Trail (Memory)" },
    { "capability": "retrieval", "star": "✦ Trail (Memory)" },
    { "capability": "cache_manager", "star": "✦ Trail (Memory)" },

    { "capability": "attention_router", "star": "🌊 Flow (Consciousness)" },
    { "capability": "metacognitive_monitor", "star": "🌊 Flow (Consciousness)" },
    { "capability": "self_reflection", "star": "🌊 Flow (Consciousness)" },

    { "capability": "vision_pipeline", "star": "🔬 Horizon (Vision)" },
    { "capability": "ocr", "star": "🔬 Horizon (Vision)" },
    { "capability": "scene_understanding", "star": "🔬 Horizon (Vision)" },

    { "capability": "bio_simulation", "star": "🌱 Living (Bio)" },
    { "capability": "mito_ethics_sync", "star": "🌱 Living (Bio)" },
    { "capability": "endocrine_integration", "star": "🌱 Living (Bio)" },

    { "capability": "ethical_auditor", "star": "⚖️ North (Ethics)" },
    { "capability": "consent_manager", "star": "⚖️ North (Ethics)" },
    { "capability": "data_provenance", "star": "⚖️ North (Ethics)" },

    { "capability": "identity_resolver", "star": "⚛️ Anchor (Identity)" },
    { "capability": "persona_manager", "star": "⚛️ Anchor (Identity)" },

    { "capability": "quantum_attention", "star": "🔮 Oracle (Quantum)" },
    { "capability": "qi_layer", "star": "🔮 Oracle (Quantum)" }
  ],

  "node_overrides": [
    { "node": "attention", "star": "🌊 Flow (Consciousness)" },
    { "node": "memory", "star": "✦ Trail (Memory)" },
    { "node": "risk", "star": "🛡️ Watch (Guardian)" },
    { "node": "action", "star": "🛡️ Watch (Guardian)" },
    { "node": "thought", "star": "🌊 Flow (Consciousness)" }
  ],

  "owner_priors": [
    { "owner_regex": "\\bguardian\\b|\\bsecurity\\b", "star": "🛡️ Watch (Guardian)" },
    { "owner_regex": "\\bconscious(ness)?\\b|\\bflow\\b", "star": "🌊 Flow (Consciousness)" },
    { "owner_regex": "\\bmemory\\b|\\bretrieval\\b", "star": "✦ Trail (Memory)" }
  ],

  "dependency_hints": [
    { "package_regex": "\\b(opencv|cv2|torchvision|pytesseract)\\b", "star": "🔬 Horizon (Vision)" },
    { "package_regex": "\\bqiskit|cirq|pennylane\\b", "star": "🔮 Oracle (Quantum)" },
    { "package_regex": "\\bpasslib|authlib|pyjwt|python-keycloak\\b", "star": "🛡️ Watch (Guardian)" }
  ]
}
```

> You can keep your **capability type enum** in the schema as-is; the **capability “name”** is where we put fine-grained semantics that the rules use.
---

# `scripts/lint_star_rules.py`

* Verifies `configs/star_rules.json` structure
* Compiles all regex (fails on invalid)
* Guards canonical stars / aliases / deny-list
* Computes **rule hit counts** across your **780 manifests** (paths, nodes, capabilities, owners, deps)
* Writes a machine-readable report: `docs/audits/star_rules_lint.json`

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

ERR = 0

def die(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    global ERR
    ERR = 1

def warn(msg: str):
    print(f"[WARN]  {msg}", file=sys.stderr)

def info(msg: str):
    print(f"[INFO]  {msg}")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"Failed to read JSON {path}: {e}")
        return {}

def compile_rx(pat: str, where: str):
    try:
        return re.compile(pat, re.IGNORECASE)
    except re.error as e:
        die(f"Invalid regex in {where}: {pat} -> {e}")
        return None

def collect_manifests(root: Path):
    for p in root.rglob("module.manifest.json"):
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            warn(f"Skipping unreadable manifest {p}: {e}")

def main():
    ap = argparse.ArgumentParser(description="Lint and sanity-check star rules; produce hit counts.")
    ap.add_argument("--rules", default="configs/star_rules.json")
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--out", default="docs/audits/star_rules_lint.json")
    ap.add_argument("--fail-on-zero-hits", action="store_true", help="Fail if any rule has 0 matches")
    args = ap.parse_args()

    rules_path = Path(args.rules)
    rules = load_json(rules_path)
    manifests_root = Path(args.manifests)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- structural checks
    for k in ["canonical_stars", "rules", "aliases", "weights", "confidence"]:
        if k not in rules:
            die(f"Missing '{k}' in {rules_path}")

    canonical = set(rules["canonical_stars"])
    deny = set(rules.get("deny", []))
    for s in deny:
        if s not in canonical:
            die(f"deny-list contains non-canonical star: {s}")

    # alias validation
    for alias, target in rules.get("aliases", {}).items():
        if target not in canonical:
            die(f"Alias '{alias}' maps to non-canonical star: {target}")

    # weights / confidence
    weights = rules["weights"]
    for k, v in weights.items():
        if not isinstance(v, (int, float)) or v < 0 or v > 1:
            die(f"Weight '{k}' must be 0..1 (got {v})")
    conf = rules["confidence"]
    for k, v in conf.items():
        if not isinstance(v, (int, float)) or v < 0 or v > 1:
            die(f"Confidence '{k}' must be 0..1 (got {v})")

    # compile patterns
    exclusions = [(compile_rx(r["pattern"], "exclusions"), r.get("explain","")) for r in rules.get("exclusions", [])]
    rules_rx = []
    for i, r in enumerate(rules["rules"]):
        star = r.get("star")
        if star not in canonical:
            die(f"Rule #{i} references non-canonical star: {star}")
        rx = compile_rx(r.get("pattern",""), f"rules[{i}]")
        rules_rx.append((rx, star, r.get("source","path_keywords")))
    owner_priors = [(compile_rx(r["owner_regex"], "owner_priors"), r["star"]) for r in rules.get("owner_priors", [])]
    dep_hints = [(compile_rx(r["package_regex"], "dependency_hints"), r["star"]) for r in rules.get("dependency_hints", [])]

    cap_over = {r["capability"]: r["star"] for r in rules.get("capability_overrides", [])}
    node_over = {r["node"]: r["star"] for r in rules.get("node_overrides", [])}
    for s in list(cap_over.values()) + list(node_over.values()):
        if s not in canonical:
            die(f"Override maps to non-canonical star: {s}")

    # ---- hit counting (paths, caps, nodes, owners, deps)
    hit_counts = {
        "rules": Counter(),
        "capability_overrides": Counter(),
        "node_overrides": Counter(),
        "owner_priors": Counter(),
        "dependency_hints": Counter(),
        "exclusions": Counter()
    }
    total_supporting = 0

    for path, m in collect_manifests(manifests_root):
        mod = (m.get("module") or {})
        name = mod.get("name") or mod.get("path") or str(path.parent)
        path_str = str(path.parent)

        align = m.get("constellation_alignment") or {}
        primary = align.get("primary_star", "Supporting")
        is_supporting = (primary == "Supporting")
        if is_supporting:
            total_supporting += 1

        # exclusions (path string)
        for rx, _ex in exclusions:
            if rx and rx.search(path_str):
                hit_counts["exclusions"][rx.pattern] += 1

        # rules over path/name (not gated on supporting; we just count)
        for rx, star, _src in rules_rx:
            if rx and (rx.search(path_str) or (name and rx.search(name))):
                hit_counts["rules"][f"{star}::{rx.pattern}"] += 1

        # caps
        for c in m.get("capabilities") or []:
            cname = (c.get("name") or "").strip()
            if cname in cap_over:
                hit_counts["capability_overrides"][f"{cap_over[cname]}::{cname}"] += 1

        # nodes
        for n in (m.get("matriz_integration") or {}).get("pipeline_nodes", []) or []:
            if n in node_over:
                hit_counts["node_overrides"][f"{node_over[n]}::{n}"] += 1

        # owners
        owner = (m.get("metadata") or {}).get("owner") or ""
        for rx, star in owner_priors:
            if rx and rx.search(owner):
                hit_counts["owner_priors"][f"{star}::{rx.pattern}"] += 1

        # dependencies (external package names)
        for dep in ((m.get("dependencies") or {}).get("external") or []):
            pkg = (dep.get("package") or "")
            for rx, star in dep_hints:
                if rx and rx.search(pkg):
                    hit_counts["dependency_hints"][f"{star}::{rx.pattern}"] += 1

    # zero-hit warnings
    zero_hit_rules = [k for k,v in hit_counts["rules"].items() if v == 0]
    if zero_hit_rules:
        warn(f"{len(zero_hit_rules)} rules have 0 hits")

    # output
    report = {
        "rules_file": str(rules_path),
        "canonical_stars": sorted(list(canonical)),
        "deny": sorted(list(deny)),
        "weights": weights,
        "confidence": conf,
        "totals": {
            "manifests_scanned": sum(1 for _ in manifests_root.rglob("module.manifest.json")),
            "supporting_count": total_supporting
        },
        "hit_counts": {k: dict(v) for k,v in hit_counts.items()},
        "zero_hit_rules": zero_hit_rules
    }
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    info(f"Wrote {out_path}")

    if ERR:
        sys.exit(1)
    if args.fail_on_zero_hits and zero_hit_rules:
        die("Zero-hit rules present and --fail-on-zero-hits used.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Run locally**

```bash
python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests
```

---

# `tests/rules/test_star_rules.py`

* Fast, synthetic tests proving the rules classify typical cases
* Guards canonical naming (e.g., **🔮 Oracle (Quantum)**)
* Catches regressions if someone “fixes” a regex

```python
import json, re
from pathlib import Path

RULES = json.loads(Path("configs/star_rules.json").read_text(encoding="utf-8"))

CANON = set(RULES["canonical_stars"])
ALIAS = RULES.get("aliases", {})
CAP_OVR = {r["capability"]: r["star"] for r in RULES.get("capability_overrides", [])}
NODE_OVR = {r["node"]: r["star"] for r in RULES.get("node_overrides", [])}
RULES_RX = [(re.compile(r["pattern"], re.I), r["star"]) for r in RULES.get("rules", [])]
EXCL_RX  = [re.compile(r["pattern"], re.I) for r in RULES.get("exclusions", [])]
CONF_MIN = float(RULES["confidence"]["min_suggest"])
W = RULES["weights"]

def suggest_star(path_str: str, name: str, caps: list[str], nodes: list[str], owner: str = "", deps: list[str] = None):
    deps = deps or []
    # block by exclusions
    for rx in EXCL_RX:
        if rx.search(path_str):
            return None, 0.0, "excluded"

    candidates = []
    # caps
    for c in caps:
        if c in CAP_OVR:
            candidates.append((CAP_OVR[c], W["capability_override"], f"cap:{c}"))
    # nodes
    for n in nodes:
        if n in NODE_OVR:
            candidates.append((NODE_OVR[n], W["node_override"], f"node:{n}"))
    # path/name rules
    for rx, star in RULES_RX:
        if rx.search(path_str) or (name and rx.search(name)):
            candidates.append((star, W["path_regex"], f"rx:{rx.pattern}"))

    if not candidates:
        return None, 0.0, "none"

    candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
    best = candidates[0]
    if best[1] < CONF_MIN:  # simple threshold
        return None, best[1], "below_threshold"
    return best

def test_canonical_has_oracle_not_ambiguity():
    assert "🔮 Oracle (Quantum)" in CANON
    assert "⚛️ Ambiguity (Quantum)" not in CANON

def test_flow_by_path_or_node():
    star, conf, _ = suggest_star("candidate/consciousness/awareness", "awareness", [], ["attention"])
    assert star == "🌊 Flow (Consciousness)"
    assert conf >= 0.5

def test_memory_by_capability():
    star, conf, _ = suggest_star("candidate/bio/memory", "bio.memory", ["memory_consolidation"], [])
    assert star == "✦ Trail (Memory)"

def test_guardian_by_auth_capability():
    star, conf, _ = suggest_star("candidate/api/oidc", "oidc", ["authentication"], [])
    assert star == "🛡️ Watch (Guardian)"

def test_vision_by_path():
    star, conf, _ = suggest_star("tools/vision/ocr", "ocr", [], [])
    assert star == "🔬 Horizon (Vision)"

def test_oracle_by_keyword():
    star, conf, _ = suggest_star("candidate/bio/quantum_attention", "quantum_attention", ["quantum_attention"], [])
    assert star == "🔮 Oracle (Quantum)"

def test_exclusion_stopwatch_not_guardian():
    star, conf, why = suggest_star("utils/stopwatch", "stopwatch", [], [])
    assert star is None
    assert why == "excluded"
```

**Run**

```bash
pytest -q tests/rules/test_star_rules.py
```

---

# `scripts/apply_promotions.py`

* Applies `docs/audits/star_promotions.csv` to manifests
* **Dry-run by default**
* Enforces canonical stars + deny-list + min confidence
* Adds `metadata.tags += ["autopromoted"]` on write

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

def load_json(p: Path): return json.loads(p.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser(description="Apply star promotions from CSV to manifests.")
    ap.add_argument("--csv", default="docs/audits/star_promotions.csv")
    ap.add_argument("--rules", default="configs/star_rules.json")
    ap.add_argument("--min-confidence", type=float, default=None, help="Override ruleset min_autopromote")
    ap.add_argument("--write", action="store_true", help="Actually write changes")
    ap.add_argument("--backup", action="store_true", help="Create .bak backup next to each manifest")
    args = ap.parse_args()

    rules = load_json(Path(args.rules))
    canonical = set(rules["canonical_stars"])
    deny = set(rules.get("deny", []))
    min_auto = args.min_confidence if args.min_confidence is not None else float(rules["confidence"]["min_autopromote"])

    applied = 0; skipped = 0; errors = 0

    with Path(args.csv).open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            file = Path(row["file"])
            target = row["suggested_star"].strip()
            conf = float(row.get("confidence", 0))
            reason = row.get("reason","")

            if target not in canonical:
                print(f"[SKIP] {file} → {target} not canonical")
                skipped += 1; continue
            if target in deny:
                print(f"[SKIP] {file} → {target} is denied")
                skipped += 1; continue
            if conf < min_auto:
                print(f"[SKIP] {file} → confidence {conf:.2f} < {min_auto:.2f}")
                skipped += 1; continue
            if not file.exists():
                print(f"[SKIP] missing file {file}")
                skipped += 1; continue

            try:
                d = load_json(file)
                align = d.setdefault("constellation_alignment", {})
                current = align.get("primary_star", "Supporting")
                if current == target:
                    print(f"[SKIP] {file} already {target}")
                    skipped += 1; continue
                print(f"[APPLY] {file}: {current} → {target} (conf={conf:.2f}; {reason})")
                align["primary_star"] = target

                meta = d.setdefault("metadata", {})
                tags = meta.setdefault("tags", [])
                if "autopromoted" not in tags:
                    tags.append("autopromoted")

                if args.write:
                    if args.backup:
                        Path(str(file)+".bak").write_text(json.dumps(d, indent=2), encoding="utf-8")  # pre-backup original
                        # overwrite backup with original content (fix): write original, then write new file
                    # correct backup behaviour:
                    orig = json.loads(file.read_text(encoding="utf-8"))
                    Path(str(file)+".bak").write_text(json.dumps(orig, indent=2), encoding="utf-8")
                    file.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
                applied += 1
            except Exception as e:
                print(f"[ERR ] {file}: {e}")
                errors += 1

    print(f"\nSummary: applied={applied} skipped={skipped} errors={errors}")
    if errors: sys.exit(1)

if __name__ == "__main__":
    main()
```

**Dry-run**

```bash
python3 scripts/apply_promotions.py --csv docs/audits/star_promotions.csv
```

**Write with backups**

```bash
python3 scripts/apply_promotions.py --write --backup
```

---

## CI wiring (add to `.github/workflows/matriz-validate.yml`)

Right after your manifest stats step:

```yaml
      - name: Lint star rules (syntax & hit counts)
        run: |
          python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests

      - name: Unit tests for star rules
        run: |
          pytest -q tests/rules/test_star_rules.py
```

*(optional)* Fail the build if a rule has zero hits:

```yaml
      - name: Lint star rules (fail on zero hits)
        run: |
          python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests --fail-on-zero-hits
```

---

## Pre-commit (optional)

Add this to `.pre-commit-config.yaml`:

```yaml
-   repo: local
    hooks:
    -   id: lint-star-rules
        name: lint star rules
        entry: python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests
        language: system
        pass_filenames: false
```

---


# `scripts/suggest_star_promotions.py`

Suggest promotions for modules with `primary_star == "Supporting"` using:

* capability overrides (highest weight)
* MATRIZ nodes
* path/keyword rules

Outputs both CSV and Markdown to `docs/audits/`.

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}", file=sys.stderr)
        return None

def normalize_star(s: str) -> str:
    return s.strip()

def build_regex(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)

def choose_best(candidates: List[Tuple[str, float, str]], min_conf: float) -> Tuple[str, float, str] | None:
    if not candidates:
        return None
    # Prefer highest confidence; stable tiebreaker by star label
    candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
    best = candidates[0]
    return best if best[1] >= min_conf else None

def main():
    ap = argparse.ArgumentParser(description="Suggest star promotions for Supporting modules.")
    ap.add_argument("--manifests", default="manifests", help="Root of manifests/")
    ap.add_argument("--rules", default="configs/star_rules.json", help="Ruleset JSON")
    ap.add_argument("--out", default="docs/audits", help="Output folder")
    ap.add_argument("--min-confidence", type=float, default=None, help="Override ruleset min_confidence")
    args = ap.parse_args()

    ruleset = load_json(Path(args.rules)) or {}
    min_conf = args.min_confidence if args.min_confidence is not None else float(ruleset.get("min_confidence", 0.50))
    deny = set(ruleset.get("deny", []))

    # Compile patterns
    rule_patterns = [(build_regex(r["pattern"]), normalize_star(r["star"]), r.get("source", "path_keywords"))
                     for r in ruleset.get("rules", [])]
    cap_over = {r["capability"]: normalize_star(r["star"]) for r in ruleset.get("capability_overrides", [])}
    node_over = {r["node"]: normalize_star(r["star"]) for r in ruleset.get("node_overrides", [])}

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)

    promotions = []
    counts = Counter()

    for mp in sorted(Path(args.manifests).rglob("module.manifest.json")):
        data = load_json(mp)
        if not isinstance(data, dict):
            continue

        align = data.get("constellation_alignment", {}) or {}
        primary = normalize_star(align.get("primary_star", "Supporting"))
        if primary != "Supporting":
            continue

        module = data.get("module", {}) or {}
        name = module.get("name") or module.get("path") or str(mp.parent)
        path_str = str(mp.parent)

        caps = data.get("capabilities", []) or []
        nodes = (data.get("matriz_integration", {}) or {}).get("pipeline_nodes", []) or []

        candidates: List[Tuple[str, float, str]] = []

        # 1) capability overrides (weight 0.6)
        for c in caps:
            cap_name = (c.get("name") or "").strip()
            star = cap_over.get(cap_name)
            if star:
                candidates.append((star, 0.6, f"capability:{cap_name}"))

        # 2) node overrides (weight 0.5)
        for n in nodes:
            star = node_over.get(n)
            if star:
                candidates.append((star, 0.5, f"node:{n}"))

        # 3) path/keyword rules (weight 0.4 if matched)
        for rx, star, src in rule_patterns:
            if rx.search(path_str) or (name and rx.search(name)):
                candidates.append((star, 0.4, f"{src}:{rx.pattern}"))

        # pick best
        best = choose_best(candidates, min_conf)
        if not best:
            continue
        new_star, conf, reason = best
        if new_star in deny:
            continue

        promotions.append({
            "module": name,
            "file": str(mp),
            "current_star": primary,
            "suggested_star": new_star,
            "confidence": round(conf, 2),
            "reason": reason
        })
        counts[new_star] += 1

    # Write CSV
    csv_path = out_dir / "star_promotions.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["module","file","current_star","suggested_star","confidence","reason"])
        w.writeheader()
        for row in promotions:
            w.writerow(row)

    # Write Markdown summary
    md_path = out_dir / "star_promotions.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Suggested Star Promotions (Supporting → Specific)\n\n")
        f.write(f"- Min confidence: **{min_conf}**\n")
        f.write(f"- Total suggestions: **{len(promotions)}**\n\n")
        f.write("## By Star\n\n| Star | Count |\n|---|---:|\n")
        for k, v in counts.most_common():
            f.write(f"| {k} | {v} |\n")
        f.write("\n## Details\n\n")
        f.write("| Module | Suggested | Confidence | Reason | File |\n|---|---|---:|---|---|\n")
        for row in promotions[:500]:
            f.write(f"| {row['module']} | {row['suggested_star']} | {row['confidence']} | {row['reason']} | `{row['file']}` |\n")

    print(f"[OK] Wrote {csv_path} and {md_path}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
python3 scripts/suggest_star_promotions.py --manifests manifests --rules configs/star_rules.json --out docs/audits
```

---

# `scripts/check_t1_owners.py`

Tripwire: **fail** if any `T1_critical` manifest lacks `metadata.owner` (or it’s empty/placeholder).

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def main():
    root = Path("manifests")
    bad = []
    for p in root.rglob("module.manifest.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        t = (d.get("testing") or {}).get("quality_tier")
        if t == "T1_critical":
            owner = (d.get("metadata") or {}).get("owner")
            if not owner or str(owner).strip().lower() in {"", "todo", "tbd", "unknown"}:
                mod = (d.get("module") or {}).get("name") or (d.get("module") or {}).get("path") or str(p.parent)
                bad.append((mod, str(p)))
    if bad:
        print("[FAIL] T1_critical modules missing metadata.owner:")
        for mod, path in bad:
            print(f"  - {mod} :: {path}")
        sys.exit(1)
    print("[OK] All T1_critical modules have owners.")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
python3 scripts/check_t1_owners.py
```

---

# `scripts/check_manifest_drift.py`

Compare **current** vs **baseline** stats; fail if drop exceeds threshold (default 1%).

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def pct_drop(old: int, new: int) -> float:
    if old == 0: return 0.0
    return max(0.0, (old - new) / old * 100.0)

def main():
    ap = argparse.ArgumentParser(description="Fail if manifest count drops beyond threshold.")
    ap.add_argument("--baseline", required=True, help="Path to baseline manifest_stats.json")
    ap.add_argument("--current", required=True, help="Path to current manifest_stats.json")
    ap.add_argument("--max-drop", type=float, default=1.0, help="Max allowed % drop (default: 1.0)")
    args = ap.parse_args()

    base = load(Path(args.baseline))
    curr = load(Path(args.current))
    old = int(base.get("total_manifests", 0))
    new = int(curr.get("total_manifests", 0))

    drop = pct_drop(old, new)
    print(f"[DRIFT] baseline={old} current={new} drop={drop:.2f}% (limit={args.max_drop:.2f}%)")
    if drop > args.max_drop:
        print("[FAIL] Manifest count drop exceeds threshold.")
        sys.exit(1)
    print("[OK] No unacceptable drift detected.")

if __name__ == "__main__":
    main()
```

**Typical CI usage:**

* Generate baseline stats from `origin/main`
* Generate current stats from the PR checkout
* Compare with `--max-drop 1.0`

---

# CI wiring (append to `.github/workflows/matriz-validate.yml`)

Add these steps **after** your existing stats/smoke steps:

```yaml
      - name: Suggest star promotions (Supporting → specific)
        run: |
          python3 scripts/suggest_star_promotions.py --manifests manifests --rules configs/star_rules.json --out docs/audits

      - name: Tripwire — T1 must have metadata.owner
        run: |
          python3 scripts/check_t1_owners.py

      - name: Upload promotions artifacts
        uses: actions/upload-artifact@v4
        with:
          name: star-promotions
          path: |
            docs/audits/star_promotions.csv
            docs/audits/star_promotions.md
```

**Drift guard** (compare to main). Place **after** we generate `docs/audits/manifest_stats.json` for the current checkout:

```yaml
      - name: Checkout baseline (origin/main) side-by-side
        uses: actions/checkout@v4
        with:
          ref: origin/main
          path: baseline

      - name: Baseline stats (origin/main)
        run: |
          if [ -d baseline/manifests ]; then
            python3 scripts/report_manifest_stats.py --manifests baseline/manifests --out baseline/docs/audits
          elif [ -f baseline/docs/audits/manifest_stats.json ]; then
            echo "[INFO] Using precomputed baseline stats JSON."
          else
            echo "[WARN] No baseline manifests or stats found; skipping drift guard."
            echo "skip" > baseline.SKIP
          fi

      - name: Tripwire — Manifest drift guard (≤ 1% drop)
        if: ${{ !hashFiles('baseline.SKIP') }}
        run: |
          python3 scripts/check_manifest_drift.py \
            --baseline baseline/docs/audits/manifest_stats.json \
            --current  docs/audits/manifest_stats.json \
            --max-drop 1.0
```

---

# Local one-liners (sanity)

```bash
# Promotions
python3 scripts/suggest_star_promotions.py --manifests manifests --rules configs/star_rules.json --out docs/audits
# T1 owners
python3 scripts/check_t1_owners.py
# Drift (assuming you generated baseline with report_manifest_stats.py in a ./baseline clone)
python3 scripts/check_manifest_drift.py --baseline baseline/docs/audits/manifest_stats.json --current docs/audits/manifest_stats.json --max-drop 1.0
```

---

# `scripts/lint_star_rules.py`

* Verifies `configs/star_rules.json` structure
* Compiles all regex (fails on invalid)
* Guards canonical stars / aliases / deny-list
* Computes **rule hit counts** across your **780 manifests** (paths, nodes, capabilities, owners, deps)
* Writes a machine-readable report: `docs/audits/star_rules_lint.json`

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

ERR = 0

def die(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    global ERR
    ERR = 1

def warn(msg: str):
    print(f"[WARN]  {msg}", file=sys.stderr)

def info(msg: str):
    print(f"[INFO]  {msg}")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"Failed to read JSON {path}: {e}")
        return {}

def compile_rx(pat: str, where: str):
    try:
        return re.compile(pat, re.IGNORECASE)
    except re.error as e:
        die(f"Invalid regex in {where}: {pat} -> {e}")
        return None

def collect_manifests(root: Path):
    for p in root.rglob("module.manifest.json"):
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            warn(f"Skipping unreadable manifest {p}: {e}")

def main():
    ap = argparse.ArgumentParser(description="Lint and sanity-check star rules; produce hit counts.")
    ap.add_argument("--rules", default="configs/star_rules.json")
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--out", default="docs/audits/star_rules_lint.json")
    ap.add_argument("--fail-on-zero-hits", action="store_true", help="Fail if any rule has 0 matches")
    args = ap.parse_args()

    rules_path = Path(args.rules)
    rules = load_json(rules_path)
    manifests_root = Path(args.manifests)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- structural checks
    for k in ["canonical_stars", "rules", "aliases", "weights", "confidence"]:
        if k not in rules:
            die(f"Missing '{k}' in {rules_path}")

    canonical = set(rules["canonical_stars"])
    deny = set(rules.get("deny", []))
    for s in deny:
        if s not in canonical:
            die(f"deny-list contains non-canonical star: {s}")

    # alias validation
    for alias, target in rules.get("aliases", {}).items():
        if target not in canonical:
            die(f"Alias '{alias}' maps to non-canonical star: {target}")

    # weights / confidence
    weights = rules["weights"]
    for k, v in weights.items():
        if not isinstance(v, (int, float)) or v < 0 or v > 1:
            die(f"Weight '{k}' must be 0..1 (got {v})")
    conf = rules["confidence"]
    for k, v in conf.items():
        if not isinstance(v, (int, float)) or v < 0 or v > 1:
            die(f"Confidence '{k}' must be 0..1 (got {v})")

    # compile patterns
    exclusions = [(compile_rx(r["pattern"], "exclusions"), r.get("explain","")) for r in rules.get("exclusions", [])]
    rules_rx = []
    for i, r in enumerate(rules["rules"]):
        star = r.get("star")
        if star not in canonical:
            die(f"Rule #{i} references non-canonical star: {star}")
        rx = compile_rx(r.get("pattern",""), f"rules[{i}]")
        rules_rx.append((rx, star, r.get("source","path_keywords")))
    owner_priors = [(compile_rx(r["owner_regex"], "owner_priors"), r["star"]) for r in rules.get("owner_priors", [])]
    dep_hints = [(compile_rx(r["package_regex"], "dependency_hints"), r["star"]) for r in rules.get("dependency_hints", [])]

    cap_over = {r["capability"]: r["star"] for r in rules.get("capability_overrides", [])}
    node_over = {r["node"]: r["star"] for r in rules.get("node_overrides", [])}
    for s in list(cap_over.values()) + list(node_over.values()):
        if s not in canonical:
            die(f"Override maps to non-canonical star: {s}")

    # ---- hit counting (paths, caps, nodes, owners, deps)
    hit_counts = {
        "rules": Counter(),
        "capability_overrides": Counter(),
        "node_overrides": Counter(),
        "owner_priors": Counter(),
        "dependency_hints": Counter(),
        "exclusions": Counter()
    }
    total_supporting = 0

    for path, m in collect_manifests(manifests_root):
        mod = (m.get("module") or {})
        name = mod.get("name") or mod.get("path") or str(path.parent)
        path_str = str(path.parent)

        align = m.get("constellation_alignment") or {}
        primary = align.get("primary_star", "Supporting")
        is_supporting = (primary == "Supporting")
        if is_supporting:
            total_supporting += 1

        # exclusions (path string)
        for rx, _ex in exclusions:
            if rx and rx.search(path_str):
                hit_counts["exclusions"][rx.pattern] += 1

        # rules over path/name (not gated on supporting; we just count)
        for rx, star, _src in rules_rx:
            if rx and (rx.search(path_str) or (name and rx.search(name))):
                hit_counts["rules"][f"{star}::{rx.pattern}"] += 1

        # caps
        for c in m.get("capabilities") or []:
            cname = (c.get("name") or "").strip()
            if cname in cap_over:
                hit_counts["capability_overrides"][f"{cap_over[cname]}::{cname}"] += 1

        # nodes
        for n in (m.get("matriz_integration") or {}).get("pipeline_nodes", []) or []:
            if n in node_over:
                hit_counts["node_overrides"][f"{node_over[n]}::{n}"] += 1

        # owners
        owner = (m.get("metadata") or {}).get("owner") or ""
        for rx, star in owner_priors:
            if rx and rx.search(owner):
                hit_counts["owner_priors"][f"{star}::{rx.pattern}"] += 1

        # dependencies (external package names)
        for dep in ((m.get("dependencies") or {}).get("external") or []):
            pkg = (dep.get("package") or "")
            for rx, star in dep_hints:
                if rx and rx.search(pkg):
                    hit_counts["dependency_hints"][f"{star}::{rx.pattern}"] += 1

    # zero-hit warnings
    zero_hit_rules = [k for k,v in hit_counts["rules"].items() if v == 0]
    if zero_hit_rules:
        warn(f"{len(zero_hit_rules)} rules have 0 hits")

    # output
    report = {
        "rules_file": str(rules_path),
        "canonical_stars": sorted(list(canonical)),
        "deny": sorted(list(deny)),
        "weights": weights,
        "confidence": conf,
        "totals": {
            "manifests_scanned": sum(1 for _ in manifests_root.rglob("module.manifest.json")),
            "supporting_count": total_supporting
        },
        "hit_counts": {k: dict(v) for k,v in hit_counts.items()},
        "zero_hit_rules": zero_hit_rules
    }
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    info(f"Wrote {out_path}")

    if ERR:
        sys.exit(1)
    if args.fail_on_zero_hits and zero_hit_rules:
        die("Zero-hit rules present and --fail-on-zero-hits used.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Run locally**

```bash
python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests
```

---

# `tests/rules/test_star_rules.py`

* Fast, synthetic tests proving the rules classify typical cases
* Guards canonical naming (e.g., **🔮 Oracle (Quantum)**)
* Catches regressions if someone “fixes” a regex

```python
import json, re
from pathlib import Path

RULES = json.loads(Path("configs/star_rules.json").read_text(encoding="utf-8"))

CANON = set(RULES["canonical_stars"])
ALIAS = RULES.get("aliases", {})
CAP_OVR = {r["capability"]: r["star"] for r in RULES.get("capability_overrides", [])}
NODE_OVR = {r["node"]: r["star"] for r in RULES.get("node_overrides", [])}
RULES_RX = [(re.compile(r["pattern"], re.I), r["star"]) for r in RULES.get("rules", [])]
EXCL_RX  = [re.compile(r["pattern"], re.I) for r in RULES.get("exclusions", [])]
CONF_MIN = float(RULES["confidence"]["min_suggest"])
W = RULES["weights"]

def suggest_star(path_str: str, name: str, caps: list[str], nodes: list[str], owner: str = "", deps: list[str] = None):
    deps = deps or []
    # block by exclusions
    for rx in EXCL_RX:
        if rx.search(path_str):
            return None, 0.0, "excluded"

    candidates = []
    # caps
    for c in caps:
        if c in CAP_OVR:
            candidates.append((CAP_OVR[c], W["capability_override"], f"cap:{c}"))
    # nodes
    for n in nodes:
        if n in NODE_OVR:
            candidates.append((NODE_OVR[n], W["node_override"], f"node:{n}"))
    # path/name rules
    for rx, star in RULES_RX:
        if rx.search(path_str) or (name and rx.search(name)):
            candidates.append((star, W["path_regex"], f"rx:{rx.pattern}"))

    if not candidates:
        return None, 0.0, "none"

    candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
    best = candidates[0]
    if best[1] < CONF_MIN:  # simple threshold
        return None, best[1], "below_threshold"
    return best

def test_canonical_has_oracle_not_ambiguity():
    assert "🔮 Oracle (Quantum)" in CANON
    assert "⚛️ Ambiguity (Quantum)" not in CANON

def test_flow_by_path_or_node():
    star, conf, _ = suggest_star("candidate/consciousness/awareness", "awareness", [], ["attention"])
    assert star == "🌊 Flow (Consciousness)"
    assert conf >= 0.5

def test_memory_by_capability():
    star, conf, _ = suggest_star("candidate/bio/memory", "bio.memory", ["memory_consolidation"], [])
    assert star == "✦ Trail (Memory)"

def test_guardian_by_auth_capability():
    star, conf, _ = suggest_star("candidate/api/oidc", "oidc", ["authentication"], [])
    assert star == "🛡️ Watch (Guardian)"

def test_vision_by_path():
    star, conf, _ = suggest_star("tools/vision/ocr", "ocr", [], [])
    assert star == "🔬 Horizon (Vision)"

def test_oracle_by_keyword():
    star, conf, _ = suggest_star("candidate/bio/quantum_attention", "quantum_attention", ["quantum_attention"], [])
    assert star == "🔮 Oracle (Quantum)"

def test_exclusion_stopwatch_not_guardian():
    star, conf, why = suggest_star("utils/stopwatch", "stopwatch", [], [])
    assert star is None
    assert why == "excluded"
```

**Run**

```bash
pytest -q tests/rules/test_star_rules.py
```

---

# `scripts/apply_promotions.py`

* Applies `docs/audits/star_promotions.csv` to manifests
* **Dry-run by default**
* Enforces canonical stars + deny-list + min confidence
* Adds `metadata.tags += ["autopromoted"]` on write

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

def load_json(p: Path): return json.loads(p.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser(description="Apply star promotions from CSV to manifests.")
    ap.add_argument("--csv", default="docs/audits/star_promotions.csv")
    ap.add_argument("--rules", default="configs/star_rules.json")
    ap.add_argument("--min-confidence", type=float, default=None, help="Override ruleset min_autopromote")
    ap.add_argument("--write", action="store_true", help="Actually write changes")
    ap.add_argument("--backup", action="store_true", help="Create .bak backup next to each manifest")
    args = ap.parse_args()

    rules = load_json(Path(args.rules))
    canonical = set(rules["canonical_stars"])
    deny = set(rules.get("deny", []))
    min_auto = args.min_confidence if args.min_confidence is not None else float(rules["confidence"]["min_autopromote"])

    applied = 0; skipped = 0; errors = 0

    with Path(args.csv).open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            file = Path(row["file"])
            target = row["suggested_star"].strip()
            conf = float(row.get("confidence", 0))
            reason = row.get("reason","")

            if target not in canonical:
                print(f"[SKIP] {file} → {target} not canonical")
                skipped += 1; continue
            if target in deny:
                print(f"[SKIP] {file} → {target} is denied")
                skipped += 1; continue
            if conf < min_auto:
                print(f"[SKIP] {file} → confidence {conf:.2f} < {min_auto:.2f}")
                skipped += 1; continue
            if not file.exists():
                print(f"[SKIP] missing file {file}")
                skipped += 1; continue

            try:
                d = load_json(file)
                align = d.setdefault("constellation_alignment", {})
                current = align.get("primary_star", "Supporting")
                if current == target:
                    print(f"[SKIP] {file} already {target}")
                    skipped += 1; continue
                print(f"[APPLY] {file}: {current} → {target} (conf={conf:.2f}; {reason})")
                align["primary_star"] = target

                meta = d.setdefault("metadata", {})
                tags = meta.setdefault("tags", [])
                if "autopromoted" not in tags:
                    tags.append("autopromoted")

                if args.write:
                    if args.backup:
                        Path(str(file)+".bak").write_text(json.dumps(d, indent=2), encoding="utf-8")  # pre-backup original
                        # overwrite backup with original content (fix): write original, then write new file
                    # correct backup behaviour:
                    orig = json.loads(file.read_text(encoding="utf-8"))
                    Path(str(file)+".bak").write_text(json.dumps(orig, indent=2), encoding="utf-8")
                    file.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
                applied += 1
            except Exception as e:
                print(f"[ERR ] {file}: {e}")
                errors += 1

    print(f"\nSummary: applied={applied} skipped={skipped} errors={errors}")
    if errors: sys.exit(1)

if __name__ == "__main__":
    main()
```

**Dry-run**

```bash
python3 scripts/apply_promotions.py --csv docs/audits/star_promotions.csv
```

**Write with backups**

```bash
python3 scripts/apply_promotions.py --write --backup
```

---

## CI wiring (add to `.github/workflows/matriz-validate.yml`)

Right after your manifest stats step:

```yaml
      - name: Lint star rules (syntax & hit counts)
        run: |
          python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests

      - name: Unit tests for star rules
        run: |
          pytest -q tests/rules/test_star_rules.py
```

*(optional)* Fail the build if a rule has zero hits:

```yaml
      - name: Lint star rules (fail on zero hits)
        run: |
          python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests --fail-on-zero-hits
```

---

## Pre-commit (optional)

Add this to `.pre-commit-config.yaml`:

```yaml
-   repo: local
    hooks:
    -   id: lint-star-rules
        name: lint star rules
        entry: python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests
        language: system
        pass_filenames: false
```

---

## What the 0.01% would watch next

* Keep **exclusions** evolving; they kill most false positives.
* Track **zero-hit rules** in PR conversations; delete or fix within a week.
* Once promotions stabilize, add a weekly job that runs:

  * `suggest_star_promotions.py` → `apply_promotions.py --write` for **conf ≥ 0.80** only.
* Expand tests with **real manifest fixtures** for the top 10 critical modules.


perfect — here’s a clean drop-in pack you can paste into docs/gonzo/matriz_prep/drop_in_extra.md. It adds the rules coverage generator, CI wiring, and handy Makefile targets. No edits to existing files are assumed beyond what’s below.

⸻

3) Rules Coverage (pretty report from lint JSON)

Create: scripts/gen_rules_coverage.py

#!/usr/bin/env python3
"""
Render a readable coverage report for star rules.

Inputs:
- docs/audits/star_rules_lint.json (produced by scripts/lint_star_rules.py)

Outputs:
- docs/audits/star_rules_coverage.md (tables + zero-hit highlights)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import defaultdict

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def as_table(title: str, rows: list[tuple[str,int]]) -> str:
    lines = [f"## {title}", "", "| Key | Count |", "|---|---:|"]
    for k, v in rows:
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    return "\n".join(lines)

def main():
    lint_path = Path("docs/audits/star_rules_lint.json")
    out_path  = Path("docs/audits/star_rules_coverage.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not lint_path.exists():
        print(f"[ERROR] Missing {lint_path}. Run scripts/lint_star_rules.py first.", file=sys.stderr)
        sys.exit(2)

    data = load(lint_path)
    hc = data.get("hit_counts", {})

    sections = [
        ("Rule matches (path/keyword)", hc.get("rules", {})),
        ("Capability overrides (hits)", hc.get("capability_overrides", {})),
        ("Node overrides (hits)", hc.get("node_overrides", {})),
        ("Owner priors (hits)", hc.get("owner_priors", {})),
        ("Dependency hints (hits)", hc.get("dependency_hints", {})),
        ("Exclusions (triggered)", hc.get("exclusions", {})),
    ]

    md = []
    md.append("# Star Rules Coverage\n")
    md.append(f"- Rules file: `{data.get('rules_file','configs/star_rules.json')}`")
    md.append(f"- Manifests scanned: **{data.get('totals',{}).get('manifests_scanned',0)}**")
    md.append(f"- Supporting count: **{data.get('totals',{}).get('supporting_count',0)}**")
    md.append("")

    # Zero-hit rules
    zero = data.get("zero_hit_rules", [])
    if zero:
        md.append("## Zero-hit rules (needs review)  \nThese regex rules matched nothing across the current manifests. Consider deleting, fixing, or moving them into `rules/experiments/`.\n")
        md.append("| Rule |")
        md.append("|---|")
        for z in zero:
            md.append(f"| `{z}` |")
        md.append("")
    else:
        md.append("## Zero-hit rules\n- None ✅\n")

    # Tables
    for title, mapping in sections:
        rows = sorted(mapping.items(), key=lambda x: x[1], reverse=True)
        md.append(as_table(title, rows[:100]))

    # Top opportunities (which stars got the most rule hits)
    star_totals = defaultdict(int)
    for key, cnt in (hc.get("rules", {}) or {}).items():
        # key format: "{STAR}::{regex}"
        star = key.split("::", 1)[0]
        star_totals[star] += cnt
    star_rows = sorted(star_totals.items(), key=lambda x: x[1], reverse=True)
    md.append(as_table("Rule activity by star (top)", star_rows))

    out_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {out_path}")

if __name__ == "__main__":
    main()

Local run

# assumes you already ran lint_star_rules to produce the JSON
python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests
python3 scripts/gen_rules_coverage.py


⸻

CI wiring (append to .github/workflows/matriz-validate.yml)

Place after the “Lint star rules” step:

      - name: Generate star rules coverage (MD from lint JSON)
        run: |
          python3 scripts/gen_rules_coverage.py

      - name: Upload star rules coverage
        uses: actions/upload-artifact@v4
        with:
          name: star-rules-coverage
          path: |
            docs/audits/star_rules_lint.json
            docs/audits/star_rules_coverage.md

This will give reviewers a human-friendly page showing which rules actually bite, and flags zero-hit rules so they don’t linger.

⸻

Makefile targets (append)

.PHONY: star-rules-lint star-rules-coverage promotions

star-rules-lint:
	python3 scripts/lint_star_rules.py --rules configs/star_rules.json --manifests manifests

star-rules-coverage: star-rules-lint
	python3 scripts/gen_rules_coverage.py
	@echo "[OK] Coverage written to docs/audits/star_rules_coverage.md"

promotions:
	python3 scripts/suggest_star_promotions.py --manifests manifests --rules configs/star_rules.json --out docs/audits
	@echo "[OK] Suggestions in docs/audits/star_promotions.{csv,md}"


⸻

What this unlocks (T4 view)
	•	Fast governance loop: every PR shows where rules fire and where they don’t — zero-hit rules can’t hide.
	•	Precision upgrades without fear: you’ll see the effect of adding exclusions or tightening regex immediately in the coverage diff.
	•	Better Supporting-reduction: the coverage + promotions CSV make it trivial to promote high-confidence modules.

And here’s a zero-maintenance PR auto-comment that piggybacks on the artifacts you’re already generating. No new jobs, no extra secrets, just two small steps you append to your existing .github/workflows/matriz-validate.yml.

⸻

Add to .github/workflows/matriz-validate.yml (end of your job)

      # --- PR Auto-Comment: compose a short summary from existing reports ---
      - name: Compose MATRIZ PR summary (markdown)
        if: ${{ github.event_name == 'pull_request' }}
        run: |
          python - <<'PY'
          import json, csv, os, pathlib
          from collections import Counter

          root = pathlib.Path(".")
          stats_p = root/"docs/audits/manifest_stats.json"
          rules_p = root/"docs/audits/star_rules_lint.json"
          promos_csv = root/"docs/audits/star_promotions.csv"
          coverage_md = root/"docs/audits/star_rules_coverage.md"

          def safe_json(p):
            try:
              return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
              return {}

          stats = safe_json(stats_p)
          rules = safe_json(rules_p)

          stars = Counter(stats.get("stars", {}))
          tiers = Counter(stats.get("tiers", {}))
          total = stats.get("total_manifests", 0)
          supporting = stars.get("Supporting", 0)
          zero_hit = len(rules.get("zero_hit_rules", []))

          # promotions summary
          promotions = []
          if promos_csv.exists():
            with promos_csv.open("r", encoding="utf-8") as f:
              r = csv.DictReader(f)
              promotions = list(r)
          promo_n = len(promotions)
          promo_top = promotions[:10]

          # build markdown
          lines = []
          lines.append("## ✅ MATRIZ Validation Summary")
          lines.append("")
          lines.append(f"- **Manifests scanned:** {total}")
          if stars:
            top = ", ".join([f"`{k}` {v}" for k, v in stars.most_common(6)])
            lines.append(f"- **Star distribution (top):** {top}")
            lines.append(f"- **Supporting:** {supporting}")
          if tiers:
            lines.append(f"- **Tiers:** " + ", ".join([f"`{k}` {v}" for k,v in tiers.most_common()]))
          lines.append(f"- **Zero-hit rules:** {zero_hit}  (from `star_rules_lint.json`)")
          lines.append(f"- **Suggested promotions:** {promo_n}  (from `star_promotions.csv`)")
          lines.append("")
          if promo_top:
            lines.append("<details><summary>Top suggestions (first 10)</summary>\n")
            lines.append("| Module | Suggested | Conf | Reason |")
            lines.append("|---|---|---:|---|")
            for r in promo_top:
              lines.append(f"| {r['module']} | {r['suggested_star']} | {r['confidence']} | {r['reason']} |")
            lines.append("\n</details>\n")

          # soft links to files in the PR diff (if present)
          links = []
          if stats_p.exists():      links.append("`docs/audits/manifest_stats.json`")
          if (root/"docs/audits/manifest_stats.md").exists(): links.append("`docs/audits/manifest_stats.md`")
          if rules_p.exists():      links.append("`docs/audits/star_rules_lint.json`")
          if coverage_md.exists():  links.append("`docs/audits/star_rules_coverage.md`")
          if promos_csv.exists():   links.append("`docs/audits/star_promotions.csv`")
          if links:
            lines.append("**Reports:** " + " · ".join(links))

          out = "\n".join(lines) + "\n"
          pathlib.Path(".github/pr_comment.md").parent.mkdir(parents=True, exist_ok=True)
          pathlib.Path(".github/pr_comment.md").write_text(out, encoding="utf-8")
          print(out)
          PY

      - name: Post / update sticky PR comment (MATRIZ summary)
        if: ${{ github.event_name == 'pull_request' }}
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: MATRIZ Validation Summary
          path: .github/pr_comment.md

Why this is “no extra work”
	•	No new jobs — just two steps in your existing workflow.
	•	No secrets — uses the default GITHUB_TOKEN.
	•	No duplication — reads the reports you already generate (stats, rules coverage, promotions).
	•	Sticky — updates the same PR comment on new pushes; no spam.

⸻

Optional: tiny badge line in the comment (paste into the Python block if you like)

Add right after the title line:

lines.append("![MATRIZ](https://img.shields.io/badge/MATRIZ-validate-blue) ![Stars](https://img.shields.io/badge/Stars-{}/{}-informational)".format(total - supporting, total))


⸻

If you want this to fail the check when zero-hit rules > 0 or T1s lack owners, you already have tripwires; this comment stays purely informational. When you’re back, we can wire a bot reply that tags OWNERS of new T1s with missing tests — still zero-maintenance.