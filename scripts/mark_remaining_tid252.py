#!/usr/bin/env python3
"""
Mark remaining TID252 violations with noqa comments.

For non-__init__.py files where relative imports may need future refactoring.
"""

import re
import sys
from pathlib import Path


def mark_relative_imports(py_file: Path) -> int:
    """Add noqa comments to relative imports in regular Python files."""
    if not py_file.exists():
        return 0

    content = py_file.read_text()
    lines = content.splitlines(keepends=True)
    modified = 0

    for i, line in enumerate(lines):
        # Match relative imports
        if re.match(r'^from \.([\w.]+)? import ', line.strip()):
            # Skip if already has noqa
            if '# noqa' in line:
                continue

            # Add noqa comment with TODO for future refactoring
            lines[i] = line.rstrip() + '  # noqa: TID252 TODO: convert to absolute import\n'
            modified += 1

    if modified > 0:
        py_file.write_text(''.join(lines))

    return modified


def main():
    """Mark all remaining TID252 violations in production lanes."""
    repo_root = Path(__file__).parent.parent

    # Get list of files with TID252 violations from ruff
    import subprocess
    import json

    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', 'lukhas/', 'core/', 'MATRIZ/',
         '--select', 'TID252', '--output-format', 'json'],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    violations = json.loads(result.stdout)
    files_with_violations = set()

    for violation in violations:
        file_path = Path(violation['filename'])
        # Skip __init__.py files (already handled)
        if file_path.name != '__init__.py':
            files_with_violations.add(repo_root / file_path)

    total_marked = 0
    files_modified = 0

    for file_path in sorted(files_with_violations):
        marked = mark_relative_imports(file_path)
        if marked > 0:
            total_marked += marked
            files_modified += 1
            print(f"✓ {file_path.relative_to(repo_root)}: {marked} imports marked")

    print(f"\n✅ Marked {total_marked} relative imports in {files_modified} regular Python files")
    return 0


if __name__ == '__main__':
    sys.exit(main())
