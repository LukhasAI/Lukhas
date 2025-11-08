#!/usr/bin/env python3
"""
Comprehensive Trinity → Constellation Framework Codemod

This script systematically updates Constellation Framework references to Constellation Framework
across Python files, preserving 4-star system mapping and updating terminology comprehensively.

Mapping:
- Constellation Framework → Constellation Framework
- Trinity → Constellation (in context)
- triad → constellation (identifiers)
- trinity → constellation (identifiers)

Usage:
    python3 scripts/codemods/trinity_to_constellation_comprehensive.py --apply

Options:
    --dry-run    Show what would be changed without applying
    --apply      Apply the changes to files
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing importTuple

# Repository root
ROOT = Path(__file__).resolve().parents[2]

# Comprehensive replacement patterns
REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    # Framework name replacements
    (re.compile(r'\bTrinity Framework\b'), 'Constellation Framework'),
    (re.compile(r'\bTRINITY_FRAMEWORK\b'), 'CONSTELLATION_FRAMEWORK'),
    (re.compile(r'\btrinity_framework\b'), 'constellation_framework'),

    # Method and function names
    (re.compile(r'\bget_triad_context\b'), 'get_constellation_context'),
    (re.compile(r'\bget_trinity_context\b'), 'get_constellation_context'),
    (re.compile(r'\binitialize_triad_frameworks\b'), 'initialize_constellation_frameworks'),
    (re.compile(r'\binitialize_trinity_frameworks\b'), 'initialize_constellation_frameworks'),
    (re.compile(r'\bprocess_triad_decision\b'), 'process_constellation_decision'),
    (re.compile(r'\bprocess_trinity_decision\b'), 'process_constellation_decision'),
    (re.compile(r'\bactivate_triad_framework\b'), 'activate_constellation_framework'),
    (re.compile(r'\bactivate_trinity_framework\b'), 'activate_constellation_framework'),
    (re.compile(r'\bget_triad_status\b'), 'get_constellation_status'),
    (re.compile(r'\bget_trinity_status\b'), 'get_constellation_status'),
    (re.compile(r'\bget_triad_metrics\b'), 'get_constellation_metrics'),
    (re.compile(r'\bget_trinity_metrics\b'), 'get_constellation_metrics'),
    (re.compile(r'\bget_triad_integrator\b'), 'get_constellation_integrator'),
    (re.compile(r'\bget_trinity_integrator\b'), 'get_constellation_integrator'),
    (re.compile(r'\binitialize_triad_consciousness\b'), 'initialize_constellation_consciousness'),
    (re.compile(r'\binitialize_trinity_consciousness\b'), 'initialize_constellation_consciousness'),

    # Class names
    (re.compile(r'\bTrinityFrameworkIntegrator\b'), 'ConstellationFrameworkIntegrator'),
    (re.compile(r'\bTriadFrameworkIntegrator\b'), 'ConstellationFrameworkIntegrator'),
    (re.compile(r'\bTrinityIntegrationConfig\b'), 'ConstellationIntegrationConfig'),
    (re.compile(r'\bTriadIntegrationConfig\b'), 'ConstellationIntegrationConfig'),
    (re.compile(r'\bTrinityState\b'), 'ConstellationState'),
    (re.compile(r'\bTriadState\b'), 'ConstellationState'),

    # Variable and parameter names
    (re.compile(r'\btrinity_coupling\b'), 'constellation_coupling'),
    (re.compile(r'\btriad_coupling\b'), 'constellation_coupling'),
    (re.compile(r'\btrinity_status\b'), 'constellation_status'),
    (re.compile(r'\btriad_status\b'), 'constellation_status'),
    (re.compile(r'\btrinity_integration\b'), 'constellation_integration'),
    (re.compile(r'\btriad_integration\b'), 'constellation_integration'),
    (re.compile(r'\btrinity_metrics\b'), 'constellation_metrics'),
    (re.compile(r'\btriad_metrics\b'), 'constellation_metrics'),

    # Parameter names in function calls
    (re.compile(r'\bconstellation_framework\s*=\s*"([⚛️🧠🛡️])"'), r'constellation_star="\1"'),

    # Comments and docstrings (contextual)
    (re.compile(r'# Constellation Framework'), '# Constellation Framework'),
    (re.compile(r'Constellation Framework integration'), 'Constellation Framework integration'),
    (re.compile(r'Constellation Framework coordination'), 'Constellation Framework coordination'),
    (re.compile(r'Constellation Framework consciousness'), 'Constellation Framework consciousness'),
    (re.compile(r'Constellation Framework identity'), 'Constellation Framework identity'),
    (re.compile(r'Constellation Framework components'), 'Constellation Framework components'),
    (re.compile(r'Constellation components'), 'Constellation components'),

    # Generic Trinity → Constellation (careful with context)
    (re.compile(r'\bTrinity\b(?=\s+(?:Framework|integration|coordination|consciousness|identity|components))'), 'Constellation'),

    # Logging messages
    (re.compile(r'Constellation Framework Integrator'), 'Constellation Framework Integrator'),
    (re.compile(r'Constellation Framework Integration'), 'Constellation Framework Integration'),
    (re.compile(r'Constellation Framework integration'), 'Constellation Framework integration'),
    (re.compile(r'Constellation integration'), 'Constellation integration'),
]

# Directories to scan (Python files only)
SCAN_DIRS = [
    'lukhas',
    'candidate',
    'scripts',
    'tests',
    'tools'
]

# Files to exclude
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    '.venv',
    '.env',
    'node_modules',
    '*.pyc',
    '*.pyo',
    '*.egg-info',
    'build',
    'dist'
]


def should_skip_path(path: Path) -> bool:
    """Check if path should be skipped."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)


