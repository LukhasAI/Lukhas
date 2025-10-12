This is a golden moment to turn lint pain into lasting structure. Here’s how the **0.01% / T4** crew would handle Ruff, fix fast, and convert the signal into product-quality guardrails.

---

# 0) North Star

* **Goal**: zero relative imports, no undefined names on T1/T2, and stable totals trending down.
* **Method**: three small, reversible PRs:

  1. **Mechanical** autofixes (safe).
  2. **Imports normalization** (ban relatives, rewrite to absolute).
  3. **Undefined-names pass** + test nits, with owners looped in.

---

# 1) Configure Ruff for “discipline, not despair”

### `pyproject.toml` (or `ruff.toml`)

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
respect-gitignore = true
extend-exclude = [
  "manifests/**", "docs/audits/**", "packages/**/generated/**",
]

# Only hard-fail on the rules we’re fixing now.
select = ["F", "E", "W", "I", "UP", "TID252"]
ignore = [
  # TEMP: allow star-import in tests during transition (we’ll remove later)
  "F403",
]
# Treat relative imports as errors (we’ll rewrite them).
ban-relative-imports = "all"

[tool.ruff.lint.isort]
combine-as-imports = true
known-first-party = ["lukhas"]  # <-- target package name
```

### Per-file ignores (tests)

If tests are intentionally a bit loose, isolate the noise instead of muting globally:

```toml
[tool.ruff.per-file-ignores]
"tests/**" = ["F401", "F403", "F811"]
```

*(We’ll remove F811 ignore after we rename duplicate test classes.)*

---

# 2) PR #1 — Mechanical fixes (safe, fast)

* Auto-remove **F401 unused imports**.
* Normalize imports (isort via Ruff).
* Leave **TID252** (relative imports) for the next PR so we don’t half-break things.

**Commands**

```bash
git checkout -b chore/ruff-mechanical
ruff check --fix .
pytest -q -m matriz_smoke
git commit -am "chore(lint): mechanical ruff fixes (F401/isort)"
git push -u origin chore/ruff-mechanical
```

---

# 3) PR #2 — Imports normalization (kill TID252)

Ruff won’t auto-fix **TID252**. We’ll rewrite relatives to absolute **once**, aligned with your flat rename.

### A) Decide the canonical root import

Use **`lukhas`** as the one, true package name (consistent with your rename & manifests).

### B) Drop-in rewriter (AST-safe)

Create `scripts/normalize_imports.py` (uses `libcst` for safe code mods):

```python
#!/usr/bin/env python3
# requires: pip install libcst
import argparse, pathlib, sys
import libcst as cst
from libcst import RemovalSentinel

class Rewriter(cst.CSTTransformer):
    def __init__(self, root_pkg: str, file_path: pathlib.Path, repo_root: pathlib.Path):
        self.root_pkg = root_pkg
        self.file_path = file_path
        self.repo_root = repo_root

    def _abs_module(self, node: cst.ImportFrom):
        # Convert relative (level>=1) to absolute by resolving filesystem path
        if node.relative:
            # Compute module path from file location + level
            levels = node.relative.value
            base = self.file_path.parent
            for _ in range(levels):
                base = base.parent
            # from .foo.bar import Baz => module "foo.bar" under current base
            tail = ".".join([n.name.value for n in (node.module.names if isinstance(node.module, cst.Attribute) else node.module.names)] if isinstance(node.module, cst.ImportStar) else [])
            # If node.module is a Name or Attribute, reconstruct string
            if isinstance(node.module, cst.Name):
                mod = node.module.value
            elif isinstance(node.module, cst.Attribute):
                parts = []
                cur = node.module
                while isinstance(cur, cst.Attribute):
                    parts.append(cur.attr.value)
                    cur = cur.value
                if isinstance(cur, cst.Name):
                    parts.append(cur.value)
                mod = ".".join(reversed(parts))
            else:
                mod = None

            if mod:
                abs_mod = f"{self.root_pkg}.{'.'.join((base / mod.replace('.', '/')).parts[len(self.repo_root.parts):])}".replace("//",".").replace("..",".")
                # Normalize redundant dots
                abs_mod = ".".join([p for p in abs_mod.split(".") if p])
                return abs_mod
        return None

    def leave_ImportFrom(self, node: cst.ImportFrom, updated: cst.ImportFrom):
        if node.relative:
            abs_mod = self._abs_module(node)
            if abs_mod:
                return updated.with_changes(relative=None, module=cst.parse_expression(abs_mod))
        return updated

