#!/usr/bin/env python3
"""
T4 Scaffold Guard - Protect auto-generated scaffold files from manual edits.
Prevents commits that modify scaffold-generated files without proper provenance.
"""

import subprocess
import sys
from pathlib import Path

PROV_PREFIX = "# @generated LUKHAS scaffold v1"

def get_staged_files():
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []

def is_scaffold_file(file_path):
    """Check if a file should be scaffold-managed based on path patterns."""
    path = Path(file_path)

    # Check if it's in a module directory under lukhas/
    if not str(path).startswith("lukhas/"):
        return False

    # Check for scaffold-managed file patterns
    scaffold_patterns = [
        "docs/README.md",
        "docs/api.md",
        "tests/test_*_unit.py",
        "tests/test_*_integration.py"
    ]

    relative_to_module = "/".join(path.parts[2:])  # Remove lukhas/module_name/

    for pattern in scaffold_patterns:
        if pattern.replace("*", "") in relative_to_module:
            return True

    return False

def has_provenance_header(file_path):
    """Check if file has proper scaffold provenance header."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            return first_line == PROV_PREFIX.strip()
    except Exception:
        return False

def main():
    """Main scaffold guard function."""
    staged_files = get_staged_files()

    # Filter to scaffold-managed files
    scaffold_files = [f for f in staged_files if is_scaffold_file(f)]

    if not scaffold_files:
        return 0  # No scaffold files being modified

    # Check each scaffold file for proper provenance
    violations = []

    for file_path in scaffold_files:
        if not Path(file_path).exists():
            continue  # File was deleted, that's okay

        if not has_provenance_header(file_path):
            violations.append(file_path)

    if violations:
        print("❌ T4 Scaffold Guard: Manual edits detected in auto-generated files", file=sys.stderr)
        print("", file=sys.stderr)
        print("The following files appear to be scaffold-managed but lack provenance headers:", file=sys.stderr)
        for violation in violations:
            print(f"   📄 {violation}", file=sys.stderr)
        print("", file=sys.stderr)
        print("🔧 To fix this issue:", file=sys.stderr)
        print("   1. Revert manual changes: git checkout HEAD -- <file>", file=sys.stderr)
        print("   2. Edit templates in templates/module_scaffold/ instead", file=sys.stderr)
        print("   3. Re-sync with: make scaffold-apply", file=sys.stderr)
        print("", file=sys.stderr)
        print("🚫 To force commit anyway (not recommended):", file=sys.stderr)
        print("   git commit --no-verify", file=sys.stderr)
        return 1

    print("✅ T4 Scaffold Guard: All scaffold files have proper provenance")
    return 0

if __name__ == "__main__":
    sys.exit(main())
