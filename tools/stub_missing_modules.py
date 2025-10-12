#!/usr/bin/env python3
"""
Stub missing modules to unblock test collection.

Strategy: Create minimal __init__.py stubs for all missing modules
so tests can at least collect. Mark them clearly as stubs.
"""
import re
import subprocess
from pathlib import Path


def get_missing_modules():
    """Extract all unique missing module names from pytest."""
    result = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )

    modules = set()
    for line in result.stderr.split('\n'):
        # ModuleNotFoundError: No module named 'bridge.api.analysis'
        match = re.search(r"No module named '([^']+)'", line)
        if match:
            modules.add(match.group(1))

    return sorted(modules)

def create_stub(module_path):
    """Create a stub __init__.py for a missing module."""
    parts = module_path.split('.')
    dir_path = Path(*parts)

    # Create directory structure
    dir_path.mkdir(parents=True, exist_ok=True)

    # Create stub __init__.py
    init_file = dir_path / '__init__.py'
    if not init_file.exists():
        stub_content = f'''"""
STUB MODULE: {module_path}

This module was auto-generated to fix test collection errors.
Original module is missing or was never implemented.

Status: STUB - Needs implementation or removal
Created: 2025-10-06 (v0.03-prep baseline)
Tracking: docs/v0.03/KNOWN_ISSUES.md
"""

# TODO: Implement actual module or remove dead imports
'''
        init_file.write_text(stub_content)
        return True

    return False

def comment_out_broken_import(file_path, import_line):
    """Comment out a broken import line."""
    if not Path(file_path).exists():
        return False

    content = Path(file_path).read_text()
    original = content

    # Comment out the import
    if import_line in content:
        commented = f"# STUB: {import_line}  # Module missing - stubbed for v0.03-prep"
        content = content.replace(import_line, commented)

    if content != original:
        Path(file_path).write_text(content)
        return True

    return False

def main():
    print("🔍 Finding missing modules...")
    missing = get_missing_modules()

    if not missing:
        print("✅ No missing modules!")
        return 0

    print(f"📦 Found {len(missing)} missing modules:")
    for mod in missing[:15]:
        print(f"  - {mod}")
    if len(missing) > 15:
        print(f"  ... and {len(missing) - 15} more")
    print()

    print("🔧 Creating stub modules...")
    created = 0
    for module in missing:
        if create_stub(module):
            created += 1
            print(f"  ✅ {module}")

    print()
    print(f"📝 Created {created} stub modules")
    print()

    print("🔍 Re-checking collection...")
    result = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )

    errors = result.stderr.count('ERROR')
    print(f"📊 Remaining errors: {errors}")

    if errors == 0:
        print("🎉 SUCCESS: All modules now importable!")
        print()
        print("⚠️  NOTE: These are STUBS - they need actual implementation or removal")
        print("   See each stub __init__.py for TODO notes")
        return 0
    else:
        print(f"⚠️  Still have {errors} errors - may be import name errors or other issues")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
