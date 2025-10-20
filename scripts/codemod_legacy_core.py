#!/usr/bin/env python3
"""
Module: codemod_legacy_core.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

import argparse
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP_DIRS = {"tests", ".venv", "venv", "build", "dist", "__pycache__", "quarantine", "mcp-lukhas-sse", "site-packages", "vendor", ".git", "temp", "node_modules", "backups"}

class Rewriter(ast.NodeTransformer):
    def visit_Import(self, node):
        for n in node.names:
            if n.name == "core" or n.name.startswith("core."):
                n.name = "lukhas." + n.name if not n.name.startswith("lukhas.") else n.name
        return node
    def visit_ImportFrom(self, node):
        if node.module and (node.module == "core" or node.module.startswith("core.")):
            node.module = "lukhas." + node.module if not node.module.startswith("lukhas.") else node.module
        return node

def rewrite_file(p: pathlib.Path, write: bool) -> bool:
    if not p.is_file():
        # Skip directories and non-files
        return False
    try:
        src = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, IsADirectoryError, PermissionError):
        # Skip binary files, directories, or permission issues
        return False
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    new = ast.unparse(Rewriter().visit(tree))  # Py3.9+: if not available, use astor
    if new != src:
        if write:
            p.write_text(new, encoding="utf-8")
        print(p)
        return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply changes")
    args = ap.parse_args()
    changed = 0
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.match("core/__init__.py"):
            continue
        changed += rewrite_file(path, args.write) or 0
    sys.exit(0 if not changed else (0 if args.write else 2))

if __name__ == "__main__":
    main()
