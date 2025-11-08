#!/usr/bin/env python3
"""
Root Directory Hygiene Validator

Ensures only approved files exist at the repository root.
Used in pre-commit hooks and CI checks.

Exit codes:
    0 - All root files are allowed
    1 - Unauthorized files found at root
    2 - Configuration error
"""

import fnmatch
import sys
from pathlib import Path
def load_allowlist(allowlist_path: Path) -> list[str]:
    """Load patterns from .root-allowlist file."""
    if not allowlist_path.exists():
        print(f"ERROR: Allowlist file not found: {allowlist_path}", file=sys.stderr)
        sys.exit(2)

    patterns = []
    with open(allowlist_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                patterns.append(line)

    return patterns


def get_root_files(repo_root: Path) -> set[str]:
    """Get all files and directories at repository root."""
    items = set()
    for item in repo_root.iterdir():
        items.add(item.name)
    return items


def is_allowed(name: str, patterns: list[str]) -> bool:
    """Check if a file/directory matches any allowed pattern."""
    for pattern in patterns:
        # Direct match
        if name == pattern:
            return True
        # Glob pattern match
        if fnmatch.fnmatch(name, pattern):
            return True
        # Directory pattern (ends with /)
        if pattern.endswith('/') and name == pattern.rstrip('/'):
            return True
    return False


def main() -> int:
    """Main validation logic."""
    repo_root = Path(__file__).parent.parent.resolve()
    allowlist_path = repo_root / '.root-allowlist'

    # Load allowed patterns
    patterns = load_allowlist(allowlist_path)

    # Get current root files
    root_files = get_root_files(repo_root)

    # Check each file
    violations = []
    for name in sorted(root_files):
        if not is_allowed(name, patterns):
            violations.append(name)

    # Report results
    if violations:
        print("❌ Root directory hygiene check FAILED", file=sys.stderr)
        print(f"\nUnauthorized files at repository root ({len(violations)}):", file=sys.stderr)
        for name in violations:
            print(f"  - {name}", file=sys.stderr)

        print("\n📋 To fix this:", file=sys.stderr)
        print("  1. Move files to appropriate subdirectories:", file=sys.stderr)
        print("     - Documentation → docs/", file=sys.stderr)
        print("     - Agent guides → docs/agents/", file=sys.stderr)
        print("     - Session notes → docs/sessions/", file=sys.stderr)
        print("     - Status reports → docs/project_status/", file=sys.stderr)
        print("     - Test files → docs/testing/", file=sys.stderr)
        print("     - Security docs → docs/security/", file=sys.stderr)
        print("  2. Or add to .root-allowlist if legitimately needed at root", file=sys.stderr)
        print("  3. Run: scripts/validate_root_hygiene.py", file=sys.stderr)

        return 1

    print("✅ Root directory hygiene check PASSED")
    print(f"   All {len(root_files)} items at root are authorized")
    return 0


if __name__ == '__main__':
    sys.exit(main())
