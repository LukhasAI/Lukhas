#!/usr/bin/env python3
"""
Final Constellation Consistency Codemod

Ensures complete Trinity → Constellation migration and updates all
constellation definitions to be consistent with the dynamic star-node model.

Changes:
1. Remaining Trinity → Constellation references
2. "4-star" → "dynamic constellation" (not limited to 4 stars)
3. Fixed star counts → organic/scalable constellation model
4. Consistent constellation terminology throughout

Usage:
    python3 scripts/codemods/constellation_consistency_final.py --apply
"""

import argparse
import re
from pathlib import Path

# Repository root
ROOT = Path(__file__).resolve().parents[2]

# Comprehensive replacement patterns
REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    # Remaining Trinity references
    (re.compile(r'\bTrinity Framework\b'), 'Constellation Framework'),
    (re.compile(r'\bTRINITY_FRAMEWORK\b'), 'CONSTELLATION_FRAMEWORK'),
    (re.compile(r'\btrinity_framework\b'), 'constellation_framework'),
    (re.compile(r'\bTrinity\b(?=\s+(?:[Ff]ramework|[Ii]ntegration|[Cc]oordination|[Cc]onsciousness|[Ii]dentity|[Cc]omponents))'), 'Constellation'),

    # Trinity-specific method and class names
    (re.compile(r'\bget_trinity_context\b'), 'get_constellation_context'),
    (re.compile(r'\btrinity_integration\b'), 'constellation_integration'),
    (re.compile(r'\btrinity_status\b'), 'constellation_status'),
    (re.compile(r'\bTrinityState\b'), 'ConstellationState'),
    (re.compile(r'\bTrinityIntegrator\b'), 'ConstellationIntegrator'),
    (re.compile(r'\bTrinityFrameworkValidator\b'), 'ConstellationFrameworkValidator'),
    (re.compile(r'\btrinity_framework_validator\b'), 'constellation_framework_validator'),
    (re.compile(r'\btrinity_framework_monitor\b'), 'constellation_framework_monitor'),

    # Directory and file names with trinity
    (re.compile(r'/trinity/'), '/constellation/'),
    (re.compile(r'trinity_integration\.py'), 'constellation_integration.py'),

    # Fixed 4-star references → Dynamic constellation model
    (re.compile(r'\b4-star Constellation Framework\b'), 'Constellation Framework'),
    (re.compile(r'\b4-Star Constellation Framework\b'), 'Constellation Framework'),
    (re.compile(r'\bfour-star Constellation Framework\b'), 'Constellation Framework'),
    (re.compile(r'\bFour-Star Constellation Framework\b'), 'Constellation Framework'),
    (re.compile(r'\b4-star constellation\b'), 'constellation'),
    (re.compile(r'\b4-Star constellation\b'), 'constellation'),
    (re.compile(r'\bfour-star constellation\b'), 'constellation'),
    (re.compile(r'\bFour-Star constellation\b'), 'constellation'),

    # Orchestration references - replace fixed counts with dynamic
    (re.compile(r'\b4-Star Orchestration\b'), 'Dynamic Constellation Orchestration'),
    (re.compile(r'\b4-star orchestration\b'), 'dynamic constellation orchestration'),
    (re.compile(r'\b4-Star Framework Active\b'), 'Dynamic Constellation Framework Active'),
    (re.compile(r'\b4-star framework\b'), 'constellation framework'),

    # Documentation improvements - emphasize dynamic/scalable nature
    (re.compile(r'The \*\*4-star Constellation Framework\*\*'), 'The **Constellation Framework**'),
    (re.compile(r'The 4-star Constellation Framework'), 'The Constellation Framework'),
    (re.compile(r'across the 4-star Constellation Framework'), 'across the Constellation Framework'),
    (re.compile(r'coordinates across the 4-star Constellation Framework'), 'coordinates across the dynamic Constellation Framework'),

    # Specific count references in descriptions
    (re.compile(r'"4-Star Constellation Framework stars"'), '"Dynamic Constellation Framework stars"'),
    (re.compile(r'4-star system'), 'constellation system'),
    (re.compile(r'4-Star system'), 'constellation system'),
    (re.compile(r'four-star system'), 'constellation system'),

    # Comment and docstring updates
    (re.compile(r'# 4-star'), '# Constellation'),
    (re.compile(r'# Four-star'), '# Constellation'),
    (re.compile(r'4-star model'), 'constellation model'),
    (re.compile(r'four-star model'), 'constellation model'),

    # Specific file paths that need updating
    (re.compile(r'lukhas/trinity/'), 'lukhas/constellation/'),
    (re.compile(r'candidate/consciousness/trinity/'), 'candidate/consciousness/constellation/'),

    # Log messages and status indicators
    (re.compile(r'Trinity integration'), 'Constellation integration'),
    (re.compile(r'Trinity coordination'), 'Constellation coordination'),
    (re.compile(r'Trinity status'), 'Constellation status'),
    (re.compile(r'Trinity health'), 'Constellation health'),

    # Configuration and settings
    (re.compile(r'trinity_enabled'), 'constellation_enabled'),
    (re.compile(r'TRINITY_ENABLED'), 'CONSTELLATION_ENABLED'),
    (re.compile(r'trinity_mode'), 'constellation_mode'),
    (re.compile(r'TRINITY_MODE'), 'CONSTELLATION_MODE'),

    # Branding and messaging consistency
    (re.compile(r'traditional monolithic AI architectures with a distributed cognitive coordination system'),
     'traditional monolithic AI architectures with a dynamic constellation of cognitive domains'),

    # Update specific constellation star language to be more flexible
    (re.compile(r'4 stars: ⚛️ ✦ 🔬 🛡️'), 'core stars: ⚛️ ✦ 🔬 🛡️ (with dynamic expansion)'),
    (re.compile(r'four core stars'), 'core constellation stars'),
    (re.compile(r'Four core stars'), 'Core constellation stars'),
]

