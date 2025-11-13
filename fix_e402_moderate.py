#!/usr/bin/env python3
"""
E402 Phase 2: Moderate Import Fixes
====================================

Fixes moderate E402 violations where imports can be moved after
docstrings but require careful reordering.
"""

from pathlib import Path


def fix_bridge_api_validation():
    """Fix bridge/api/validation.py E402 violations."""

    file_path = Path("bridge/api/validation.py")
    if not file_path.exists():
        return False

    lines = file_path.read_text().splitlines()

    # Find the end of the docstring
    docstring_end = None
    in_docstring = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '"""' and not in_docstring:
            in_docstring = True
        elif stripped == '"""' and in_docstring:
            docstring_end = i
            break

    if docstring_end is None:
        print("Could not find docstring end")
        return False

    # Find imports that start after docstring
    import_start = docstring_end + 1
    import_lines = []
    non_import_lines = []

    # Separate imports from other code
    for i in range(import_start, len(lines)):
        line = lines[i]
        stripped = line.strip()

        if (stripped.startswith('import ') or stripped.startswith('from ')) and not stripped.startswith('#'):
            import_lines.append(line)
        else:
            non_import_lines.append((i, line))

    # Rebuild the file
    new_lines = []

    # Add everything before imports
    new_lines.extend(lines[:import_start])

    # Add organized imports
    if import_lines:
        new_lines.extend(import_lines)
        new_lines.append('')  # Blank line after imports

    # Add remaining content
    for _, line in non_import_lines:
        new_lines.append(line)

    # Write back
    file_path.write_text('\n'.join(new_lines) + '\n')
    print("✅ Fixed bridge/api/validation.py")
    return True

def fix_moderate_files():
    """Fix moderate complexity E402 files."""

    moderate_files = [
        "bridge/api/validation.py",
        "bridge/llm_wrappers/openai_modulated_service.py",
        "core/identity/consciousness_namespace_isolation.py",
        "core/identity_integration.py",
        "core/module_registry.py",
    ]

    success_count = 0

    for file_path in moderate_files[:3]:  # Start with first 3 for testing
        print(f"🔄 Fixing {file_path}...")

        if file_path == "bridge/api/validation.py":
            if fix_bridge_api_validation():
                success_count += 1
        # Add more specific fixes for other files as needed

    return success_count

if __name__ == "__main__":
    print("🔧 E402 Phase 2: Moderate Import Fixes")
    print("=" * 40)

    success_count = fix_moderate_files()
    print(f"\n📊 Fixed {success_count} files")