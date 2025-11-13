## T4 Lint Platform - Patch Specification
### What this adds (summary)

1. New policy doc: `docs/policies/T4_LINT_PLATFORM.md` (vision + governance for lint findings).
2. New annotator for generic lint findings: `tools/ci/lint_annotator.py` (creates structured inline `TODO[T4-LINT-ISSUE]` JSON).
3. New validator: `tools/ci/check_lint_issues_todo.py` (validates structured tags and quality).
4. Autofix runner: `tools/ci/lint_autofix.sh` (runs safe auto-fixers like `ruff --fix`, `isort`, etc., and opens PRs).
5. GitHub Action: `.github/workflows/t4-lint-platform.yml` (runs validator and optional autofix CI).
6. Small update to `scripts/replace_t4_policy.sh` to include these new files.
7. Guidance + runbook to triage the specific linter errors you listed into remediation paths (autofix, annotate, manual refactor, training).

---

## 1 — Files to add (exact content)

Place these files in the workspace and commit them to a new branch. I give the full contents so the agent can `git add` immediately.

---

### `docs/policies/T4_LINT_PLATFORM.md`

````markdown
# T4 — Lint Platform Policy (v1.0)

T4 Lint Platform: treat linter findings as *first-class technical intent* and a prioritized backlog of fixes. Structured annotations in code are human-friendly; the Intent Registry is the authoritative catalog. The platform automates safe fixes, generates issues/PRs for planned work, and enforces quality rules in CI.

## Scope
Production lanes: `lukhas/`, `core/`, `api/`, `consciousness/`, `memory/`, `identity/`, `MATRIZ/`.
Excluded: `candidate/`, `labs/`, `archive/`, `quarantine/`, `.venv/`, `node_modules/`, `.git/`, `reports/`.

## Core idea
- **Annotation**: a single-line JSON inline annotation on the offending line: `TODO[T4-LINT-ISSUE]: {...}`.
- **Intent Registry**: structured DB of lint intents (status, owner, ticket, remediation plan).
- **Lifecycle**: `reserved` → `planned` → `committed` → `implemented` → `expired`.
- **Policy**: For categories requiring non-trivial refactor (e.g., F821 undefined-name), an `owner` + `ticket` is required before merging.
- **Autofix-first**: where a safe linter autofix exists (ruff/isort), run it automatically and propose PRs; only annotate if autofix is not available or if it is risky.

