#!/usr/bin/env python3
"""
Bulk textual fixer for common broken patterns in tools/*.py.

Fixes:
- Replace "# " artifacts with standard "# " comments
- Normalize startswith/strip patterns expecting comment markers
- Loosen malformed "any(" to "any("

This is a conservative, text-only pass to restore parseability.
"""
from __future__ import annotations

from pathlib import Path


def process_text(text: str) -> str:
    # Core normalization: broken "# " → "# "
    new = text.replace("# ", "# ")

    # Specific APIs likely affected
    new = new.replace('startswith("# ")', 'startswith("#")')
    new = new.replace("startswith('# ')", "startswith('#')")
    new = new.replace('strip("# ".strip())', 'strip("#")')
    new = new.replace("strip('# ' .strip())", "strip('#')")

    # Regex patterns that used the broken marker
    new = new.replace('r"# .*$"', 'r"# .*$"')
    new = new.replace('r"^# +\\s+"', 'r"^# +\\s+"')

    # Malformed any( → any(
    new = new.replace("any(", "any(")

    return new


def main() -> int:
    root = Path("tools")
    if not root.exists():
        print("tools/ directory not found")
        return 2

    changed = 0
    for path in root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        new = process_text(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1

    print(f"Updated {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())