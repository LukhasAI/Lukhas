#!/usr/bin/env python3
"""
LibCST-based fixer for boolean-name typos:
Replace bare Name('false') -> Name('False') and Name('true') -> Name('True').

Usage:
# Dry-run on files mentioned in /tmp/ruff_f821.json (auto-targeting)
python3 tools/ci/f821_fix_booleans.py --dry-run

# Or dry-run on explicit files
python3 tools/ci/f821_fix_booleans.py --dry-run --files file1.py file2.py

# Apply changes (backups saved)
python3 tools/ci/f821_fix_booleans.py --apply --files file1.py file2.py
"""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import libcst as cst


class BooleanTyposTransformer(cst.CSTTransformer):
    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        if original_node.value == "false":
            return cst.Name("False")
        if original_node.value == "true":
            return cst.Name("True")
        return updated_node


def run_on_file(path: Path, dry_run: bool = True):
    src = path.read_text()
    module = cst.parse_module(src)
    new = module.visit(BooleanTyposTransformer())
    if new.code == module.code:
        return False, ""
    if dry_run:
        with tempfile.NamedTemporaryFile("w", delete=False) as fh:
            fh.write(new.code)
            tmp = fh.name
        diff = subprocess.run(
            ["git", "diff", "--no-index", "--", str(path), tmp],
            capture_output=True,
            text=True,
        )
        os.unlink(tmp)
        return True, diff.stdout
    else:
        # backup
        bakdir = Path("codemod_backups")
        bakdir.mkdir(exist_ok=True)
        bakname = bakdir / f"{path.name}.bak"
        bakname.write_text(path.read_text())
        path.write_text(new.code)
        return True, f"APPLIED to {path}"


def collect_boolean_f821_files(ruff_json_path: Path):
    if not ruff_json_path.exists():
        return []
    data = json.loads(ruff_json_path.read_text())
    target_files = set()
    for e in data:
        msg = e.get("message", "")
        if "Undefined name `false`" in msg or "Undefined name `true`" in msg:
            target_files.add(e["filename"])
    return sorted(target_files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", default=[])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ruff-json", default="/tmp/ruff_f821_clean.json")
    args = ap.parse_args()

    files = args.files[:]
    if not files:
        files = collect_boolean_f821_files(Path(args.ruff_json))

    if not files:
        print("No target files found for boolean fixes.")
        return

    changed_any = False
    for f in files:
        p = Path(f)
        if not p.exists():
            print("Missing:", f)
            continue
        ok, out = run_on_file(p, dry_run=not args.apply)
        if ok:
            changed_any = True
            marker = "DRY" if not args.apply else "APPLIED"
            print(f"== {marker} == {f}")
            print(out[:10000])
        else:
            print(f"No change: {f}")

    if changed_any and args.apply:
        print("\nAll applied. Run ruff/py_compile/tests to verify.")
    elif not changed_any:
        print("No changes necessary.")


if __name__ == "__main__":
    main()