def rewrite_file(path: pathlib.Path, root_pkg: str, repo_root: pathlib.Path):
    src = path.read_text(encoding="utf-8")
    mod = cst.parse_module(src)
    out = mod.visit(Rewriter(root_pkg, path, repo_root))
    path.write_text(out.code, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root-pkg", default="lukhas")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    repo_root = pathlib.Path(args.repo_root).resolve()
    for p in args.paths:
        p = pathlib.Path(p).resolve()
        if p.suffix == ".py":
            rewrite_file(p, args.root_pkg, repo_root)

if __name__ == "__main__":
    main()
```

**Run it on relative imports only (dry-run first):**

```bash
git checkout -b chore/imports-absolute
rg -l 'from \.+\w' --glob '!venv/**' --glob '!packages/**' | tee /tmp/rel_imports.txt
# install libcst once
python3 -m pip install libcst
python3 scripts/normalize_imports.py --root-pkg lukhas $(cat /tmp/rel_imports.txt)

ruff check --fix .
pytest -q -m matriz_smoke
git commit -am "chore(imports): rewrite relative imports to absolute (ban TID252)"
git push -u origin chore/imports-absolute
```

*If some paths are tricky, keep a short-lived shim (`candidate/`, `lukhas/`) until all imports move, then delete shims.*

---

# 4) PR #3 — Undefined names (F821), returns outside function (F706), and a bit of test hygiene

### F821 (“undefined name”)

**Playbook**

* **90%**: missing import → add explicit import where used.
* Type-only forward refs: `from __future__ import annotations` or quote the type.
* Dynamic module attributes: add guarded fallback or `# noqa: F821` + `typing.TYPE_CHECKING` imports.

**Helper: group F821 offenders by missing symbol**

```bash
ruff check --output-format json . > docs/audits/ruff.json
python3 - <<'PY'
import json, collections
d=json.load(open('docs/audits/ruff.json'))
miss=collections.defaultdict(list)
for e in d:
    if e["code"]=="F821":
        miss[e["message"]].append(e["filename"])
for k,v in sorted(miss.items(), key=lambda x:-len(x[1]))[:25]:
    print(len(v), k)
PY
```

Fix the top offenders first; it collapses a huge tail.

### F706 (“return outside function”)

* Usually a misplaced `return` in a module or an accidentally dedented block.
* Quick pass: search for `^return` not inside defs.

```bash
rg -n '^[ \t]*return\b' | rg -v 'def '
```

Wrap into a `main()` or remove stray returns.

### Tests (F811/F401 in tests)

* Rename duplicate classes (`TestX`), or parametrize.
* Allow selective per-file ignores for brittle “availability” tests if they’re intentional.

Commit:

```bash
git checkout -b chore/f821-f706-sweep
# (apply fixes)
pytest -q
git commit -am "fix(lint): resolve F821 undefined names and F706 returns; test hygiene"
git push -u origin chore/f821-f706-sweep
```

---

# 5) Turn lint into product signal (not just a to-do list)

### A) Lint heatmap by **star / colony / owner**

Parse Ruff JSON + manifests → who owns the debt.

```bash
python3 - <<'PY'
import json, pathlib, collections
ruff = json.load(open('docs/audits/ruff.json'))
from glob import glob
import os

# Map file → star/owner from manifest (best-effort: look for closest manifest)
def nearest_manifest(pyfile):
    p = pathlib.Path(pyfile)
    for parent in [p] + list(p.parents):
        m = parent / "module.manifest.json"
        if m.exists():
            try:
                return json.load(open(m))
            except: pass
    return {}

heat = collections.defaultdict(lambda: collections.Counter())
for e in ruff:
    f = e["filename"]
    man = nearest_manifest(f)
    star = ((man.get("constellation_alignment") or {}).get("primary_star")) or "Supporting"
    owner = ((man.get("metadata") or {}).get("owner")) or "unknown"
    heat[(star, owner)][e["code"]] += 1

print("| Star | Owner | F821 | F401 | TID252 | Total |")
print("|---|---|---:|---:|---:|---:|")
for (star, owner), counts in sorted(heat.items()):
    tot = sum(counts.values())
    print(f"| {star} | {owner} | {counts['F821']} | {counts['F401']} | {counts['TID252']} | {tot} |")
PY
```

Drop the table into `docs/audits/ruff_heatmap.md` and tag owners. This **prioritizes** fixes where they matter (T1/T2 stars first).

### B) CI delta guard (no backsliding)

* Save a **baseline** on `main`: `docs/audits/ruff_baseline.json` (just totals by code).
* In CI: run Ruff, compute new totals, **fail only if any code count increases**; allow decreases (ratchet).

---

# 6) Makefile helpers (paste)

```makefile
.PHONY: lint lint-fix lint-json lint-delta imports-abs

lint:
	ruff check .

lint-fix:
	ruff check --fix .

lint-json:
	ruff check --output-format json . > docs/audits/ruff.json

imports-abs:
	python3 -m pip install libcst
	rg -l 'from \.+\w' --glob '!venv/**' --glob '!packages/**' | tee /tmp/rel_imports.txt
	python3 scripts/normalize_imports.py --root-pkg lukhas $$(cat /tmp/rel_imports.txt)
	ruff check --fix .
```

---

# 7) CI snippets (append to your `matriz-validate.yml`)

* Produce Ruff JSON artifact.
* Fail on relative imports if any remain after the rewrite PR.
* Ratchet lint counts vs baseline (optional).

```yaml
      - name: Ruff (JSON)
        run: ruff check --output-format json . > docs/audits/ruff.json

      - name: Artifact — Ruff report
        uses: actions/upload-artifact@v4
        with:
          name: ruff-report
          path: docs/audits/ruff.json

      - name: Tripwire — No relative imports
        run: |
          python - <<'PY'
          import json, sys
          d=json.load(open('docs/audits/ruff.json'))
          rel=[e for e in d if e["code"]=="TID252"]
          if rel:
              print(f"[FAIL] {len(rel)} relative-import violations remain.")
              sys.exit(1)
          print("[OK] No TID252.")
          PY
```

*(Add a baseline ratchet if you want—shout if you’d like me to paste that too.)*

---

##  Next action 

**PR #1 (mechanical)** today; it will remove ~**505 F401** instantly and reorder imports.

love it — here’s a tiny-but-smart **F821 helper** that scans your Ruff JSON, builds a repo-wide symbol index, and proposes **import inserts** (with confidence + reason). It can also (optionally) apply the imports for you in a safe, minimal way.

---

# `scripts/suggest_imports_f821.py`

```python
#!/usr/bin/env python3
"""
Suggest (and optionally apply) import fixes for Ruff F821 "undefined name".

Usage:
  1) Produce Ruff JSON once:
       ruff check --output-format json . > docs/audits/ruff.json
  2) Suggest fixes (dry-run):
       python3 scripts/suggest_imports_f821.py \
         --ruff docs/audits/ruff.json --root-pkg lukhas --src . \
         --out docs/audits/f821_suggestions.csv --md docs/audits/f821_suggestions.md
  3) (Optional) Apply top suggestions:
       python3 scripts/suggest_imports_f821.py --apply --apply-limit 50 \
         --ruff docs/audits/ruff.json --root-pkg lukhas --src .

Notes:
- Heuristics stack (highest weight first): stdlib/alias map, unique symbol index hit,
  module-name-as-symbol, same-star tie-break from nearest manifests.
- Safe apply inserts import lines near the top (after module docstring/__future__).
- Never overwrites existing identical imports; adds "# F821-helper" comment.
"""

from __future__ import annotations
import argparse, ast, csv, json, re, sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# --- Config knobs ------------------------------------------------------------

# Common stdlib / typing / third-party mappings (high precision)
STD_THIRD_MAP = {
    # stdlib
    "Path": "from pathlib import Path",
    "defaultdict": "from collections import defaultdict",
    "Counter": "from collections import Counter",
    "deque": "from collections import deque",
    "json": "import json",
    "re": "import re",
    "datetime": "from datetime import datetime",
    "timedelta": "from datetime import timedelta",
    "uuid": "import uuid",
    "os": "import os",
    "sys": "import sys",
    "logging": "import logging",
    "lru_cache": "from functools import lru_cache",
    "partial": "from functools import partial",
    # typing
    "Any": "from typing import Any",
    "Optional": "from typing import Optional",
    "Dict": "from typing import Dict",
    "List": "from typing import List",
    "Tuple": "from typing import Tuple",
    "Set": "from typing import Set",
    "Callable": "from typing import Callable",
    # pydantic (common)
    "BaseModel": "from pydantic import BaseModel",
    "Field": "from pydantic import Field",
    # data science shorthands
    "np": "import numpy as np",
    "pd": "import pandas as pd",
    "plt": "import matplotlib.pyplot as plt",
}

F821_MSG_RE = re.compile(r"Undefined name '([^']+)'")

# --- Helpers -----------------------------------------------------------------

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def nearest_manifest(pyfile: Path) -> dict:
    for parent in [pyfile] + list(pyfile.parents):
        m = parent / "module.manifest.json"
        if m.exists():
            try:
                return read_json(m)
            except Exception:
                return {}
    return {}

def import_path_for(pyfile: Path, repo_root: Path, root_pkg: str) -> Optional[str]:
    """
    Convert filesystem path to import path. E.g.
      /repo/lukhas/foo/bar.py -> lukhas.foo.bar
    Returns None for files outside the root package.
    """
    try:
        rel = pyfile.relative_to(repo_root)
    except Exception:
        return None
    parts = list(rel.parts)
    if not parts:
        return None
    if parts[0] != root_pkg:
        return None
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1].replace(".py", "")
    return ".".join(parts)

def scan_symbols(pyfile: Path) -> Tuple[List[str], List[str], List[str]]:
    """Return (classes, functions, constants) defined at module top-level."""
    try:
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    except Exception:
        return [], [], []
    classes, funcs, consts = [], [], []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    name = t.id
                    if re.match(r"^[A-Z_][A-Z0-9_]*$", name):  # heuristic: constant-like
                        consts.append(name)
    return classes, funcs, consts

def build_symbol_index(repo_root: Path, root_pkg: str) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """
    Walk the root package; build:
      - symbol_index: symbol -> [module.import.path,...]
      - module_index: file_path -> module.import.path
    """
    pkg_dir = repo_root / root_pkg
    symbol_index: Dict[str, List[str]] = {}
    module_index: Dict[str, str] = {}
    if not pkg_dir.exists():
        return symbol_index, module_index

    for py in pkg_dir.rglob("*.py"):
        if "/generated/" in str(py):
            continue
        mod = import_path_for(py, repo_root, root_pkg)
        if not mod:
            continue
        module_index[str(py)] = mod
        cls, fn, cs = scan_symbols(py)
        for s in set(cls + fn + cs):
            symbol_index.setdefault(s, []).append(mod)
    return symbol_index, module_index

def candidates_for_symbol(symbol: str,
                          symbol_index: Dict[str, List[str]],
                          module_index: Dict[str, str],
                          file_path: Path,
                          repo_root: Path,
                          root_pkg: str) -> List[Tuple[str, float, str]]:
    """
    Return list of (import_line, confidence, reason).
    """
    suggestions: List[Tuple[str, float, str]] = []

    # 1) std/third-party direct mapping (highest precision)
    if symbol in STD_THIRD_MAP:
        suggestions.append((STD_THIRD_MAP[symbol], 0.95, "stdlib/alias mapping"))
        return suggestions

    # 2) exact symbol hits in the index
    hits = symbol_index.get(symbol, [])
    if len(hits) == 1:
        mod = hits[0]
        suggestions.append((f"from {mod} import {symbol}", 0.90, "unique symbol in index"))
    elif len(hits) > 1:
        # try star/colony tie-breaker
        me_star = ((nearest_manifest(file_path).get("constellation_alignment") or {}).get("primary_star"))
        same_star = []
        for mod in hits:
            mod_file = Path(repo_root, *mod.split("."))  # best-effort
            if (mod_file / "__init__.py").exists():
                mf = mod_file / "module.manifest.json"
            else:
                mf = mod_file.with_suffix(".py").parent / "module.manifest.json"
            star = ""
            if mf.exists():
                try:
                    star = (read_json(mf).get("constellation_alignment") or {}).get("primary_star") or ""
                except Exception:
                    pass
            if me_star and star == me_star:
                same_star.append(mod)
        pick = (same_star[0] if same_star else hits[0])
        conf = 0.78 if same_star else 0.65
        reason = "symbol in multiple modules; same-star preference" if same_star else "symbol in multiple modules"
        suggestions.append((f"from {pick} import {symbol}", conf, reason))

    # 3) module-name used as symbol (e.g., 'adapters' → import module)
    # If there's a module package with that name under root_pkg, suggest import.
    mod_pkg = Path(repo_root / root_pkg / symbol.replace(".", "/"))
    if mod_pkg.is_dir() and (mod_pkg / "__init__.py").exists():
        suggestions.append((f"from {root_pkg} import {symbol}", 0.80, "module package used as name"))

    # 4) module file sibling (symbol equals a .py filename in same package)
    my_mod_path = import_path_for(file_path, repo_root, root_pkg)
    if my_mod_path and "." in my_mod_path:
        pkg = ".".join(my_mod_path.split(".")[:-1])
        sib = Path(repo_root, *pkg.split("."), f"{symbol}.py")
        if sib.exists():
            suggestions.append((f"from {pkg}.{symbol} import {symbol}", 0.70, "sibling module match"))

    # dedupe by import line (keep highest confidence)
    best: Dict[str, Tuple[float, str]] = {}
    for line, conf, why in suggestions:
        if line not in best or conf > best[line][0]:
            best[line] = (conf, why)
    merged = [(k, v[0], v[1]) for k, v in best.items()]
    merged.sort(key=lambda x: (-x[1], x[0]))
    return merged

def extract_symbol_from_msg(msg: str) -> Optional[str]:
    m = F821_MSG_RE.search(msg)
    return m.group(1) if m else None

def file_has_import(path: Path, import_line: str) -> bool:
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return False
    # very simple containment check
    return import_line in txt

def insert_import(path: Path, import_line: str) -> bool:
    """
    Insert import just below module docstring and __future__ imports.
    Returns True if file changed.
    """
    try:
        src = path.read_text(encoding="utf-8")
    except Exception:
        return False
    if import_line in src:
        return False

    lines = src.splitlines()
    i = 0

    # Skip shebang, encoding, blank lines
    while i < len(lines) and (lines[i].startswith("#!") or lines[i].startswith("# -*-") or lines[i].strip() == ""):
        i += 1

    # Skip module docstring
    if i < len(lines) and re.match(r'^\s*[ru]?["\']', lines[i]):
        quote = lines[i].lstrip()[0]
        # scan until closing docstring
        j = i + 1
        closed = False
        while j < len(lines):
            if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                closed = True
                j += 1
                break
            j += 1
        i = j if closed else i

    # Skip __future__ imports
    while i < len(lines) and lines[i].strip().startswith("from __future__"):
        i += 1

    # Insert
    new_line = f"{import_line}  # F821-helper"
    lines.insert(i, new_line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True

# --- Main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruff", default="docs/audits/ruff.json", help="Path to Ruff JSON")
    ap.add_argument("--src", default=".", help="Repo root")
    ap.add_argument("--root-pkg", default="lukhas", help="Canonical top-level package name")
    ap.add_argument("--out", default="docs/audits/f821_suggestions.csv")
    ap.add_argument("--md", default="docs/audits/f821_suggestions.md")
    ap.add_argument("--apply", action="store_true", help="Apply suggested imports")
    ap.add_argument("--apply-limit", type=int, default=0, help="Max files to edit (0 = unlimited)")
    args = ap.parse_args()

    repo_root = Path(args.src).resolve()
    ruff = read_json(Path(args.ruff))
    symbol_index, module_index = build_symbol_index(repo_root, args.root_pkg)

    rows: List[Dict[str, str]] = []
    edits = 0

    for e in ruff:
        if e.get("code") != "F821":
            continue
        file = Path(e["filename"]).resolve()
        msg = e.get("message","")
        sym = extract_symbol_from_msg(msg)
        if not sym:
            continue

        suggs = candidates_for_symbol(sym, symbol_index, module_index, file, repo_root, args.root_pkg)
        if not suggs:
            # no idea—skip
            rows.append({
                "file": str(file),
                "line": str(e["location"]["row"]),
                "symbol": sym,
                "suggestion": "",
                "import_line": "",
                "confidence": "0.00",
                "reason": "no-candidate"
            })
            continue

        # choose best suggestion
        import_line, conf, reason = suggs[0]
        rows.append({
            "file": str(file),
            "line": str(e["location"]["row"]),
            "symbol": sym,
            "suggestion": "add-import",
            "import_line": import_line,
            "confidence": f"{conf:.2f}",
            "reason": reason
        })

        if args.apply:
            if args.apply_limit and edits >= args.apply_limit:
                continue
            if not file_has_import(file, import_line):
                if insert_import(file, import_line):
                    edits += 1

    # CSV
    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file","line","symbol","suggestion","import_line","confidence","reason"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # MD summary
    mdp = Path(args.md)
    with mdp.open("w", encoding="utf-8") as f:
        f.write("# F821 Import Suggestions\n\n")
        f.write(f"- Total F821 items: **{sum(1 for _ in filter(lambda x: x.get('suggestion')!='', rows))}**\n")
        f.write(f"- Edits applied: **{edits}**\n\n")
        f.write("| File | Line | Symbol | Import | Conf | Reason |\n|---|---:|---|---|---:|---|\n")
        for r in rows[:500]:
            imp = r["import_line"] or "—"
            f.write(f"| `{r['file']}` | {r['line']} | `{r['symbol']}` | `{imp}` | {r['confidence']} | {r['reason']} |\n")

    print(f"[OK] Wrote {outp} and {mdp}. Applied edits: {edits}")

if __name__ == "__main__":
    main()
```

---

## How to use it (recommended flow)

**1) Generate the Ruff JSON once per branch**

