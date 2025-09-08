---
title: The Plan
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["testing", "concept"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "quantum"]
  audience: ["dev"]
---

# Claude Code:

Context: You have write access to the repo. Please implement the following exactly. All scripts must be idempotent and safe by default (dry-run where applicable), with clear stdout logs. Put generated artifacts under artifacts/refactor/ (git-ignored). Avoid modifying non-Python files except where explicitly called out.

0) Create base folders & .gitignore entries
	1.	Create directories:

	•	tools/refactor/
	•	artifacts/refactor/

	2.	Update/append to .gitignore (do not remove existing rules):

# refactor artifacts
artifacts/
*.dot
*.png
*.svg
dependency_graph.mmd
module_map.json
module_map.csv
snapshot_*.txt


⸻

1) Off-workspace backup (NEW requirement)

Create tools/refactor/backup_to_local_archive.sh:

#!/usr/bin/env bash
set -euo pipefail

# Back up the entire repo (including .git) to ~/LOCAL-REPOS/lukhas-archive/<timestamp>/
# This keeps test runs in the working copy clean and avoids cross-contamination.

ARCHIVE_ROOT="${HOME}/LOCAL-REPOS/lukhas-archive"
TS="$(date +%Y%m%d-%H%M%S)"
DEST="${ARCHIVE_ROOT}/lukhas-${TS}"

mkdir -p "${ARCHIVE_ROOT}"

echo "[backup] Archiving repo to: ${DEST}"
# Use rsync to preserve permissions and include dotfiles (incl. .git)
# Exclude common heavy caches that are not source of truth.
rsync -a \
  --delete \
  --exclude='.venv' \
  --exclude='venv' \
  --exclude='.mypy_cache' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='node_modules' \
  ./ "${DEST}/"

echo "[backup] Done."
echo "[backup] Verify at: ${DEST}"

Make it executable:

chmod +x tools/refactor/backup_to_local_archive.sh


⸻

2) Pre-migration snapshot log

Create tools/refactor/pre_migration_snapshot.sh:

#!/usr/bin/env bash
set -euo pipefail

OUT="artifacts/refactor/snapshot_$(date +%Y%m%d-%H%M%S).txt"
mkdir -p artifacts/refactor

{
  echo "=== PRE-MIGRATION SNAPSHOT ==="
  echo "Timestamp: $(date -Is)"
  echo
  echo "== Git =="
  git rev-parse --abbrev-ref HEAD || true
  git rev-parse HEAD || true
  echo
  echo "== Git status =="
  git status -s || true
  echo
  echo "== File counts (by extension) =="
  find . -type f -not -path './.git/*' | awk -F. '/\./ {print $NF}' | sort | uniq -c | sort -nr
  echo
  echo "== Top-level directories =="
  find . -maxdepth 2 -type d -not -path './.git*' | sort
  echo
  echo "== Python package roots (have __init__.py) =="
  find . -name '__init__.py' -printf '%h\n' | sort -u
  echo
  echo "== Pytest discovery =="
  pytest --collect-only -q || true
} > "${OUT}"

echo "[snapshot] Wrote ${OUT}"

Make it executable:

chmod +x tools/refactor/pre_migration_snapshot.sh


⸻

3) Import/Class/Function map (AST walker)

Create tools/refactor/log_imports_and_symbols.py:

#!/usr/bin/env python3
"""
Walks the repo, parses .py files via AST, and emits:
- artifacts/refactor/module_map.json
- artifacts/refactor/module_map.csv

For each file:
  path, module_name, imports (list), from_imports (list), classes (list), functions (list)
Skips .git, venvs, caches, artifacts/, node_modules.
"""

import ast
import json
import csv
import os
from pathlib import Path

ROOT = Path(".").resolve()

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules", "artifacts"}

def iter_py_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                yield Path(dirpath) / fn

def module_name_from_path(p: Path) -> str:
    rel = p.resolve().relative_to(ROOT)
    parts = list(rel.parts)
    if parts and parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    # strip leading "."
    return ".".join([x for x in parts if x not in ("",)])

