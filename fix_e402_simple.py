#!/usr/bin/env python3
"""
E402 Phase 1: Simple Import Fixes
==================================

Fixes simple E402 violations where imports just need to be moved
after docstrings and comments to the top of the file.
"""

import subprocess
from pathlib import Path
from typing import List, Tuple

def get_simple_e402_files() -> List[str]:
    """Get files categorized as 'simple' for E402 fixes."""
    # From our analysis, these are the simple files (1-3 violations each)
    simple_files = [
        "fix_deprecated_typing.py",
        "fix_syntax_errors.py", 
        "fix_tests_typing.py",
        "governance/guardian_policies.py",
        "governance/guardian_reflector.py",
        "governance/guardian_serializers.py",
        "governance/policy.py",
        "governance/reflection.py",
        "governance/reflection_systems.py",
        "lukhas_website/lukhas/api/middleware/audit.py",
        "lukhas_website/lukhas/api/middleware/metrics.py",
        "matriz/consciousness/reflection/unified_reflection.py",
        "serve/api/integrated_consciousness_api.py",
        "tools/analysis/comprehensive_f821_eliminator.py",
        "tools/ci/f821_import_inserter.py",
        "tools/ci/f821_scan.py",
        "tools/fix_f821_mass_elimination.py",
        "tools/t4_master_fix.py"
    ]

    # Filter to existing files
    existing_files = []
    for file_path in simple_files:
        if Path(file_path).exists():
            existing_files.append(file_path)

    return existing_files

def fix_simple_e402(file_path: str) -> bool:
    """
    Fix simple E402 violations in a file by moving imports to proper location.

    Strategy:
    1. Identify proper location after docstring/comments
    2. Extract misplaced imports
    3. Move them to correct position
    4. Preserve file functionality
    """

    try:
        path = Path(file_path)
        lines = path.read_text().splitlines()

        # Find where imports should start (after docstring/header comments)
        import_start_line = find_import_start_position(lines)

        # Find all import lines that are misplaced
        misplaced_imports = find_misplaced_imports(lines, import_start_line)

        if not misplaced_imports:
            return True  # No work needed

        # Extract and reorganize
        new_lines = reorganize_imports(lines, import_start_line, misplaced_imports)

        # Write back to file
        path.write_text('\n'.join(new_lines) + '\n')

        print(f"✅ Fixed {file_path} - moved {len(misplaced_imports)} imports")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def find_import_start_position(lines: List[str]) -> int:
    """Find the line number where imports should start."""

    in_docstring = False
    docstring_quote = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip shebang and encoding
        if stripped.startswith('#!') or 'coding:' in stripped or 'encoding:' in stripped:
            continue

        # Handle docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_quote = '"""' if stripped.startswith('"""') else "'''"
                if stripped.count(docstring_quote) >= 2:
                    # Single line docstring
                    continue
                else:
                    # Multi-line docstring starts
                    in_docstring = True
                    continue
        else:
            # We're in a docstring, look for end
            if docstring_quote in stripped:
                in_docstring = False
                docstring_quote = None
                continue

        # Skip comments and empty lines
        if stripped.startswith('#') or not stripped:
            continue

        # Skip from __future__ imports (must be at top)
        if stripped.startswith('from __future__'):
            continue

        # Found first non-comment, non-docstring line
        return i

    # Default to end of file if no content found
    return len(lines)

def find_misplaced_imports(lines: List[str], proper_start: int) -> List[Tuple[int, str]]:
    """Find import lines that appear after the proper import position."""

    misplaced = []

    for i, line in enumerate(lines):
        if i < proper_start:
            continue

        stripped = line.strip()

        # Check if this is an import line
        if (stripped.startswith('import ') or stripped.startswith('from ')) and not stripped.startswith('#'):
            # Skip imports that are likely conditional or in functions
            if is_safe_to_move_import(lines, i):
                misplaced.append((i, line))

    return misplaced

def is_safe_to_move_import(lines: List[str], import_line: int) -> bool:
    """Check if an import is safe to move to top of file."""

    # Look at context around the import
    context_start = max(0, import_line - 3)
    context_end = min(len(lines), import_line + 2)

    context = '\n'.join(lines[context_start:context_end])

    # Don't move if it's inside a function/class/conditional
    unsafe_patterns = [
        'def ',
        'class ',
        'if ',
        'try:',
        'except',
        'with ',
        'for ',
        'while ',
        'elif ',
        'else:',
        'sys.path'
    ]

    for pattern in unsafe_patterns:
        if pattern in context:
            return False

    return True

def reorganize_imports(lines: List[str], import_start: int, misplaced_imports: List[Tuple[int, str]]) -> List[str]:
    """Reorganize the file to move imports to proper position."""

    new_lines = []
    misplaced_line_nums = {line_num for line_num, _ in misplaced_imports}

    # Copy lines before import position, skipping misplaced imports
    for i, line in enumerate(lines):
        if i < import_start and i not in misplaced_line_nums:
            new_lines.append(line)

    # Add the misplaced imports at the proper position
    import_lines = [import_line for _, import_line in misplaced_imports]
    if import_lines:
        new_lines.extend(import_lines)
        if import_start < len(lines) and lines[import_start].strip():
            new_lines.append('')  # Add blank line after imports

    # Copy remaining lines, skipping misplaced imports
    for i, line in enumerate(lines):
        if i >= import_start and i not in misplaced_line_nums:
            new_lines.append(line)

    return new_lines

def validate_syntax(file_path: str) -> bool:
    """Validate that the file still has correct syntax after changes."""
    try:
        result = subprocess.run(
            ['python3', '-m', 'py_compile', file_path],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def main():
    """Fix simple E402 violations in identified files."""

    print("🔧 E402 Phase 1: Fixing Simple Import Issues")
    print("=" * 50)

    simple_files = get_simple_e402_files()

    if not simple_files:
        print("✅ No simple E402 files found to fix")
        return

    print(f"📋 Found {len(simple_files)} files to fix:")
    for file_path in simple_files:
        print(f"   • {file_path}")
    print()

    success_count = 0

    for file_path in simple_files:
        print(f"🔄 Processing {file_path}...")

        # Check current E402 violations
        result = subprocess.run(
            ['python3', '-m', 'ruff', 'check', '--select', 'E402', '--no-fix', file_path],
            capture_output=True, text=True
        )

        if 'E402' not in result.stdout:
            print(f"   ℹ️  No E402 violations found, skipping")
            continue

        # Fix the file
        if fix_simple_e402(file_path):
            # Validate syntax is still correct
            if validate_syntax(file_path):
                success_count += 1
            else:
                print(f"   ⚠️  Syntax error after fix, you may need to check {file_path}")

    print(f"\n📊 Results: {success_count}/{len(simple_files)} files fixed successfully")

    # Check overall E402 improvement
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'E402', '--no-fix', '.'],
        capture_output=True, text=True
    )

    remaining_count = result.stdout.count('E402')
    print(f"📈 Remaining E402 violations: {remaining_count}")

if __name__ == "__main__":
    main()