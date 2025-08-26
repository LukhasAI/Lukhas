Totally get it—let’s remove ambiguity and give Copilot zero wiggle room. Below are the exact file contents for each missing/empty file, matching the T4 plan we already agreed on. Paste them verbatim, save, and run the quick validations at the end.

⸻

1) tools/ci/nightly_autofix.sh  (make executable)

#!/usr/bin/env bash
set -euo pipefail

# Nightly repo-wide pass:
# - ruff JSON + SARIF
# - safe CST fixes per .t4autofix.toml
# - format (ruff/black/isort)
# - annotate TODO[T4-AUTOFIX] for remaining/risky issues
# - minimal reality run (records only)
# - write summary + commit

mkdir -p reports/lints reports/autofix reports/todos

# Versions for provenance
{
  echo "ruff $(ruff --version 2>/dev/null || echo 'n/a')"
  echo "black $(black --version 2>/dev/null || echo 'n/a')"
  echo "isort $(isort --version-number 2>/dev/null || echo 'n/a')"
  python -V
} > reports/autofix/tool_versions.txt || true

# 1) Lint across repo
ruff check --fix --output-format json --output-file reports/lints/ruff.json . || true
ruff check --output-format sarif --output-file reports/lints/ruff.sarif . || true

# 2) Safe CST fixes (policy-scoped)
python tools/ci/auto_fix_safe.py || true

# 3) Format (idempotent)
ruff format . || true
black . || true
isort . --profile black || true

# 4) Mark TODOs for remaining/risky issues and produce TODO index
python tools/ci/mark_todos.py || true

# 5) Minimal reality check (do not fail nightly; just record)
set +e
pytest -q tests/test_imports.py tests/test_integration.py tests/golden/ > reports/autofix/reality.txt 2>&1
set -e

# 6) Summarize
python - << 'PY'
from pathlib import Path
import json
lines = ["# Nightly Autofix Summary",""]
lints = Path("reports/lints/ruff.json")
todos = Path("reports/todos/index.json")
if lints.exists():
    j = json.loads(lints.read_text() or "[]")
    lines.append(f"* Ruff findings: {len(j)}")
if todos.exists():
    tj = json.loads(todos.read_text() or "{}")
    lines.append(f"* TODO markers added: {sum(len(v) for v in tj.get('files', {}).values())}")
Path("reports/autofix/summary.md").write_text("\n".join(lines) + "\n")
PY

# 7) Commit changes if any
if ! git diff --quiet; then
  git add -A
  git commit -m "chore(autofix-nightly): apply safe fixes + annotate TODO[T4-AUTOFIX]"
fi

After saving: chmod +x tools/ci/nightly_autofix.sh

⸻

2) .github/workflows/ci-autofix-label.yml

name: T4 Autofix Merge Guard

on:
  pull_request:
    types: [opened, synchronize, labeled, unlabeled, reopened]

jobs:
  guard:
    if: contains(github.event.pull_request.labels.*.name, 'autofix')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install ruff tomli
      - name: Lint (report only)
        run: |
          mkdir -p reports/lints
          ruff check --output-format json --output-file reports/lints/ruff.json .
      - name: Fail if safe-fixable issues remain
        run: |
          python - << 'PY'
          import json, sys, pathlib
          try:
            import tomllib
          except Exception:
            import tomli as tomllib
          policy = tomllib.loads(pathlib.Path(".t4autofix.toml").read_text("utf-8"))
          allow = set(policy.get("rules",{}).get("allow", []))
          data = json.loads(pathlib.Path("reports/lints/ruff.json").read_text() or "[]")
          remaining = [d for d in data if d.get("code") in allow]
          if remaining:
            print("❌ Safe-fixable issues still present under 'autofix' label.")
            print("Count:", len(remaining))
            sys.exit(1)
          print("✅ No safe-fixable issues remain.")
          PY


⸻

3) .github/workflows/nightly-autofix.yml

name: T4 Nightly Autofix

on:
  schedule:
    - cron: "17 2 * * *"   # 02:17 UTC nightly
  workflow_dispatch: {}