def parse_file(p: Path):
    try:
        src = p.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src)
    except Exception as e:
        return {"path": str(p), "error": str(e), "imports": [], "from_imports": [], "classes": [], "functions": [], "module": module_name_from_path(p)}

    imports, from_imports, classes, functions = [], [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = [a.name for a in node.names if a.name]
            from_imports.append({"module": mod, "names": names})
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return {
        "path": str(p),
        "module": module_name_from_path(p),
        "imports": sorted(set(imports)),
        "from_imports": from_imports,
        "classes": sorted(set(classes)),
        "functions": sorted(set(functions)),
    }

def main():
    out_dir = ROOT / "artifacts" / "refactor"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "module_map.json"
    csv_path = out_dir / "module_map.csv"

    rows = []
    for py in iter_py_files(ROOT):
        rows.append(parse_file(py))

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "module", "imports", "from_imports", "classes", "functions"])
        for r in rows:
            w.writerow([
                r.get("path", ""),
                r.get("module", ""),
                ";".join(r.get("imports", [])),
                ";".join(
                    f'{fi["module"]}:{",".join(fi["names"])}' for fi in r.get("from_imports", [])
                ),
                ";".join(r.get("classes", [])),
                ";".join(r.get("functions", [])),
            ])

    print(f"[map] Wrote {json_path} and {csv_path}. Total files: {len(rows)}")

if __name__ == "__main__":
    main()

Make it executable:

chmod +x tools/refactor/log_imports_and_symbols.py


⸻

4) Dependency graph (Graphviz DOT + Mermaid)

Create tools/refactor/generate_dependency_graph.py:

#!/usr/bin/env python3
"""
Generates a simple import dependency graph using the module_map.json produced by log_imports_and_symbols.py.
Outputs:
- artifacts/refactor/dependency_graph.dot (Graphviz)
- artifacts/refactor/dependency_graph.mmd (Mermaid)

Nodes are module names (derived from paths). Edges for:
  - 'import X'
  - 'from X import Y'
"""

import json
from pathlib import Path

ROOT = Path(".").resolve()
MAP_JSON = ROOT / "artifacts" / "refactor" / "module_map.json"
OUT_DIR = ROOT / "artifacts" / "refactor"

def sanitize(module: str) -> str:
    return module.replace("-", "_")

def main():
    if not MAP_JSON.exists():
        raise SystemExit("[deps] module_map.json not found. Run log_imports_and_symbols.py first.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(MAP_JSON.read_text(encoding="utf-8"))

    edges = set()
    nodes = set()

    for row in data:
        src = row.get("module") or row.get("path")
        if not src:
            continue
        nodes.add(src)
        # direct imports
        for imp in row.get("imports", []):
            nodes.add(imp)
            edges.add((src, imp))
        # from imports
        for fi in row.get("from_imports", []):
            mod = fi.get("module") or ""
            if mod:
                nodes.add(mod)
                edges.add((src, mod))

    # Graphviz DOT
    dot_path = OUT_DIR / "dependency_graph.dot"
    with dot_path.open("w", encoding="utf-8") as f:
        f.write("digraph G {\n  rankdir=LR;\n  node [shape=box, fontsize=10];\n")
        for n in sorted(nodes):
            f.write(f'  "{sanitize(n)}";\n')
        for a, b in sorted(edges):
            f.write(f'  "{sanitize(a)}" -> "{sanitize(b)}";\n')
        f.write("}\n")

    # Mermaid
    mmd_path = OUT_DIR / "dependency_graph.mmd"
    with mmd_path.open("w", encoding="utf-8") as f:
        f.write("flowchart LR\n")
        for a, b in sorted(edges):
            f.write(f'  {sanitize(a)} --> {sanitize(b)}\n')

    print(f"[deps] Wrote {dot_path} and {mmd_path}. Nodes={len(nodes)} Edges={len(edges)}")

if __name__ == "__main__":
    main()

Make it executable:

chmod +x tools/refactor/generate_dependency_graph.py


⸻

5) Quantum → qi merger with dry-run + logging

