 
---

# 1) Troubleshooting page — `docs/check_contracts_refs.md`

````markdown
# Contracts Reference Checks — Troubleshooting

This guide helps resolve CI failures from:
- `scripts/validate_contract_refs.py`
- `docs/check_links.py` (when linking to contracts in docs)

## Contract IDs: Naming Rules

- Format: **`<topic>@v<major>`**
- Allowed chars in `<topic>`: `[a-z0-9_.:-]+`
- Examples:
  - `memory.write@v1`
  - `guardian.policy.violation@v1`
  - `identity.oauth.callback@v2`

## Typical Failure Messages

- **`invalid contract id: X`**
  - The ID doesn’t match `<topic>@v<major>`.
  - ✅ Fix: Rename to `something.meaningful@v1`.

- **`unknown contract: X`**
  - A manifest references a contract not found in `contracts/`.
  - ✅ Fix: Create `contracts/<ID>.json` with a JSON Schema for the payload.

- **Anchor mismatch (`[FAIL missing anchor]`)**
  - A Markdown link uses `#heading` that doesn’t exist in the target file.
  - ✅ Fix: Ensure the target page has a `# Heading` that slugifies to that anchor.

## How to Add a New Contract

1. Pick an ID:
   - `my.feature.event@v1`
2. Create schema:
   - `contracts/my.feature.event@v1.json`
3. Update manifests that publish/subscribe:
   - `observability.events.publishes/subscribes` list must include the exact ID.
4. Validate locally:
   ```bash
   python scripts/validate_contract_refs.py
   python docs/check_links.py --root .
````

## Versioning Guidance

* Backward-compatible changes: expand schema in place (still `@v1`).
* Breaking changes: bump to `@v2` and keep both schemas side-by-side until migration completes.

## Quick Checklist

* [ ] IDs conform to `<topic>@v<major>`
* [ ] Schema exists under `contracts/`
* [ ] Manifests reference existing IDs
* [ ] Docs link to the right files/anchors
* [ ] CI green: contract validator & link checker

````

---

# 2) Stats reporter — `scripts/report_manifest_stats.py`

```python
#!/usr/bin/env python3
"""
Compute manifest stats (per star, per tier, context coverage) and export:
- docs/audits/manifest_stats.json
- docs/audits/manifest_stats.md

Usage:
  python scripts/report_manifest_stats.py [--manifests manifests] [--out docs/audits]
"""
import json, pathlib, datetime, collections

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--out", default="docs/audits")
    args = ap.parse_args()

    root = pathlib.Path(".").resolve()
    mroot = (root / args.manifests)
    outdir = (root / args.out); outdir.mkdir(parents=True, exist_ok=True)

    records = []
    total = 0
    stars = collections.Counter()
    tiers = collections.Counter()
    context_yes = 0

    for mf in mroot.rglob("module.manifest.json"):
        total += 1
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        star = (m.get("constellation_alignment", {}) or {}).get("primary_star") or "Supporting"
        tier = (m.get("testing", {}) or {}).get("quality_tier") or "T4_experimental"
        ctx = (mf.parent / "lukhas_context.md").exists()

        stars[star] += 1
        tiers[tier] += 1
        if ctx: context_yes += 1

        records.append({
            "path": str(mf.parent),
            "module": m.get("module", {}).get("name") or m.get("module", {}).get("path"),
            "star": star,
            "tier": tier,
            "has_context": ctx,
            "matriz_nodes": (m.get("matriz_integration", {}) or {}).get("pipeline_nodes", []),
        })

    context_pct = round(100.0 * context_yes / max(1, total), 1)

    data = {
        "generated_at": datetime.datetime.utcnow().isoformat()+"Z",
        "total_manifests": total,
        "by_star": stars,
        "by_tier": tiers,
        "context_coverage_pct": context_pct,
        "sample": records[:30],
    }

    # JSON
    (outdir / "manifest_stats.json").write_text(
        json.dumps(data, indent=2, default=lambda x: dict(x) if isinstance(x, collections.Counter) else x),
        encoding="utf-8"
    )

    # Markdown
    md = []
    md.append(f"# Manifest Stats\n\n_Generated {data['generated_at']}_\n\n")
    md.append(f"- **Total manifests:** {total}\n")
    md.append(f"- **Context coverage:** {context_pct}%\n\n")

    md.append("## By Star\n\n| Star | Count |\n|---|---:|\n")
    for star, cnt in stars.most_common():
        md.append(f"| {star} | {cnt} |\n")

    md.append("\n## By Tier\n\n| Tier | Count |\n|---|---:|\n")
    for tier, cnt in tiers.most_common():
        md.append(f"| {tier} | {cnt} |\n")

    (outdir / "manifest_stats.md").write_text("".join(md), encoding="utf-8")
    print("Wrote docs/audits/manifest_stats.{json,md}")

if __name__ == "__main__":
    main()
````

**Makefile additions**

```make
stats:
	python scripts/report_manifest_stats.py --manifests manifests --out docs/audits
```

**(Optional) CI step**

```yaml
      - name: Build manifest stats
        run: |
          python scripts/report_manifest_stats.py --manifests manifests --out docs/audits
      - name: Upload stats
        uses: actions/upload-artifact@v4
        with:
          name: manifest-stats
          path: docs/audits/manifest_stats.*
          if-no-files-found: ignore
```

---

# 3) A few more 0.01% / T4 moves (tight, high-ROI)