jobs:
  nightly:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install ruff black isort libcst tomli pytest coverage pytest-cov
      - name: Prepare branch
        run: |
          BR="autofix/nightly-$(date +%Y%m%d)"
          git checkout -B "$BR"
          echo "BRANCH=$BR" >> $GITHUB_ENV
      - name: Run nightly autofix
        env:
          AUTOFIX_MODE: nightly
          T4_AUTOFIX: "1"
        run: |
          bash tools/ci/nightly_autofix.sh
          # Coverage for needs-golden (best-effort)
          coverage run -m pytest -q tests/test_imports.py tests/test_integration.py tests/golden/ || true
          coverage json -o reports/autofix/coverage.json || true
      - name: Ownership routing table
        run: |
          python - << 'PY'
          from pathlib import Path
          import json
          try:
            from tools.ci.owners_from_codeowners import map_files_to_owners
          except Exception:
            print("owners_from_codeowners missing; skip.")
            raise SystemExit(0)
          todos = Path("reports/todos/index.json")
          body = Path("reports/autofix/summary.md")
          if not (todos.exists() and body.exists()):
              raise SystemExit(0)
          data = json.loads(todos.read_text() or "{}")
          files = sorted(list(data.get("files", {}).keys()))
          if not files:
              raise SystemExit(0)
          mapping = map_files_to_owners(files)
          lines = ["\n## Ownership Routing", "", "| File | Owners |", "|---|---|"]
          for f in files:
              owners = " ".join(mapping.get(f, [])) or "_unowned_"
              lines.append(f"| `{f}` | {owners} |")
          body.write_text(body.read_text() + "\n" + "\n".join(lines) + "\n")
          PY
      - name: Commit changes
        run: |
          if ! git diff --quiet; then
            git add -A
            git commit -m "chore(autofix-nightly): nightly pass + reports"
          fi
      - name: Create or update PR
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          BR="$BRANCH"
          TITLE="Nightly autofix & TODO pass"
          BODY="$(cat reports/autofix/summary.md || echo 'Nightly autofix run.')"
          gh pr view "$BR" &>/dev/null && \
            gh pr edit "$BR" --title "$TITLE" --body "$BODY" --add-label "autofix-nightly" || \
            gh pr create --title "$TITLE" --body "$BODY" --base main --head "$BR" --label "autofix-nightly"
      - name: needs-golden label if uncovered changed files
        env: { GH_TOKEN: ${{ github.token }} }
        run: |
          python tools/ci/needs_golden.py > /tmp/ng.json || echo '{"needs_golden":[]}' > /tmp/ng.json
          PR_NUMBER=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number')
          NEED=$(jq -r '.needs_golden | length' /tmp/ng.json 2>/dev/null || echo 0)
          if [ "$NEED" != "0" ] && [ -n "$PR_NUMBER" ]; then
            gh pr edit "$PR_NUMBER" --add-label "needs-golden"
          fi


⸻

4) tools/ci/mark_todos.py

from pathlib import Path
import json
try:
    import tomllib  # py311
except Exception:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[2]
RUFF_JSON = ROOT / "reports" / "lints" / "ruff.json"
POLICY = ROOT / ".t4autofix.toml"
OUT_JSON = ROOT / "reports" / "todos" / "index.json"
OUT_MD   = ROOT / "reports" / "todos" / "summary.md"

TAG = "TODO[T4-AUTOFIX]"

def load_policy():
    if not POLICY.exists():
        return {"rules":{"allow":[],"block":[]}, "scope":{"allow":["**/*.py"], "deny":[]}, "interfaces":{"deny_patterns":[]}}
    with POLICY.open("rb") as f:
        return tomllib.load(f)

def fnmatch_any(path, patterns):
    from fnmatch import fnmatch
    return any(fnmatch(path, p) for p in patterns)

