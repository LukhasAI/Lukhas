
---

## 1) `scripts/validate_context_front_matter.py`

A zero-dep (optional PyYAML) validator that checks every `lukhas_context.md`’s YAML front-matter against its sibling `module.manifest.json`:

* Required keys: `star`, `tier`, `matriz`, `owner` (and `colony` recommended)
* Canonicalizes `star` using `star_canon_py` if installed, else `scripts/star_canon.json`
* Ensures `tier` ↔ manifest `testing.quality_tier` consistency (hard fail for T1/T2)
* Ensures all manifest MATRIZ nodes are present in `matriz` array (hard fail)
* For T1/T2: fails if `owner` is missing or `unassigned`
* Writes a report to `docs/audits/context_lint.txt`

```python
#!/usr/bin/env python3
"""
Validate lukhas_context.md front-matter against module.manifest.json.

- Required keys: star, tier, matriz (list), owner
- Canonicalize 'star' via star canon (python package if available, else scripts/star_canon.json)
- Hard-fail on:
  * Missing front-matter or required keys
  * T1/T2 with owner missing/unassigned
  * MATRIZ nodes in manifest not present in context
  * Tier mismatch (for T1/T2)
- Warn (not fail) on:
  * Star mismatch (context vs manifest)
  * Missing 'colony'

Writes report: docs/audits/context_lint.txt
Exit 1 on failures.
"""
import pathlib, re, json, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "audits" / "context_lint.txt"

def load_star_canon():
    # Prefer python package if present
    try:
        from star_canon import canon as canon_fn  # type: ignore
        return canon_fn()
    except Exception:
        pass
    # Fallback to local JSON
    p = ROOT / "scripts" / "star_canon.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"stars": [], "aliases": {}}

def normalize_star(name: str, canon: dict) -> str:
    if not name:
        return name
    stars = set(canon.get("stars", []))
    aliases = canon.get("aliases", {})
    return name if name in stars else aliases.get(name, name)

FM_START = re.compile(r"^\s*---\s*$")
FM_END   = re.compile(r"^\s*---\s*$")

def parse_front_matter(md_text: str):
    """
    Minimal YAML front-matter reader.
    Tries PyYAML if available; falls back to a tiny parser for required keys.
    """
    lines = md_text.splitlines()
    if not lines or not FM_START.match(lines[0]):
        return None
    # find end marker
    end_idx = None
    for i in range(1, min(len(lines), 200)):  # only scan first 200 lines
        if FM_END.match(lines[i]):
            end_idx = i
            break
    if end_idx is None:
        return None
    block = "\n".join(lines[1:end_idx])

    # Try PyYAML if available
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(block) or {}
        return data
    except Exception:
        pass

    # Tiny parser for required fields
    data = {}
    current_map = data
    indent_stack = [0]
    map_stack = [data]

    def set_kv(container, k, v):
        k = k.strip()
        v = v.strip()
        # list like [a, b]
        if v.startswith("[") and v.endswith("]"):
            arr = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            container[k] = arr
        else:
            container[k] = v

    for raw in block.splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        while indent < indent_stack[-1]:
            indent_stack.pop()
            map_stack.pop()
        line = raw.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            if v.strip() == "":
                # start nested map (we only care about top-level keys we’ll read directly)
                new_map = {}
                map_stack[-1][k.strip()] = new_map
                map_stack.append(new_map)
                indent_stack.append(indent + 2)
            else:
                set_kv(map_stack[-1], k, v)
    return data

def read_manifest_for(md_path: pathlib.Path):
    mf = md_path.parent / "module.manifest.json"
    if not mf.exists():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return None

def main():
    docs = ROOT / "docs"
    manifests_root = ROOT / "manifests"
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    canon = load_star_canon()
    failures = 0
    warns = 0
    rows = []

    ctx_files = list(manifests_root.rglob("lukhas_context.md"))
    for ctx in sorted(ctx_files):
        manifest = read_manifest_for(ctx)
        text = ctx.read_text(encoding="utf-8", errors="ignore")
        fm = parse_front_matter(text)

        if fm is None:
            failures += 1
            rows.append(f"[FAIL] {ctx}: missing or invalid front-matter block")
            continue

        star = str(fm.get("star", "")).strip()
        tier = str(fm.get("tier", "")).strip()
        owner = str(fm.get("owner", "")).strip()
        matriz = fm.get("matriz", [])
        colony = fm.get("colony", None)

        if not star or not tier or not isinstance(matriz, list) or not owner:
            failures += 1
            rows.append(f"[FAIL] {ctx}: required keys missing (need star, tier, matriz[], owner)")
            continue

        star_norm = normalize_star(star, canon)
        if star_norm != star:
            warns += 1
            rows.append(f"[WARN] {ctx}: star normalized '{star}' -> '{star_norm}'")

        if colony in (None, "", "—"):
            warns += 1
            rows.append(f"[WARN] {ctx}: colony missing (recommended)")

        if manifest:
            m_star = (manifest.get("constellation_alignment", {}) or {}).get("primary_star")
            m_tier = (manifest.get("testing", {}) or {}).get("quality_tier")
            m_nodes = (manifest.get("matriz_integration", {}) or {}).get("pipeline_nodes", [])
            m_owner = (manifest.get("metadata", {}) or {}).get("owner", "").strip()

            # Star mismatch => warn
            if m_star and m_star != star_norm:
                warns += 1
                rows.append(f"[WARN] {ctx}: star '{star_norm}' != manifest '{m_star}'")

            # Tier mismatch: hard-fail for T1/T2, warn otherwise
            if m_tier and m_tier != tier:
                if m_tier in ("T1_critical", "T2_important") or tier in ("T1_critical", "T2_important"):
                    failures += 1
                    rows.append(f"[FAIL] {ctx}: tier '{tier}' != manifest '{m_tier}'")
                else:
                    warns += 1
                    rows.append(f"[WARN] {ctx}: tier '{tier}' != manifest '{m_tier}'")

            # MATRIZ coverage: all manifest nodes must appear in front-matter
            missing_nodes = [n for n in (m_nodes or []) if n not in (matriz or [])]
            if missing_nodes:
                failures += 1
                rows.append(f"[FAIL] {ctx}: missing MATRIZ nodes: {missing_nodes} (manifest={m_nodes}, context={matriz})")

            # Owner discipline for T1/T2
            if (m_tier in ("T1_critical", "T2_important")):
                if not owner or owner.lower() == "unassigned":
                    failures += 1
                    rows.append(f"[FAIL] {ctx}: T1/T2 must have owner (found '{owner or 'none'}')")
                if m_owner and owner != m_owner:
                    warns += 1
                    rows.append(f"[WARN] {ctx}: owner '{owner}' != manifest '{m_owner}'")

        else:
            warns += 1
            rows.append(f"[WARN] {ctx}: no sibling module.manifest.json found")

    header = f"# Context Front-Matter Report\nGenerated {datetime.datetime.utcnow().isoformat()}Z\n"
    body = "\n".join(rows)
    summary = f"\nFailures: {failures} | Warnings: {warns} | Files checked: {len(ctx_files)}\n"
    REPORT.write_text(header + "\n" + body + "\n" + summary, encoding="utf-8")

    print(summary.strip())
    if failures:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 2) Makefile — add target

Append these lines:

```make
context-validate:
	python scripts/validate_context_front_matter.py
