#!/usr/bin/env python3
"""
Fix test import errors by mapping to actual module locations.

Strategy:
1. Collect all ModuleNotFoundError from pytest
2. Find actual module locations in codebase
3. Update imports with correct paths
4. Validate by re-running collection
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def get_import_errors():
    """Get all import errors from pytest collection."""
    result = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )

    errors = defaultdict(list)
    current_file = None

    for line in result.stderr.split('\n'):
        # Extract test file
        if line.startswith('ERROR '):
            match = re.search(r'ERROR (tests/\S+\.py)', line)
            if match:
                current_file = match.group(1)

        # Extract missing module
        elif current_file and 'ModuleNotFoundError' in line:
            match = re.search(r"No module named '([^']+)'", line)
            if match:
                module = match.group(1)
                if module not in errors[current_file]:
                    errors[current_file].append(module)

        # Extract import name errors
        elif current_file and 'cannot import name' in line:
            match = re.search(r"cannot import name '([^']+)' from '([^']+)'", line)
            if match:
                name, from_module = match.groups()
                errors[current_file].append(f"{from_module}.{name}")

    return dict(errors)

def find_module_location(module_name):
    """Find where a module actually exists."""
    # Try variations
    candidates = [
        module_name,  # consciousness.dream
        f"candidate.{module_name}",  # candidate.consciousness.dream
        f"lukhas.{module_name}",  # consciousness.dream (via hook)
    ]

    # Also try partial matches
    parts = module_name.split('.')
    if len(parts) > 1:
        candidates.extend([
            parts[0],  # consciousness
            f"candidate.{parts[0]}",  # candidate.consciousness
            '.'.join(parts[:-1]),  # consciousness (without .dream)
        ])

    # Check which ones exist as directories or .py files
    for candidate in candidates:
        path_parts = candidate.split('.')

        # Check as package (directory with __init__.py)
        pkg_path = Path(*path_parts)
        if pkg_path.is_dir():
            if (pkg_path / '__init__.py').exists():
                return candidate, str(pkg_path)
            else:
                # Missing __init__.py - note for creation
                return candidate, f"MISSING_INIT:{pkg_path}"

        # Check as module (.py file)
        mod_path = Path(*path_parts[:-1]) / f"{path_parts[-1]}.py"
        if mod_path.exists():
            return candidate, str(mod_path)

    return None, None

def fix_imports_in_file(test_file, missing_modules):
    """Fix imports in a test file."""
    file_path = Path(test_file)
    if not file_path.exists():
        return False, []

    content = file_path.read_text()
    original = content
    fixes_applied = []

    for module in missing_modules:
        # Find actual location
        actual_module, location = find_module_location(module)

        if actual_module and not location.startswith('MISSING_INIT'):
            # Replace import
            patterns = [
                f"from {module} import",
                f"import {module}",
            ]

            for pattern in patterns:
                if pattern in content:
                    new_pattern = pattern.replace(module, actual_module)
                    content = content.replace(pattern, new_pattern)
                    fixes_applied.append(f"{module} → {actual_module}")

        elif location and location.startswith('MISSING_INIT'):
            # Need to create __init__.py
            pkg_path = Path(location.replace('MISSING_INIT:', ''))
            fixes_applied.append(f"NEED_INIT: {pkg_path}")

    if content != original:
        file_path.write_text(content)
        return True, fixes_applied

    return False, fixes_applied

def create_missing_init_files():
    """Create missing __init__.py files."""
    # Common packages that need __init__.py
    packages_needing_init = [
        'consciousness',
        'consciousness/dream',
        'consciousness/awareness',
        'consciousness/reflection',
        'candidate/cognitive_core',
        'candidate/observability',
        'candidate/memory/backends',
        'governance/ethics',
        'governance/identity/core',
        'core/identity',
        'core/collective',
        'core/breakthrough',
        'memory',
        'memory/fakes',
    ]

    created = []
    for pkg in packages_needing_init:
        pkg_path = Path(pkg)
        if pkg_path.is_dir():
            init_file = pkg_path / '__init__.py'
            if not init_file.exists():
                # Create minimal __init__.py
                init_file.write_text(f'"""{pkg.replace("/", ".")} package."""\n')
                created.append(str(init_file))

    return created

def main():
    print("🔍 Step 1: Analyzing test import errors...")
    errors = get_import_errors()

    if not errors:
        print("✅ No import errors found!")
        return 0

    print(f"📊 Found {len(errors)} test files with import errors")
    print(f"📦 Total unique modules: {len({m for mods in errors.values() for m in mods})}")
    print()

    print("🔧 Step 2: Creating missing __init__.py files...")
    created_inits = create_missing_init_files()
    if created_inits:
        print(f"✅ Created {len(created_inits)} __init__.py files:")
        for init in created_inits[:10]:
            print(f"  - {init}")
        if len(created_inits) > 10:
            print(f"  ... and {len(created_inits) - 10} more")
    else:
        print("  No missing __init__.py files")
    print()

    print("🔧 Step 3: Fixing import statements...")
    fixed_count = 0
    all_fixes = []

    for test_file, missing in sorted(errors.items()):
        fixed, fixes = fix_imports_in_file(test_file, missing)
        if fixed:
            fixed_count += 1
            all_fixes.extend(fixes)
            print(f"✅ {test_file}")
            for fix in fixes[:3]:
                print(f"  - {fix}")
            if len(fixes) > 3:
                print(f"  ... and {len(fixes) - 3} more")

    print()
    print(f"📝 Fixed imports in {fixed_count} test files")
    print(f"📝 Total fixes applied: {len(all_fixes)}")
    print()

    print("🔍 Step 4: Validating fixes...")
    result = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )

    # Count remaining errors
    remaining = result.stderr.count('ERROR')
    print(f"📊 Remaining collection errors: {remaining}")

    if remaining == 0:
        print("🎉 SUCCESS: All test collection errors resolved!")
        return 0
    else:
        print(f"⚠️  Still have {remaining} errors - may need manual intervention")
        print("   Run: python3 -m pytest --collect-only -q 2>&1 | grep ERROR | head -20")
        return 1

if __name__ == "__main__":
    sys.exit(main())
