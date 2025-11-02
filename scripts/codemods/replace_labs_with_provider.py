#!/usr/bin/env python3
"""
Codemod: replace top-level `from labs.xxx import name1, name2` with importlib-based lazy assignments.
Usage:
  python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/patches
  python3 scripts/codemods/replace_labs_with_provider.py --apply
"""
from __future__ import annotations

import argparse
import difflib
from pathlib import Path
from typing import Iterator

import libcst as cst
from libcst import helpers as cst_helpers

# NOTE: This codemod is intentionally conservative. It only converts top-level
# ImportFrom nodes whose module string starts with "labs". It does not change call sites
# aggressively — we create top-level names that callers can use, but callers may need manual review.


class LabsImportRewriter(cst.CSTTransformer):
    def __init__(self) -> None:
        self._scope_depth = 0
        self._importlib_present = False
        self._importlib_inserted = False

    # Track scope depth so we only rewrite module-level imports.
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:  # noqa: D401 - standard CST hook
        self._scope_depth += 1

    def leave_FunctionDef(self, original_node: cst.FunctionDef) -> None:  # noqa: D401 - standard CST hook
        self._scope_depth -= 1

    def visit_ClassDef(self, node: cst.ClassDef) -> None:  # noqa: D401 - standard CST hook
        self._scope_depth += 1

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:  # noqa: D401 - standard CST hook
        self._scope_depth -= 1

    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            if not isinstance(alias, cst.ImportAlias):
                continue
            name = cst_helpers.get_full_name_for_node(alias.name)
            if name == "importlib":
                self._importlib_present = True

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        module = node.module
        if module is not None:
            name = cst_helpers.get_full_name_for_node(module)
            if name == "importlib":
                self._importlib_present = True

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.CSTNode:
        # Only act on `from labs... import ...` at module level
        if self._scope_depth != 0:
            return updated_node
        module = original_node.module
        if module is None or original_node.relative:
            return updated_node
        module_code = cst_helpers.get_full_name_for_node(module)
        if not module_code or not module_code.startswith("labs"):
            return updated_node

        names: list[tuple[str, str | None]] = []
        for alias in original_node.names:
            if not isinstance(alias, cst.ImportAlias):
                return updated_node
            if isinstance(alias, cst.ImportStar):
                return updated_node
            if not isinstance(alias.name, cst.Name):
                return updated_node
            if alias.asname and not isinstance(alias.asname.name, cst.Name):
                return updated_node
            target = alias.asname.name.value if alias.asname else None
            names.append((alias.name.value, target))

        if not names:
            return updated_node

        try_items = [
            cst.parse_statement(
                f"_mod = importlib.import_module({repr(module_code)})\n"
            )
        ]
        for imported_name, alias in names:
            target = alias if alias else imported_name
            try_items.append(
                cst.parse_statement(f"{target} = getattr(_mod, {repr(imported_name)})\n")
            )

        except_items = [
            cst.parse_statement(f"{alias if alias else name} = None\n")
            for name, alias in names
        ]

        try_stmt = cst.Try(
            body=cst.IndentedBlock(try_items),
            handlers=[
                cst.ExceptHandler(
                    type=cst.Name("Exception"),
                    body=cst.IndentedBlock(except_items),
                )
            ],
            orelse=None,
            finalbody=None,
        )

        statements: list[cst.BaseStatement] = []
        if not self._importlib_present and not self._importlib_inserted:
            statements.append(cst.parse_statement("import importlib\n"))
            self._importlib_inserted = True
        statements.append(try_stmt)

        return cst.FlattenSentinel(statements)


def process_file(path: Path) -> tuple[str, str] | None:
    src = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src)
    except Exception as exc:  # pragma: no cover - logged for operator awareness
        print(f"[skip] parse error {path}: {exc}")
        return None
    rewriter = LabsImportRewriter()
    new_module = module.visit(rewriter)
    new_src = new_module.code
    if new_src != src:
        return src, new_src
    return None


def collect_py_files(root: Path) -> Iterator[Path]:
    for p in root.rglob("*.py"):
        if any(x in p.parts for x in (".venv", "venv", ".git", "tests", "docs", "artifacts", "archive")):
            continue
        yield p


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="/tmp/codmod_patches")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    count = 0
    for file_path in collect_py_files(root):
        res = process_file(file_path)
        if not res:
            continue
        old, new = res
        rel = file_path.relative_to(root)
        patch_path = outdir / (str(rel).replace("/", "__") + ".patch")
        diff = "\n".join(
            difflib.unified_diff(
                old.splitlines(),
                new.splitlines(),
                fromfile=str(file_path),
                tofile=str(file_path),
                lineterm="",
            )
        )
        patch_path.write_text(diff, encoding="utf-8")
        print(f"[info] wrote patch {patch_path}")
        count += 1
        if args.apply:
            bak = file_path.with_suffix(file_path.suffix + ".bak")
            if not bak.exists():
                file_path.write_text(new, encoding="utf-8")
                print(f"[apply] updated {file_path} (backup at {bak})")
    print(f"[info] total patches: {count}")


if __name__ == "__main__":
    main()
