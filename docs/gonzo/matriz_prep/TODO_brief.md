# To: **Claude Code** — Orchestrate “TODO Purge & Prod Hardening”

**Objectives (today → this week)**

1. Eliminate fake/obsolete TODOs and surface only *actionable* debt.
2. Keep MATRIZ discipline intact (schema v1.1.0, Oracle/Flow canon, CI tripwires).
3. Prepare a focused, mechanical task pack for **Codex**; keep the cross-module/ambiguity decisions for you.

**Ground truth (files already in repo):**

* MATRIZ validator workflow with tripwires and star rules/reporting.
* Link checker for docs & manifests.
* Contract ref validator + guardian belt.
* Star rules + rule tooling (lint/coverage/promotions).
* T1 owner tripwire, manifest drift guard, MATRIZ smoke.
* Owners map (note: still contains “candidate.*” patterns you’ll update in the rename step). 

---

## Plan & sequencing

### Phase 0 — Safety rails (you)

* Confirm the CI job is green on `main` with all MATRIZ steps present (no edits needed unless we add new tripwires).
* Snapshot current manifest stats (for drift checks): artifact is produced by `report_manifest_stats.py` in CI; we’ll use it as the baseline for rename work. 

### Phase 1 — **Codex** pack: purge *fake* TODOs, surface *real* ones (mechanical)

**Deliver these to Codex verbatim (below “Pack for Codex”).**
Scope: remove linter-generated “TODO” noise, harvest legitimate TODOs into a CSV + GitHub Issues, and keep CI green.

* No schema/code semantics changed.
* Tripwires remain enforcing: no “Ambiguity” star, no empty capabilities, no `colony: null`, T1 must have owners & `test_paths`.

### Phase 2 — Rename lanes, *without breaking prod* (you lead, Codex assists)

**Goal:** retire legacy lane names and move toward a presentable, future-proof structure:

* `candidate/` → `labs/`
* `lukhas/` = the production surface (keep)
* Eliminate any lingering `lucas/`/`Lucas/` spellings; standardize to **lukhas**.

**Safe migration steps (you):**

1. Create a long-lived branch `feat/restructure-labs`.
2. Codemod **paths only** first; *don’t* change imports yet:

   ```bash
   # Dry-run listing
   rg -n "^(from|import)\s+lucas\b|candidate/|/\blucas\b" -g '!venv' -S

   # Move dir (git-aware)
   git mv candidate labs

   # Update non-import path references in scripts & manifests
   rg -l '"module":\s*\{"path":\s*"candidate/' manifests | xargs gsed -i 's#"candidate/#"labs/#g'
   rg -l 'candidate/' | xargs gsed -i 's#\bcandidate/#labs/#g'
   ```
3. Add a **temporary import shim** package `labs_shim/` (if needed) that re-exports old module names to new ones — remove after follow-up PRs.
4. Update **OWNERS.toml** patterns: `"candidate.*"` → `"labs.*"`. 
5. Run CI + smoke. If anything regresses, bisect to the specific codemod.

*(Rationale: this keeps MATRIZ manifests + dashboards coherent while we refactor code imports incrementally.)*

### Phase 3 — Star hygiene & promotions (optional, you)

* Run rule coverage + promotions suggestion; review and promote only >0.7 confidence.

  * `python3 scripts/gen_rules_coverage.py` → MD report. 
  * `python3 scripts/suggest_star_promotions.py` → CSV & MD suggestions. 
  * `python3 scripts/apply_promotions.py --in docs/audits/star_promotions.csv --min 0.7 --dry-run` then apply. 

---

# **Pack for Codex** — “TODO Purge & Prod Hardening (Mechanical)”

> **Mission:** Remove fake/obsolete TODOs, harvest real TODOs to CSV + issues, keep CI green, no semantics changed.

## 1) Remove auto-generated “fake TODOs”

These are linter scaffolds, not work items.

```bash
# Invalid-syntax pseudo TODOs
rg -l "# noqa: invalid-syntax\s+# TODO:" candidate labs lukhas | xargs -I{} gsed -i 's/# noqa: invalid-syntax  # TODO:.*$/# noqa: invalid-syntax/'

# F821 pseudo TODOs
rg -l "# noqa: F821\s+# TODO:" candidate labs lukhas | xargs -I{} gsed -i 's/# noqa: F821  # TODO:.*$/# noqa: F821/'

# Legacy REALITY_TODO (obsolete tracker)
rg -l "REALITY_TODO" | xargs -I{} gsed -i 's/.*REALITY_TODO.*//'
```