def find_python_files() -> list[Path]:
    """Find all Python files to process."""
    files = []

    for scan_dir in SCAN_DIRS:
        scan_path = ROOT / scan_dir
        if not scan_path.exists():
            continue

        for py_file in scan_path.rglob('*.py'):
            if not should_skip_path(py_file):
                files.append(py_file)

    return sorted(files)


def apply_replacements(content: str) -> tuple[str, int]:
    """Apply all replacement patterns to content."""
    new_content = content
    total_changes = 0

    for pattern, replacement in REPLACEMENTS:
        new_content, count = pattern.subn(replacement, new_content)
        total_changes += count

    return new_content, total_changes


def process_file(file_path: Path, dry_run: bool = True) -> tuple[bool, int]:
    """Process a single file for Trinity → Constellation replacements."""
    try:
        with open(file_path, encoding='utf-8') as f:
            original_content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Skipping {file_path}: {e}")
        return False, 0

    new_content, change_count = apply_replacements(original_content)

    if change_count == 0:
        return False, 0

    if dry_run:
        print(f"DRY-RUN: {file_path} - {change_count} changes")
        return True, change_count
    else:
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        if not backup_path.exists():
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)

        # Apply changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"UPDATED: {file_path} - {change_count} changes")
        return True, change_count


def main():
    """Main codemod execution."""
    parser = argparse.ArgumentParser(description='Trinity → Constellation Framework codemod')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without applying')
    parser.add_argument('--apply', action='store_true',
                       help='Apply the changes to files')

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: Must specify either --dry-run or --apply")
        parser.print_help()
        return 1

    if args.apply and args.dry_run:
        print("Error: Cannot specify both --dry-run and --apply")
        return 1

    dry_run = args.dry_run

    print("🌌 Trinity → Constellation Framework Codemod")
    print(f"Mode: {'DRY-RUN' if dry_run else 'APPLY CHANGES'}")
    print(f"Repository: {ROOT}")
    print("=" * 60)

    # Find Python files
    python_files = find_python_files()
    print(f"Found {len(python_files)} Python files to scan")

    # Process files
    modified_files = []
    total_changes = 0

    for file_path in python_files:
        was_modified, change_count = process_file(file_path, dry_run)
        if was_modified:
            modified_files.append((file_path, change_count))
            total_changes += change_count

    # Summary
    print("=" * 60)
    print("Summary:")
    print(f"Files scanned: {len(python_files)}")
    print(f"Files modified: {len(modified_files)}")
    print(f"Total changes: {total_changes}")

    if modified_files:
        print("\nModified files:")
        for file_path, count in modified_files:
            rel_path = file_path.relative_to(ROOT)
            print(f"  {rel_path}: {count} changes")

    if dry_run and modified_files:
        print("\n🚀 To apply changes, run:")
        print(f"python3 {__file__} --apply")

    return 0


if __name__ == '__main__':
    exit(main())
