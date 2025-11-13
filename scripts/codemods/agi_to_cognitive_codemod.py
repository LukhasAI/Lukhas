#!/usr/bin/env python3
"""
AGI Core → Cognitive Core Migration Codemod

Updates all references from cognitive_core to cognitive_core and modernizes
AGI terminology to align with LUKHAS AI branding guidelines.

Changes:
- cognitive_core → cognitive_core (paths and imports)
- AGI → AI/Cognitive (in context)
- AGI Core → Cognitive Core
- Cognitive infrastructure → Cognitive infrastructure

Usage:
    python3 scripts/codemods/agi_to_cognitive_codemod.py --apply
"""

import argparse
import re
from pathlib import Path

# Repository root
ROOT = Path(__file__).resolve().parents[2]

# Comprehensive replacement patterns
REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    # Path and import updates
    (re.compile(r"\bagi_core\b"), "cognitive_core"),
    (re.compile(r"\bfrom cognitive_core\b"), "from cognitive_core"),
    (re.compile(r"\bimport cognitive_core\b"), "import cognitive_core"),
    # Directory and file references
    (re.compile(r"/cognitive_core/"), "/cognitive_core/"),
    # Class and function names with AGI
    (re.compile(r"\bAGI_Core\b"), "CognitiveCore"),
    (re.compile(r"\bAGICore\b"), "CognitiveCore"),
    (re.compile(r"\bagi_core_"), "cognitive_core_"),
    (re.compile(r"\bget_agi_core_info\b"), "get_cognitive_core_info"),
    (re.compile(r"\bAGI_SERVICE\b"), "COGNITIVE_SERVICE"),
    (re.compile(r"\bagi_service\b"), "cognitive_service"),
    (re.compile(r"\bAGIService\b"), "CognitiveService"),
    # Documentation and comments
    (re.compile(r"\bAGI Core Infrastructure\b"), "Cognitive Core Infrastructure"),
    (re.compile(r"\bAGI core\b"), "Cognitive core"),
    (re.compile(r"\bAGI capabilities\b"), "Cognitive capabilities"),
    (re.compile(r"\bAGI functionality\b"), "Cognitive functionality"),
    (re.compile(r"\bAGI infrastructure\b"), "Cognitive infrastructure"),
    (re.compile(r"\bAGI enhancement\b"), "Cognitive enhancement"),
    (re.compile(r"\bAGI testing\b"), "Cognitive testing"),
    (re.compile(r"\bAGI system\b"), "Cognitive system"),
    (re.compile(r"\bAGI platform\b"), "AI platform"),
    (re.compile(r"\bAGI architecture\b"), "AI architecture"),
    (re.compile(r"\bAGI development\b"), "AI development"),
    # Variable and config names
    (re.compile(r"\bagi_enhanced_"), "cognitive_enhanced_"),
    (re.compile(r"\bAGI_ENHANCED_"), "COGNITIVE_ENHANCED_"),
    (re.compile(r"\bagi_orchestration\b"), "cognitive_orchestration"),
    (re.compile(r"\bAGI_ORCHESTRATION\b"), "COGNITIVE_ORCHESTRATION"),
    # File and module descriptions
    (re.compile(r'"Advanced cognitive AI'), '"Advanced cognitive AI'),
    (re.compile(r'"Cognitive testing'), '"Cognitive testing'),
    (re.compile(r'"Comprehensive cognitive'), '"Comprehensive cognitive'),
    (re.compile(r"Advanced Cognitive capabilities"), "Advanced cognitive capabilities"),
    (re.compile(r"state-of-the-art cognitive AI"), "state-of-the-art cognitive AI"),
    # Logging and error messages
    (re.compile(r"Cognitive Core initialized"), "Cognitive Core initialized"),
    (re.compile(r"Cognitive service"), "Cognitive service"),
    (re.compile(r"Cognitive module"), "Cognitive module"),
]

# Directories to scan
SCAN_DIRS = [
    "cognitive_core",
    "tests/unit/cognitive_core",
    "serve",
    "scripts",
    "candidate",
    "lukhas",
    "tools",
]

# Files to exclude
EXCLUDE_PATTERNS = [
    ".git",
    "__pycache__",
    ".venv",
    "*.pyc",
    "*.pyo",
    "*.egg-info",
    "build",
    "dist",
    ".bak",
]


def should_skip_path(path: Path) -> bool:
    """Check if path should be skipped."""
    path_str = str(path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)


def find_files_to_process() -> list[Path]:
    """Find all files that need AGI → Cognitive updates."""
    files = []

    for scan_dir in SCAN_DIRS:
        scan_path = ROOT / scan_dir
        if not scan_path.exists():
            continue

        for file_path in scan_path.rglob("*"):
            if (file_path.is_file() and (not should_skip_path(file_path))) and file_path.suffix in {
                ".py",
                ".md",
                ".txt",
                ".yaml",
                ".yml",
                ".json",
                ".rst",
            }:
                # Process Python files, markdown, and other text files
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
    """Process a single file for AGI → Cognitive replacements."""
    try:
        with open(file_path, encoding="utf-8") as f:
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
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        if not backup_path.exists():
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(original_content)

        # Apply changes
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"UPDATED: {file_path} - {change_count} changes")
        return True, change_count


def main():
    """Main codemod execution."""
    parser = argparse.ArgumentParser(description="AGI Core → Cognitive Core migration codemod")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without applying"
    )
    parser.add_argument("--apply", action="store_true", help="Apply the changes to files")

    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: Must specify either --dry-run or --apply")
        parser.print_help()
        return 1

    if args.apply and args.dry_run:
        print("Error: Cannot specify both --dry-run and --apply")
        return 1

    dry_run = args.dry_run

    print("🧠 AGI Core → Cognitive Core Migration Codemod")
    print(f"Mode: {'DRY-RUN' if dry_run else 'APPLY CHANGES'}")
    print(f"Repository: {ROOT}")
    print("=" * 60)

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
    print("=" * 60)
    print("Summary:")
    print(f"Files scanned: {len(files_to_process)}")
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


if __name__ == "__main__":
    exit(main())
