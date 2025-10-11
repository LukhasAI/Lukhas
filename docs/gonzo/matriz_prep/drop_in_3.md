
---

# 1) Link checker (drop-in)

**File:** `docs/check_links.py`

```python
#!/usr/bin/env python3
"""
Link checker for internal docs.

- Scans all Markdown files under ./docs and ./manifests for:
  - relative file links (./path.md, ../path, docs/foo.md)
  - in-file anchors (#heading) — verified against actual headings
  - optional external http(s) links (opt-in via --external)
- Writes a report to docs/audits/linkcheck.txt
- Exits 1 if any internal links are broken (external links are WARNs unless --strict)

Usage:
  python docs/check_links.py [--root .] [--external] [--strict]
"""
import argparse, pathlib, re, sys, urllib.request, urllib.error

HEADING_RE = re.compile(r'^\s{0,3}#{1,6}\s+(.*)\s*$')
LINK_RE = re.compile(r'\[[^\]]+\]\(([^)]+)\)')

def slugify(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[\s]+', '-', text)
    return text

def extract_headings(md_text: str):
    anchors = set()
    for line in md_text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            anchors.add("#"+slugify(m.group(1)))
    return anchors

def iter_markdown_files(root: pathlib.Path):
    for p in root.rglob("*.md"):
        if any(seg in p.parts for seg in (".venv","venv",".git")): 
            continue
        yield p

def is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

def check_external(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as r:
            return 200 <= r.status < 400
    except Exception:
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--external", action="store_true")
    ap.add_argument("--strict", action="store_true", help="fail build on bad external links too")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    docs = root / "docs"
    manifests = root / "manifests"
    audit_dir = docs / "audits"; audit_dir.mkdir(parents=True, exist_ok=True)
    report = []

    broken_internal = 0
    broken_external = 0

    # cache headings for anchors
    heading_cache = {}

    for md in list(iter_markdown_files(docs)) + (list(iter_markdown_files(manifests)) if manifests.exists() else []):
        text = md.read_text(encoding="utf-8", errors="ignore")
        anchors = extract_headings(text)
        heading_cache[md] = anchors

    for md in list(iter_markdown_files(docs)) + (list(iter_markdown_files(manifests)) if manifests.exists() else []):
        base = md.parent
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in LINK_RE.finditer(text):
            url = m.group(1).strip()
            if url.startswith("mailto:") or url.startswith("tel:"):
                continue
            if is_external(url):
                if not args.external:
                    report.append(f"WARN external unchecked: {md}:{m.start()} → {url}")
                else:
                    ok = check_external(url)
                    if not ok:
                        broken_external += 1
                        report.append(f"FAIL external: {md}:{m.start()} → {url}")
                continue

            # split anchor
            path_part, anchor_part = (url.split("#", 1) + [""])[:2]
            target = (base / path_part).resolve() if path_part else md
            if not target.exists():
                broken_internal += 1
                report.append(f"FAIL missing file: {md}:{m.start()} → {url}")
                continue

            if anchor_part:
                anchor = "#"+slugify(anchor_part)
                # target headings
                if target.suffix.lower() == ".md":
                    if target not in heading_cache:
                        heading_cache[target] = extract_headings(target.read_text(encoding="utf-8", errors="ignore"))
                    if anchor not in heading_cache[target]:
                        broken_internal += 1
                        report.append(f"FAIL missing anchor: {md}:{m.start()} → {url}")

    out = "\n".join(report) + ("\n" if report else "")
    (audit_dir / "linkcheck.txt").write_text(out, encoding="utf-8")
    print(out or "OK: no issues found")
    print(f"Broken internal: {broken_internal}; Broken external: {broken_external}")
    if broken_internal or (args.strict and broken_external):
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Add to CI** (append to your `manifest-validate.yml`):

```yaml
      - name: Check internal links
        run: |
          python docs/check_links.py --root .
        continue-on-error: false

      - name: Upload linkcheck report
        uses: actions/upload-artifact@v4
        with:
          name: linkcheck
          path: docs/audits/linkcheck.txt
          if-no-files-found: ignore
```

---

# 2) Brief to **Claude Code** (implement these 0.01% moves)

Paste the following brief straight to Claude Code:

---

## Project: LUKHAS 0.01% Upgrades — Implementation Brief

**Context:** We’ve standardized manifests & Constellation. Now implement the following upgrades with tight acceptance checks. Use small, dependency-light code; keep changes incremental and reviewable.

---

### A) Star Canon as distributable packages (Python + JS)

**Create (Python):** `packages/star_canon_py/pyproject.toml`

```toml
[project]
name = "star-canon-py"
version = "0.1.0"
requires-python = ">=3.9"
description = "LUKHAS Constellation star canon and alias normalization"
authors = [{name="LUKHAS"}]
readme = "README.md"
```

**Create:** `packages/star_canon_py/star_canon/__init__.py`

```python
from importlib.resources import files
import json, functools

@functools.lru_cache()
def canon():
    p = files(__package__) / "star_canon.json"
    return json.loads(p.read_text(encoding="utf-8"))