1. **Owner gates in CI**: Fail if any `T1_critical` manifest has `owner="unassigned"`. (Two lines in `validate_manifests.py`.)
2. **Star drift sentinel**: Add a step that compares star counts to yesterday’s stats; if a star’s share swings >10% without `FREEZE.md` note, open a warning PR comment.
3. **Schema lockfile**: Commit a minified copy of the active schema as `schemas/.lock/schema@1.1.0.json` so reviews see exactly what validators used on that commit.
4. **Context lints**: Tiny script to enforce YAML front-matter keys (`star/tier/matriz/owner`) exist in each `lukhas_context.md`.
5. **“Hot paths” registry**: Add `hotpath` optional key in manifests for a callable import path used by smoke tests (replaces import timing with something representative later).
6. **Contracts CHANGELOG**: `contracts/CHANGELOG.md` tracks every new/bumped contract ID with a 1-liner impact.
7. **PR templates**: `.github/pull_request_template.md` includes checkboxes for updated manifest/context, contracts, and perf target notes for T1/T2.
8. **SLO badges**: Add `latency_target_p95` and a tiny script to render per-module badge svgs under `docs/stars/` for demos.
9. **Minimal “demo harness”**: `demos/constellation_top.ipynb` (or `.py`) that loads stats and prints top 5 gaps by star (owner actions).

---

# 4) Full Kick-off Brief for **Claude Code**

Paste this as the **single prompt** to start Claude Code on implementation:

---

**Title:** LUKHAS — Finalize 0.01% Upgrades & Docs Discipline

**Goal:** Land a tight set of build-time guardrails and visibility tools around our MATRIZ manifests, Constellation, and docs so we can move code safely after artifacts are complete.

## Tasks (do in small PRs if needed)

1. **Docs: link checker in CI**

   * Ensure `docs/check_links.py` exists (see attached spec).
   * Add a CI step to run it (internal links required, external optional).

2. **Contracts Registry**

   * Ensure `contracts/` exists with at least three example IDs:

     * `memory.write@v1`, `guardian.policy.violation@v1`, `identity.oauth.callback@v1`
   * Wire `scripts/validate_contract_refs.py` in CI (fail on unknown/invalid IDs).
   * Add `docs/check_contracts_refs.md` (provided) to the repo.

3. **Star Canon packages**

   * Create `packages/star_canon_py` (pyproject + module) that exposes `canon()` and `normalize()`.
   * (Optional) Add `packages/star-canon-js` with `index.js` exporting the canon and `normalize()` for web UIs.
   * Update generators to prefer the Python package if available; fallback to `scripts/star_canon.json`.

4. **Golden Manifests & Test**

   * Add three goldens under `tests/manifests/golden/` (Anchor/Flow/Watch).
   * Add `tests/test_golden_manifests.py` using `jsonschema` to ensure schema stability.
   * Confirm pytest passes locally and in CI.

5. **Release Freeze**

   * Add `release/FREEZE.md` checklist.
   * Add PR template `.github/pull_request_template.md` with checkboxes:

     * Updated manifests/context
     * Contracts references valid
     * Perf target note for T1/T2 (or “n/a”)

6. **CI Concurrency & Artifacts**

   * Add `concurrency:` block to workflows.
   * Upload artifacts: `linkcheck.txt`, `manifest_report.json` (if generator writes it).

7. **Owners Map**

   * Create `OWNERS.toml` and update `scripts/generate_module_manifests.py` to stamp `metadata.owner` via glob rules.
   * Add a CI guard: fail if any `T1_critical` manifest has `owner="unassigned"`.

8. **Smoke Shards**

   * Ensure `pytest.ini` has `matriz_smoke` marker.
   * Add `tests/smoke/test_matriz_smoke.py` (provided) capped to keep runtime < 120s.
   * For now, it times a module import; later we’ll switch to a real `hotpath` callable from manifest.

9. **Guardian Belt**

   * Add `scripts/policy_guard.py` (provided).
   * CI step fails when T1 code contains `eval/exec/subprocess.*` unless manifest includes `security.policies: ["allow-dangerous-exec"]`.

10. **Stats & Dashboards**

* Add `scripts/report_manifest_stats.py` (provided); Makefile target `make stats`.
* CI step that generates `docs/audits/manifest_stats.{json,md}` and uploads them as artifacts.

11. **Context Discipline**

* Standardize `lukhas_context.md` with YAML front-matter:

  ```
  ---
  star: <canonical star>
  tier: <T1_critical|T2_important|T3_standard|T4_experimental>
  matriz: [<nodes>]
  colony: <domain>
  owner: <team|agent>
  contracts:
    publishes: []
    subscribes: []
  observability:
    logger: <name>
  ---
  ```
* (Optional small script) Validate front-matter keys exist for manifests flagged T1/T2.

## Acceptance

* CI green with the new steps; concurrency enabled; artifacts uploaded.
* `make top` and `make stats` run successfully and produce outputs under `docs/`.
* Golden manifests validate under the active schema.
* Link checker catches at least one intentional broken link in a local branch (for proof), then green after fix.
* A `T1_critical` manifest fails CI if `owner` is missing or dangerous calls are present (and passes after adding the policy or refactor).

## Commands (local)

```bash
pip install -r requirements.txt || true
pip install jsonschema pre-commit detect-secrets

pre-commit install && pre-commit install --hook-type commit-msg

make patch-schema
make manifests
make validate
make badges
make top
make stats

python docs/check_links.py --root .
python scripts/validate_contract_refs.py
pytest -q -m matriz_smoke
```

**Notes:** Keep PRs focused. Prefer small diffs. Avoid new heavy deps. Ask for owner assignment on any T1 without a clear team. Where ambiguity exists on star or colony, default to **Supporting** and open a tracking TODO.

---

