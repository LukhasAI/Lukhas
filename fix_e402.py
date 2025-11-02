#!/usr/bin/env python3
"""
Script to fix E402 errors by moving imports to top of file.
Handles common patterns while preserving functionality.
"""

import re
from pathlib import Path
from typing import List, Tuple
import sys


def extract_file_parts(content: str) -> Tuple[str, str, str, str]:
    """
    Extract: shebang, docstring, imports, rest
    """
    lines = content.split('\n')

    shebang = ""
    docstring = ""
    imports = []
    rest = []

    i = 0

    # Extract shebang
    if lines and lines[0].startswith('#!'):
        shebang = lines[0] + '\n'
        i = 1

    # Extract module-level docstring
    in_docstring = False
    docstring_delimiter = None
    docstring_lines = []

    # Skip blank lines and comments before docstring
    while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith('#')):
        docstring_lines.append(lines[i])
        i += 1

    # Check for docstring
    if i < len(lines):
        line = lines[i].strip()
        if line.startswith('"""') or line.startswith("'''"):
            in_docstring = True
            docstring_delimiter = '"""' if line.startswith('"""') else "'''"
            docstring_lines.append(lines[i])
            i += 1

            # Multi-line docstring
            if line != docstring_delimiter and not line.endswith(docstring_delimiter):
                while i < len(lines):
                    docstring_lines.append(lines[i])
                    if docstring_delimiter in lines[i]:
                        i += 1
                        break
                    i += 1

    docstring = '\n'.join(docstring_lines) if docstring_lines else ""

    # Now collect everything else
    while i < len(lines):
        rest.append(lines[i])
        i += 1

    rest_content = '\n'.join(rest)

    # Find all imports in rest_content
    import_lines = []
    non_import_lines = []

    for line in rest.split('\n') if isinstance(rest, str) else rest:
        stripped = line.strip()
        if (stripped.startswith('import ') or
            stripped.startswith('from ') or
            (stripped and import_lines and not stripped and not non_import_lines)):  # blank line after import
            import_lines.append(line)
        else:
            non_import_lines.append(line)

    imports_content = '\n'.join(import_lines)
    rest_content = '\n'.join(non_import_lines)

    return shebang, docstring, imports_content, rest_content


def fix_e402_in_file(filepath: Path) -> bool:
    """
    Fix E402 errors in a file by moving imports to top.
    Returns True if file was modified.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    lines = content.split('\n')

    # Find module docstring end
    docstring_end = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip shebang and encoding
        if i == 0 and (stripped.startswith('#!') or stripped.startswith('# coding') or stripped.startswith('# -*- coding')):
            continue

        # Skip comments and blank lines before docstring
        if not in_docstring and (not stripped or stripped.startswith('#')):
            continue

        # Start of docstring
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            in_docstring = True
            docstring_char = '"""' if stripped.startswith('"""') else "'''"

            # Single line docstring
            if stripped.count(docstring_char) >= 2:
                docstring_end = i + 1
                break
            continue

        # End of docstring
        if in_docstring and docstring_char in line:
            docstring_end = i + 1
            break

    if docstring_end == 0:
        # No docstring found, check for encoding/comments
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            docstring_end = i
            break

    # Collect imports and non-imports
    imports = []
    non_imports = []
    seen_code = False

    for i, line in enumerate(lines[docstring_end:], start=docstring_end):
        stripped = line.strip()

        # Track if we've seen actual code (not imports/comments/blank)
        if stripped and not stripped.startswith('#') and not stripped.startswith('import ') and not stripped.startswith('from '):
            seen_code = True

        # Collect imports that come after code (E402 violations)
        if seen_code and (stripped.startswith('import ') or stripped.startswith('from ')):
            imports.append(line)
        elif i < docstring_end:
            non_imports.append(line)

    if not imports:
        return False

    # Rebuild file: header + existing imports + E402 imports + rest
    header = lines[:docstring_end]

    # Find existing imports block
    existing_imports = []
    rest_start = docstring_end

    for i in range(docstring_end, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith('import ') or stripped.startswith('from ') or (not stripped and i < len(lines) - 1):
            existing_imports.append(lines[i])
        else:
            rest_start = i
            break

    # Rest of content (excluding E402 imports)
    rest = []
    for i, line in enumerate(lines[rest_start:], start=rest_start):
        stripped = line.strip()
        if not (stripped.startswith('import ') or stripped.startswith('from ')):
            rest.append(line)

    # Combine
    new_content = (
        '\n'.join(header) + '\n\n' +
        '\n'.join(existing_imports + imports).strip() + '\n\n' +
        '\n'.join(rest).strip() + '\n'
    )

    # Write back
    try:
        filepath.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False


def main():
    # Get list of files with E402 errors
    import subprocess

    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '.', '--select', 'E402', '--output-format=concise'],
        capture_output=True,
        text=True
    )

    files_to_fix = set()
    for line in result.stdout.split('\n'):
        if 'E402' in line and not any(x in line for x in ['archive/', 'gemini-dev/', 'b1db8919']):
            filepath = line.split(':')[0]
            if filepath:
                files_to_fix.add(filepath)

    print(f"Found {len(files_to_fix)} files with E402 errors")

    fixed = 0
    for filepath in sorted(files_to_fix):
        path = Path(filepath)
        if path.exists():
            if fix_e402_in_file(path):
                fixed += 1
                print(f"Fixed: {filepath}")

    print(f"\nFixed {fixed} files")


if __name__ == '__main__':
    main()