# File patterns to include
INCLUDE_PATTERNS = ['.py', '.md', '.txt', '.yaml', '.yml', '.json', '.rst']

# Directories to scan
SCAN_DIRS = [
    '.',  # Scan entire repository
]

# Files and directories to exclude
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    '.venv',
    'node_modules',
    '*.pyc',
    '*.pyo',
    '*.egg-info',
    'build',
    'dist',
    '.bak'
]


def should_skip_path(path: Path) -> bool:
    """Check if path should be skipped."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)


def find_files_to_process() -> list[Path]:
    """Find all files that need consistency updates."""
    files = []

    for scan_dir in SCAN_DIRS:
        scan_path = ROOT / scan_dir
        if not scan_path.exists():
            continue

        for file_path in scan_path.rglob('*'):
            if (file_path.is_file() and
                not should_skip_path(file_path) and
                file_path.suffix in INCLUDE_PATTERNS):
                files.append(file_path)

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
    """Process a single file for consistency updates."""
    try:
        with open(file_path, encoding='utf-8') as f:
            original_content = f.read()
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        if not dry_run:
            print(f"Skipping {file_path}: {e}")
        return False, 0

    new_content, change_count = apply_replacements(original_content)

    if change_count == 0:
        return False, 0

    if dry_run:
        print(f"DRY-RUN: {file_path.relative_to(ROOT)} - {change_count} changes")
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

        print(f"UPDATED: {file_path.relative_to(ROOT)} - {change_count} changes")
        return True, change_count


def main():
    """Main codemod execution."""
    parser = argparse.ArgumentParser(description='Final Constellation Consistency Codemod')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without applying')
    parser.add_argument('--apply', action='store_true',
                       help='Apply the changes to files')
    parser.add_argument('--trinity-only', action='store_true',
                       help='Only fix Trinity references, skip constellation updates')

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: Must specify either --dry-run or --apply")
        parser.print_help()
        return 1

    if args.apply and args.dry_run:
        print("Error: Cannot specify both --dry-run and --apply")
        return 1

    dry_run = args.dry_run

    print("🌌 Final Constellation Consistency Codemod")
    print(f"Mode: {'DRY-RUN' if dry_run else 'APPLY CHANGES'}")
    if args.trinity_only:
        print("Scope: Trinity references only")
    else:
        print("Scope: Complete constellation consistency")
    print(f"Repository: {ROOT}")
    print("=" * 70)

    # Filter replacements if trinity-only mode
    if args.trinity_only:
        global REPLACEMENTS
        REPLACEMENTS = [r for r in REPLACEMENTS if 'trinity' in r[0].pattern.lower() or 'Trinity' in r[0].pattern]

    # Find files to process
    files_to_process = find_files_to_process()
    print(f"Found {len(files_to_process)} files to scan")

    # Process files
    modified_files = []
    total_changes = 0

    for file_path in files_to_process:
        was_modified, change_count = process_file(file_path, dry_run)
        if was_modified:
            modified_files.append((file_path, change_count))
            total_changes += change_count

    # Summary
    print("=" * 70)
    print("Summary:")
    print(f"Files scanned: {len(files_to_process)}")
    print(f"Files modified: {len(modified_files)}")
    print(f"Total changes: {total_changes}")

    if modified_files and not dry_run:
        print("\nTop 10 most changed files:")
        for file_path, count in sorted(modified_files, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = file_path.relative_to(ROOT)
            print(f"  {rel_path}: {count} changes")

    if dry_run and modified_files:
        print("\n🚀 To apply changes, run:")
        print(f"python3 {__file__} --apply")
        if args.trinity_only:
            print(f"python3 {__file__} --apply --trinity-only")

    return 0


if __name__ == '__main__':
    exit(main())
