#!/usr/bin/env python3
"""
Batch fix E402 errors by reorganizing imports to top of file.
"""

import subprocess
import sys


def get_files_with_e402(directory=None):
    """Get list of files with E402 errors."""
    cmd = ['python3', '-m', 'ruff', 'check', '--select', 'E402', '--output-format=concise']
    if directory:
        cmd.append(directory)
    else:
        cmd.append('.')

    result = subprocess.run(cmd, capture_output=True, text=True)

    files = set()
    for line in result.stdout.split('\n'):
        if 'E402' in line:
            parts = line.split(':')
            if parts and not any(x in parts[0] for x in ['archive/', 'gemini-dev/', 'b1db8919']):
                files.add(parts[0])

    return sorted(files)


def fix_simple_logger_pattern(filepath):
    """
    Fix pattern where logger is defined before docstring.
    Pattern:
        import logging
        logger = logging.getLogger(...)
        '''docstring'''
        other imports...

    Should be:
        '''docstring'''
        import logging
        other imports...
        logger = logging.getLogger(...)
    """
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    lines = content.split('\n')

    # Check for the logger pattern
    shebang_idx = -1
    logging_import_idx = -1
    logger_def_idx = -1
    docstring_start_idx = -1
    docstring_end_idx = -1

    # Find components
    for i, line in enumerate(lines):
        stripped = line.strip()

        if i == 0 and stripped.startswith('#!'):
            shebang_idx = i
            continue

        if 'import logging' in line and logging_import_idx == -1:
            logging_import_idx = i
            continue

        if stripped.startswith('logger =') and 'getLogger' in line and logger_def_idx == -1:
            logger_def_idx = i
            continue

        if (stripped.startswith('"""') or stripped.startswith("'''")) and docstring_start_idx == -1:
            docstring_start_idx = i
            delimiter = '"""' if stripped.startswith('"""') else "'''"

            # Check if single-line docstring
            if stripped.count(delimiter) >= 2:
                docstring_end_idx = i
                break

            # Multi-line docstring
            for j in range(i + 1, len(lines)):
                if delimiter in lines[j]:
                    docstring_end_idx = j
                    break
            break

    # Only fix if we have the pattern: logging import, logger def, then docstring
    if (logging_import_idx != -1 and logger_def_idx != -1 and
        docstring_start_idx != -1 and logging_import_idx < logger_def_idx < docstring_start_idx):

        # Reconstruct file
        new_lines = []

        # Add shebang if present
        if shebang_idx != -1:
            new_lines.append(lines[shebang_idx])

        # Add docstring
        for i in range(docstring_start_idx, docstring_end_idx + 1):
            new_lines.append(lines[i])

        new_lines.append('')  # Blank line after docstring

        # Add logging import
        new_lines.append(lines[logging_import_idx])

        # Add other imports (scan rest of file)
        in_import_block = False
        import_lines = []
        other_lines = []

        for i in range(docstring_end_idx + 1, len(lines)):
            stripped = lines[i].strip()

            # Skip logger definition and logging import (already added)
            if i == logger_def_idx or i == logging_import_idx:
                continue

            # Collect imports
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append(lines[i])
                in_import_block = True
            elif in_import_block and not stripped:
                # Blank line in import block
                import_lines.append(lines[i])
            elif in_import_block and stripped.startswith('#'):
                # Comment in import block
                import_lines.append(lines[i])
            elif in_import_block and (stripped.startswith('try:') or 'BRANDING' in stripped or 'AVAILABLE' in stripped):
                # try/except import blocks
                import_lines.append(lines[i])
            elif in_import_block and stripped.startswith('except'):
                import_lines.append(lines[i])
            else:
                other_lines.append(lines[i])

        # Add collected imports
        new_lines.extend(import_lines)
        new_lines.append('')

        # Add logger definition
        new_lines.append(lines[logger_def_idx])
        new_lines.append('')

        # Add rest of file
        new_lines.extend(other_lines)

        # Write back
        new_content = '\n'.join(new_lines)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False

    return False


def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = None

    files = get_files_with_e402(directory)
    print(f"Found {len(files)} files with E402 errors")

    fixed = 0
    for filepath in files:
        if fix_simple_logger_pattern(filepath):
            fixed += 1
            print(f"Fixed: {filepath}")

    print(f"\nFixed {fixed}/{len(files)} files")

    # Show remaining errors
    remaining = get_files_with_e402(directory)
    print(f"Remaining files with E402: {len(remaining)}")


if __name__ == '__main__':
    main()
