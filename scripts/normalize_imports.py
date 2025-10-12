#!/usr/bin/env python3
"""
Normalize relative imports to absolute imports.

Requires: pip install libcst

Usage:
    python3 scripts/normalize_imports.py --check       # Dry-run
    python3 scripts/normalize_imports.py --apply       # Write changes
"""
from __future__ import annotations
import argparse
import pathlib
import sys

try:
    import libcst as cst
except ImportError:
    print("[ERROR] libcst not installed. Run: pip install libcst")
    sys.exit(1)


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
            import subprocess
            import shlex
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
