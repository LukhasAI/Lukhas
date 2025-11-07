#!/usr/bin/env python3
"""
Driver to run fix_b008 transformer over a code tree.

Usage:
  python3 tools/ci/codemods/run_fix_b008.py --root lukhas --dry-run
  python3 tools/ci/codemods/run_fix_b008.py --root lukhas --apply
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

try:
    import libcst as cst
    from tools.ci.codemods.fix_b008 import FixB008Transformer
except ImportError:
    print("Error: libcst not installed. Run: pip install libcst")
    sys.exit(1)

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
