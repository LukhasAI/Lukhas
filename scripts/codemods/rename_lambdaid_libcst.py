"""
Safe AST-aware codemod to rename `lambda_id` -> `lid` in Python source files.

Usage:
  python scripts/codemods/rename_lambdaid_libcst.py --dry-run
  python scripts/codemods/rename_lambdaid_libcst.py --apply

Notes:
- Operates only on .py files.
- Replacements are applied to identifiers, attribute names, keyword arguments,
  and dict literal string keys inside Python source only.
- This intentionally avoids touching non-Python files and avoids replacing the
  `lambda` keyword.
- When run with --apply the script creates backups with a `.bak` suffix.
"""

from __future__ import annotations

import argparse
import contextlib
from collections.abc import Iterable
from pathlib import Path

import libcst as cst


class LambdaIdTransformer(cst.CSTTransformer):
    """Transformer that renames occurrences of `lambda_id` -> `lid` safely.

    - Renames Name nodes (variables, parameters, local usage)
    - Renames attribute access .lambda_id -> .lid
    - Renames keyword argument identifiers
    - Rewrites dict literal string keys 'lambda_id' -> 'lid'
    """

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        if original_node.value == "lambda_id":
            return cst.Name("lid")
        return updated_node

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute) -> cst.Attribute:
        # Attribute.attr can be a Name or an Attribute; handle Name attr
        attr = original_node.attr
        if isinstance(attr, cst.Name) and attr.value == "lambda_id":
            return updated_node.with_changes(attr=cst.Name("lid"))
        return updated_node

    def leave_Param(self, original_node: cst.Param, updated_node: cst.Param) -> cst.Param:
        # Rename parameter name only if it's exactly lambda_id
        name = original_node.name
        if name and isinstance(name, cst.Name) and name.value == "lambda_id":
            return updated_node.with_changes(name=cst.Name("lid"))
        return updated_node

    def leave_Arg(self, original_node: cst.Arg, updated_node: cst.Arg) -> cst.Arg:
        # Keyword arguments: .keyword is a Name or None
        kw = original_node.keyword
        if kw and isinstance(kw, cst.Name) and kw.value == "lambda_id":
            return updated_node.with_changes(keyword=cst.Name("lid"))
        return updated_node

    def leave_DictElement(self, original_node: cst.DictElement, updated_node: cst.DictElement) -> cst.DictElement:
        # Replace string keys in dict literals: 'lambda_id' -> 'lid'
        key = original_node.key
        if isinstance(key, cst.SimpleString):
            # SimpleString includes quotes; strip and compare
            with contextlib.suppress(Exception):
                cst.helpers.parse_expression(key.value)
            # Simpler: inspect raw value for exact matches of quoted forms
            raw = key.value
            for q in ("'lambda_id'", '"lambda_id"'):
                if raw == q:
                    new_key = cst.SimpleString(raw.replace("lambda_id", "lid"))
                    return updated_node.with_changes(key=new_key)
        return updated_node


EXCLUDES = {".git", "venv", ".venv", "node_modules", "dist", "build"}


def iter_python_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        # skip excluded directories
        if any(part in EXCLUDES for part in p.parts):
            continue
        yield p


def process_file(path: Path) -> tuple[bool, str, str]:
    """Process a file and return (changed, original_text, new_text)."""
    original = path.read_text(encoding="utf8", errors="surrogateescape")
    try:
        module = cst.parse_module(original)
    except Exception:
        return False, original, original  # skip files that don't parse

    mod = module.visit(LambdaIdTransformer())
    new = mod.code
    changed = new != original
    return changed, original, new


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AST-safe rename lambda_id -> lid in .py files")
    parser.add_argument("--root", "-r", default=".", help="Repository root to scan")
    parser.add_argument("--dry-run", action="store_true", help="Only report changes")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes in-place (creates .bak backups)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    files_changed = 0
    edits = []

    for p in iter_python_files(root):
        changed, original, new = process_file(p)
        if not changed:
            continue
        files_changed += 1
        edits.append(p)
        if args.dry_run:
            print(f"DRY-RUN: Would update: {p}")
        elif args.apply:
            bak = p.with_suffix(p.suffix + ".bak")
            p.write_text(new, encoding="utf8")
            # create backup only if it doesn't already exist to avoid overwriting
            if not bak.exists():
                bak.write_text(original, encoding="utf8")
            print(f"APPLIED: Updated {p} (backup: {bak})")

    print(f"Done. Files matched: {len(list(iter_python_files(root))}; files changed: {files_changed}")
    if files_changed and args.dry_run:
        print("Run with --apply to perform changes (creates .bak backups).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
