#!/usr/bin/env python3
"""
Module: check_encoding.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Pre-commit hook: Check markdown files for UTF-8 encoding.
"""

import sys
from pathlib import Path


def check_encoding(file_path: Path) -> bool:
    """Check if file is valid UTF-8."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except UnicodeDecodeError as e:
        print(f"❌ {file_path}: Not valid UTF-8 - {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"⚠️  {file_path}: Cannot read - {e}", file=sys.stderr)
        return True  # Don't block on read errors


def main():
    """Check all provided files."""
    files = [Path(f) for f in sys.argv[1:]]

    if not files:
        return 0

    errors = 0
    for file_path in files:
        if not check_encoding(file_path):
            errors += 1

    if errors:
        print(f"\n❌ {errors} file(s) with encoding errors", file=sys.stderr)
        print("   Re-encode to UTF-8 with: python3 - <<'PY'", file=sys.stderr)
        print("from pathlib import Path", file=sys.stderr)
        print("p = Path('...')", file=sys.stderr)
        print("p.write_bytes(p.read_bytes().decode('latin-1', 'replace').encode('utf-8'))", file=sys.stderr)
        print("PY", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
