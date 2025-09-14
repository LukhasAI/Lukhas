
What we’ll add
	•	A tiny tool that:
	1.	runs ruff for F401 (unused imports),
	2.	inserts # TODO[T4-UNUSED-IMPORT]: <why?> on the import line (idempotent),
	3.	logs each edit to reports/todos/unused_imports.jsonl,
	4.	opens a file-level TODO header the first time a file gets tagged.
	•	A CI + pre-commit path that fails if there are new unused imports without TODO tags.
	•	A waiver file for deliberate placeholders (e.g., future MATRIZ hooks).

⸻

1) Script (drop in tools/ci/mark_unused_imports_todo.py)

#!/usr/bin/env python3
"""
Mark unused imports with TODOs instead of deleting them.

- Runs ruff F401 to find unused imports
- Adds inline marker: # TODO[T4-UNUSED-IMPORT]: <reason>
- Adds a file header if first TODO in file
- Skips files/lines already annotated or waived
- Emits JSONL log to reports/todos/unused_imports.jsonl
"""
import json, os, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORTS = REPO / "reports" / "todos"
REPORTS.mkdir(parents=True, exist_ok=True)
LOG = REPORTS / "unused_imports.jsonl"
WAIVERS = REPO / "AUDIT" / "waivers" / "unused_imports.yaml"

# files/dirs to ignore by policy
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine"}
SKIP_PREFIXES = tuple(str(REPO / d) + os.sep for d in SKIP_DIRS)

HEADER_BLOCK = "# ---\n# TODO[T4-UNUSED-IMPORT]: This file contains unused imports intentionally kept.\n# Add a reason per line or remove when implemented.\n# ---\n"

TODO_TAG = "TODO[T4-UNUSED-IMPORT]"
INLINE_PATTERN = re.compile(rf"#\s*{re.escape(TODO_TAG)}")
IMPORT_LINE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+.*)$")

def load_waivers():
    try:
        import yaml
        data = yaml.safe_load(WAIVERS.read_text()) or {}
        # Example structure:
        # waivers:
        #   - file: lukhas/foo.py
        #     line: 27          # optional
        #     reason: "kept for MATRIZ-R2"
        w = data.get("waivers", [])
        out = {}
        for it in w:
            p = (REPO / it["file"]).resolve()
            out.setdefault(str(p), set()).add(int(it.get("line", 0)))
        return out
    except Exception:
        return {}

def ruff_F401():
    # returns list of tuples (path, line, message)
    cmd = ["python3", "-m", "ruff", "check", "--select", "F401", "--output-format", "json", "."]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if p.returncode not in (0,1):  # 0=clean, 1=findings
        print(p.stderr or p.stdout, file=sys.stderr)
        sys.exit(p.returncode)
    items = json.loads(p.stdout or "[]")
    res = []
    for it in items:
        f = (REPO / it["filename"]).resolve()
        if str(f).startswith(SKIP_PREFIXES):
            continue
        res.append((str(f), it["location"]["row"], it["message"]))
    return res

def ensure_header(text):
    # add header if no prior TODO tag present
    if TODO_TAG not in text:
        return HEADER_BLOCK + text
    return text

def mark_line(text, line_no, reason):
    lines = text.splitlines()
    idx = line_no - 1
    if idx < 0 or idx >= len(lines):
        return text, False
    if INLINE_PATTERN.search(lines[idx]):
        return text, False
    if not IMPORT_LINE.match(lines[idx]):
        return text, False
    lines[idx] = f"{lines[idx]}  # {TODO_TAG}: {reason}"
    return "\n".join(lines) + ("\n" if not text.endswith("\n") else ""), True

