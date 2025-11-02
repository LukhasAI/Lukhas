#!/usr/bin/env python3
"""
Bulk fix E402 errors for LUKHAS codebase.
Handles the common pattern: logging import + logger def before docstring.
"""

import re
import subprocess
from pathlib import Path


def fix_file(filepath):
    """Fix E402 errors in a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, OSError, UnicodeDecodeError) as e:
        print(f"Failed to read {filepath}: {e}")
        return False

    lines = content.split("\n")
    if not lines:
        return False

    # Parse file structure
    shebang = None
    early_imports = []
    logger_def = None
    docstring_lines = []
    late_imports = []
    rest_lines = []

    i = 0

    # Extract shebang
    if lines[0].startswith("#!"):
        shebang = lines[0]
        i = 1

    # Scan for pattern: imports + logger before docstring
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Found docstring start
        if stripped.startswith('"""') or stripped.startswith("'''"):
            # Save docstring
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

        # Collect early imports (before docstring)
        if stripped.startswith("import ") or stripped.startswith("from "):
            early_imports.append(line)
            i += 1
            continue

        # Logger definition
        if "logger" in stripped.lower() and ("getLogger" in line or "logging.get" in line):
            logger_def = line
            i += 1
            continue

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Hit non-import/non-logger code before docstring
        i += 1

    # Now collect remaining imports and code
    in_import_block = True
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Collect imports
        if stripped.startswith("import ") or stripped.startswith("from "):
            late_imports.append(line)
            i += 1
            continue

        # Try/except blocks often contain imports
        if stripped.startswith("try:"):
            # Capture entire try block
            indent_level = len(line) - len(line.lstrip())
            late_imports.append(line)
            i += 1
            while i < len(lines):
                block_line = lines[i]
                block_stripped = block_line.strip()
                block_indent = len(block_line) - len(block_line.lstrip())

                if block_stripped and block_indent <= indent_level and not block_stripped.startswith("except"):
                    break

                late_imports.append(block_line)
                i += 1
                if block_stripped.startswith("except"):
                    # Continue capturing except block
                    i += 1
                    while i < len(lines):
                        except_line = lines[i]
                        except_stripped = except_line.strip()
                        except_indent = len(except_line) - len(except_line.lstrip())

                        if except_stripped and except_indent <= indent_level:
                            break

                        late_imports.append(except_line)
                        i += 1
                    break
            continue

        # Blank lines in import section
        if not stripped and in_import_block:
            late_imports.append(line)
            i += 1
            continue

        # Comments in import section
        if stripped.startswith("#") and in_import_block:
            late_imports.append(line)
            i += 1
            continue

        # Everything else
        in_import_block = False
        rest_lines.append(line)
        i += 1

    # Reconstruct file
    new_lines = []

    # Shebang
    if shebang:
        new_lines.append(shebang)

    # Docstring
    if docstring_lines:
        new_lines.extend(docstring_lines)
        new_lines.append("")

    # All imports (early + late)
    all_imports = early_imports + late_imports
    if all_imports:
        new_lines.extend(all_imports)
        new_lines.append("")

    # Logger definition
    if logger_def:
        new_lines.append(logger_def)
        new_lines.append("")

    # Rest of code
    new_lines.extend(rest_lines)

    # Write back
    new_content = "\n".join(new_lines)

    # Only write if content changed
    if new_content != content:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except (IOError, OSError) as e:
            print(f"Failed to write {filepath}: {e}")
            return False

    return False


def main():
    # Get files with E402 errors
    result = subprocess.run(
        ["python3", "-m", "ruff", "check", ".", "--select", "E402", "--output-format=concise"],
        capture_output=True,
        text=True,
    )

    files = set()
    for line in result.stdout.split("\n"):
        if "E402" in line:
            parts = line.split(":")
            if parts and not any(x in parts[0] for x in ["archive/", "gemini-dev/", "b1db8919"]):
                files.add(parts[0])

    print(f"Found {len(files)} files with E402 errors")

    # Focus on high-priority directories first
    priority_dirs = ["bridge/", "core/", "matriz/", "lukhas/"]
    priority_files = [f for f in files if any(f.startswith(d) for d in priority_dirs)]

    print(f"Fixing {len(priority_files)} files in priority directories")

    fixed = 0
    for filepath in sorted(priority_files):
        if Path(filepath).exists():
            if fix_file(filepath):
                fixed += 1
                print(f"✓ {filepath}")

    print(f"\nFixed {fixed} files")

    # Check remaining errors
    result = subprocess.run(
        ["python3", "-m", "ruff", "check", ".", "--select", "E402", "--output-format=concise"],
        capture_output=True,
        text=True,
    )

    remaining = len(
        [
            l
            for l in result.stdout.split("\n")
            if "E402" in l and not any(x in l for x in ["archive/", "gemini-dev/", "b1db8919"])
        ]
    )
    print(f"Remaining E402 errors: {remaining}")


if __name__ == "__main__":
    main()
