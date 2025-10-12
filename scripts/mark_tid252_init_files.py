#!/usr/bin/env python3
"""
Mark TID252 violations in __init__.py files with noqa comments.

Relative imports in __init__.py files are idiomatic Python for package
re-exports, so we mark them as acceptable technical debt.
"""

import re
import sys
from pathlib import Path


def mark_init_relative_imports(init_file: Path) -> int:
    """Add noqa comments to relative imports in __init__.py files."""
    if not init_file.exists():
        return 0

    content = init_file.read_text()
    lines = content.splitlines(keepends=True)
    modified = 0

    for i, line in enumerate(lines):
        # Match relative imports
        if re.match(r'^from \.([\w.]+)? import ', line.strip()):
            # Skip if already has noqa
            if '# noqa' in line:
                continue

            # Add noqa comment
            lines[i] = line.rstrip() + '  # noqa: TID252 (relative imports in __init__.py are idiomatic)\n'
            modified += 1

    if modified > 0:
        init_file.write_text(''.join(lines))

    return modified


def main():
    """Mark all __init__.py files in production lanes."""
    repo_root = Path(__file__).parent.parent
    production_lanes = ['lukhas', 'core', 'MATRIZ']

    total_marked = 0
    files_modified = 0

    for lane in production_lanes:
        lane_path = repo_root / lane
        if not lane_path.exists():
            continue

        # Find all __init__.py files
        for init_file in lane_path.rglob('__init__.py'):
            marked = mark_init_relative_imports(init_file)
            if marked > 0:
                total_marked += marked
                files_modified += 1
                print(f"✓ {init_file.relative_to(repo_root)}: {marked} imports marked")

    print(f"\n✅ Marked {total_marked} relative imports in {files_modified} __init__.py files")
    return 0


if __name__ == '__main__':
    sys.exit(main())
