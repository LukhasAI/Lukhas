#!/usr/bin/env python3
"""Fix E402 errors in qi/, vivox/, products/, and other remaining directories."""

import subprocess
from pathlib import Path


def fix_file(filepath):
    """Fix E402 errors in a single file."""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Failed to read {filepath}: {e}")
        return False

    lines = content.split('\n')
    if not lines:
        return False

    # Find shebang, early code before docstring, docstring, then rest
    shebang = None
    before_docstring = []
    docstring_lines = []
    after_docstring = []

    i = 0

    # Extract shebang
    if lines[0].startswith('#!'):
        shebang = lines[0]
        i = 1

    # Collect everything before docstring
    found_docstring = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Found docstring
        if stripped.startswith('"""') or stripped.startswith("'''"):
            found_docstring = True
            delimiter = '"""' if stripped.startswith('"""') else "'''"
            docstring_lines.append(line)

            # Single-line docstring
            if stripped.count(delimiter) >= 2:
                i += 1
            else:
                # Multi-line docstring
                i += 1
                while i < len(lines):
                    docstring_lines.append(lines[i])
                    if delimiter in lines[i]:
                        i += 1
                        break
                    i += 1
            break

        before_docstring.append(line)
        i += 1

    if not found_docstring:
        return False

    # Collect rest
    after_docstring = lines[i:]

    # Extract imports and constants from before_docstring
    imports = []
    constants = []
    other = []

    for line in before_docstring:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            imports.append(line)
        elif 'logger' in stripped.lower() and ('getLogger' in line or 'logging.' in line):
            other.append(line)  # Logger will go after imports
        elif stripped.startswith('__') and '=' in stripped:
            constants.append(line)  # Module constants
        elif not stripped or stripped.startswith('#'):
            pass  # Skip blank/comments for now
        else:
            other.append(line)

    # Extract imports from after_docstring
    after_imports = []
    after_constants = []
    rest = []

    in_import_section = True
    for line in after_docstring:
        stripped = line.strip()

        if stripped.startswith('import ') or stripped.startswith('from '):
            after_imports.append(line)
            continue

        if stripped.startswith('__') and '=' in stripped and in_import_section:
            after_constants.append(line)
            continue

        if stripped.startswith('try:'):
            # Capture try/except import blocks
            len(line) - len(line.lstrip())
            after_imports.append(line)

            # Read until end of try/except
            temp_rest = []
            for remaining_line in rest:
                temp_rest.append(remaining_line)
            rest = []

            continue

        if not stripped and in_import_section:
            # Blank line in imports
            continue

        if stripped.startswith('#') and in_import_section:
            # Comment in imports
            continue

        # Actual code starts
        in_import_section = False
        rest.append(line)

    # Reconstruct file
    new_lines = []

    # Shebang
    if shebang:
        new_lines.append(shebang)

    # Docstring
    new_lines.extend(docstring_lines)
    new_lines.append('')

    # All imports
    all_imports = imports + after_imports
    if all_imports:
        new_lines.extend(all_imports)
        new_lines.append('')

    # Module constants
    all_constants = constants + after_constants
    if all_constants:
        new_lines.extend(all_constants)
        new_lines.append('')

    # Logger and other early code
    if other:
        new_lines.extend(other)
        new_lines.append('')

    # Rest of code
    new_lines.extend(rest)

    new_content = '\n'.join(new_lines)

    # Only write if changed
    if new_content != content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False

    return False


def main():
    # Get files with E402 in remaining directories
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '.', '--select', 'E402', '--output-format=concise'],
        capture_output=True,
        text=True
    )

    files = set()
    for line in result.stdout.split('\n'):
        if 'E402' in line:
            parts = line.split(':')
            if parts and not any(x in parts[0] for x in ['archive/', 'gemini-dev/', 'b1db8919']):
                # Focus on qi/, vivox/, products/, lukhas_website/
                if any(parts[0].startswith(d) for d in ['qi/', 'vivox/', 'lukhas_website/']):
                    files.add(parts[0])

    print(f"Found {len(files)} files to fix")

    fixed = 0
    for filepath in sorted(files):
        if Path(filepath).exists() and fix_file(filepath):
            fixed += 1
            print(f"✓ {filepath}")

    print(f"\nFixed {fixed} files")

    # Check remaining
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '.', '--select', 'E402', '--output-format=concise'],
        capture_output=True,
        text=True
    )

    remaining = len([line for line in result.stdout.split('\n')
                    if 'E402' in line and not any(x in line for x in ['archive/', 'gemini-dev/', 'b1db8919'])])
    print(f"Remaining E402 errors: {remaining}")


if __name__ == '__main__':
    main()
