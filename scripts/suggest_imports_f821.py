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

import argparse
import ast
import contextlib
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

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
    for parent in [pyfile, *list(pyfile.parents)]:
        m = parent / "module.manifest.json"
        if m.exists():
            try:
                return read_json(m)
            except Exception:
                return {}
    return {}

def import_path_for(pyfile: Path, repo_root: Path, root_pkg: str) -> str | None:
    """
    Convert filesystem path to import path. E.g.
      /repo/lukhas/foo/bar.py -> foo.bar
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
                with contextlib.suppress(Exception):
                    star = (read_json(mf).get("constellation_alignment") or {}).get("primary_star") or ""
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

def extract_symbol_from_msg(msg: str) -> str | None:
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
        lines[i].lstrip()[0]
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
            # no idea-skip
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
            if not file_has_import(file, import_line) and insert_import(file, import_line):
                edits += 1

    # CSV
    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_scripts_suggest_imports_f821_py_L334"}
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
            imp = r["import_line"] or "-"
            f.write(f"| `{r['file']}` | {r['line']} | `{r['symbol']}` | `{imp}` | {r['confidence']} | {r['reason']} |\n")

    print(f"[OK] Wrote {outp} and {mdp}. Applied edits: {edits}")

if __name__ == "__main__":
    main()