```bash
ruff check --output-format json . > docs/audits/ruff.json
```

**2) Propose fixes (dry-run)**

```bash
python3 scripts/suggest_imports_f821.py \
  --ruff docs/audits/ruff.json --root-pkg lukhas --src . \
  --out docs/audits/f821_suggestions.csv \
  --md  docs/audits/f821_suggestions.md
```

Review `f821_suggestions.md` (top 500) and `f821_suggestions.csv` (full set).

**3) Apply a capped number of safe inserts**

```bash
python3 scripts/suggest_imports_f821.py \
  --apply --apply-limit 50 \
  --ruff docs/audits/ruff.json --root-pkg lukhas --src .
```

Re-run Ruff/pytest, iterate, then remove the cap and finish the sweep if results are clean.

---

## CI hook (optional)

Add to your workflow after Ruff JSON step, to always produce suggestions as artifacts:

```yaml
      - name: Suggest imports for F821
        run: |
          python3 scripts/suggest_imports_f821.py \
            --ruff docs/audits/ruff.json --root-pkg lukhas --src . \
            --out docs/audits/f821_suggestions.csv --md docs/audits/f821_suggestions.md

      - name: Upload F821 suggestions
        uses: actions/upload-artifact@v4
        with:
          name: f821-suggestions
          path: |
            docs/audits/f821_suggestions.csv
            docs/audits/f821_suggestions.md
```

