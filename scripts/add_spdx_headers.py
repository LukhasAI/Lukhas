#!/usr/bin/env python3
"""
Module: add_spdx_headers.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Add SPDX license headers to source files (advisory).

Injects SPDX-License-Identifier and Author headers to files lacking them.
Supports Python (.py) and YAML (.yaml, .yml) files.

Usage:
    python scripts/add_spdx_headers.py \
      --roots scripts api \
      --spdx "SPDX-License-Identifier: Proprietary" \
      --author "LUKHAS Development Team" \
      --filetype py

Author: LUKHAS Development Team
Last Updated: 2025-10-19
"""
import argparse
import pathlib


HEADER_PY = '''"""
{spdx}
Author: {author}
"""'''

HEADER_YAML = "# {spdx}\n# Author: {author}\n"


def add_header(path: pathlib.Path, header_py: str, header_yaml: str) -> bool:
    """Add SPDX header to a source file if missing.

    Args:
        path (pathlib.Path): File to update.
        header_py (str): Header block for Python files.
        header_yaml (str): Header block for YAML files.

    Returns:
        bool: True if the file was modified, False if already compliant.

    Raises:
        UnicodeDecodeError: If the file cannot be decoded as UTF-8.

    Example:
        >>> # doctest: +SKIP
        >>> from pathlib import Path
        >>> p = Path('tmp_demo.py'); _ = p.write_text('print("hi")')
        >>> add_header(p, '"""\\nSPDX-License-Identifier: MIT\\nAuthor: Test\\n"""', '# SPDX-License-Identifier: MIT\n# Author: Test\n')
        True
    """
    txt = path.read_text(encoding="utf-8")

    # Skip if header already exists
    first_lines = "\n".join(txt.splitlines()[:5])
    if ("SPDX-License-Identifier" in first_lines) or ("Author:" in first_lines):
        return False

    # Add appropriate header
    if path.suffix in (".yml", ".yaml"):
        txt = header_yaml + txt
    else:
        txt = header_py + "\n" + txt

    path.write_text(txt, encoding="utf-8")
    return True


def main():
    p = argparse.ArgumentParser(description="Add SPDX headers to source files")
    p.add_argument("--roots", nargs="+", required=True, help="Root directories to process")
    p.add_argument("--spdx", required=True, help="SPDX identifier string")
    p.add_argument("--author", required=True, help="Author attribution")
    p.add_argument("--filetype", choices=["py", "yaml"], default="py", help="File type to process")
    args = p.parse_args()

    header_py_formatted = HEADER_PY.format(spdx=args.spdx, author=args.author)
    header_yaml_formatted = HEADER_YAML.format(spdx=args.spdx, author=args.author)

    changed = 0
    for root in args.roots:
        rootp = pathlib.Path(root)
        if not rootp.exists():
            print(f"⚠️  Skipping non-existent root: {root}")
            continue

        patterns = (["**/*.py"] if args.filetype == "py" else ["**/*.yaml", "**/*.yml"])
        for pat in patterns:
            for pth in rootp.rglob(pat):
                if add_header(pth, header_py_formatted, header_yaml_formatted):
                    changed += 1

    print(f"✅ Updated {changed} files with SPDX headers")


if __name__ == "__main__":
    main()