```

---

## 3) Pre-commit — add local hook

Append to your existing `.pre-commit-config.yaml` under the `repo: local` block:

```yaml
      - id: context-front-matter-validate
        name: Validate context front-matter
        entry: python scripts/validate_context_front_matter.py
        language: system
        pass_filenames: false
        stages: [commit, push]
```

---

## 4) CI — add a job step

In your `.github/workflows/manifest-validate.yml`, add after manifest validation:

```yaml
      - name: Validate context front-matter
        run: |
          python scripts/validate_context_front_matter.py
      - name: Upload context lint report
        uses: actions/upload-artifact@v4
        with:
          name: context-lint
          path: docs/audits/context_lint.txt
          if-no-files-found: ignore
```

---

## 5) `.github/pull_request_template.md`

Drop this in to enforce discipline on every PR:

```markdown
# Summary
<!-- What changed and why -->

## Checks

- [ ] Manifests updated if packages/modules moved or capabilities changed
- [ ] `lukhas_context.md` present/updated with YAML front-matter
- [ ] Contracts references valid (`scripts/validate_contract_refs.py`)
- [ ] Link checker passes (`docs/check_links.py`)
- [ ] Smoke suite passes locally: `pytest -q -m matriz_smoke` (<120s)
- [ ] T1/T2: owner set, latency_target_p95 set or explicitly n/a
- [ ] Release freeze notes updated if relevant (`release/FREEZE.md`)

## Notes for Reviewers
<!-- Risks, follow-ups, perf/observability considerations -->
```

---

## 6) Quick run (local)

```bash
# once
pip install pre-commit detect-secrets jsonschema
pre-commit install && pre-commit install --hook-type commit-msg

# validate everything
make context-validate
python docs/check_links.py --root .
python scripts/validate_contract_refs.py
pytest -q -m matriz_smoke
```

---

### That’s it — with this last patch you’ve got:

* Artifact discipline (manifests + context) **enforced**.
* Canonical star mapping everywhere.
* Contracts referenced and versioned cleanly.
* CI that fails on real risks, and produces actionable reports.