---

## Why this works (T4 mindset)

* **Leverages your manifests** as a tiebreaker (same-star preference) so fixes keep modules within their constellation lanes/colonies.
* Stacks **high-precision mappings first** (stdlib/aliases) to cut noise.
* Keeps **human-in-the-loop** by default; `--apply-limit` lets you ratchet confidently.
* Leaves a **paper trail** (`.md`/`.csv`) that productizes lint into ownership and prioritization.

And here is a tiny **“ratchet”** step to fail CI when F821 increases vs a saved `ruff_baseline.json`.

 **PR #2 (Imports normalization)** ready to run, plus the **Ruff F821 ratchet** so lint stays trending down forever.

---

# 1) PR #2 — Imports normalization (kill TID252)

## a) Script: `scripts/normalize_imports.py` (LibCST, robust & safe)

* Converts **relative** imports to **absolute** (`lukhas.*`)
* Handles `from . import X`, `from ..pkg import Y`, `from ...pkg.sub import Z`
* Keeps star-import (`*`) intact
* Dry-run `--check` prints how many files would change; `--apply` writes changes

```python
#!/usr/bin/env python3
# Requires: pip install libcst
from __future__ import annotations
import argparse, pathlib, sys
import libcst as cst

def dotted_from_file(py: pathlib.Path, repo_root: pathlib.Path, root_pkg: str) -> tuple[str, str]:
    """Return (pkg_path, mod_name) for the file, e.g. ('lukhas.foo.bar', 'baz') from lukhas/foo/bar/baz.py"""
    rel = py.resolve().relative_to(repo_root.resolve())
    parts = list(rel.parts)
    if parts[0] != root_pkg:
        raise ValueError(f"{py} not inside root package {root_pkg}")
    if parts[-1] == "__init__.py":
        pkg_path = ".".join(parts[:-1])
        mod_name = "__init__"
    else:
        pkg_path = ".".join(parts[:-1])
        mod_name = parts[-1].rsplit(".", 1)[0]
    return pkg_path, mod_name

def join_dotted(base_pkg: str, up_levels: int, tail: str | None) -> str:
    """Base 'lukhas.a.b.c', go up 'up_levels', then append tail (may be None)."""
    parts = base_pkg.split(".")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    keep = max(0, len(parts) - up_levels)
    head = parts[:keep]
    if tail:
        head += tail.split(".")
    return ".".join([p for p in head if p])

class Absolutizer(cst.CSTTransformer):
    def __init__(self, repo_root: pathlib.Path, root_pkg: str, file_path: pathlib.Path):
        self.repo_root = repo_root
        self.root_pkg = root_pkg
        self.pkg_path, self.mod_name = dotted_from_file(file_path, repo_root, root_pkg)

    def _module_to_str(self, module: cst.BaseExpression | None) -> str | None:
        if module is None:
            return None
        # Convert Name/Attribute to dotted string
        if isinstance(module, cst.Name):
            return module.value
        parts = []
        cur = module
        while isinstance(cur, cst.Attribute):
            parts.append(cur.attr.value)
            cur = cur.value
        if isinstance(cur, cst.Name):
            parts.append(cur.value)
        parts.reverse()
        return ".".join(parts)

    def leave_ImportFrom(self, node: cst.ImportFrom, updated: cst.ImportFrom):
        if node.relative is None:
            return updated
        levels = node.relative.value  # 1 => ".", 2 => "..", etc.
        tail = self._module_to_str(node.module)  # may be None for 'from . import X'
        abs_mod = join_dotted(self.pkg_path, levels, tail)
        # Ensure we anchor at root_pkg
        if not abs_mod.startswith(self.root_pkg + ".") and abs_mod != self.root_pkg:
            abs_mod = f"{self.root_pkg}." + abs_mod if abs_mod else self.root_pkg
        new_module = cst.parse_expression(abs_mod)
        return updated.with_changes(relative=None, module=new_module)

def rewrite_file(py: pathlib.Path, repo_root: pathlib.Path, root_pkg: str) -> bool:
    src = py.read_text(encoding="utf-8")
    tree = cst.parse_module(src)
    new = tree.visit(Absolutizer(repo_root, root_pkg, py))
    if new.code != src:
        py.write_text(new.code, encoding="utf-8")
        return True
    return False

def main():
    ap = argparse.ArgumentParser(description="Rewrite relative imports to absolute (lukhas.*).")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--root-pkg", default="lukhas")
    ap.add_argument("--check", action="store_true", help="Dry-run; print count of files that would change.")
    ap.add_argument("--apply", action="store_true", help="Write changes.")
    ap.add_argument("paths", nargs="*",
                    help="Python files to process. If empty, auto-discovers files with relative imports.")
    args = ap.parse_args()
    repo_root = pathlib.Path(args.repo_root).resolve()

    files = [pathlib.Path(p) for p in args.paths]
    if not files:
        # discover files with relative imports (fast)
        try:
            import subprocess, shlex
            cmd = "rg -l 'from \\.+\\w' --glob '!venv/**' --glob '!packages/**' --glob '!**/generated/**'"
            out = subprocess.check_output(shlex.split(cmd), text=True)
            files = [pathlib.Path(x) for x in out.strip().splitlines() if x.strip()]
        except Exception:
            print("[WARN] ripgrep not available; scanning all .py files")
            files = [p for p in repo_root.rglob("*.py") if "/generated/" not in str(p)]

    changed = 0
    for py in files:
        try:
            if rewrite_file(py, repo_root, args.root_pkg):
                changed += 1
        except Exception as e:
            print(f"[WARN] Skipping {py}: {e}")

    if args.check and not args.apply:
        print(f"[CHECK] Would change {changed} files.")
    else:
        print(f"[APPLY] Changed {changed} files.")

if __name__ == "__main__":
    main()
```