## Annotation schema (inline)
Example:
```py
# TODO[T4-LINT-ISSUE]: {"id":"t4-lint-01a2","code":"F821","reason":"undefined-name 'np'","suggestion":"Add import numpy as np or qualify name","owner":null,"ticket":null,"status":"reserved","created_at":"2025-10-XXT12:00:00Z"}
x = np.array([1,2,3])
````

Fields:

* `id` (required): `t4-lint-<hex>`
* `code` (required): linter code (F821, B008, SIM102, RUF012, etc.)
* `reason` (required): short description
* `suggestion` (optional): automated suggested change (or `"autofix:ruff"` when auto-fix applied)
* `owner`, `ticket` (required when status == `planned` or `committed`)
* `status` (required): `reserved|planned|committed|implemented|expired`
* `created_at`, `modified_at` timestamps populated by tools

## Policies & remediations (high level)

* `autofixable` codes (e.g., import sorting, many SIM/RUF fixes): run `ruff --fix`, `isort`, `python -m ruff` auto-fixers in CI and create PRs automatically.
* `surgical-refactor` codes (e.g., B008 default arg, RUF012 mutable-class-default): prefer scripted codemods (LibCST) that create safe PRs.
* `manual-review` codes (e.g., F821 undefined-name, B904 raise-without-from): annotate with status `reserved` and create a triage issue. If automated suggestion matches single-file pattern, propose PR with suggested fix for maintainer review.
* `education` codes (style/collapsible if): create playbooks for maintainers and optionally apply auto-simplification.

## Metrics

* Per-code counts, Annotation Quality Score, Autofix PR rate, Time-to-Implement, Staleness.

## Governance

* `reserved` items older than 30 days escalate to architecture guild.
* `planned`/`committed` require `owner` + `ticket`.
* Autofix PRs should be reviewed within 3 business days.

## Implementation notes

* Tools: `ruff`, `isort`, `libcst` (for codemods), `gh` CLI for PR automation, SQLite Intent Registry.
* Start with dry-run/autofix pipeline for 2–4 weeks.

````

---

### `tools/ci/lint_annotator.py`
This is a general annotator that runs `ruff` (or other linters) for a provided list of codes, and writes inline structured TODOs `TODO[T4-LINT-ISSUE]` when it cannot autofix or when told `--annotate-all`.

**Add this file:**
```python
#!/usr/bin/env python3
"""
T4 Lint Annotator: run ruff for a set of codes and create structured inline annotations
for findings that need tracking.

Usage:
  python3 tools/ci/lint_annotator.py --paths lukhas core --codes F821,F403,B008 --dry-run
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
import uuid

REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "reports" / "todos" / "lint_issues.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)

TODO_TAG = "TODO[T4-LINT-ISSUE]"
INLINE_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}\s*:\s*(\{{.*\}})\s*$")
IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+.*)$")

def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def make_id() -> str:
    return f"t4-lint-{uuid.uuid4().hex[:8]}"

def run_ruff_select(paths: list[str], codes: list[str]) -> list[dict]:
    cmd = ["python3", "-m", "ruff", "check", "--select", ",".join(codes), "--output-format", "json", *paths]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode not in (0,1):
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(proc.returncode)
    try:
        return json.loads(proc.stdout or "[]")
    except Exception:
        return []

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="+", default=["lukhas", "core"])
    ap.add_argument("--codes", required=True, help="Comma-separated list of codes to check (e.g., F821,F403,B008)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--annotate-all", action="store_true", help="Annotate even if ruff says autofixable")
    ap.add_argument("--owner", default=None)
    ap.add_argument("--ticket", default=None)
    return ap.parse_args()

def annotate_line(text: str, line_no: int, payload: dict):
    lines = text.splitlines()
    idx = line_no - 1
    if idx < 0 or idx >= len(lines):
        return text, False
    line = lines[idx]
    if INLINE_RE.search(line):
        return text, False
    json_compact = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    lines[idx] = f"{line}  # {TODO_TAG}: {json_compact}"
    new_text = "\n".join(lines)
    if not text.endswith("\n"):
        new_text += "\n"
    return new_text, True

def main():
    args = parse_args()
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    # Resolve roots
    roots = []
    for p in args.paths:
        p = p.strip()
        rp = (REPO / p).resolve()
        if rp.exists():
            roots.append(str(rp.relative_to(REPO)))
    if not roots:
        print("No valid roots. Exiting.")
        sys.exit(0)

    findings = run_ruff_select(roots, codes)
    edits = 0
    new_entries = []
    for it in findings:
        file_path = (REPO / it["filename"]).resolve()
        line = int(it["location"]["row"])
        msg = it.get("message", "")
        code = it.get("code") or it.get("message", "").split()[0]

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Skip if already annotated
        try:
            target_line = text.splitlines()[line-1]
            if INLINE_RE.search(target_line):
                continue
        except Exception:
            pass

        # Build payload
        payload = {
            "id": make_id(),
            "code": code,
            "reason": msg,
            "suggestion": None,
            "owner": args.owner,
            "ticket": args.ticket,
            "status": "reserved",
            "created_at": iso_now()
        }

        # Basic suggestion heuristics for certain codes
        if code == "F821":
            # suggest import if token looks like a module alias (heuristic)
            token = None
            try:
                token = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", target_line)[0]
            except Exception:
                token = None
            if token:
                payload["suggestion"] = f"Consider adding import for '{token}', or define it before use."
        elif code == "F401":
            payload["suggestion"] = "Import is unused; consider removing or mark by TODO[T4-UNUSED-IMPORT]."
        elif code.startswith("B") and code in ("B008", "B018", "B007"):
            payload["suggestion"] = "Refactor suggested: move default arg to None, avoid useless expression, don't use loop-control variable."
        # ... add more heuristics as needed

        new_text, changed = annotate_line(text, line, payload)
        if changed:
            if args.dry_run:
                print(f"[DRY] Would annotate {file_path}:{line} - {code} - {payload['reason']}")
            else:
                file_path.write_text(new_text, encoding="utf-8")
            edits += 1
            new_entries.append({
                "id": payload["id"], "file": str(file_path.relative_to(REPO)), "line": line,
                "code": payload["code"], "reason": payload["reason"], "status": payload["status"], "created_at": payload["created_at"]
            })

    if not args.dry_run and new_entries:
        with LOG.open("a", encoding="utf-8") as fh:
            for e in new_entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"Annotations created: {edits}")

if __name__ == "__main__":
    main()
````

---

### `tools/ci/check_lint_issues_todo.py`

Validator: run `ruff` for a list of codes, ensure inline `TODO[T4-LINT-ISSUE]` exists or that the issue is autofixed; check quality rules.

**Add this file:**

```python
#!/usr/bin/env python3
"""
T4 Lint Issues Validator: ensure every lint finding in production lanes is either:
- annotated with TODO[T4-LINT-ISSUE] structured JSON, or
- has been autofixed (no finding), or
- waived via AUDIT/waivers/unused_imports.yaml
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODO_TAG = "TODO[T4-LINT-ISSUE]"
INLINE_JSON_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}\s*:\s*(\{{.*\}})\s*$")
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports"}
WAIVERS = REPO / "AUDIT" / "waivers" / "unused_imports.yaml"

def parse_inline_json(line: str):
    m = INLINE_JSON_RE.search(line)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None

