#!/usr/bin/env python3
"""
Automated # noqa comment addition script.

Finds delayed imports in tests/ and tools/ directories and adds
# noqa: E402 comments with explanatory reasons.
"""

import ast
import pathlib
import sys
from typing import List, Tuple


def find_delayed_imports(file_path: pathlib.Path) -> List[Tuple[int, str]]:
    """
    Find imports that occur after module-level code.

    Returns list of (line_number, import_statement) tuples.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        delayed_imports = []
        found_non_import = False

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if found_non_import and hasattr(node, 'lineno'):
                    # Get the import statement text
                    lines = content.splitlines()
                    if node.lineno <= len(lines):
                        import_line = lines[node.lineno - 1].strip()
                        delayed_imports.append((node.lineno, import_line))
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign)):
                found_non_import = True

        return delayed_imports

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return []


def add_noqa_to_line(line: str) -> str:
    """Add # noqa: E402 comment to import line if not already present."""
    if '# noqa' in line or '# type: ignore' in line:
        return line

    # Add the noqa comment with reason
    return f"{line}  # noqa: E402 - delayed import for test/tool isolation"


def process_file(file_path: pathlib.Path, dry_run: bool = False) -> int:
    """
    Process a single Python file, adding # noqa comments to delayed imports.

    Returns number of lines modified.
    """
    delayed_imports = find_delayed_imports(file_path)

    if not delayed_imports:
        return 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modifications = 0
        for line_num, _ in delayed_imports:
            if line_num <= len(lines):
                original = lines[line_num - 1]
                modified = add_noqa_to_line(original.rstrip()) + '\n'

                if original != modified:
                    lines[line_num - 1] = modified
                    modifications += 1
                    print(f"  Line {line_num}: Added # noqa comment")

        if modifications > 0 and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        return modifications

    except Exception as e:
        print(f"Error modifying {file_path}: {e}", file=sys.stderr)
        return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Add # noqa: E402 comments to delayed imports in tests/ and tools/'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--dir',
        action='append',
        default=[],
        help='Additional directories to process (default: tests/, tools/)'
    )

    args = parser.parse_args()

    # Default directories
    base_dirs = ['tests', 'tools']
    if args.dir:
        base_dirs.extend(args.dir)

    total_files = 0
    total_modifications = 0

    for base_dir in base_dirs:
        dir_path = pathlib.Path(base_dir)

        if not dir_path.exists():
            print(f"Warning: Directory {base_dir} does not exist, skipping")
            continue

        print(f"\nProcessing directory: {base_dir}")

        for py_file in dir_path.rglob('*.py'):
            modifications = process_file(py_file, dry_run=args.dry_run)

            if modifications > 0:
                total_files += 1
                total_modifications += modifications
                print(f"✓ {py_file}: {modifications} line(s) modified")

    print(f"\n{'Dry run: ' if args.dry_run else ''}Processed {total_files} files, "
          f"{total_modifications} total modifications")

    return 0 if total_modifications == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
