# High-leverage hygiene & visibility for MATRIZ
---

## 1) Pre-commit (copy as `.pre-commit-config.yaml`)

```yaml
repos:
  # Core hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict

  # Ruff linter + formatter (use Ruff as single source of truth)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Conventional commits (commit-msg hook)
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.28.0
    hooks:
      - id: commitizen
        stages: [commit-msg]

  # Secrets baseline (fast, repo-friendly)
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]

  # Local hooks (schema & manifest checks)
  - repo: local
    hooks:
      - id: manifest-validate
        name: Validate MATRIZ manifests (jsonschema)
        entry: python scripts/validate_manifests.py --schema schemas/matriz_module_compliance.schema.json --root .
        language: system
        pass_filenames: false
        stages: [commit, push]
      - id: forbid-debug-prints
        name: Forbid debug prints
        entry: bash -c "rg -n \"\\b(print|pdb\\.set_trace)\\b\" --glob '!venv' --glob '!**/*.md' && exit 1 || exit 0"
        language: system
        pass_filenames: false
        stages: [commit]
```

**Setup (once):**

```bash
pip install pre-commit detect-secrets
detect-secrets scan > .secrets.baseline
pre-commit install
pre-commit install --hook-type commit-msg
```

---

## 2) Tiny JSON config for the Markdown “Top” generator

### `scripts/top_config.json`

```json
{
  "title": "Constellation Top",
  "limit_per_star": 15,
  "stars_order": [
    "⚛️ Anchor (Identity)",
    "✦ Trail (Memory)",
    "🔬 Horizon (Vision)",
    "🌱 Living (Bio)",
    "🌙 Drift (Dream)",
    "⚖️ North (Ethics)",
    "🛡️ Watch (Guardian)",
    "🔮 Oracle (Quantum)",
    "🌊 Flow (Consciousness)"
  ],
  "sections": [
    {"name": "Top Critical (T1)", "tiers": ["T1_critical"]},
    {"name": "Important (T2)", "tiers": ["T2_important"]},
    {"name": "Gaps (no context.md)", "tiers": ["T1_critical","T2_important","T3_standard","T4_experimental"], "missing_context_only": true}
  ]
}
```

### `scripts/gen_constellation_top.py`

```python
#!/usr/bin/env python3
"""
Generate docs/CONSTELLATION_TOP.md + per-star pages from manifests.

Inputs:
  - scripts/top_config.json
  - scripts/star_canon.json
  - manifests/**/module.manifest.json

Outputs:
  - docs/CONSTELLATION_TOP.md
  - docs/stars/<star_slug>.md
"""
import json, pathlib, datetime, re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "manifests"
DOCS = ROOT / "docs"
STARS_DIR = DOCS / "stars"
CONFIG = pathlib.Path(__file__).resolve().parent / "top_config.json"
CANON = pathlib.Path(__file__).resolve().parent / "star_canon.json"

def slug(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s.lower()

def load_manifests():
    for f in MANIFESTS.rglob("module.manifest.json"):
        try:
            yield f, json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue

def main():
    conf = json.loads(CONFIG.read_text(encoding="utf-8"))
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    order = conf.get("stars_order", canon.get("stars", []))
    stars_set = set(canon.get("stars", []))

    # Aggregate
    per_star = defaultdict(list)
    total = 0
    for path, m in load_manifests():
        total += 1
        star = (m.get("constellation_alignment", {}).get("primary_star")
                or "Supporting")
        if star not in stars_set and star != "Supporting":
            # normalize via aliases
            star = canon.get("aliases", {}).get(star, star)
        tier = m.get("testing", {}).get("quality_tier", "T4_experimental")
        fqn = m.get("module", {}).get("name") or m.get("module", {}).get("path")
        ctx = (path.parent / "lukhas_context.md").exists()
        info = {
            "fqn": fqn,
            "path": str(path.parent.relative_to(ROOT)),
            "tier": tier,
            "ctx": ctx,
            "matriz": ",".join(m.get("matriz_integration",{}).get("pipeline_nodes", []))
        }
        per_star[star].append(info)

    # Ensure dirs
    STARS_DIR.mkdir(parents=True, exist_ok=True)

    # Per star pages
    perstar_links = []
    for star in order:
        items = per_star.get(star, [])
        items.sort(key=lambda x: (x["tier"], x["fqn"]))
        star_slug = slug(star)
        out = STARS_DIR / f"{star_slug}.md"
        lines = [f"# {star}\n", f"_Generated {datetime.datetime.utcnow().isoformat()}Z_\n",
                 f"\n**Modules:** {len(items)}\n\n",
                 "| Tier | MATRIZ | Context | Module | Path |\n|---|---|---|---|---|\n"]
        for it in items:
            lines.append(f"| {it['tier']} | {it['matriz']} | {'✅' if it['ctx'] else '—'} | `{it['fqn']}` | `{it['path']}` |\n")
        out.write_text("".join(lines), encoding="utf-8")
        perstar_links.append(f"- [{star}](stars/{star_slug}.md) — {len(items)} modules")

    # Top summary
    md = [f"# {conf.get('title','Constellation Top')}\n",
          f"_Generated {datetime.datetime.utcnow().isoformat()}Z_\n\n",
          f"**Total manifests scanned:** {total}\n\n",
          "## Stars\n", "\n".join(perstar_links), "\n\n"]

    limit = conf.get("limit_per_star", 15)
    for section in conf.get("sections", []):
        name = section["name"]
        tiers = set(section.get("tiers", []))
        missing_ctx_only = section.get("missing_context_only", False)
        md.append(f"## {name}\n")
        for star in order:
            items = per_star.get(star, [])
            if tiers:
                items = [i for i in items if i["tier"] in tiers]
            if missing_ctx_only:
                items = [i for i in items if not i["ctx"]]
            if not items:
                continue
            md.append(f"\n### {star}\n")
            md.append("| Tier | MATRIZ | Context | Module | Path |\n|---|---|---|---|---|\n")
            for it in items[:limit]:
                md.append(f"| {it['tier']} | {it['matriz']} | {'✅' if it['ctx'] else '—'} | `{it['fqn']}` | `{it['path']}` |\n")
        md.append("\n")

    (DOCS / "CONSTELLATION_TOP.md").write_text("".join(md), encoding="utf-8")
    print("Generated docs/CONSTELLATION_TOP.md and docs/stars/*.md")

if __name__ == "__main__":
    main()
```