Create tools/refactor/merge_quantum_to_qi.py:

#!/usr/bin/env python3
"""
Moves specific quantum_* dirs into qi/* as per migration plan.
- Default is --dry-run (prints actions only).
- Writes a move log CSV to artifacts/refactor/merge_log_<ts>.csv
- Only moves listed mappings by default; pass --include-wildcards to also move any other top-level quantum_* -> qi/<same_name_without_prefix> (safeguarded).

Mappings:
  quantum_core                 -> qi/core
  quantum_attention            -> qi/attention
  quantum_entropy              -> qi/entropy
  quantum_steganographic_demo  -> qi/steganography

Safety:
  - Creates destination dirs if needed.
  - Refuses to overwrite existing non-empty destinations unless --force.
  - Skips if source doesn't exist.
"""

import argparse
import csv
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(".").resolve()
ART = ROOT / "artifacts" / "refactor"
ART.mkdir(parents=True, exist_ok=True)

MAPPINGS = {
    "quantum_core": "qi/core",
    "quantum_attention": "qi/attention",
    "quantum_entropy": "qi/entropy",
    "quantum_steganographic_demo": "qi/steganography",
}

def is_empty_dir(p: Path) -> bool:
    return p.is_dir() and not any(p.iterdir())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default).")
    ap.add_argument("--execute", action="store_true", help="Perform actual moves.")
    ap.add_argument("--force", action="store_true", help="Allow moving into existing non-empty dest.")
    ap.add_argument("--include-wildcards", action="store_true",
                    help="Also move any other top-level quantum_* -> qi/<suffix>")
    args = ap.parse_args()

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = ART / f"merge_log_{ts}.csv"

    actions = []

    # Listed mappings
    for src_name, dest_rel in MAPPINGS.items():
        src = ROOT / src_name
        dest = ROOT / dest_rel
        if not src.exists():
            actions.append(("SKIP-NOT-FOUND", str(src), str(dest)))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not (args.force or is_empty_dir(dest)):
            actions.append(("SKIP-DEST-NOT-EMPTY", str(src), str(dest)))
            continue
        actions.append(("MOVE", str(src), str(dest)))

    # Optional wildcards
    if args.include_wildcards:
        for item in ROOT.iterdir():
            if item.is_dir() and item.name.startswith("quantum_") and item.name not in MAPPINGS:
                suffix = item.name.replace("quantum_", "")
                dest = ROOT / "qi" / suffix
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists() and not (args.force or is_empty_dir(dest)):
                    actions.append(("SKIP-DEST-NOT-EMPTY", str(item), str(dest)))
                    continue
                actions.append(("MOVE", str(item), str(dest)))

    # Print plan
    for act, s, d in actions:
        print(f"[{act}] {s} -> {d}")

    # Execute
    if args.execute:
        for act, s, d in actions:
            if act == "MOVE":
                shutil.move(s, d)

        # Log CSV
        with log_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["action", "source", "dest"])
            for row in actions:
                w.writerow(row)
        print(f"[merge] Logged to {log_path}")
    else:
        print("[merge] Dry run only. Use --execute to perform changes.")

if __name__ == "__main__":
    main()

Make it executable:

chmod +x tools/refactor/merge_quantum_to_qi.py


⸻

6) Leftover “quantum” import checker

Create tools/refactor/check_leftover_quantum.py:

#!/usr/bin/env python3
"""
Searches for leftover references to 'quantum' imports after migration.
Outputs a report to artifacts/refactor/quantum_leftover_references.txt
and prints a summary to stdout.
"""

import re
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "artifacts" / "refactor" / "quantum_leftover_references.txt"

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", "artifacts"}