**Acceptance:** `rg -n "noqa: invalid-syntax\s+# TODO|noqa: F821\s+# TODO|REALITY_TODO" | wc -l` ⇒ **0**

## 2) Harvest *real* TODOs to CSV (new script to add)

Create **`scripts/harvest_todos.py`** that scans `lukhas/`, `labs/`, `packages/`, `tools/`, `tests/`, `docs/` for lines matching `TODO:` (and our specialist markers), emitting `docs/audits/todos.csv` with columns:

```
path,line,kind,owner_hint,priority,tag,text
```

Rules:

* `TODO[QUANTUM-BIO:specialist]` → `kind=specialist`, `owner_hint=quantum-bio`, `priority=P2`
* `TODO[GLYPH:specialist]` → `owner_hint=glyph`
* `TODO[CONSTELLATION:specialist]` → `owner_hint=constellation`
* Plain `TODO:` → `kind=general`
* Map obvious priorities: `TODO(P0|P1|P2)` if present; else default `P2`.

**Add to repo** and run:

```bash
python3 scripts/harvest_todos.py --roots lukhas labs packages tools tests docs --out docs/audits/todos.csv
```

**Acceptance:** `docs/audits/todos.csv` exists, > 0 lines, and contains **no** entries from step 1’s fake classes.

## 3) (Optional) Bulk create GitHub Issues from CSV

Add a safe, dry-run script **`scripts/create_issues_from_csv.py`** that reads `docs/audits/todos.csv` and emits GitHub CLI commands (not auto-exec) into `docs/audits/todos_gh.sh`. You (humans) can then skim & run:

```bash
gh auth status
bash docs/audits/todos_gh.sh
```

Each issue title: `TODO: {first 80 chars}`
Labels: `debt`, `matriz`, `{owner_hint}` (if present), `priority/{P0|P1|P2}`.
Milestone: `MATRIZ-R2` (if exists).

## 4) Keep CI green / discipline pack intact

* Run local CI parity:

  ```bash
  python docs/check_links.py --root .
  python scripts/validate_contract_refs.py
  python scripts/validate_context_front_matter.py
  python scripts/policy_guard.py
  pytest -q -m matriz_smoke || true
  ```

  (All are wired in CI as well.)

**Acceptance:** `gh pr status` shows the `MATRIZ Validate` workflow passing with these steps present. 

## 5) Leave “specialist” TODOs intact (just tracked)

* Do **not** delete `TODO[QUANTUM-BIO:specialist]`, `TODO[GLYPH:specialist]`, `TODO[CONSTELLATION:specialist]`. These feed expert batches later.

---

## Hand-offs & boundaries

* **Codex** owns Phase 1 (mechanical).
* **Claude Code** owns Phase 2 rename + any star promotions + complex cross-module fallout.
* Tripwires keep us safe:

  * Deprecated star names blocked. 
  * T1 owners and `test_paths` enforced.
  * Manifest drift guarded. 

---

## Exit criteria

* **Fake TODOs = 0** (command in Phase 1).
* `docs/audits/todos.csv` checked in, with specialist items labeled.
* CI green (`MATRIZ Validate`) with star rules/coverage and auditors producing artifacts. 
* No “Ambiguity (Quantum)” anywhere; Oracle (Quantum) canonical enforced. 

---

## Notes on the lane rename (ahead of time)

When you start Phase 2, remember:

* Update **OWNERS.toml** patterns from `candidate.*` → `labs.*`. 
* Re-run star rule lint + coverage after the move to catch any new path-based matches.
* Keep **MATRIZ smoke** in the loop — it imports star-critical modules and will catch bad import paths quickly. 

---

# Short brief you can paste to **Codex**

> **Title:** MATRIZ — TODO Purge & Prod Hardening (Mechanical)
>
> **Goals:**
>
> 1. Remove all fake/obsolete TODOs (noqa invalid-syntax/F821 scaffolds, REALITY_TODO).
> 2. Harvest legitimate TODOs into `docs/audits/todos.csv` with owner hints & priorities.
> 3. Keep CI/MATRIZ discipline pack green; no semantic changes.
>
> **Steps:**
>
> * Run the exact cleanup commands in “Pack for Codex → 1) Remove fake TODOs”.
> * Add `scripts/harvest_todos.py` (as spec’d) and produce `docs/audits/todos.csv`.
> * (Optional) Add `scripts/create_issues_from_csv.py` and generate `docs/audits/todos_gh.sh` (dry-run).
> * Run local validators: link checker, contract refs, context front-matter, guardian belt, smoke. (These match CI.)
> * Push a PR titled `chore(debt): purge fake TODOs + harvest real TODOs`.
>
> **Acceptance:**
>
> * `rg` confirms **0** fake TODOs.
> * `docs/audits/todos.csv` exists with specialist items untouched, properly labeled.
> * `MATRIZ Validate` workflow passes end-to-end and emits audits. 

