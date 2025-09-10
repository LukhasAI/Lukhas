#!/usr/bin/env python3
"""
Fail-closed acceptance gate:
- Scans ALL files under 'lukhas/' (the accepted lane)
- Blocks any import (static or dynamic) of candidate/, quarantine/, archive/
- Flags "facade" files (tiny wrappers that are mostly imports)
Exit code: 0 = pass, 1 = violations
"""
import ast
import os
import sys

FORBIDDEN_ROOTS = ("candidate", "quarantine", "archive")
ACCEPTED_ROOT = "lukhas"

violations = []


def is_facade(py_path, tree, src):
    total_lines = len(src.splitlines())
    if total_lines == 0:
        return False
    import_lines = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # approximate: count the line as an import line
            import_lines += 1
    # Facade heuristic: very small files dominated by imports
    return (total_lines < 40) and (import_lines / max(1, total_lines) > 0.6)


def check_file(py_path):
    try:
        with open(py_path, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src, filename=py_path)
    except Exception as e:
        violations.append((py_path, f"AST parse error: {e}"))
        return

    # Block static imports of forbidden roots
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = (alias.name or "").split(".")[0]
                if name in FORBIDDEN_ROOTS:
                    violations.append((py_path, f"Illegal import of '{name}'"))
        elif isinstance(node, ast.ImportFrom):
            modroot = (node.module or "").split(".")[0]
            if modroot in FORBIDDEN_ROOTS:
                violations.append((py_path, f"Illegal import-from '{modroot}.*'"))

        # Block simple dynamic imports that reference forbidden roots
        elif isinstance(node, ast.Call):
            # __import__("candidate.x") or importlib.import_module("candidate.x")
            callee = ""
            if isinstance(node.func, ast.Name):
                callee = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee = node.func.attr

            if callee in {"__import__", "import_module"} and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                    root = arg0.value.split(".")[0]
                    if root in FORBIDDEN_ROOTS:
                        violations.append((py_path, f"Illegal dynamic import of '{root}'"))

    # Facade detection (warn-level; make it error to enforce)
    try:
        if is_facade(py_path, tree, src):
            violations.append((py_path, "Facade wrapper detected (tiny & mostly imports)"))
    except Exception as e:
        violations.append((py_path, f"Facade check error: {e}"))


def main():
    if not os.path.isdir(ACCEPTED_ROOT):
        print(f"[gate] '{ACCEPTED_ROOT}' not found; nothing to check.")
        sys.exit(0)

    for d, _, files in os.walk(ACCEPTED_ROOT):
        for f in files:
            if f.endswith(".py"):
                check_file(os.path.join(d, f))

    if violations:
        print("❌ Acceptance gate violations:")
        for path, msg in violations:
            print(f" - {path}: {msg}")
        sys.exit(1)
    else:
        print("✅ Acceptance gate passed (no illegal imports or facades detected).")
        sys.exit(0)


if __name__ == "__main__":
    main()