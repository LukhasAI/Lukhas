#!/usr/bin/env python3
"""
Init File Validator
Tests that all created __init__.py files can be imported successfully.
"""

import importlib
import sys
from pathlib import Path


def validate_init_files() -> bool:
    """Validate all __init__.py files can be imported"""
    root_path = Path(".")
    init_files = list(root_path.rglob("__init__.py"))

    passed = 0
    failed = 0

    for init_file in init_files:
        module_path = str(init_file.parent).replace("/", ".").replace("\\", ".")
        try:
            importlib.import_module(module_path)
            print(f"✅ {module_path}")
            passed += 1
        except Exception as e:
            print(f"❌ {module_path}: {e}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = validate_init_files()
    sys.exit(0 if success else 1)