---

Next, two helper scripts (`harvest_todos.py` and `create_issues_from_csv.py`) for Codex to drop in exactly:

awesome — here’s a clean drop-in for **Claude Code** to save, plus usage so he can prep the workspace and hand the execution to **Codex**.

---

# To: **Claude Code** — Save these two tools and prep for Codex

**Create:**

* `scripts/harvest_todos.py`
* `scripts/create_issues_from_csv.py`

**Make them executable, add Make targets, and wire a small CI artifact upload.**
Codex will then run them to purge/triage TODOs and (optionally) generate GH issue commands.

---

## `scripts/harvest_todos.py`

```python
#!/usr/bin/env python3
"""
Harvest real TODO/FIXME items into a CSV for triage, skipping known fake/linter "TODO" noise.

Outputs: docs/audits/todos.csv with columns:
path,line,kind,owner_hint,priority,tag,text

Kinds: general|specialist|fixme
Owner hints: extracted from TODO[AREA:specialist] (e.g., QUANTUM-BIO → quantum-bio)
Priority: inferred from tokens (P0/P1/P2/P3/HIGH/LOW); default P2 for specialist, P3 otherwise.
Tag: free-form tag parsed from bracket or None.

Usage:
  python3 scripts/harvest_todos.py --roots lukhas labs packages tools tests docs --out docs/audits/todos.csv
"""
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path

# Recognize TODO flavors
RX_TODO = re.compile(r'(?i)\bTODO\b(?P<bracket>\[[^\]]+\])?(?P<colon>[:：]\s*|$)')
RX_FIXME = re.compile(r'(?i)\bFIXME\b[:：]?\s*')
# Specialist marker: TODO[AREA:specialist]
RX_SPECIALIST = re.compile(r'(?i)TODO\[(?P<area>[A-Z0-9\-_/]+)\s*:\s*specialist\]')
# Priority hints
RX_PRIORITY = re.compile(r'(?i)\b(P0|P1|P2|P3|BLOCKER|HIGH|LOW|TRIVIAL)\b')
# Known fake TODO noise we must skip completely
RX_FAKE = re.compile(r'(?i)#\s*noqa:\s*(F821|invalid-syntax)\s*#\s*TODO:|REALITY_TODO')

TEXT_SUFFIXES = {
    ".py",".md",".markdown",".txt",".rst",".ini",".cfg",".conf",".toml",".yaml",".yml",".json",
    ".js",".jsx",".ts",".tsx",".sh",".bash",".zsh",".ps1",".sql",".proto",".java",".kt",".go"
}
EXCLUDE_DIRS = {".git","venv",".venv","node_modules","dist","build","__pycache__",
                ".mypy_cache",".ruff_cache",".pytest_cache",".tox",".idea",".vscode",".DS_Store"}

def priority_from_text(text:str, specialist:bool)->str:
    m = RX_PRIORITY.search(text or "")
    if m:
        tok = m.group(1).upper()
        if tok in {"BLOCKER","HIGH"}: return "P0" if tok=="BLOCKER" else "P1"
        if tok in {"LOW","TRIVIAL"}: return "P3"
        return tok
    return "P2" if specialist else "P3"

def is_text_file(path:Path)->bool:
    return path.suffix in TEXT_SUFFIXES

def scan_file(path:Path):
    items = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return items
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        if RX_FAKE.search(raw):
            # skip fake/linter TODO scaffolds & legacy trackers
            continue
        kind = None
        specialist = False
        owner_hint = ""
        tag = ""

        if RX_FIXME.search(raw):
            kind = "fixme"
        m = RX_TODO.search(raw)
        if m:
            kind = kind or "general"
            br = (m.group("bracket") or "").strip("[]").strip()
            if br:
                tag = br
            sm = RX_SPECIALIST.search(raw)
            if sm:
                specialist = True
                owner_hint = sm.group("area").lower()
                kind = "specialist"

            prio = priority_from_text(raw, specialist)
            text_part = raw
            # Attempt to keep only content after TODO/FIXME marker for readability
            try:
                # split on first occurrence of "TODO" or "FIXME"
                split_point = None
                mt = re.search(r'(?i)TODO|FIXME', raw)
                if mt: split_point = mt.end()
                text_part = raw[split_point:].strip() if split_point else raw
            except Exception:
                pass

            items.append({
                "path": str(path),
                "line": idx,
                "kind": kind,
                "owner_hint": owner_hint,
                "priority": prio,
                "tag": tag,
                "text": text_part
            })
        elif kind == "fixme":
            prio = priority_from_text(raw, False)
            items.append({
                "path": str(path),
                "line": idx,
                "kind": "fixme",
                "owner_hint": "",
                "priority": prio,
                "tag": "",
                "text": raw
            })
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", default=["lukhas","labs","packages","tools","tests","docs"])
    ap.add_argument("--out", default="docs/audits/todos.csv")
    args = ap.parse_args()

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for root in args.roots:
        base = Path(root)
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                if p.name in EXCLUDE_DIRS: 
                    continue
                # skip hidden dirs
                if p.name.startswith("."): 
                    continue
                continue
            if not is_text_file(p): 
                continue
            # skip hidden files
            if any(seg.startswith(".") for seg in p.parts):
                continue
            rows.extend(scan_file(p))

    # de-duplicate exact duplicates (path,line,text)
    seen = set()
    dedup = []
    for r in rows:
        key = (r["path"], r["line"], r["text"])
        if key in seen: 
            continue
        seen.add(key)
        dedup.append(r)

    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path","line","kind","owner_hint","priority","tag","text"])
        w.writeheader()
        w.writerows(dedup)

    print(f"[OK] wrote {outp} ({len(dedup)} items)")

if __name__ == "__main__":
    sys.exit(main() or 0)
```