def main():
    if not RUFF_JSON.exists():
        print("No ruff.json; skipping TODO tagging.")
        return 0
    policy = load_policy()
    allow_codes = set(policy.get("rules",{}).get("allow", []))
    deny_globs  = policy.get("scope",{}).get("deny", [])
    iface_deny  = policy.get("interfaces",{}).get("deny_patterns", [])

    data = json.loads(RUFF_JSON.read_text() or "[]")
    by_file = {}
    for d in data:
        fn = d.get("filename")
        code = d.get("code")
        if not fn or fnmatch_any(fn, deny_globs) or fnmatch_any(fn, iface_deny):
            continue
        # annotate for non-allow OR still-present allow (nudges)
        if code in allow_codes or code not in allow_codes:
            by_file.setdefault(fn, []).append(d)

    index = {"files":{}}
    for fn, items in by_file.items():
        p = Path(fn)
        if not p.exists() or p.suffix != ".py":
            continue
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        grouped = {}
        for it in items:
            ln = int(it.get("location",{}).get("row", 0) or 0)
            if ln <= 0 or ln > len(lines):
                continue
            grouped.setdefault(ln, []).append(it)
        added = []
        for ln, xs in sorted(grouped.items()):
            existing = lines[ln-1]
            if TAG in existing:
                continue
            msg = xs[0].get("message","review")
            codes = sorted({x.get("code") for x in xs if x.get("code")})
            comment = f"# {TAG}[{','.join(codes)}]: {msg}"
            lines.insert(ln-1, comment)
            added.append({"line": ln, "codes": [x.get("code") for x in xs]})
        if added:
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            index["files"][fn] = added

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(index, indent=2), encoding="utf-8")

    total = sum(len(v) for v in index["files"].values())
    md = ["# TODO Index (Nightly)", f"* Files with TODOs: {len(index['files'])}", f"* Total TODOs: {total}", ""]
    for fn, items in sorted(index["files"].items()):
        md.append(f"## {fn}")
        for it in items:
            codes = ",".join(filter(None, it["codes"]))
            md.append(f"- L{it['line']}: `{codes}`")
        md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Annotated {total} TODOs across {len(index['files'])} files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())


⸻

5) reports/todos/summary.md  (optional placeholder)

# TODO Index (Nightly)
* Files with TODOs: 0
* Total TODOs: 0

_Run the nightly workflow to populate this report._


⸻

6) CODEOWNERS  (only if missing or you want defaults)

If you don’t have one yet, here’s a safe starter that routes core areas. Adjust owners to your GitHub handles:

# Path pattern      @owners
/lukhas/**          @Gonzalo @Agent01
/candidate/**       @Agent02
/universal_language/** @Agent03
/tools/**           @Agent04
/tests/**           @Gonzalo


⸻

Also referenced earlier (if Copilot flagged missing)

These two helpers are used by the nightly and needs-golden steps—include them if they’re not already present.

tools/ci/owners_from_codeowners.py

from pathlib import Path

def parse_codeowners(text: str):
    rules = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split()
        if len(parts) >= 2:
            pattern, owners = parts[0], parts[1:]
            rules.append((pattern, owners))
    return rules

def owners_for(path: str, rules):
    from fnmatch import fnmatch
    hits = []
    for pattern, owners in rules:
        if fnmatch(path, pattern):
            hits = owners  # last match wins
    return hits

def map_files_to_owners(files, codeowners_path="CODEOWNERS"):
    p = Path(codeowners_path)
    if not p.exists(): return {}
    rules = parse_codeowners(p.read_text())
    return {f: owners_for(f, rules) for f in files}

tools/ci/needs_golden.py

import json
from pathlib import Path

def changed_files_from_todo_index():
    idx = Path("reports/todos/index.json")
    if not idx.exists():
        return set()
    data = json.loads(idx.read_text() or "{}")
    return set(data.get("files", {}).keys())

def uncovered_files(coverage_json="reports/autofix/coverage.json"):
    p = Path(coverage_json)
    if not p.exists():
        return set()
    data = json.loads(p.read_text() or "{}")
    res = set()
    for path, meta in data.get("files", {}).items():
        if meta.get("summary", {}).get("percent_covered", 0) <= 0:
            res.add(path)
    return res

def main():
    changed = changed_files_from_todo_index()
    uncov = uncovered_files()
    need = sorted(changed & uncov)
    print(json.dumps({"needs_golden": need}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())


⸻

Quick validation (run these now)

# Make shell scripts executable
chmod +x tools/ci/nightly_autofix.sh

# Sanity: mark_todos doesn’t crash without ruff.json
python tools/ci/mark_todos.py

# Dry-run nightly locally (best-effort)
bash tools/ci/nightly_autofix.sh

# Workflows syntax check (GitHub will also validate on push)

Commit suggestions:
	•	chore(ci): restore nightly-autofix workflow and runner
	•	chore(ci): add merge guard for autofix label
	•	chore(ci): add mark_todos and helpers
	•	docs: seed reports/todos/summary.md
	•	chore(repo): add CODEOWNERS (initial)