def normalize(name: str) -> str:
    c = canon()
    stars = set(c["stars"])
    aliases = c["aliases"]
    if name in stars: return name
    return aliases.get(name, name)
```

**Copy** our existing `scripts/star_canon.json` into `packages/star_canon_py/star_canon/star_canon.json`.

**Wire-in:** update `scripts/generate_module_manifests.py` to import `star_canon_py.star_canon` if available; fallback to local JSON.

**Acceptance:** generator and schema patcher work with the package installed via `pip install -e packages/star_canon_py`.

**Create (JS optional):** `packages/star-canon-js/package.json`

```json
{
  "name": "@lukhas/star-canon",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js"
}
```

**Create:** `packages/star-canon-js/index.js`

```js
export { default as canon } from "../star_canon.json" assert { type: "json" };
export function normalize(name, c=undefined) {
  const C = c || canon;
  if (C.stars.includes(name)) return name;
  return C.aliases[name] || name;
}
```

---

### B) Contracts registry & validation

**Create folder:** `contracts/`

**Example schema:** `contracts/memory.write@v1.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "memory.write@v1",
  "type": "object",
  "properties": {
    "id": {"type":"string"},
    "payload": {"type":"object"},
    "ts": {"type":"string", "format":"date-time"}
  },
  "required": ["id","payload","ts"],
  "additionalProperties": false
}
```

**Create validator:** `scripts/validate_contract_refs.py`

```python
#!/usr/bin/env python3
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = list(ROOT.rglob("module.manifest.json"))
CONTRACTS = {p.stem: p for p in (ROOT/"contracts").glob("*.json")}
ID_RE = re.compile(r"^[a-z0-9_.:-]+@v\d+$")

def main():
    failures = 0
    for mf in MANIFESTS:
        m = json.loads(mf.read_text(encoding="utf-8"))
        ev = m.get("observability",{}).get("events",{})
        for kind in ("publishes","subscribes"):
            for item in ev.get(kind, []):
                stem = item
                if not ID_RE.match(stem):
                    print(f"[FAIL] {mf}: invalid contract id: {stem}")
                    failures += 1
                    continue
                key = stem.split("@",1)[0]+"@"+stem.split("@",1)[1]
                if key not in CONTRACTS:
                    print(f"[FAIL] {mf}: unknown contract: {stem}")
                    failures += 1
    print("failures:", failures)
    if failures:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**CI step (after manifest validation):**

```yaml
      - name: Validate contract references
        run: |
          python scripts/validate_contract_refs.py
```

**Acceptance:** manifests referencing events must use existing `contracts/*.json` IDs; CI fails otherwise.

---

### C) Golden sample manifests

**Add:** `tests/manifests/golden/anchor_identity.json` (and two more for Flow & Watch)

```json
{
  "schema_version": "1.1.0",
  "module": {"name":"lukhas.identity.oidc","path":"lukhas/identity/oidc","type":"package"},
  "matriz_integration": {"status":"partial","pipeline_nodes":["action"]},
  "constellation_alignment": {"primary_star":"⚛️ Anchor (Identity)"},
  "testing": {"has_tests": true, "test_paths": ["tests/lukhas/identity"], "quality_tier":"T1_critical"},
  "observability": {"spans":["oidc.login"],"metrics":[{"name":"oidc.logins","type":"counter"}],"logging":{"logger_name":"lukhas.identity.oidc","default_level":"INFO"}},
  "security": {"requires_auth": true,"data_classification":"internal"},
  "metadata": {"created":"2025-01-01T00:00:00Z","last_updated":"2025-01-01T00:00:00Z","manifest_generated":false,"owner":"platform"}
}
```

**Test:** `tests/test_golden_manifests.py`

```python
import json, glob
from jsonschema import Draft7Validator

def test_golden_manifests_validate():
    schema = json.load(open("schemas/matriz_module_compliance.schema.json"))
    v = Draft7Validator(schema)
    for f in glob.glob("tests/manifests/golden/*.json"):
        data = json.load(open(f))
        errs = list(v.iter_errors(data))
        assert not errs, f"{f} invalid: {errs[:2]}"
```

**CI:** pytest run includes this test.

---

### D) Release freeze checklist

**Create:** `release/FREEZE.md`

```markdown
# Release Freeze Checklist

- [ ] CI green on main (all workflows)
- [ ] Manifests 100% generated; critical modules have context
- [ ] Guardian/North policy review signed
- [ ] Perf smoke: p95 targets recorded & met on T1 paths
- [ ] Observability: spans/metrics/logging present for T1/T2
- [ ] Rollback plan + checkpoints documented
- [ ] Contracts versioned; breaking changes flagged
- [ ] Linkcheck clean; docs updated (Top & star pages)
```

---

### E) CI concurrency & artifacts

**Add to each workflow root:**

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Upload validator output (extend validator to write a JSON report):**
Modify `scripts/validate_manifests.py` to accept `--report-out docs/audits/manifest_report.json` (optional). Then:

```yaml
      - name: Upload manifest report
        uses: actions/upload-artifact@v4
        with:
          name: manifest-report
          path: docs/audits/manifest_report.json
          if-no-files-found: ignore
```

---

### F) Module owners mapping

**Create:** `OWNERS.toml`

```toml
[owners]
"lukhas.identity.oidc" = "platform"
"lukhas.consciousness.*" = "consciousness"
"lukhas.memory.*" = "memory"
```

**Generator change:** read `OWNERS.toml`; if a glob matches, stamp `metadata.owner`.
**Acceptance:** star-critical manifests show non-`unassigned` owner after generation.

---

### G) Smoke shards (matrix smoke, < 120s)

**Create:** `pytest.ini`

```ini
[pytest]
markers =
    matriz_smoke: quick path checks for star-critical modules
```

**Create:** `tests/smoke/test_matriz_smoke.py`

```python
import json, pathlib, time, importlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFESTS = list(ROOT.rglob("module.manifest.json"))

def iter_star_critical():
    for mf in MANIFESTS:
        m = json.loads(mf.read_text(encoding="utf-8"))
        tier = m.get("testing",{}).get("quality_tier","T4_experimental")
        if tier in ("T1_critical","T2_important"):
            yield mf, m

def import_path_from_manifest(m):
    mod = m.get("module",{}).get("name") or m.get("module",{}).get("path","").replace("/","." )
    return mod

def p95_target(m):
    return m.get("matriz_integration",{}).get("latency_target_p95", None)

def fake_call(modname):
    # placeholder for a representative, fast import or constructor call
    importlib.invalidate_caches()
    t0 = time.perf_counter()
    try:
        importlib.import_module(modname)
    except Exception:
        return None, None
    return (time.perf_counter() - t0)*1000, "import"

def test_smoke_star_critical():
    slow = []
    for mf, m in list(iter_star_critical())[:60]:  # cap to keep <120s
        modname = import_path_from_manifest(m)
        if not modname: 
            continue
        elapsed, kind = fake_call(modname)
        if elapsed is None:
            raise AssertionError(f"Import failed: {modname} ({mf})")
        target = p95_target(m)
        if target and elapsed > 2.0*target:  # warn threshold; fail hard at 2x
            slow.append((modname, elapsed, target))
    assert not slow, f"Exceeded targets: {slow[:5]}"
```

---

### H) Guardian belts (ban dangerous calls in T1 unless whitelisted)

**Create:** `scripts/policy_guard.py`

```python
#!/usr/bin/env python3
"""
Fail if T1_critical modules contain eval/exec/subprocess.* unless whitelisted via manifest.security.policies.
"""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = list(ROOT.rglob("module.manifest.json"))
BAN = [r"\beval\(", r"\bexec\(", r"\bsubprocess\."]
ALLOW_TAG = "allow-dangerous-exec"

def code_files_for_module(path_rel: str):
    p = ROOT / path_rel
    if p.is_dir():
        yield from p.rglob("*.py")
    else:
        # best effort: derive from module path
        yield from (ROOT / path_rel).parent.rglob("*.py")

def main():
    fails = []
    for mf in MANIFESTS:
        m = json.loads(mf.read_text(encoding="utf-8"))
        tier = m.get("testing",{}).get("quality_tier")
        if tier != "T1_critical":
            continue
        policies = set(m.get("security",{}).get("policies",[]))
        if ALLOW_TAG in policies:
            continue
        mod_path = m.get("module",{}).get("path")
        if not mod_path: 
            continue
        for f in code_files_for_module(mod_path):
            text = f.read_text(encoding="utf-8", errors="ignore")
            for pat in BAN:
                if re.search(pat, text):
                    fails.append(f"{f}:{pat}")
    if fails:
        print("Policy violations:\n" + "\n".join(fails[:50]))
        sys.exit(1)
    print("Guardian belt: OK")

if __name__ == "__main__":
    main()
```

**CI step:**

```yaml
      - name: Guardian belt (ban dangerous calls in T1)
        run: |
          python scripts/policy_guard.py
```

---

### I) Perf knobs (already leveraged in smoke)

* Encourage owners to set `matriz_integration.latency_target_p95` in manifests for T1/T2.
* The smoke test reads it and fails if import path exceeds `2x` the target (cheap sanity guard).
* Future: replace `fake_call` with a real, super-fast code path per module (registry-driven).

---

### J) Doc bot (link checker)

* Already provided above as `docs/check_links.py` with CI + artifact.

---

**General Acceptance for this Brief**

* All new scripts run on `python3.11` without extra deps (except `jsonschema` we already install).
* CI green with new jobs; concurrency enabled; artifacts uploaded (linkcheck + manifest_report if configured).
* `make top` still generates dashboards; link checker passes.
* Smoke suite runs in <120s on CI (use cap & skip markers if needed).

---

If you want, I can also provide:

* a tiny `docs/check_contracts_refs.md` troubleshooting page,
* and a `scripts/report_manifest_stats.py` to compute per-star/tier counts for your README badges.