def main():
    waivers = load_waivers()
    findings = ruff_F401()
    edits = 0
    LOG.touch(exist_ok=True)

    for path, line, msg in findings:
        # Skip waived files/lines
        if path in waivers and (0 in waivers[path] or line in waivers[path]):
            continue
        # Derive a minimal reason
        reason = "kept pending MATRIZ wiring (document or remove)"
        p = Path(path)
        code = p.read_text(encoding="utf-8", errors="ignore")
        new_code, changed = mark_line(code, line, reason)
        if not changed:
            continue
        # ensure header (first time)
        new_code = ensure_header(new_code)
        p.write_text(new_code, encoding="utf-8")
        edits += 1
        LOG.write_text(LOG.read_text() + json.dumps({
            "file": str(p.relative_to(REPO)),
            "line": line,
            "reason": reason,
            "message": msg
        }) + "\n")

    print(f"Marked {edits} unused import(s). Log: {LOG}")

if __name__ == "__main__":
    main()


⸻

2) Waivers file (optional, for intentional placeholders)

Create AUDIT/waivers/unused_imports.yaml:

waivers:
  # Example: keep an import for MATRIZ-R2 activation
  # - file: lukhas/matriz_bridge.py
  #   line: 42
  #   reason: "pending MATRIZ signal routing"


⸻

3) Makefile hooks

Add to your Makefile (or mk/ci.mk):

.PHONY: todos-unused
todos-unused:
	@python3 tools/ci/mark_unused_imports_todo.py

.PHONY: todos-unused-check
todos-unused-check:
	@# Fail if ruff reports F401 and the line lacks a TODO tag
	@python3 -m ruff check --select F401 --output-format json . \
	| python3 - <<'PY'
import json, sys, pathlib, re
TODO = re.compile(r"#\s*TODO\[T4-UNUSED-IMPORT\]")
bad = []
for it in json.load(sys.stdin):
    p = pathlib.Path(it["filename"])
    line = it["location"]["row"]
    try:
        s = p.read_text().splitlines()[line-1]
        if not TODO.search(s):
            bad.append(f'{p}:{line} {it["message"]}')
    except Exception:
        bad.append(f'{p}:{line} {it["message"]} (unreadable)')
if bad:
    print("Unannotated unused imports:\n" + "\n".join(bad))
    sys.exit(1)
print("OK: all unused imports are annotated.")
PY


⸻

4) Pre-commit & CI

pre-commit (add or extend):

# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: t4-unused-imports
        name: T4 unused imports annotator
        entry: python3 tools/ci/mark_unused_imports_todo.py
        language: system
        pass_filenames: false
        stages: [commit]
      - id: t4-unused-imports-check
        name: T4 unused imports must be TODO-annotated
        entry: make todos-unused-check
        language: system
        pass_filenames: false
        stages: [push]

CI gate (non-blocking or blocking—your choice):

# .github/workflows/ci.yml (add a job before lint)
t4-unused-imports:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: "3.11" }
    - run: pip install ruff
    - name: Annotate unused imports with TODOs (idempotent)
      run: python3 tools/ci/mark_unused_imports_todo.py
    - name: Ensure any remaining unused imports are annotated
      run: make todos-unused-check


⸻

5) T4 policy (drop in AUDIT/POLICIES.md)

### Unused Imports Policy (T4)
- Production lanes (lukhas/, MATRIZ/): No unused imports without explicit TODO tag.
- Experimental lanes (candidate/, quarantine/): Allowed **only** with TODO tag or waiver.
- Each TODO must state intent (e.g., “pending MATRIZ wiring”) and be cleared or waived before promotion.
- CI enforces: F401 must be annotated; unannotated F401 fails.


⸻

Why this is future-proof
	•	You don’t lose intent (kept imports are labeled with purpose).
	•	The annotator is idempotent and scope-limited (only F401 lines).
	•	Logs feed your dashboards (reports/todos/unused_imports.jsonl).
	•	You can tighten policy later: switch CI to block on any F401 in production lanes.

----

“48,540 F401” 
is noise. Your real surface is ~109 in core LUKHAS.
Here’s how to get there safely, without fighting .venv/ or candidate/ noise.
⸻