---

## `scripts/create_issues_from_csv.py`

```python
#!/usr/bin/env python3
"""
Generate a shell script with GitHub CLI commands from docs/audits/todos.csv.
(We do NOT call gh directly; we produce a reviewable script.)

Usage:
  python3 scripts/create_issues_from_csv.py \
    --csv docs/audits/todos.csv \
    --out docs/audits/todos_gh.sh \
    --repo LukhasAI/Lukhas \
    --milestone "MATRIZ-R2" \
    --label-extra matriz

Then:
  gh auth status
  bash docs/audits/todos_gh.sh
"""
from __future__ import annotations
import argparse, csv, shlex, sys
from pathlib import Path

def mk_labels(owner_hint:str, priority:str, extra:str|None):
    labels = ["debt"]
    if extra:
        labels.append(extra)
    if owner_hint:
        labels.append(f"owner/{owner_hint}")
    if priority:
        labels.append(f"priority/{priority.upper()}")
    return labels

def summarize(text:str, limit:int=80):
    t = (text or "").strip().replace("\n"," ")
    return t[:limit] + ("…" if len(t) > limit else "")

def esc_body(body:str)->str:
    # Use ANSI-C quoting via $'..' to keep newlines; escape single quotes
    return "$'" + body.replace("\\","\\\\").replace("'", r"'\''").replace("\n", r"\n") + "'"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="docs/audits/todos.csv")
    ap.add_argument("--out", default="docs/audits/todos_gh.sh")
    ap.add_argument("--repo", default="")
    ap.add_argument("--milestone", default="")
    ap.add_argument("--assignee", default="")  # e.g., @me or a username
    ap.add_argument("--label-extra", default="")  # e.g., matriz
    args = ap.parse_args()

    src = Path(args.csv)
    if not src.exists():
        print(f"[ERR] missing {src}", file=sys.stderr)
        return 2

    lines = ["#!/usr/bin/env bash", "set -euo pipefail", 'echo "Creating issues from CSV…"']
    created = 0

    with src.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            path = row.get("path","")
            line = row.get("line","")
            kind = row.get("kind","general")
            owner_hint = row.get("owner_hint","")
            priority = row.get("priority","P3")
            tag = row.get("tag","").strip()
            text = row.get("text","").strip()

            title = f"TODO: {summarize(text or f'{kind} in {path}:{line}')}"
            body = f"""# Auto-generated from {src}
**Path:** `{path}`:{line}
**Kind:** {kind}
**Owner hint:** {owner_hint or '-'}
**Priority:** {priority}
**Tag:** {tag or '-'}

**Context:**
{text or '(no additional context)'}
"""
            cmd = ["gh","issue","create","--title",title,"--body", body]
            if args.repo:
                cmd += ["--repo", args.repo]
            for lab in mk_labels(owner_hint, priority, args.label_extra or None):
                cmd += ["--label", lab]
            if args.milestone:
                cmd += ["--milestone", args.milestone]
            if args.assignee:
                cmd += ["--assignee", args.assignee]

            # Emit a line to create the issue
            # Note: we use ANSI-C quoted body for safe newlines
            pieces = []
            for i, c in enumerate(cmd):
                if i == 4 and c == body:  # --body value
                    pieces.append("--body")
                    pieces.append(esc_body(body))
                else:
                    pieces.append(shlex.quote(c))
            lines.append(" ".join(pieces))
            created += 1

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote {outp} with {created} gh issue commands")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## Claude Code — prep steps (please run)

```bash
# 0) Save scripts
mkdir -p scripts docs/audits
$EDITOR scripts/harvest_todos.py   # paste from above
$EDITOR scripts/create_issues_from_csv.py  # paste from above
chmod +x scripts/harvest_todos.py scripts/create_issues_from_csv.py

