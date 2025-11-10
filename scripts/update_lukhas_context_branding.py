#!/usr/bin/env python3
"""
Update lukhas_context.md files with branding compliance
Following LUKHAS Brand Specialist guidelines and T4 (0.01%) standards

References:
- docs/gonzo/BRAND_SPECIALIST.md
- branding/policy/BRANDING_POLICY.md
- branding/TONE_GUIDE.md
- branding/LAMBDA_SYMBOL_GUIDELINES.md
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class BrandingValidator:
    """Validates and fixes branding violations in lukhas_context.md files"""

    # Branding standards from BRANDING_POLICY.md
    DEPRECATED_TERMS = {
        "LUKHAS Cognitive AI": "LUKHAS AI",
        "Cognitive AI technology": "consciousness technology",
        "MATADA": "MATRIZ",
        "Trinity Framework": "Constellation Framework",
        "quantum processing": "quantum-inspired",
        "bio processes": "bio-inspired",
        "sentient systems": "awareness systems",
    }

    # Prohibited terms that should trigger warnings
    PROHIBITED_TERMS = [
        "production-ready",
        "guaranteed",
        "flawless",
        "perfect",
        "zero-risk",
        "unlimited",
        "unbreakable",
        "foolproof",
        "bulletproof",
        "revolutionary",
        "groundbreaking",
        "game-changing",
        "ultimate",
        "supreme",
        "best-in-class",
    ]

    def __init__(self):
        self.violations: List[Dict] = []
        self.fixes: List[Dict] = []

    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate a lukhas_context.md file for branding compliance"""
        issues = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for deprecated terms
        for old_term, new_term in self.DEPRECATED_TERMS.items():
            if old_term in content:
                issues.append(f"Deprecated term '{old_term}' should be '{new_term}'")
                self.violations.append({
                    'file': str(file_path),
                    'type': 'deprecated_term',
                    'old': old_term,
                    'new': new_term
                })

        # Check for prohibited terms
        for term in self.PROHIBITED_TERMS:
            if re.search(rf'\b{term}\b', content, re.IGNORECASE):
                issues.append(f"Prohibited term '{term}' found")
                self.violations.append({
                    'file': str(file_path),
                    'type': 'prohibited_term',
                    'term': term
                })

        # Check for proper YAML frontmatter
        if not content.startswith('---\n'):
            issues.append("Missing YAML frontmatter")

        # Check for Last Updated date
        if 'Last Updated' not in content:
            issues.append("Missing 'Last Updated' field")

        return len(issues) == 0, issues

    def fix_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Fix branding violations in a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes = []

        # Fix deprecated terms
        for old_term, new_term in self.DEPRECATED_TERMS.items():
            if old_term in content:
                content = content.replace(old_term, new_term)
                changes.append(f"Replaced '{old_term}' with '{new_term}'")

        # Update Last Updated date
        today = datetime.now().strftime('%Y-%m-%d')

        # Update existing Last Updated field
        content = re.sub(
            r'\*\*Last Updated\*\*: \d{4}-\d{2}-\d{2}',
            f'**Last Updated**: {today}',
            content
        )

        # Add Last Updated if missing
        if '**Last Updated**:' not in content:
            # Try to add it after Language field
            content = re.sub(
                r'(\*\*Language\*\*: .+)',
                rf'\1\n**Last Updated**: {today}',
                content
            )
            changes.append(f"Added Last Updated: {today}")
        else:
            changes.append(f"Updated Last Updated to {today}")

        # Ensure proper YAML frontmatter
        if not content.startswith('---\n'):
            content = '---\nstatus: wip\ntype: documentation\n---\n' + content
            changes.append("Added YAML frontmatter")

        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            self.fixes.append({
                'file': str(file_path),
                'changes': changes
            })
            return True

        return False


def find_lukhas_context_files(root_dir: Path, skip_archived: bool = True) -> List[Path]:
    """Find all lukhas_context.md files in the repository"""
    files = []

    for file_path in root_dir.rglob('lukhas_context.md'):
        # Skip archived directories
        if skip_archived and 'archive' in file_path.parts:
            continue

        files.append(file_path)

    return sorted(files)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Update lukhas_context.md files with branding compliance'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--include-archived',
        action='store_true',
        help='Include archived directories'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate, do not fix'
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    print("🔍 Finding lukhas_context.md files...")
    files = find_lukhas_context_files(
        repo_root,
        skip_archived=not args.include_archived
    )

    print(f"📁 Found {len(files)} files")

    # Validate and fix
    validator = BrandingValidator()

    files_with_issues = 0
    files_fixed = 0

    for file_path in files:
        is_valid, issues = validator.validate_file(file_path)

        if not is_valid:
            files_with_issues += 1
            print(f"\n❌ {file_path.relative_to(repo_root)}")
            for issue in issues:
                print(f"   - {issue}")

            if not args.validate_only:
                if validator.fix_file(file_path, dry_run=args.dry_run):
                    files_fixed += 1
                    if args.dry_run:
                        print("   ✓ Would fix")
                    else:
                        print("   ✓ Fixed")

    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Total files: {len(files)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Files fixed: {files_fixed}")

    if validator.violations:
        print(f"\n⚠️  Total violations: {len(validator.violations)}")

        # Group by type
        by_type = {}
        for v in validator.violations:
            vtype = v['type']
            by_type.setdefault(vtype, []).append(v)

        for vtype, violations in by_type.items():
            print(f"   - {vtype}: {len(violations)}")

    if validator.fixes:
        print(f"\n✅ Total fixes applied: {len(validator.fixes)}")

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")


if __name__ == '__main__':
    main()