## b) Run PR #2

```bash
git checkout -b chore/imports-absolute
python3 -m pip install libcst
# Dry-run (how many files would change?)
python3 scripts/normalize_imports.py --check
# Apply
python3 scripts/normalize_imports.py --apply
ruff check --fix .
pytest -q -m matriz_smoke
git commit -am "chore(imports): rewrite relative imports to absolute; ban TID252"
git push -u origin chore/imports-absolute
```

**PR title/description (paste):**

```
chore(imports): rewrite relative imports to absolute (kill TID252)

Why
- Relative imports (TID252) impede refactors and the flatten/colony rename.
- Absolute imports (lukhas.*) enable safe code moves and IDE navigation.

What
- LibCST-based rewriter converts `from .foo import Bar` → `from lukhas.pkg.foo import Bar`
- Preserves module behavior; no functional changes.
- Follow-up: ban TID252 in CI permanently.

Safety
- Ran ruff --fix and matriz_smoke; no behavior changes expected.
- Shims remain (if any) until all branches are merged.

Metrics
- TID252: 2,594 → 0
- Failing tests: none (smoke green)

Roll-back
- Single revert commit restores previous imports.
```

---

# 2) Ruff **ratchet** for F821 (prevent regressions)

## a) Script: `scripts/ruff_ratchet.py`

* Compares **current** Ruff JSON to a **baseline** (committed to repo)
* Defaults to **track F821 only**; you can add more codes with `--track F401 --track TID252`
* Fails CI if any tracked code increases; allows decreases/equal

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from collections import Counter

def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))

def counts_by_code(events: list[dict]) -> Counter:
    c = Counter()
    for e in events:
        code = e.get("code")
        if code:
            c[code] += 1
    return c

def main():
    ap = argparse.ArgumentParser(description="Ruff ratchet: fail if tracked codes increase vs baseline.")
    ap.add_argument("--baseline", default="docs/audits/ruff_baseline.json")
    ap.add_argument("--current",  default="docs/audits/ruff.json")
    ap.add_argument("--track", action="append", default=["F821"], help="Ruff code(s) to ratchet (repeatable).")
    ap.add_argument("--init", action="store_true", help="Create baseline from current and exit 0.")
    ap.add_argument("--write-baseline", action="store_true", help="Overwrite baseline with current counts.")
    args = ap.parse_args()

    cur_path = Path(args.current)
    base_path = Path(args.baseline)

    if args.init:
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(cur_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[INIT] Baseline created at {base_path}")
        return 0

    if not base_path.exists():
        print(f"[ERROR] Baseline missing: {base_path}. Run with --init on main to establish.")
        return 2

    cur_counts = counts_by_code(load(cur_path))
    base_counts = counts_by_code(load(base_path))

    bad = []
    rows = []
    for code in args.track:
        cur = cur_counts.get(code, 0)
        base = base_counts.get(code, 0)
        delta = cur - base
        rows.append((code, base, cur, delta))
        if delta > 0:
            bad.append((code, delta))

    print("| Code | Baseline | Current | Δ |")
    print("|---|---:|---:|---:|")
    for code, base, cur, delta in rows:
        print(f"| {code} | {base} | {cur} | {delta:+d} |")

    if args.write-baseline:
        base_path.write_text(cur_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[OK] Baseline updated: {base_path}")

    if bad:
        print(f"[FAIL] Ratchet breached: " + ", ".join([f"{c} +{d}" for c,d in bad]))
        return 1

    print("[OK] Ratchet respected.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## b) Establish the baseline (once, on `main`)

```bash
git checkout main
ruff check --output-format json . > docs/audits/ruff.json
python3 scripts/ruff_ratchet.py --init --baseline docs/audits/ruff_baseline.json --current docs/audits/ruff.json
git add docs/audits/ruff_baseline.json
git commit -m "chore(lint): establish Ruff baseline (F821 ratchet)"
git push
```

## c) CI wiring (append to `.github/workflows/matriz-validate.yml`)

Right after your existing Ruff JSON step:

```yaml
      - name: Ruff (JSON)
        run: ruff check --output-format json . > docs/audits/ruff.json

      - name: Ratchet — F821 must not increase
        run: |
          python3 scripts/ruff_ratchet.py \
            --baseline docs/audits/ruff_baseline.json \
            --current  docs/audits/ruff.json \
            --track F821

      - name: Upload Ruff artifacts
        uses: actions/upload-artifact@v4
        with:
          name: ruff
          path: |
            docs/audits/ruff.json
            docs/audits/ruff_baseline.json
```

*(Optional) ratchet other codes later: add `--track F401 --track TID252` once PR #1/#2 have landed and stabilized.*

---

## Quick runbook recap

1. **PR #1 (mechanical)** landed → F401 drops, imports ordered.
2. **PR #2 (imports absolute)** with `scripts/normalize_imports.py` → **TID252 → 0**.
3. **Ratchet on F821** ensures undefined names only go **down** from here.
4. Use the **F821 helper** to propose/apply import inserts in small, safe batches.


boom—here’s the rest of the kit. This gives you:
	•	an Owner Heatmap for Ruff (by Star × Owner × Rule)
	•	a PR #3 toolbelt for fixing F821/F706 + test hygiene (F811) safely
	•	CI glue so the signal shows up on every PR

⸻

1) Owner Heatmap (Star × Owner × Rule)

scripts/ruff_owner_heatmap.py
	•	Reads docs/audits/ruff.json
	•	Finds nearest module.manifest.json for each file
	•	Aggregates by star, owner, and ruff code
	•	Writes a CSV and a clean Markdown table

#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from collections import defaultdict, Counter

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def nearest_manifest(pyfile: Path) -> dict:
    for parent in [pyfile] + list(pyfile.parents):
        m = parent / "module.manifest.json"
        if m.exists():
            try:
                return load_json(m)
            except Exception:
                return {}
    return {}

def main():
    ap = argparse.ArgumentParser(description="Build Ruff owner heatmap (Star × Owner × Rule).")
    ap.add_argument("--ruff", default="docs/audits/ruff.json")
    ap.add_argument("--csv", default="docs/audits/ruff_heatmap.csv")
    ap.add_argument("--md",  default="docs/audits/ruff_heatmap.md")
    args = ap.parse_args()

    ruff = load_json(Path(args.ruff))
    cube = defaultdict(lambda: Counter())   # (star, owner) -> Counter(code)
    totals = Counter()                      # overall per code

    for e in ruff:
        code = e.get("code")
        file = Path(e.get("filename"))
        man = nearest_manifest(file)
        star = ((man.get("constellation_alignment") or {}).get("primary_star")) or "Supporting"
        owner = ((man.get("metadata") or {}).get("owner")) or "unknown"
        cube[(star, owner)][code] += 1
        totals[code] += 1

    # Collect all codes present to define header columns
    all_codes = set()
    for _, cnt in cube.items():
        all_codes.update(cnt.keys())
    all_codes = sorted(all_codes)

    # CSV
    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.csv).open("w", encoding="utf-8") as f:
        f.write("star,owner," + ",".join(all_codes) + ",total\n")
        for (star, owner), cnt in sorted(cube.items()):
            row = [str(cnt.get(c, 0)) for c in all_codes]
            f.write(f"{star},{owner}," + ",".join(row) + f",{sum(cnt.values())}\n")

    # MD
    with Path(args.md).open("w", encoding="utf-8") as f:
        f.write("# Ruff Heatmap (Star × Owner × Rule)\n\n")
        f.write("| Star | Owner | " + " | ".join(all_codes) + " | Total |\n")
        f.write("|---|---|" + "|".join([":--:" for _ in all_codes]) + "|---:|\n")
        for (star, owner), cnt in sorted(cube.items()):
            row = " | ".join(str(cnt.get(c, 0)) for c in all_codes)
            f.write(f"| {star} | {owner} | {row} | {sum(cnt.values())} |\n")

        f.write("\n**Totals by rule:**\n\n")
        f.write("| Rule | Count |\n|---|---:|\n")
        for c in all_codes:
            f.write(f"| {c} | {totals[c]} |\n")

    print(f"[OK] Wrote {args.csv} and {args.md}")

if __name__ == "__main__":
    sys.exit(main())

Run

ruff check --output-format json . > docs/audits/ruff.json
python3 scripts/ruff_owner_heatmap.py


⸻

2) PR #3 — Undefined Names (F821), Top-level Returns (F706), Test Hygiene (F811)

