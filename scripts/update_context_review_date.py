#!/usr/bin/env python3
"""
Update context file review dates and standardize Constellation Framework references.

This script updates lukhas_context.md and claude.me files with:
- Updated last_reviewed dates
- Standardized Constellation Framework 8-star system
- Trinity → Constellation framework renaming
- Basic statistics updates

Usage:
    python3 scripts/update_context_review_date.py [--dry-run] [--path PATH]
"""

import argparse
import re
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

# Full 8-star Constellation Framework
CONSTELLATION_8_STARS = "⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum"

# Patterns to replace
TRINITY_PATTERN = re.compile(r'\bTrinity Framework\b', re.IGNORECASE)
OLD_STAR_PATTERNS = [
    r'⚛️ Anchor',
    r'✦ Trail',
    r'🔬 Horizon',
    r'🛡️ Watch',
    # Add other old star names as needed
]

class ContextFileUpdater:
    """Updates context files with standardized information."""

    def __init__(self, dry_run: bool = False, review_date: Optional[str] = None):
        self.dry_run = dry_run
        self.review_date = review_date or date.today().isoformat()
        self.conflicts: List[Tuple[Path, str]] = []
        self.updated_files: List[Path] = []
        self.skipped_files: List[Path] = []

    def update_file(self, filepath: Path) -> bool:
        """Update a single context file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            original_content = content

            # Check for conflicts/unclear situations
            if self._has_conflicts(content, filepath):
                return False

            # Update YAML frontmatter
            content = self._update_frontmatter(content)

            # Update Constellation Framework references
            content = self._update_constellation_refs(content)

            # Update Trinity → Constellation
            content = TRINITY_PATTERN.sub('Constellation Framework', content)

            # Only write if changed
            if content != original_content:
                if not self.dry_run:
                    filepath.write_text(content, encoding='utf-8')
                self.updated_files.append(filepath)
                return True
            else:
                self.skipped_files.append(filepath)
                return False

        except Exception as e:
            self.conflicts.append((filepath, f"Error: {e!s}"))
            return False

    def _has_conflicts(self, content: str, filepath: Path) -> bool:
        """Check for situations that need manual review."""
        # Skip files with very recent review dates (within 3 days)
        if 'last_reviewed: 2025-11-' in content:
            match = re.search(r'last_reviewed:\s*2025-11-(\d{2})', content)
            if match:
                day = int(match.group(1))
                if day >= 8:  # Already reviewed recently
                    self.conflicts.append((filepath, "Recently reviewed (skip)"))
                    return True

        # Skip files with custom constellation mappings that don't match standard 8
        if 'constellation_stars:' in content and CONSTELLATION_8_STARS not in content:
            lines = content.split('\n')
            for line in lines:
                if 'constellation_stars:' in line.lower():
                    # Check if it's a non-standard custom mapping
                    if '"' in line and CONSTELLATION_8_STARS not in line:
                        stars = line.split(':', 1)[1].strip().strip('"')
                        # Count stars - if not 8, might be custom
                        if stars.count('·') < 7:  # Less than 8 stars
                            self.conflicts.append((filepath, f"Custom star mapping: {stars[:80]}"))
                            return True

        return False

    def _update_frontmatter(self, content: str) -> str:
        """Update YAML frontmatter."""
        lines = content.split('\n')
        in_frontmatter = False
        updated_lines = []

        for i, line in enumerate(lines):
            if i == 0 and line.strip() == '---':
                in_frontmatter = True
                updated_lines.append(line)
                continue

            if in_frontmatter and line.strip() == '---':
                in_frontmatter = False
                updated_lines.append(line)
                continue

            if in_frontmatter:
                # Update last_reviewed
                if line.startswith('last_reviewed:') or line.startswith('updated:'):
                    key = line.split(':')[0]
                    updated_lines.append(f"{key}: {self.review_date}")
                # Update constellation_stars if present and not already 8-star
                elif line.startswith('constellation_stars:'):
                    if CONSTELLATION_8_STARS not in line:
                        updated_lines.append(f'constellation_stars: "{CONSTELLATION_8_STARS}"')
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        return '\n'.join(updated_lines)

    def _update_constellation_refs(self, content: str) -> str:
        """Update constellation framework references."""
        # Replace old star names with note about full 8-star system
        for old_pattern in OLD_STAR_PATTERNS:
            if re.search(old_pattern, content):
                # Don't auto-replace - flag for manual review instead
                pass  # Let manual review handle this

        return content

    def process_directory(self, root_path: Path, pattern: str = "**/*"):
        """Process all context files in directory tree."""
        for context_file in root_path.glob(pattern):
            if context_file.name in ['claude.me', 'lukhas_context.md']:
                print(f"Processing: {context_file.relative_to(root_path)}")
                self.update_file(context_file)

    def generate_report(self) -> str:
        """Generate summary report."""
        report = []
        report.append(f"\n{'='*80}")
        report.append("CONTEXT FILE UPDATE REPORT")
        report.append(f"{'='*80}")
        report.append(f"Review Date: {self.review_date}")
        report.append(f"Dry Run: {self.dry_run}")
        report.append(f"\nUpdated Files: {len(self.updated_files)}")
        report.append(f"Skipped Files (no changes): {len(self.skipped_files)}")
        report.append(f"Conflicts (manual review needed): {len(self.conflicts)}")

        if self.conflicts:
            report.append(f"\n{'='*80}")
            report.append("FILES REQUIRING MANUAL REVIEW:")
            report.append(f"{'='*80}")
            for filepath, reason in self.conflicts:
                report.append(f"\n{filepath}")
                report.append(f"  Reason: {reason}")

        if self.dry_run and self.updated_files:
            report.append(f"\n{'='*80}")
            report.append("FILES THAT WOULD BE UPDATED:")
            report.append(f"{'='*80}")
            for filepath in self.updated_files[:20]:  # Show first 20
                report.append(f"  {filepath}")
            if len(self.updated_files) > 20:
                report.append(f"  ... and {len(self.updated_files) - 20} more")

        return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='Update context file review dates')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be updated without making changes')
    parser.add_argument('--path', type=Path,
                       default=Path('/Users/agi_dev/LOCAL-REPOS/Lukhas'),
                       help='Root path to process (default: Lukhas repository)')
    parser.add_argument('--pattern', type=str,
                       default='**/*',
                       help='Glob pattern for files (default: **/*)')
    parser.add_argument('--date', type=str,
                       help='Review date (default: today, format: YYYY-MM-DD)')
    parser.add_argument('--report', type=Path,
                       help='Save conflict report to file')

    args = parser.parse_args()

    updater = ContextFileUpdater(dry_run=args.dry_run, review_date=args.date)

    print(f"Scanning {args.path} for context files...")
    print(f"Pattern: {args.pattern}")
    print(f"Dry run: {args.dry_run}\n")

    updater.process_directory(args.path, args.pattern)

    report = updater.generate_report()
    print(report)

    if args.report:
        args.report.write_text(report, encoding='utf-8')
        print(f"\nReport saved to: {args.report}")


if __name__ == '__main__':
    main()