1) Verify the real F401 count (deterministic)

# Clean, scoped counts
python3 - <<'PY'
import json, subprocess
def count(paths):
    p = subprocess.run(["python3","-m","ruff","check","--select","F401","--output-format","json",*paths],
                       capture_output=True,text=True)
    items = json.loads(p.stdout or "[]")
    print(sum(1 for _ in items))
print("lukhas+MATRIZ F401:", end=" "); count(["lukhas","MATRIZ"])
print("core/api/consciousness/identity/memory F401:", end=" "); count(["lukhas/core","lukhas/api","lukhas/consciousness","lukhas/identity","lukhas/memory"])
PY

2) Lock the scope in config (so CI & editors agree)

pyproject.toml (ruff section):

[tool.ruff]
target-version = "py311"
extend-exclude = [
  ".venv", "node_modules", "archive", "quarantine", "reports",
]
# candidate is experimental—exclude from *blocking* runs
exclude = ["candidate"]

[tool.ruff.lint]
select = ["E9","F63","F7","F82","F401"]
# Optional: allow unused imports in __init__.py so package exports aren’t flagged
per-file-ignores = { "__init__.py" = ["F401"] }

.ruffignore (belt-and-suspenders for CLIs/IDEs that read it):

.venv/
node_modules/
archive/
quarantine/
reports/
candidate/

3) Make the policy explicit (block vs warn)
	•	Blocking job (PRs fail) runs on lukhas/ and MATRIZ/:

# .github/workflows/ci.yml (snippet)
jobs:
  ruff-block:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - name: Ruff (block on prod lanes)
        run: |
          python3 -m ruff check --select F401 lukhas MATRIZ

	•	Warn-only job (logs but doesn’t fail) for api/ ops/ tools/ serve/:

  ruff-warn:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - name: Ruff (warn on aux lanes)
        run: |
          python3 -m ruff check --select F401 lukhas/api ops tools serve || true

4) Turn unused imports → must-TODOs (prod lanes only)

Use your annotator but scope it:

python3 tools/ci/mark_unused_imports_todo.py --paths lukhas MATRIZ
# Then enforce: any remaining F401 in prod must have the TODO tag
make todos-unused-check

If you need the --paths switch added to the script, I can paste that patch—easy change to walk only given roots.

5) Pre-commit: fast feedback, correct scope

# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-prod-f401
        name: Ruff F401 (prod lanes)
        entry: python3 -m ruff check --select F401 lukhas MATRIZ
        language: system
        pass_filenames: false
      - id: t4-unused-imports
        name: Add TODOs for unused imports
        entry: python3 tools/ci/mark_unused_imports_todo.py --paths lukhas MATRIZ
        language: system
        pass_filenames: false

6) Makefile QoL

.PHONY: lint-f401-prod lint-f401-warn
lint-f401-prod:
	python3 -m ruff check --select F401 lukhas MATRIZ
lint-f401-warn:
	python3 -m ruff check --select F401 lukhas/api ops tools serve || true

7) Quick fix now (109 errors playbook)
	•	Run annotator on prod lanes (keeps intent, doesn’t break you):

python3 tools/ci/mark_unused_imports_todo.py --paths lukhas MATRIZ


	•	Then spend 30 min actually deleting the obvious cruft in lukhas/core (most of the 78 are easy removes). Keep TODO-tagged imports only if tied to MATRIZ-R1/R2 work, and reference the contract in the comment:

from lukhas.governance.guardian import GuardianValidator  # TODO[T4-UNUSED-IMPORT]: used in MATRIZ-R2 trace validation (contract: AUDIT/NODE_CONTRACTS/lukhas_api.json)



8) Prevent recurrence
	•	Add a debt ratchet: record F401 count per package; fail CI only if it increases.
	•	Keep candidate/ excluded from blocking runs; revisit once a module promotes into lukhas/.

⸻

