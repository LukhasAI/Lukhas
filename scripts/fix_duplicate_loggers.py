#!/usr/bin/env python3
"""
Automated script to fix common logging standard violations.

Usage:
    python scripts/fix_duplicate_loggers.py --dry-run  # Preview changes
    python scripts/fix_duplicate_loggers.py             # Apply fixes
    python scripts/fix_duplicate_loggers.py --path lukhas/core  # Fix specific path
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class LoggingStandardFixer:
    """Fix common logging standard violations."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_modified = 0
        self.issues_fixed = 0

    def find_python_files(self, root_path: Path) -> List[Path]:
        """Find all Python files in the given path."""
        if root_path.is_file():
            return [root_path]
        return list(root_path.rglob("*.py"))

    def fix_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Fix logging issues in a single file.

        Returns:
            (modified, issues_found)
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            issues = []

            # Fix 1: Replace logging.warn with logging.warning
            warn_pattern = r'\blogging\.warn\('
            if re.search(warn_pattern, content):
                content = re.sub(warn_pattern, 'logging.warning(', content)
                issues.append("Replaced deprecated logging.warn with logging.warning")

            # Fix 2: Detect duplicate logger definitions
            logger_lines = []
            for i, line in enumerate(content.split('\n'), 1):
                if re.match(r'^logger\s*=\s*logging\.getLogger', line.strip()):
                    logger_lines.append((i, line))

            if len(logger_lines) > 1:
                # Keep only the first logger definition
                issues.append(f"Found {len(logger_lines)} logger definitions, keeping only the first")
                lines = content.split('\n')
                for line_num, _ in logger_lines[1:]:
                    if line_num - 1 < len(lines):
                        lines[line_num - 1] = "# " + lines[line_num - 1]  # Comment out duplicates
                content = '\n'.join(lines)

            # Fix 3: Replace hardcoded logger names with __name__
            hardcoded_pattern = r'logging\.getLogger\(["\'](?!__name__)[^"\']+["\']\)'
            if re.search(hardcoded_pattern, content):
                content = re.sub(
                    hardcoded_pattern,
                    'logging.getLogger(__name__)',
                    content
                )
                issues.append("Replaced hardcoded logger names with __name__")

            # Fix 4: Flag direct root logger usage (but don't auto-fix, too risky)
            root_logger_pattern = r'\blogging\.(info|debug|warning|error|critical|exception)\('
            if re.search(root_logger_pattern, content):
                issues.append("⚠️  WARNING: Direct root logger usage detected (manual fix required)")

            modified = content != original_content

            if modified and not self.dry_run:
                file_path.write_text(content, encoding="utf-8")
                self.files_modified += 1
                self.issues_fixed += len(issues)

            return modified, issues

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}", file=sys.stderr)
            return False, []

    def run(self, path: Path) -> None:
        """Run the fixer on all Python files in the path."""
        files = self.find_python_files(path)
        print(f"Scanning {len(files)} Python files in {path}...")

        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified\n")

        modified_files = []

        for file_path in files:
            # Skip test files and migrations
            if "test_" in file_path.name or "migration" in str(file_path):
                continue

            modified, issues = self.fix_file(file_path)

            if issues:
                relative_path = file_path.relative_to(Path.cwd())
                print(f"\n📄 {relative_path}")
                for issue in issues:
                    print(f"   {'[DRY RUN] ' if self.dry_run else ''}✓ {issue}")

                if modified:
                    modified_files.append(file_path)

        print("\n" + "=" * 60)
        if self.dry_run:
            print(f"🔍 DRY RUN SUMMARY:")
            print(f"   Would modify {len(modified_files)} files")
        else:
            print(f"✅ SUMMARY:")
            print(f"   Modified {self.files_modified} files")
            print(f"   Fixed {self.issues_fixed} issues")

        if modified_files:
            print(f"\n📋 Modified files:")
            for f in modified_files[:10]:
                print(f"   - {f.relative_to(Path.cwd())}")
            if len(modified_files) > 10:
                print(f"   ... and {len(modified_files) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="Fix common logging standard violations"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Path to scan (default: current directory)"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"❌ Error: Path {args.path} does not exist", file=sys.stderr)
        sys.exit(1)

    fixer = LoggingStandardFixer(dry_run=args.dry_run)
    fixer.run(args.path)


if __name__ == "__main__":
    main()