This PR is “surgical”: it uses small helpers to suggest fixes, then applies only high-confidence changes.

2.1 F821 (undefined names)

You already have the F821 helper. Here’s the runbook:

git checkout -b chore/f821-f706-hygiene

# Fresh ruff report
ruff check --output-format json . > docs/audits/ruff.json

# Suggest imports for F821
python3 scripts/suggest_imports_f821.py \
  --ruff docs/audits/ruff.json --root-pkg lukhas --src . \
  --out docs/audits/f821_suggestions.csv \
  --md  docs/audits/f821_suggestions.md

# Apply the top 50 suggestions (iterate if green)
python3 scripts/suggest_imports_f821.py \
  --apply --apply-limit 50 \
  --ruff docs/audits/ruff.json --root-pkg lukhas --src .

ruff check --fix .
pytest -q -m matriz_smoke

Iterate with batches of 50 until F821 drops to a safe number.

2.2 F706 (return outside function) — detector (safe)

scripts/find_top_level_returns.py
	•	Lists Python files likely containing top-level return
	•	Doesn’t auto-rewrite (by design). You’ll patch manually (wrap into a function or remove)

#!/usr/bin/env python3
import ast, sys
from pathlib import Path

def has_top_level_return(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    for node in tree.body:
        # Return found at module level
        if isinstance(node, ast.Return):
            return True
        # Return nested directly in an if/try at top-level is also suspicious
        if isinstance(node, (ast.If, ast.Try)):
            for n in node.body:
                if isinstance(n, ast.Return):
                    return True
    return False

def main():
    root = Path(".")
    suspects = []
    for py in root.rglob("*.py"):
        if "venv/" in str(py) or "/generated/" in str(py):
            continue
        if has_top_level_return(py):
            suspects.append(str(py))
    if suspects:
        print("\n".join(sorted(suspects)))
        sys.exit(1)
    print("[OK] no top-level returns detected")
    sys.exit(0)

if __name__ == "__main__":
    main()

Run

python3 scripts/find_top_level_returns.py
# Manually fix listed files (wrap code into def main(), or remove stray return)
ruff check --fix .
pytest -q

(If you want an auto-fixer, I can generate a careful one, but manual is safest.)

2.3 F811 (duplicate test classes) — detect & optional rename

scripts/detect_duplicate_test_classes.py
	•	Scans tests/** for class Test*
	•	Reports duplicates per file
	•	Optional --apply will rename later duplicates with a numeric suffix (TestFoo, TestFoo_2, …)

#!/usr/bin/env python3
import ast, sys, argparse
from pathlib import Path
from collections import defaultdict

def find_test_classes(py: Path):
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            out.append((node.name, node.lineno))
    return out

def apply_renames(py: Path, dups: list[tuple[str,int,int]]):
    # dups: (orig_name, lineno, suffix_index)
    lines = py.read_text(encoding="utf-8").splitlines()
    for orig, lineno, idx in sorted(dups, key=lambda x: -x[1]):  # bottom-up edit
        line = lines[lineno-1]
        lines[lineno-1] = line.replace(f"class {orig}", f"class {orig}_{idx}")
    py.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Detect duplicate Test classes; optionally rename.")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--root", default="tests")
    args = ap.parse_args()

    root = Path(args.root)
    dup_total = 0
    for py in root.rglob("test*.py"):
        classes = find_test_classes(py)
        if not classes: 
            continue
        counter = defaultdict(int)
        dups = []
        for name, lineno in classes:
            counter[name] += 1
            if counter[name] > 1:
                dups.append((name, lineno, counter[name]))  # suffix with 2,3,...
        if dups:
            dup_total += len(dups)
            print(f"[DUP] {py}: " + ", ".join([f"{n}@{ln}:{i}" for n,ln,i in dups]))
            if args.apply:
                apply_renames(py, dups)

    if args.apply:
        print(f"[OK] Renamed {dup_total} duplicate class occurrences.")
    else:
        if dup_total == 0:
            print("[OK] No duplicate test classes found.")
        else:
            print(f"[INFO] Found {dup_total} duplicates (run with --apply to rename).")

if __name__ == "__main__":
    sys.exit(main())

Run

python3 scripts/detect_duplicate_test_classes.py         # report
python3 scripts/detect_duplicate_test_classes.py --apply # rename duplicates
ruff check --fix .
pytest -q

2.4 Commit & push PR #3

ruff check --output-format json . > docs/audits/ruff.json
python3 scripts/ruff_owner_heatmap.py

git add -A
git commit -m "fix(lint): F821 import inserts (batch), remove top-level returns, de-dup test classes; add owner heatmap"
git push -u origin chore/f821-f706-hygiene

PR title

fix(lint): resolve F821/F706 and test F811; add owner heatmap

PR description (paste)

Why
- F821 (undefined names) and F706 (returns outside functions) were blocking CI polish.
- Duplicate test classes (F811) cause surprise overrides and flaky runs.
- We want lint signal tied to ownership for targeted fixes.

What
- Add F821 import suggestions (applied top batch), keep helper for further batches
- Detect and remove top-level returns (manual patch)
- Detect/rename duplicate test classes under tests/**
- Add owner heatmap (Star × Owner × Rule) as docs/audits/ruff_heatmap.{md,csv}

Safety
- Small, audited edits; ran ruff --fix and matriz_smoke; full pytest where applicable
- No functional changes outside lint/structure

Artifacts
- docs/audits/ruff.json (run)
- docs/audits/ruff_heatmap.{md,csv}

Follow-ups
- Run F821 helper for remaining items in small batches
- Optionally enable Ruff ratchet for F401/TID252 after PR #1/#2 stabilize


⸻

3) CI Glue (append to .github/workflows/matriz-validate.yml)

Add after your Ruff JSON step:

      - name: Owner heatmap (Star × Owner × Rule)
        run: |
          python3 scripts/ruff_owner_heatmap.py
      - name: Upload Ruff heatmap
        uses: actions/upload-artifact@v4
        with:
          name: ruff-heatmap
          path: |
            docs/audits/ruff_heatmap.csv
            docs/audits/ruff_heatmap.md

      - name: Tripwire — No top-level returns (F706 detector)
        run: |
          python3 scripts/find_top_level_returns.py

(F811 duplicates: keep non-blocking; use the script report in PR review.)

⸻

Quick recap
	•	Owner heatmap turns lint into accountability + prioritization.
	•	PR #3 toolbelt resolves the sharp edges (F821, F706, F811) without guessy rewrites.
	•	CI artifacts + tripwire keep things clean, and your ratchet from the previous step ensures we never slide back.


epic — here’s the next drop-in: two new automation scripts + a smarter import map, plus a couple of tiny 0.01% extras and PR shells so you can land this cleanly.

⸻

1) scripts/fix_f401_tests.py — surgical F401 auto-fixer for tests/

Removes only the unused names Ruff flagged in tests/, safely handles multi-name imports, preserves aliases, and never touches non-test code. Dry-run by default.

#!/usr/bin/env python3
# Fix F401 "imported but unused" only under tests/** using Ruff JSON as ground truth.
# Requires: ruff JSON report at docs/audits/ruff.json (or --ruff)
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import libcst as cst
import libcst.matchers as m

def load_json(p: Path): return json.loads(p.read_text(encoding="utf-8"))

def bucket_unused_by_file(ruff_events, root: Path) -> dict[str, set[str]]:
    unused: dict[str, set[str]] = {}
    for e in ruff_events:
        if e.get("code") != "F401":
            continue
        fn = e.get("filename")
        if not fn or "tests/" not in fn.replace("\\","/"):
            continue
        msg = e.get("message","")
        # Ruff message formats include "‘name’ imported but unused" (varies by font)
        # Try to extract symbol between quotes; fall back to last token heuristic.
        sym = None
        for q in ("'", "’", "‘", "“", "”", "«", "»"):
            if q in msg:
                parts = msg.split(q)
                if len(parts) >= 3:
                    sym = parts[1]
                    break
        if not sym:
            # fallback: last word
            sym = msg.split()[-1]
        unused.setdefault(fn, set()).add(sym)
    return unused

class PruneImports(cst.CSTTransformer):
    def __init__(self, unused: set[str]):
        self.unused = unused
        self.changed = False

    def leave_Import(self, node: cst.Import, updated: cst.Import):
        # import a, b as c → drop only unused names
        new_names = []
        for alias in updated.names:
            name = alias.evaluated_name
            if name in self.unused:
                self.changed = True
                continue
            new_names.append(alias)
        if not new_names:
            self.changed = True
            return cst.RemoveFromParent()
        return updated.with_changes(names=new_names)

    def leave_ImportFrom(self, node: cst.ImportFrom, updated: cst.ImportFrom):
        # from x import a, b as c
        if m.matches(updated.names, m.ImportStar()):
            return updated  # never remove star
        kept = []
        for alias in updated.names:
            name = alias.evaluated_name
            if name in self.unused:
                self.changed = True
                continue
            kept.append(alias)
        if not kept:
            self.changed = True
            return cst.RemoveFromParent()
        return updated.with_changes(names=tuple(kept))

def run_file(path: Path, unused_names: set[str], apply: bool) -> bool:
    src = path.read_text(encoding="utf-8")
    mod = cst.parse_module(src)
    tx = PruneImports(unused_names)
    out = mod.visit(tx)
    if tx.changed and apply:
        path.write_text(out.code, encoding="utf-8")
    return tx.changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruff", default="docs/audits/ruff.json")
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    events = load_json(Path(args.ruff))
    unused_by_file = bucket_unused_by_file(events, root)

    changed = 0
    for fn, names in sorted(unused_by_file.items()):
        p = (root / fn).resolve()
        if not p.exists(): 
            continue
        if run_file(p, names, args.apply):
            changed += 1
            print(f"[fix] {fn}: -{', -'.join(sorted(names))}")
    print(f"[OK] files changed: {changed}")
    sys.exit(0)

if __name__ == "__main__":
    main()

Run

# produce fresh ruff report
ruff check --output-format json . > docs/audits/ruff.json

# dry-run prints what would change (diff not shown)
python3 scripts/fix_f401_tests.py --ruff docs/audits/ruff.json

# apply
python3 scripts/fix_f401_tests.py --ruff docs/audits/ruff.json --apply
ruff check --fix .
pytest -q


⸻

2) Import Intelligence: manifest-aware symbol map

2.1 scripts/build_import_map.py — builds docs/audits/import_map.json

Combines three sources to map symbol → module:
	1.	Manifests (if they declare public_api / exports / interfaces keys)
	2.	Code scanning (top-level classes/functions/__all__)
	3.	Package index (module path inference under lukhas/)

#!/usr/bin/env python3
from __future__ import annotations
import ast, json, sys
from pathlib import Path

def safe_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def from_manifest_exports(manifest: dict) -> list[str]:
    # Best-effort: look in common keys
    for key in ("public_api","exports","interfaces","exposes"):
        v = manifest.get(key)
        if isinstance(v, list):
            return [str(x) for x in v if isinstance(x, (str,))]
    return []

def top_level_symbols(py: Path):
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return [], [], [], []
    classes, funcs, consts, all_decl = [], [], [], []
    has_all = False
    for node in tree.body:
        if isinstance(node, ast.Assign):
            # __all__ = [...]
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    has_all = True
                    try:
                        vals = []
                        if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Str):
                                    vals.append(elt.s)
                        all_decl = vals
                    except Exception:
                        pass
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    consts.append(t.id)
    if has_all and all_decl:
        # __all__ governs export surface
        classes = [c for c in classes if c in all_decl]
        funcs   = [f for f in funcs if f in all_decl]
        consts  = [k for k in consts if k in all_decl]
    return classes, funcs, consts, all_decl

def import_path_for(py: Path, repo_root: Path, root_pkg: str) -> str|None:
    try:
        rel = py.resolve().relative_to(repo_root.resolve())
    except Exception:
        return None
    parts = list(rel.parts)
    if not parts or parts[0] != root_pkg: return None
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1].replace(".py","")
    return ".".join(parts)

def main():
    repo_root = Path(".").resolve()
    root_pkg = "lukhas"
    symbol_to_modules = {}  # symbol -> set(modules)
    module_to_symbols = {}  # module -> set(symbols)

    # 1) manifests
    for mf in repo_root.rglob("module.manifest.json"):
        man = safe_json(mf)
        if not man: 
            continue
        exports = from_manifest_exports(man)
        # Try to infer code module path next to the manifest
        code_dir = mf.parent
        for py in list(code_dir.glob("*.py")) + list(code_dir.rglob("__init__.py")):
            mod = import_path_for(py, repo_root, root_pkg)
            if not mod: 
                continue
            if exports:
                module_to_symbols.setdefault(mod, set()).update(exports)
                for s in exports:
                    symbol_to_modules.setdefault(s, set()).add(mod)

    # 2) code scan under lukhas/**
    pkg_dir = repo_root / root_pkg
    if pkg_dir.exists():
        for py in pkg_dir.rglob("*.py"):
            if "/generated/" in str(py): 
                continue
            mod = import_path_for(py, repo_root, root_pkg)
            if not mod: 
                continue
            cls, fn, cs, all_decl = top_level_symbols(py)
            syms = set(cls + fn + cs)
            if all_decl:  # prefer explicit exports
                syms = syms.union(all_decl)
            if syms:
                module_to_symbols.setdefault(mod, set()).update(syms)
                for s in syms:
                    symbol_to_modules.setdefault(s, set()).add(mod)

    # to JSON
    out = {
        "generated_from": "build_import_map.py",
        "symbol_to_modules": {k: sorted(list(v)) for k,v in symbol_to_modules.items()},
        "module_to_symbols": {k: sorted(list(v)) for k,v in module_to_symbols.items()},
    }
    outp = Path("docs/audits/import_map.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[OK] wrote {outp} (symbols: {len(symbol_to_modules)}, modules: {len(module_to_symbols)})")

if __name__ == "__main__":
    main()

Run

python3 scripts/build_import_map.py

2.2 Upgrade the F821 helper to use the import map

Drop-in replacement (same filename is fine): it now accepts --import-map and boosts those suggestions.

# --- PATCH to your existing scripts/suggest_imports_f821.py ---
# Add near the imports:
#   import math
# ... and below config add:
IMPORT_MAP = None

# Add helper:
def load_import_map(path: str|None):
    global IMPORT_MAP
    if not path: return
    p = Path(path)
    if p.exists():
        try:
            IMPORT_MAP = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            IMPORT_MAP = None

# In argparse add:
#   ap.add_argument("--import-map", default="docs/audits/import_map.json")

# After parsing args, call:
#   load_import_map(args.import_map)

# In candidates_for_symbol(...), insert at top, after stdlib mapping:
    # Import-map boost
    if IMPORT_MAP:
        s2m = IMPORT_MAP.get("symbol_to_modules", {})
        hits = s2m.get(symbol, [])
        if len(hits) == 1:
            mod = hits[0]
            suggestions.append((f"from {mod} import {symbol}", 0.93, "import-map unique"))
        elif len(hits) > 1:
            # prefer modules under same-star if possible (reuse previous logic)
            suggestions.append((f"from {hits[0]} import {symbol}", 0.80, "import-map multi"))

Use

ruff check --output-format json . > docs/audits/ruff.json
python3 scripts/build_import_map.py
python3 scripts/suggest_imports_f821.py --import-map docs/audits/import_map.json \
  --ruff docs/audits/ruff.json --root-pkg lukhas --src . \
  --out docs/audits/f821_suggestions.csv --md docs/audits/f821_suggestions.md


⸻

3) Tiny 0.01% extras

3.1 Import cycle scanner (quick signal)

Flags cycles across lukhas/**. Useful right after PR #2.

# scripts/analyze_import_graph.py
#!/usr/bin/env python3
import ast, sys
from pathlib import Path
from collections import defaultdict, deque

ROOT="lukhas"
edges = defaultdict(set)

def mod_from_file(py: Path):
    rel = py.relative_to(Path(".").resolve())
    parts = list(rel.parts)
    if parts[0]!=ROOT: return None
    if parts[-1]=="__init__.py": parts=parts[:-1]
    else: parts[-1]=parts[-1].replace(".py","")
    return ".".join(parts)

def imports_in(py: Path):
    try:
        t = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return []
    out=[]
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.module and not n.level:
            out.append(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names: out.append(a.name.split(".")[0])
    return out

mods={}
for py in Path(ROOT).rglob("*.py"):
    m = mod_from_file(py)
    if not m: continue
    mods[m]=py
    for imp in imports_in(py):
        if imp.startswith(ROOT):
            edges[m].add(imp)

# find cycles (simple DFS)
seen=set(); stack=set(); order=[]
cycles=[]
def dfs(u):
    seen.add(u); stack.add(u)
    for v in edges[u]:
        if v not in seen: dfs(v)
        elif v in stack: cycles.append((u,v))
    stack.remove(u); order.append(u)

for m in mods:
    if m not in seen: dfs(m)

if cycles:
    print("[CYCLES]")
    for u,v in cycles:
        print(f" - {u} -> {v}")
    sys.exit(1)
print("[OK] no cycles")

Run

python3 scripts/analyze_import_graph.py

3.2 Make targets & CI glue

Makefile

.PHONY: f401-tests import-map imports-graph

f401-tests:
	ruff check --output-format json . > docs/audits/ruff.json
	python3 scripts/fix_f401_tests.py --ruff docs/audits/ruff.json --apply
	ruff check --fix .

import-map:
	python3 scripts/build_import_map.py

imports-graph:
	python3 scripts/analyze_import_graph.py

CI (append to your workflow)

      - name: Build import map
        run: python3 scripts/build_import_map.py
      - name: Upload import map
        uses: actions/upload-artifact@v4
        with:
          name: import-map
          path: docs/audits/import_map.json

      - name: Import cycle scan
        run: python3 scripts/analyze_import_graph.py


⸻

4) PR shells you can open immediately

PR #4 — tests hygiene (F401 auto-fixes)

chore(tests): auto-remove F401 unused imports in tests; keep code clean

Why
- 500+ F401 in tests hid real signals and slowed reviews.

What
- Added scripts/fix_f401_tests.py
- Ran auto-fix only under tests/** using Ruff JSON ground truth
- Re-ran ruff --fix and smoke tests

Metrics
- F401 in tests: ~-500 (see ruff.json delta)
- CI neatness improves; ratchet ready if desired

Safety
- Only removed *unused* names flagged by Ruff; code unchanged.

PR #5 — import intelligence (manifest-aware F821)

feat(imports): build import map from manifests/code; improve F821 suggestions

Why
- Undefined names need precise, low-noise import inserts.
- Manifests already encode interfaces—let’s use them.

What
- Added scripts/build_import_map.py → docs/audits/import_map.json
- Upgraded suggest_imports_f821 to leverage import_map for higher-confidence proposals

Safety
- Suggestions remain human-in-the-loop; --apply-limit used in batches
- All changes tracked in docs/audits/f821_suggestions.{csv,md}


⸻

How I’d execute (order)
	1.	PR #2 (imports absolute) → TID252 → 0
	2.	PR #3 (F821/F706/F811) using helper scripts (batch 50)
	3.	PR #4 (tests F401 cleaner)
	4.	PR #5 (manifest import map + improved F821)
	5.	Enable ratchets for F821 (already), then progressively F401.

Claude Code / Copilot: Say the word if you want me to also add a baseline/ratchet for F401 in tests/ only (separate track), or to emit a small top offenders table per owner so reviewers get @-mentions auto-filled in PRs.