**Makefile additions**

```make
top:
	python scripts/gen_constellation_top.py
```

---

## 3) Lucas Context Files — upgrade guidance (quick, high ROI)

Adopt this **header block** (first 10 lines) for **every** `lukhas_context.md` to standardize skimming:

```markdown
---
star: 🌊 Flow (Consciousness)
tier: T2_important
matriz: [thought, attention]
colony: simulation
owner: <agent or person>
contracts:
  publishes: []
  subscribes: []
observability:
  logger: <package.logger>
---
```

Followed by the scaffold you already have (What it does / Contracts / Observability / Security / Tests). This YAML front-matter makes dashboards and search trivial.

---

## 4) Safe flattening kit (optional, run after artifacts)

### `META_REGISTRY.json` (mapping legacy → new FQNs)

```json
{
  "version": 1,
  "mappings": [
    {"from": "candidate.consciousness.dream.core", "to": "lukhas.consciousness.dream.core"},
    {"from": "candidate.api.oidc", "to": "lukhas.identity.oidc"},
    {"from": "candidate.bridge.api", "to": "lukhas.interface.bridge.api"}
  ]
}
```

### `scripts/flatten_imports.py`

```python
#!/usr/bin/env python3
"""
Rewrite imports according to META_REGISTRY.json mapping (dry-run by default).

Usage:
  python scripts/flatten_imports.py --registry META_REGISTRY.json [--apply]
"""
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = list(ROOT.rglob("*.py"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="META_REGISTRY.json")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    reg = json.loads(pathlib.Path(args.registry).read_text(encoding="utf-8"))
    repls = [(r["from"], r["to"]) for r in reg.get("mappings", [])]

    changed = 0
    for f in PY:
        if f.as_posix().startswith(("venv/", ".venv/")):
            continue
        text = f.read_text(encoding="utf-8")
        orig = text
        for src, dst in repls:
            text = re.sub(rf"\bfrom {re.escape(src)}\b", f"from {dst}", text)
            text = re.sub(rf"\bimport {re.escape(src)}\b", f"import {dst}", text)
        if text != orig:
            changed += 1
            print(("DRY" if not args.apply else "APPLY"), f"→ {f}")
            if args.apply:
                f.write_text(text, encoding="utf-8")
    print("Files touched:", changed)

if __name__ == "__main__":
    main()
```

**Tip:** run `python scripts/flatten_imports.py` (dry-run), inspect diffs, then `--apply` in a small batch.

---

## 5) Extra 0.01% moves (surgical, high leverage)

1. **Star Canon as NPM/py pkg**: export `star_canon.json` via a tiny Python module and (optionally) web UI bundle so docs, schema, and generators all import the same constants.
2. **Contracts registry**: `contracts/` folder with `<topic>@v1.json` schemas; manifests’ `events.publishes/subscribes` must match these IDs.
3. **Golden sample manifests**: `tests/manifests/golden/*.json` validated in CI to prevent schema regressions.
4. **Freeze tags**: adopt `release/FREEZE.md` with checkboxes (perf/obs/security signoffs) used during Go/No-Go.
5. **CI concurrency**: cancel superseded runs on PR updates; tighten timeouts; upload validator output as an artifact.
6. **Module owners file**: `OWNERS.toml` mapping FQNs → owners, used by the generator to stamp `metadata.owner`.
7. **Smoke shards**: create `pytest -k matriz_smoke` suite that only hits star-critical surfaces; target < 120s.
8. **Guardian belts**: simple code-level guards—ban `eval/exec` and `subprocess` in T1 unless whitelisted via policy.
9. **Perf knobs**: in manifests, allow per-module `latency_target_p95` and assert them in smoke (warn if exceeded).
10. **Doc bots**: add a `docs/check_links.py` to flag broken cross-links in context files and star pages.

---

## 6) CI patchlets (add to your existing workflow)

* **Cache** pip:

```yaml
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

* **Cancel in-progress on new push**:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

---

## 7) Quick commands (wire the new bits)

```bash
# pre-commit
pip install pre-commit detect-secrets
detect-secrets scan > .secrets.baseline
pre-commit install && pre-commit install --hook-type commit-msg

# generate constellation dashboards
make top

# optional: dry-run import flattening
python scripts/flatten_imports.py --registry META_REGISTRY.json
```

---

## 8) What to update now (prioritized)

* **Update all star-critical `lukhas_context.md`** with the YAML header and fill Contracts/Observability/Security.
* **Adopt pre-commit** in the repo (it saves hours immediately).
* **Run the “Top” generator** and skim `docs/CONSTELLATION_TOP.md` to assign owners / fill the biggest gaps.
* **Decide & lock the first batch of FQN mappings** in `META_REGISTRY.json`, but run the rewrite **after** artifacts land.