def load_waivers():
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not WAIVERS.exists():
        return {}
    try:
        data = yaml.safe_load(WAIVERS.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    out = {}
    for it in data.get("waivers", []):
        p = (REPO / it["file"]).resolve()
        out.setdefault(str(p), set()).add(int(it.get("line", 0)))
    return out

def run_ruff_select(paths, codes):
    cmd = ["python3", "-m", "ruff", "check", "--select", ",".join(codes), "--output-format", "json", *paths]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode not in (0,1):
        return {"error": proc.stderr or proc.stdout}
    try:
        return {"items": json.loads(proc.stdout or "[]")}
    except Exception as e:
        return {"error": str(e)}

def validate_entry(entry):
    errors = []
    if not isinstance(entry, dict):
        errors.append("annotation is not JSON-object")
        return errors
    if "id" not in entry:
        errors.append("missing id")
    if "code" not in entry:
        errors.append("missing code")
    if "reason" not in entry or not entry["reason"]:
        errors.append("missing reason")
    if entry.get("status") in ("planned","committed") and (not entry.get("owner") or not entry.get("ticket")):
        errors.append("planned/committed must have owner and ticket")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", default=["lukhas","core","api","consciousness","memory","identity","MATRIZ"])
    parser.add_argument("--codes", required=False, default="F821,F401,B904,SIM102,F403,B008,B018,RUF012,RUF006,E701,E702,RUF001,E402,F811,B007,SIM117,SIM105,SIM115")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    roots = []
    for p in args.paths:
        abs_p = (REPO / p).resolve()
        if abs_p.exists():
            roots.append(str(abs_p.relative_to(REPO)))
    if not roots:
        print(json.dumps({"status":"error","message":"no roots"}))
        sys.exit(1)

    waivers = load_waivers()
    ruff_res = run_ruff_select(roots, codes)
    if "error" in ruff_res:
        print(json.dumps({"status":"error","message":ruff_res["error"]}, indent=2))
        sys.exit(1)
    items = ruff_res["items"]
    unannotated = []
    quality_issues = []
    annotated = 0

    for it in items:
        file_abs = (REPO / it["filename"]).resolve()
        if set(file_abs.parts) & SKIP_DIRS:
            continue
        file_str = str(file_abs.relative_to(REPO))
        line = it["location"]["row"]
        # waiver?
        if str(file_abs) in waivers and (0 in waivers[str(file_abs)] or line in waivers[str(file_abs)]):
            continue
        try:
            lines = file_abs.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line-1 >= len(lines):
                unannotated.append({"file":file_str,"line":line,"msg":"line out of range"})
                continue
            line_content = lines[line-1]
            entry = parse_inline_json(line_content)
            if not entry:
                # no structured annotation: flag it
                unannotated.append({"file":file_str,"line":line,"msg":it.get("message")})
            else:
                annotated += 1
                issues = validate_entry(entry)
                if issues:
                    quality_issues.append({"file":file_str,"line":line,"issues":issues})
        except Exception:
            unannotated.append({"file":file_str,"line":line,"msg":"unreadable"})

    res = {
        "status": "pass" if not unannotated and not quality_issues else "fail",
        "annotated": annotated,
        "missing": len(unannotated),
        "quality_issues_count": len(quality_issues),
        "unannotated": unannotated,
        "quality_issues": quality_issues
    }
    if args.json_only:
        print(json.dumps(res, indent=2))
    else:
        print(json.dumps(res, indent=2))
    sys.exit(0 if res["status"]=="pass" else 1)

if __name__ == "__main__":
    main()
```

---

### `tools/ci/lint_autofix.sh`

A helper script to run safe autofixes and open PRs (the agent can run it locally or in CI).

**Add this file:**

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# codes we consider safe to autofix via ruff/isort
AUTOFIX_CODES="I001,F401,SIM102,RUF001,RUF006,RUF012,RUF001"

# 1) Run isort
echo "Running isort..."
# Only run where pyproject defines isort or run globally
isort .

# 2) Run ruff autofix for selected codes (this will edit files)
echo "Running ruff --fix for autofixable codes..."
python3 -m ruff check --fix --select $AUTOFIX_CODES

# 3) Run ruff again to see remaining issues
echo "Collecting remaining issues..."
python3 -m ruff check --select $AUTOFIX_CODES --output-format json > /tmp/ruff_post_fix.json || true

# 4) If there were changes, create a PR
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "chore(t4): apply autofix (ruff/isort) for lint-platform"
  BRANCH="t4-lint-autofix-$(date +%s)"
  git checkout -b "$BRANCH"
  git push --set-upstream origin "$BRANCH"
  if command -v gh >/dev/null 2>&1; then
    gh pr create --title "chore(t4): autofix lint issues (ruff/isort)" --body "Autofix PR from T4 Lint Platform: ruff/isort changes. Please review." --base main
  else
    echo "Autofix branch created: $BRANCH. Please open a PR manually."
  fi
else
  echo "No changes from autofix."
fi

# 5) Run annotator for remaining codes (dry-run)
python3 tools/ci/lint_annotator.py --paths lukhas core api consciousness memory identity MATRIZ --codes "F821,F403,B904,B008,B018,RUF012,RUF006,E701,E702,E402,F811,B007,SIM117,SIM105,SIM115" --dry-run
```

---

### `.github/workflows/t4-lint-platform.yml`

A GitHub Action to run validator on PRs touching production lanes and optionally to run the autofix workflow as a periodic job.

```yaml
name: T4 Lint Platform

on:
  pull_request:
    paths:
      - 'lukhas/**'
      - 'core/**'
      - 'api/**'
      - 'consciousness/**'
      - 'memory/**'
      - 'identity/**'
      - 'MATRIZ/**'
  schedule:
    - cron: '0 3 * * 1'  # weekly run to propose autofix PRs

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install ruff isort pyyaml
      - name: Run T4 lint validator
        run: python3 tools/ci/check_lint_issues_todo.py --paths lukhas core api consciousness memory identity MATRIZ --json-only

  autofix:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install autofix tools
        run: pip install ruff isort
      - name: Run autofix and create PR
        run: bash tools/ci/lint_autofix.sh
```

---

### `scripts/replace_t4_policy.sh` (update)

Add the new files to be committed. Modify the existing script to include them. If you already used a script that moved files into `docs/backup_t4`, this addition should be appended.

Add the following commands in the script before `git commit` (or replace `git add` block to include the new files):

```bash
git add docs/policies/T4_LINT_PLATFORM.md
git add tools/ci/lint_annotator.py
git add tools/ci/check_lint_issues_todo.py
git add tools/ci/lint_autofix.sh
git add .github/workflows/t4-lint-platform.yml
```

Make the scripts executable:

```bash
chmod +x tools/ci/lint_annotator.py
chmod +x tools/ci/check_lint_issues_todo.py
chmod +x tools/ci/lint_autofix.sh
```

---

## 2 — Exact agent commands (step-by-step)

Run these from repo root. The agent must have `git` and optionally `gh` CLI configured.

1. **Create branch and add files**

```bash
# From repo root
git checkout -b replace/t4-lint-platform
# Create the files above in their paths (copy/paste contents).
chmod +x tools/ci/*.py tools/ci/lint_autofix.sh scripts/replace_t4_policy.sh
git add docs/policies/T4_LINT_PLATFORM.md \
        tools/ci/lint_annotator.py \
        tools/ci/check_lint_issues_todo.py \
        tools/ci/lint_autofix.sh \
        .github/workflows/t4-lint-platform.yml \
        scripts/replace_t4_policy.sh
git commit -m "chore(t4): add Lint Platform - annotator, validator, autofix, policy"
git push --set-upstream origin replace/t4-lint-platform
```

2. **Open PR**

```bash
# Optional: use gh to open a PR
if command -v gh >/dev/null 2>&1; then
  gh pr create --title "feat(t4): T4 Lint Platform - structured lint intent tracking and autofix" --body-file .github/PULL_REQUEST_TEMPLATE/t4_policy.md --base main
else
  echo "Please create a PR from branch replace/t4-lint-platform to main"
fi
```

3. **Dry-run autofix + annotate locally**

```bash
# Run safe autofix (local)
bash tools/ci/lint_autofix.sh

# Annotate remaining important codes (dry-run first)
python3 tools/ci/lint_annotator.py --paths lukhas core api consciousness memory identity MATRIZ --codes "F821,F403,B904,B008,B018,RUF012,RUF006,E701,E702,E402,F811,B007,SIM117,SIM105,SIM115" --dry-run
```

4. **Run validator**

```bash
python3 tools/ci/check_lint_issues_todo.py --paths lukhas core api consciousness memory identity MATRIZ --json-only
```

5. **Ingest to Intent Registry (optional; uses previous intent_registry)**

```bash
python3 tools/ci/intent_registry.py
```

6. **Review & triage**

* Inspect the validator output `quality_issues` and `unannotated`.
* For `autofix` PRs created by `lint_autofix.sh`, review them and merge if safe.
* For remaining `reserved` annotations, convert high-value ones to `planned` by adding `owner` & `ticket` (or create tickets).

---

## 3 — Remediation plan for the specific codes you listed

Treat each code group as one of: **autofixable**, **codemodable**, **annotate+triage**, or **education**. Below I give concrete agent actions for each code category and a short patch strategy.

1. **F821 — undefined-name (674)**

   * **Strategy**: Annotate and attempt *automated suggestion*. Heuristics:

     * If the name looks like typical alias (`np`, `pd`, `plt`) propose standard import (`import numpy as np`).
     * If name is local variable (lowercase), suggest define/rename.
   * **Agent actions**:

     * Run annotator for F821 (dry-run first).
     * For high-confidence matches, create PRs that add the obvious import (single-line) and run tests. Use conservative heuristic only. For ambiguous cases, annotate and create triage issues.

2. **F401 — unused-import (443)**

   * **Already covered** by T4 Unused Imports Platform. Keep in autofix pipeline: run `ruff --fix` and/or the existing `unused_imports.py` migration path.

3. **B904 — raise-without-from-inside-except (315)**

   * **Strategy**: Annotate each occurrence; suggest `raise X from e` or re-raise original exception using `raise`. If suggested fix is simple, propose PR with `raise err from None` or `raise NewError from exc`. Use automated codemod for simple patterns using `libcst`.

4. **SIM102 — collapsible-if (223)**

   * **Strategy**: `ruff --fix` or `ruff`'s `simplify` rules often autofix. Use `ruff --fix --select SIM102`.

5. **F403 — undefined-local-with-import-star (174)**

   * **Strategy**: Annotate and replace `from module import *` with explicit imports. Create codemod to list used names and rewrite imports. Use `ast` analysis to find used names then update import line.

6. **B008 — function-call-in-default-argument (166)**

   * **Strategy**: Codemod: transform `def f(x=now()):` to `def f(x=None): if x is None: x=now()`. Use LibCST scripted change. Annotate if codemod uncertain.

7. **I001 — unsorted-imports (149)**

   * **Strategy**: `isort .` in autofix. Create PR automatically.

8. **B018, B007, B018, etc.**

   * **Strategy**: `B018` useless expression — annotate and if trivial, remove. `B007` loop-control variable — annotate and refactor.

9. **RUF012, RUF006, RUF001, RUF...**

   * **Strategy**: Use `ruff --fix` where available and annotate remaining.

10. **E701/E702 — multiple statements on one line (colon/semicolon)**

    * **Strategy**: Codemod to split statements into separate lines. Use `libcst` to reformat or run `black` after fix.

11. **E402 — module-import-not-at-top-of-file (47)**

    * **Strategy**: Move imports to top if safe. For imports inside functions that intentionally delay import, annotate as acceptable or leave. For accidental imports, codemod to top.

12. **F811 — redefined-while-unused (44)**

    * **Strategy**: Annotate and propose rename or remove redundant redefinition.

13. **SIM117 / SIM105 / SIM115**

    * **Strategy**: Usually refactoring suggestions — apply `ruff --fix` or codemod, else annotate.

---

## 4 — How to convert these to opportunities (visionary list to include in the patch)

Add to the new policy file (or as `docs/gonzo/T4_LINT_OPPORTUNITIES.md`) the following program-level opportunities (agent should add this doc too or append into `T4_LINT_PLATFORM.md`):

* **Autofix PR Bot** — weekly runs call `lint_autofix.sh`, create PRs with autofixed changes. Analysts review and merge. Metrics: PR acceptance rate and coverage.
* **Codemod Library** — a small library of safe LibCST codemods for B008, RUF012, F403, E701/E702, F811. Each codemod exposes `--dry-run` and `--apply` modes.
* **Lint Triage Board** — GitHub project board auto-filled from Intent Registry with owners + ETA; monthly “Lint Garage” working session to clear top 20 high-impact `reserved` items.
* **IDE Quick-Fix Plugin** — ship VSCode snippets/commands using the structured TODO schema so maintainers can mark `planned` or open ticket from the editor.
* **Learning & Playbooks** — for common patterns (function default args, import star) add short playbooks and examples in `docs/gonzo/lint_playbooks/`.
* **Security gating** — use lint metrics as part of release readiness: critical rules (F821, F403, B904) must be at 90% health before release.

(Agent: add this document `docs/gonzo/T4_LINT_OPPORTUNITIES.md` or append to the policy doc.)

---

## 5 — Exact git / PR update to add the Lint Platform to the existing patch

If you previously created `replace/t4-policy-platform` branch, create a new branch derived from it and push changes:

```bash
# If on the replace/t4-policy-platform branch:
git checkout replace/t4-policy-platform
git pull origin replace/t4-policy-platform

# Create a focused branch for lint platform changes
git checkout -b replace/t4-lint-platform

# Add all new files (from above)
git add docs/policies/T4_LINT_PLATFORM.md \
        tools/ci/lint_annotator.py \
        tools/ci/check_lint_issues_todo.py \
        tools/ci/lint_autofix.sh \
        .github/workflows/t4-lint-platform.yml \
        scripts/replace_t4_policy.sh

git commit -m "feat(t4): add Lint Platform - structured lint annotator, validator, autofix, policy"
git push --set-upstream origin replace/t4-lint-platform

# Create PR
gh pr create --title "feat(t4): T4 Lint Platform" --body "Adds lint-platform: annotator, validator, autofix, and policy." --base main
```

If you prefer to add these files directly into the prior PR branch, replace the branch name accordingly.

---

## 6 — Post-PR runbook (agent actions after PR created)

1. **CI dry-run**: run validator in PR (CI step runs automatically). Inspect `unannotated` and `quality_issues`.
2. **Autofix PRs**: allow scheduled autofix job to open PRs. Review quickly and accept safe ones (imports, isort, black-style fixes).
3. **Triage**: For top offenders (sort by occurrence), assign owners and create `planned` issues. Use Intent Registry queries: `SELECT * FROM intents ORDER BY created_at DESC LIMIT 50;`
4. **Codemod pilot**: implement one codemod (e.g., B008 transform). Run on few packages; open PR with tests.
5. **Metrics & dashboard**: feed `reports/todos/*.jsonl` + intent_registry DB into a dashboard (Grafana/Metabase) for KPIs.

---

## 7 — Safety & conservative defaults (important)

* **Start with dry-run / non-blocking**: validator in PRs should *report* quality issues but not fail CI for 2–4 weeks. After tuning, flip to strict.
* **Autofix PRs must be human-reviewed**, and the bot should not merge automatically.
* **Codemods require tests**: any codemod PR should run full test suite.
* **Annotations must not contain secrets**; add a linter to check comment content for high-entropy strings.

-

## 

Perfecto — aquí tienes **dos entregables listos** para agregar al parche que ya creamos:

1. Un documento visionario **`docs/gonzo/T4_LINT_OPPORTUNITIES.md`** (opportunities / playbook) — en **English** (para evitar ambigüedad con código) con un **resumen en español** al principio, listo para commitear.
2. Un **codemod LibCST (starter)** que corrige **B008 — `function-call-in-default-argument`** de forma segura: `tools/ci/codemods/fix_b008.py`, más un script conductor `tools/ci/codemods/run_fix_b008.py` y un pequeño `run` helper. Todo listo para *dry-run* y *apply*, con instrucciones de git/PR para que Claude Agent lo ejecute.

Abajo tienes ambos archivos completos + **instrucciones precisas, linea-a-linea** que el agente debe ejecutar (branching, dry-run, aplicar, tests, PR). Lo entrego en español para que todo quede claro.

---

## 1) `docs/gonzo/T4_LINT_OPPORTUNITIES.md`

**(archivo para agregar a la rama `replace/t4-lint-platform`)**

```markdown
# T4 — Lint Opportunities & Playbook

**Resumen (español)**
Este documento resume oportunidades concretas para convertir alertas del linter en trabajo priorizado y valor técnico. Propone canales (autofix PRs, codemods, playbooks, tablero de triage) y pasos operativos para incorporar estas oportunidades al parche T4 Lint Platform ya creado.

---

## Vision (English)
T4 Lint Platform should not only track unused-imports but turn the whole lint surface into an actionable, measurable backlog of engineering work. Each lint finding becomes a tracked Intent (TODO[T4-LINT-ISSUE]) or an automated PR when safe. The platform prioritizes: safety → automation → human triage.

## Opportunities (concrete)

### 1. Autofix PR Bot (low-friction wins)
Weekly scheduled CI job that:
- Runs `isort`, `black`, `ruff --fix` where safe.
- Commits, opens a PR branch `t4-lint-autofix-<ts>`.
- Tracks PR metrics: acceptance rate, review time, lines changed.
**Value:** Rapid, low-risk cleanups for style & trivial issues (I001, F401, SIM102, RUF001...).

### 2. Codemod Library (safe but powerful)
A small library of LibCST codemods for surgical transformations:
- B008 (function-call-in-default-argument) — starter codemod included.
- F403 (import-star → explicit imports): codemod that infers used names.
- E701/E702 → split statements on separate lines.
Codemods support `--dry-run` & `--apply`, generate tests, and create PRs when applied.

### 3. Lint Triage Board + Intent Registry
- Intent Registry (SQLite) becomes source of truth; feed a GitHub Project / board with columns: `New`, `Reserved`, `Planned`, `Committed`, `Implemented`.
- Monthly "Lint Garage" working session to clear top 20 `reserved` high-impact items.

### 4. IDE Quick-Fixes & Developer UX
- Provide VSCode snippets that parse `TODO[T4-LINT-ISSUE]` structured JSON and allow maintainers to:
  - Create ticket (GH) and mark `planned`.
  - Apply suggestion locally and open PR.

### 5. Codified Playbooks & Training
- `docs/gonzo/lint_playbooks/` with recipes for common refactors:
  - B008: pattern + codemod explanation + tests.
  - F821: safe import heuristics, how to decide.
  - F403: how to replace `from x import *`.

### 6. Release Readiness & Security Gates
- Critical rules (F821, F403, B904) have thresholds for release. If any regresses above X, fail release checklist.

## Implementation Roadmap (90 days)
1. **Week 1–2**: Add Autofix scheduler (weekly) + isort & ruff --fix flow (dry-run).  
2. **Week 3–4**: Deploy Intent Registry + board; wire annotator for lint issues.  
3. **Week 5–8**: Deliver codemods: B008 (pilot), F403 (pilot). Run small pilots.  
4. **Week 9–12**: Iterate on UX (VSCode quick-fix) and enable stricter CI rules for production lanes.

## Acceptance Criteria
- Autofix PR acceptance rate > 70% after first 4 weeks.
- Top 10 lint findings show a 50% reduction after 12 weeks.
- All `planned` entries have owner + ticket before merging.

## Safety & Governance
- Autofix PRs require human review; do not merge automatically.
- Codemods run with `--dry-run` first, and all PRs must include tests.
- Annotations must not include secrets (DLP scan on comment content).

---

**End of document.**
```

---

## 2) Codemod LibCST: `tools/ci/codemods/fix_b008.py` (starter)

> **Propósito**: detectar parámetros con valor por defecto que son llamadas (ej. `def f(x=now()):`) y reescribirlos a `x=None` + insertar al comienzo del cuerpo:
>
> ```py
> if x is None:
>     x = now()
> ```
>
> El codemod trata: positional params, pos-only, kw-only, y mantiene anotaciones. Evita duplicar el patrón si ya existe un `if <name> is None: <name> = ...` cercano (primeras 6 sentencias del cuerpo).

**Archivo: `tools/ci/codemods/fix_b008.py`**

```python
#!/usr/bin/env python3
"""
LibCST transformer to fix B008: function-call-in-default-argument.

Usage as module (driver provided separately) to run in dry-run or apply mode.
"""
from __future__ import annotations
import libcst as cst
from libcst import matchers as m
from typing import List, Tuple, Optional


def _is_call(node: Optional[cst.BaseExpression]) -> bool:
    return isinstance(node, cst.Call)


def _has_existing_none_check(param_name: str, body: cst.IndentedBlock) -> bool:
    """
    Detect a pattern at the top of the function body like:
      if <param_name> is None:
          <param_name> = <something>
    Searches first few statements to avoid false positives deeper in body.
    """
    for stmt in body.body[:6]:
        if isinstance(stmt, cst.If):
            test = stmt.test
            # We expect a Comparison: Name(param) is None
            if isinstance(test, cst.Comparison):
                left = test.left
                if isinstance(left, cst.Name) and left.value == param_name:
                    for comp in test.comparisons:
                        if isinstance(comp.operator, cst.Is) and isinstance(comp.comparator, cst.Name) and comp.comparator.value == "None":
                            # check that body assigns param_name
                            for inner in stmt.body.body:
                                if isinstance(inner, cst.SimpleStatementLine):
                                    for expr in inner.body:
                                        if isinstance(expr, cst.Assign):
                                            for targ in expr.targets:
                                                if isinstance(targ.target, cst.Name) and targ.target.value == param_name:
                                                    return True
    return False


class FixB008Transformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        params = updated_node.params

        # helper to process a list of Param nodes and produce new ones plus fixes
        def process_param_list(param_list: List[cst.Param]) -> Tuple[List[cst.Param], List[Tuple[str, cst.BaseExpression]]]:
            new_params = []
            fixes: List[Tuple[str, cst.BaseExpression]] = []
            for p in param_list:
                if p.default and _is_call(p.default):
                    # Skip if default already 'None' or if it's a simple literal
                    param_name = p.name.value
                    # Create new param default = None
                    new_p = p.with_changes(default=cst.Name("None"))
                    new_params.append(new_p)
                    fixes.append((param_name, p.default))
                else:
                    new_params.append(p)
            return new_params, fixes

        # process positional, posonly, kwonly
        pos_params, pos_fixes = process_param_list(list(params.params))
        posonly_params, posonly_fixes = process_param_list(list(params.posonly_params))
        kwonly_params, kwonly_fixes = process_param_list(list(params.kwonly_params))

        all_fixes = pos_fixes + posonly_fixes + kwonly_fixes
        if not all_fixes:
            return updated_node  # nothing to do

        # Build new Params object
        new_params_obj = params.with_changes(
            params=pos_params,
            posonly_params=posonly_params,
            kwonly_params=kwonly_params
        )

        # If function has no body or not an IndentedBlock, skip
        body = updated_node.body
        if not isinstance(body, cst.IndentedBlock):
            return updated_node

        prepend_stmts: List[cst.BaseSmallStatement] = []
        for param_name, orig_default in all_fixes:
            # Avoid adding None-check if it already exists
            if _has_existing_none_check(param_name, body):
                continue
            # Create: if <param_name> is None: <param_name> = <orig_default>
            assign = cst.Assign(targets=[cst.AssignTarget(target=cst.Name(param_name))], value=orig_default)
            simple_assign = cst.SimpleStatementLine([assign])
            test = cst.Comparison(left=cst.Name(param_name), comparisons=[cst.ComparisonTarget(operator=cst.Is(), comparator=cst.Name("None"))])
            if_node = cst.If(test=test, body=cst.IndentedBlock(body=[simple_assign]))
            prepend_stmts.append(if_node)

        # If nothing to prepend (all had existing check), just return updated with new params
        if not prepend_stmts:
            return updated_node.with_changes(params=new_params_obj)

        # Create new body with prepended statements followed by existing body
        new_body = cst.IndentedBlock(body=[*prepend_stmts, *body.body])
        return updated_node.with_changes(params=new_params_obj, body=new_body)
```

---

## 3) Driver: `tools/ci/codemods/run_fix_b008.py`

Este script recorre archivos `.py` en una ruta dada (por defecto `lukhas`) y aplica el codemod. Tiene `--dry-run` (muestra diffs) y `--apply` (modifica ficheros). Evita directorios `SKIP_DIRS`.

**Archivo: `tools/ci/codemods/run_fix_b008.py`**

```python
#!/usr/bin/env python3
"""
Driver to run fix_b008 transformer over a code tree.

Usage:
  python3 tools/ci/codemods/run_fix_b008.py --root lukhas --dry-run
  python3 tools/ci/codemods/run_fix_b008.py --root lukhas --apply
"""
from __future__ import annotations
import argparse
from pathlib import Path
import difflib
import sys
from tools.ci.codemods.fix_b008 import FixB008Transformer
import libcst as cst

SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports", "__pycache__"}

def iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        # skip files under SKIP_DIRS
        parts = set(p.parts)
        if parts & SKIP_DIRS:
            continue
        yield p

def show_diff(orig: str, new: str, path: Path):
    diff = list(difflib.unified_diff(orig.splitlines(keepends=True), new.splitlines(keepends=True), fromfile=str(path), tofile=str(path)+" (modified)"))
    sys.stdout.writelines(diff)

def apply_to_file(path: Path, apply: bool) -> bool:
    src = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src)
    except Exception as e:
        print(f"Failed to parse {path}: {e}")
        return False
    new_module = module.visit(FixB008Transformer())
    new_src = new_module.code
    if new_src != src:
        print(f"Would modify: {path}")
        show_diff(src, new_src, path)
        if apply:
            backup = path.with_suffix(path.suffix + ".b008bak")
            path.rename(backup)
            path.write_text(new_src, encoding="utf-8")
            print(f"Applied and backed up original to {backup}")
        return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="lukhas")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print("Root not found:", root)
        sys.exit(1)

    modified = 0
    for p in iter_py_files(root):
        changed = apply_to_file(p, apply=args.apply)
        if changed:
            modified += 1

    print(f"Files with changes: {modified}")
    if modified == 0:
        print("No B008 patterns found or no file changed.")
    else:
        print("Review diffs above. If --apply used, files were modified (originals backed up with .b008bak).")

if __name__ == "__main__":
    main()
```

> **Notas técnicas** sobre codemod:
>
> * Busca llamadas (`Call`) como default; reemplaza por `None` y añade el `if x is None: x = <call>` al inicio de la función.
> * Evita duplicados: si ya existe una comprobación `if x is None: x = ...` en primer bloque, no vuelve a insertarla.
> * Maneja params posicionales, pos-only y kw-only. No intenta transformar varargs `*args` ni defaults complejos a la vez.
> * Respeta el formato y produce un diff legible.

---

## 4) Instrucciones EXACTAS para el agente (linea a linea)

A continuación el **script de pasos** que Claude Agent debe ejecutar para añadir los archivos a la rama `replace/t4-lint-platform`, hacer dry-run, aplicar cambios, ejecutar tests y abrir PRs.

> **Requisito**: tener `python3`, `pip`, `libcst`, `ruff` instalados, y `gh` CLI (opcional) autenticado.

### 4.1 — Crear branch desde `replace/t4-lint-platform` (o actualizar la que ya existe)

```bash
# Si no tienes la rama base local:
git fetch origin
git checkout -b replace/t4-lint-platform origin/replace/t4-lint-platform || git checkout -b replace/t4-lint-platform

# Crear rama para B008 codemod
git checkout -b feat/t4-b008-codemod
```

### 4.2 — Crear archivos en el repo (pegar los contenidos provistos)

Coloca:

* `docs/gonzo/T4_LINT_OPPORTUNITIES.md` (contenido arriba)
* `tools/ci/codemods/fix_b008.py`
* `tools/ci/codemods/run_fix_b008.py`

Asegúrate que la jerarquía de directorios exista:

```bash
mkdir -p docs/gonzo
mkdir -p tools/ci/codemods
```

Luego crear los ficheros con el contenido anterior (`cat > file.py <<'PY'\n...code...\nPY`), o mediante el método que prefieras.

Hazlos ejecutables:

```bash
chmod +x tools/ci/codemods/fix_b008.py
chmod +x tools/ci/codemods/run_fix_b008.py
```

### 4.3 — Añadir, commitear y push (branch local)

```bash
git add docs/gonzo/T4_LINT_OPPORTUNITIES.md tools/ci/codemods/fix_b008.py tools/ci/codemods/run_fix_b008.py
git commit -m "feat(t4): add B008 codemod and Lint Opportunities doc"
git push --set-upstream origin feat/t4-b008-codemod
```

### 4.4 — Dry-run del codemod (¡obligatorio primero!)

```bash
# Instalar libcst si no está
pip install libcst

# Dry-run sobre la carpeta lukhas (o cambia la ruta que prefieras)
python3 tools/ci/codemods/run_fix_b008.py --root lukhas --dry-run
```

**Qué esperar:** diffs en stdout para cada fichero que cambie. No habrá modificaciones en disco (solo mostrará los cambios). Revisa cuidadosamente.

### 4.5 — Aplicar los cambios (si OK)

```bash
# Aplicar changes en archivos que mostraron diffs
python3 tools/ci/codemods/run_fix_b008.py --root lukhas --apply
```

Los archivos originales se **renombrarán** con sufijo `.b008bak` como copia de seguridad.

### 4.6 — Ejecutar linter/tests localmente

Siempre ejecutar ruff y la suite de tests para asegurarse de que no rompimos nada:

```bash
# Instalar ruff si es necesario
pip install ruff

# Verificar ruff (arda)
python3 -m ruff check lukhas core api consciousness memory identity MATRIZ || true

# Ejecutar tests (ajusta la invocación según tu proyecto)
pytest -q || echo "Run full tests in CI"
```

Si las pruebas están limpias y el linter no reporta regresiones, sigue.

### 4.7 — Commit, push y abrir PR automatico

```bash
git add -A
git commit -m "fix(t4): apply B008 codemod (function-call-default-to-none)"
git push

# Abrir PR con gh (si disponible)
if command -v gh >/dev/null 2>&1; then
  gh pr create --title "fix(t4): B008 codemod - convert call-in-default-args" --body "Automated codemod for B008. Dry-run reviewed. Originals backed as .b008bak" --base replace/t4-lint-platform
else
  echo "Created branch feat/t4-b008-codemod; open PR against replace/t4-lint-platform manually."