# 1) Makefile hooks
awk 'BEGIN{p=1} {print} END{
print "";
print "todos: ## Harvest TODO/FIXME into docs/audits/todos.csv";
print "\tpython3 scripts/harvest_todos.py --roots lukhas labs packages tools tests docs --out docs/audits/todos.csv";
print "";
print "todos-issues: ## Generate gh issue commands from todos.csv";
print "\tpython3 scripts/create_issues_from_csv.py --csv docs/audits/todos.csv --out docs/audits/todos_gh.sh --label-extra matriz";
}' Makefile > Makefile.tmp && mv Makefile.tmp Makefile

# 2) Optional pre-commit (keep noise out)
python3 - <<'PY'
cfg = ".pre-commit-config.yaml"
txt = open(cfg, "r", encoding="utf-8").read()
if "forbid-fake-todos" not in txt:
    add = """
-   repo: local
    hooks:
    -   id: forbid-fake-todos
        name: forbid fake TODO snow
        entry: rg -n --pcre2 '(# noqa:\\s*(F821|invalid-syntax)\\s*#\\s*TODO:|REALITY_TODO)' --glob '!venv' --glob '!*.ipynb' .
        language: system
        pass_filenames: false
"""
    open(cfg,"a",encoding="utf-8").write(add)
PY

# 3) CI artifact (optional, in matriz-validate.yml)
# Add after star rules/coverage steps:
#   - name: Harvest TODOs (report only)
#     run: |
#       python3 scripts/harvest_todos.py --roots lukhas labs packages tools tests docs --out docs/audits/todos.csv
#   - name: Upload TODO CSV
#     uses: actions/upload-artifact@v4
#     with:
#       name: todos.csv
#       path: docs/audits/todos.csv

git add scripts docs/audits Makefile .pre-commit-config.yaml
git commit -m "chore(debt): add TODO harvest + GH issue generator tooling"
```

---

## For **Codex** — run pack (mechanical)

1. **Purge fake TODOs** (keep noqa, delete the “TODO” tail).

```bash
rg -l "# noqa: invalid-syntax\s+# TODO:" candidate labs lukhas | xargs -I{} gsed -i 's/# noqa: invalid-syntax  # TODO:.*$/# noqa: invalid-syntax/'
rg -l "# noqa: F821\s+# TODO:" candidate labs lukhas | xargs -I{} gsed -i 's/# noqa: F821  # TODO:.*$/# noqa: F821/'
rg -l "REALITY_TODO" | xargs -I{} gsed -i 's/.*REALITY_TODO.*//'
```

2. **Harvest** real TODOs → CSV.

```bash
make todos
wc -l docs/audits/todos.csv && head -5 docs/audits/todos.csv
```

3. **(Optional)** Generate GH issue commands (reviewable script).

```bash
python3 scripts/create_issues_from_csv.py \
  --csv docs/audits/todos.csv \
  --out docs/audits/todos_gh.sh \
  --repo LukhasAI/Lukhas \
  --milestone MATRIZ-R2 \
  --label-extra matriz
bash -n docs/audits/todos_gh.sh && head -10 docs/audits/todos_gh.sh
```

4. **Local validators** (must stay green):

```bash
python docs/check_links.py --root .
python scripts/validate_contract_refs.py
python scripts/validate_context_front_matter.py
python scripts/policy_guard.py
pytest -q -m matriz_smoke || true
```

**Done**. This gives you a clean, reproducible TODO pipeline: fake noise gone, real debt captured with owner hints, optional one-click issue creation, and CI artifacts for visibility.

