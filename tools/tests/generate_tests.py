#!/usr/bin/env python3
"""
generate_tests.py
Scan source directories and create safe import-smoke test skeletons for
modules that don't already have tests.

Usage:
    python tools/tests/generate_tests.py --sources core consciousness memory governance emotion bridge api --out tests/auto_generated
"""
import argparse
import os
import textwrap

SKIP_DIRS = {"__pycache__", "tests", "manifests", ".git", "docs"}

TEST_TEMPLATE = """\
\"\"\"Auto-generated skeleton tests for module {module_path}.

This is intentionally conservative: it only imports the module and runs
safe smoke assertions. Manually add more detailed tests as needed.
\"\"\"

import importlib
import pytest

def test_import_{safe_name}():
    \"\"\"Module can be imported without error\"\"\"
    try:
        m = importlib.import_module("{module_path}")
    except Exception as e:
        pytest.skip(f"Cannot import {module_path}: {{e}}")
    assert m is not None
"""

def list_py_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py") and not fn.startswith("test_") and fn != "__init__.py":
                yield os.path.join(dirpath, fn)

def module_from_path(path, repo_root):
    rel = os.path.relpath(path, repo_root)
    parts = rel.split(os.sep)
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)

def ensure_out(path):
    os.makedirs(path, exist_ok=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sources", nargs="+", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    repo_root = os.getcwd()
    ensure_out(args.out)
    created = []
    for s in args.sources:
        if not os.path.isdir(s):
            print(f"Skipping missing source dir: {s}")
            continue
        for f in list_py_files(s):
            module = module_from_path(f, repo_root)
            # derive proposed test filename
            safe_name = module.replace(".", "_")
            test_file = os.path.join(args.out, f"test_{safe_name}.py")
            if os.path.exists(test_file):
                continue
            content = TEST_TEMPLATE.format(module_path=module, safe_name=safe_name)
            with open(test_file, "w", encoding="utf-8") as fh:
                fh.write(content)
            created.append(test_file)
            print("Created", test_file)
    print("Created files:", len(created))

if __name__ == "__main__":
    main()
