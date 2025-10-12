#!/usr/bin/env python3
"""
Codemod legacy imports to canonical lukhas.* paths using LibCST.

Dry-run by default: outputs docs/audits/codemod_preview.csv with proposed edits.
Use --apply to write changes in-place.

Examples:
  python3 scripts/codemod_imports.py --roots lukhas labs core MATRIZ tests packages tools
  python3 scripts/codemod_imports.py --apply --roots lukhas labs core MATRIZ tests packages tools

Config (optional):
  --config configs/legacy_imports.yml
"""
from __future__ import annotations
import argparse, csv, sys, re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import libcst as cst
    import libcst.matchers as m
except ImportError:
    print("[ERROR] libcst not installed. Run: pip install libcst", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("[ERROR] pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

DEFAULT_MAP = {
    "candidate": "labs",
    "tools": "lukhas.tools",
    "governance": "lukhas.governance",
    "memory": "lukhas.memory",
    "ledger": "lukhas.ledger",
    "lucas": "lukhas",
    "Lucas": "lukhas",
    "LUCAS": "lukhas",
}

ALLOWLIST_DEFAULT = {"lukhas/compat", "tests/conftest.py"}

PY_GLOB = "**/*.py"
EXCLUDE_DIRS = {".git","venv",".venv","node_modules","dist","build","__pycache__",
                ".mypy_cache",".ruff_cache",".pytest_cache",".tox",".idea",".vscode"}

def load_cfg(path: str|None):
    if not path:
        return DEFAULT_MAP, ALLOWLIST_DEFAULT
    p = Path(path)
    if not p.exists():
        return DEFAULT_MAP, ALLOWLIST_DEFAULT
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    mapping = data.get("map", {}) or {}
    allow = set(data.get("allowlist", []) or [])
    # merge defaults (cfg overrides default keys)
    merged = DEFAULT_MAP.copy()
    merged.update(mapping)
    return merged, allow or ALLOWLIST_DEFAULT

def root_ok(p: Path)->bool:
    for seg in p.parts:
        if seg in EXCLUDE_DIRS:
            return False
    return True

def rewrite_root(name: str, mapping: Dict[str,str]) -> str|None:
    # If name begins with any legacy root, replace that segment
    parts = name.split(".")
    if not parts:
        return None
    root = parts[0]
    if root in mapping:
        new_root = mapping[root]
        new_name = ".".join([new_root] + parts[1:])
        return new_name
    return None

class ImportRewriter(cst.CSTTransformer):
    def __init__(self, mapping: Dict[str,str]):
        self.mapping = mapping
        self.changes: List[Tuple[str,str]] = []  # (old, new)

    def leave_Import(self, original: cst.Import, updated: cst.Import) -> cst.Import:
        names = []
        changed = False
        for alias in updated.names:
            if m.matches(alias, m.ImportAlias(name=m.Attribute() | m.Name())):
                full = alias.name.code
                new = rewrite_root(full, self.mapping)
                if new and new != full:
                    names.append(alias.with_changes(name=cst.parse_expression(new)))
                    self.changes.append((full, new))
                    changed = True
                else:
                    names.append(alias)
            else:
                names.append(alias)
        return updated.with_changes(names=tuple(names)) if changed else updated

    def leave_ImportFrom(self, original: cst.ImportFrom, updated: cst.ImportFrom) -> cst.ImportFrom:
        # from X.Y import Z
        if updated.module is None:
            return updated
        full = updated.module.code
        new = rewrite_root(full, self.mapping)
        if new and new != full:
            self.changes.append((full, new))
            return updated.with_changes(module=cst.parse_expression(new))
        return updated

    def leave_SimpleString(self, original: cst.SimpleString, updated: cst.SimpleString):
        # Opportunistic: importlib.import_module("tools.scripts") literals
        text = original.evaluated_value
        if isinstance(text, str):
            new = None
            for legacy, canonical in self.mapping.items():
                # match at start of dotted path in string
                if re.match(rf"^{re.escape(legacy)}(\.|$)", text):
                    new = re.sub(rf"^{re.escape(legacy)}", canonical, text)
                    break
            if new and new != text:
                # preserve quoting
                quote = updated.value[0]
                body = new.replace("\\", "\\\\").replace(quote, f"\\{quote}")
                return updated.with_changes(value=f"{quote}{body}{quote}")
        return updated

def process_file(path: Path, mapping: Dict[str,str], apply: bool):
    src = path.read_text(encoding="utf-8", errors="ignore")
    try:
        mod = cst.parse_module(src)
    except Exception:
        return [], False  # skip unparsable
    tr = ImportRewriter(mapping)
    new_mod = mod.visit(tr)
    changed = bool(tr.changes)
    if changed and apply:
        path.write_text(new_mod.code, encoding="utf-8")
    return tr.changes, changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", default=["lukhas","labs","core","MATRIZ","tests","packages","tools"])
    ap.add_argument("--config", default="configs/legacy_imports.yml")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default="docs/audits/codemod_preview.csv")
    args = ap.parse_args()

    mapping, _allow = load_cfg(args.config)
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    changed_files = 0
    for root in args.roots:
        base = Path(root)
        if not base.exists():
            continue
        for p in base.rglob(PY_GLOB):
            if not root_ok(p):
                continue
            changes, changed = process_file(p, mapping, args.apply)
            if changes:
                changed_files += 1 if changed else 0
                for old, new in changes:
                    rows.append({"path": str(p), "from": old, "to": new})

    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path","from","to"])
        w.writeheader()
        w.writerows(rows)

    print(f"[codemod] wrote {outp} with {len(rows)} proposed edits"
          f"{' (APPLIED)' if args.apply else ' (DRY-RUN)'}")
    print(f"[codemod] files changed: {changed_files}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