PATTERNS = [
    re.compile(r'^\s*from\s+quantum[._]', re.M),
    re.compile(r'^\s*import\s+quantum[._]', re.M),
    re.compile(r'^\s*from\s+quantum_[A-Za-z0-9_]+', re.M),
    re.compile(r'^\s*import\s+quantum_[A-Za-z0-9_]+', re.M),
]

def iter_py_files():
    for p in ROOT.rglob("*.py"):
        parts = set(p.parts)
        if parts & SKIP_DIRS:
            continue
        yield p

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    hits = []
    for py in iter_py_files():
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in PATTERNS:
            if pat.search(text):
                hits.append(str(py))
                break

    OUT.write_text("\n".join(sorted(set(hits))), encoding="utf-8")
    print(f"[leftover] Files with 'quantum' references: {len(set(hits))}")
    print(f"[leftover] See {OUT}")

if __name__ == "__main__":
    main()

Make it executable:

chmod +x tools/refactor/check_leftover_quantum.py


⸻

7) Makefile shortcuts (developer ergonomics)

Create or extend Makefile with these targets (append if Makefile exists; otherwise create):

.PHONY: backup snapshot map deps merge-dry merge merge-wild check tags test

backup:
	tools/refactor/backup_to_local_archive.sh

snapshot:
	tools/refactor/pre_migration_snapshot.sh

map:
	python3 tools/refactor/log_imports_and_symbols.py

deps:
	python3 tools/refactor/generate_dependency_graph.py

merge-dry:
	python3 tools/refactor/merge_quantum_to_qi.py --dry-run

merge:
	python3 tools/refactor/merge_quantum_to_qi.py --execute

merge-wild:
	python3 tools/refactor/merge_quantum_to_qi.py --execute --include-wildcards

check:
	python3 tools/refactor/check_leftover_quantum.py

tags:
	@git tag -a phase1-complete -m "qi/ migration done" || true
	@git tag -a phase2-complete -m "dir consolidation complete" || true
	@git tag -a phase3-complete -m "GLYPH adapter integrated" || true

test:
	python3 -m pytest -q


⸻

8) Readme snippet (developer instructions)

Append to docs/REFACTOR_PLAN.md (create if missing):

# Refactor Utilities (qi Migration)

## Quickstart
```bash
# Hour 1: OFF-WORKSPACE BACKUP + SNAPSHOT
make backup
make snapshot

# Hour 2: MAP + DEPS
make map
make deps  # produces Graphviz DOT and Mermaid

# Hour 3: DRY RUN MERGE + CHECK
make merge-dry
make check

# If dry run looks good:
make merge

# Hour 4: TESTS + LEFTOVER CHECK
make test
make check

# Git tags after each phase
make tags

Artifacts are written to artifacts/refactor/.
Backups live at ~/LOCAL-REPOS/lukhas-archive/.

---

### 9) (Optional) Minimal targeted test scaffolds

Create `tests/test_qi_migration_sanity.py` (safe, won’t fail if modules absent; skips gracefully):

```python
import importlib
import pytest

OPTIONAL_IMPORTS = [
    ("qi.core.wavefunction_manager", "WavefunctionManager"),
    ("qi.attention", "DreamEngineMerged"),
    ("qi.entropy", "EntropyProfile"),
    ("qi.entropy", "TrueQuantumRandomness"),
    ("qi.steganography", None),
]

@pytest.mark.parametrize("mod, symbol", OPTIONAL_IMPORTS)
def test_optional_imports_exist(mod, symbol):
    try:
        m = importlib.import_module(mod)
    except Exception as e:
        pytest.skip(f"Optional module missing or not yet migrated: {mod} ({e})")
        return
    if symbol:
        assert hasattr(m, symbol), f"{mod} missing {symbol}"


⸻

10) Final command summary (to run after you finish)

Do not run these, just display them for the user:

# Safety & visibility
make backup
make snapshot
make map
make deps

# Migration (review dry-run first)
make merge-dry
# If plan looks correct:
make merge

# Verify leftover imports
make check

# Run tests
make test

# Add phase tags
make tags


⸻
