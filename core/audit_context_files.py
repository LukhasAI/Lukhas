#!/usr/bin/env python3
"""
Audits all lukhas_context.md files to report on their status and health.

This script is read-only and does not modify any files.

Usage:
    python scripts/audit_context_files.py > docs/audits/context_files_health.md
"""

import os
from pathlib import Path
from datetime import datetime
import yaml
import re


def parse_frontmatter(content: str) -> dict:
    """Parses YAML frontmatter from a markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}


def audit_file(path: Path) -> dict:
    """Audits a single context file."""
    content = path.read_text()
    frontmatter = parse_frontmatter(content)
    
    last_reviewed_str = frontmatter.get('last_reviewed', '1970-01-01')
    try:
        last_reviewed_date = datetime.strptime(str(last_reviewed_str), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        last_reviewed_date = datetime(1970, 1, 1).date()

    days_since_review = (datetime.now().date() - last_reviewed_date).days

    return {
        "path": str(path),
        "owner": frontmatter.get('owner', 'N/A'),
        "stability": frontmatter.get('stability', 'unknown'),
        "last_reviewed": last_reviewed_date,
        "days_since_review": days_since_review,
        "status": frontmatter.get('status', 'N/A'),
    }


def main():
    """Finds all lukhas_context.md files and generates a health report."""
    repo_root = Path(__file__).parent.parent
    context_files = sorted(repo_root.glob('**/lukhas_context.md'))

    audits = [audit_file(p) for p in context_files]

    # Sort by oldest review date first
    audits.sort(key=lambda x: x['days_since_review'], reverse=True)

    # Generate Markdown Report
    print("# Documentation Context File Health Audit")
    print(f"\n**Date**: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"**Found**: {len(audits)} `lukhas_context.md` files.")
    print("\nFiles are sorted by the oldest `last_reviewed` date. Anything over 180 days should be reviewed.")

    print("\n| File Path | Owner | Stability | Last Reviewed | Age (Days) | Status |")
    print("|---|---|---|---|---|---|")

    for report in audits:
        age = report['days_since_review']
        age_marker = "🔴" if age > 365 else "🟡" if age > 180 else "✅"
        
        # Make path relative for cleaner output
        relative_path = os.path.relpath(report['path'], repo_root)

        print(
            f"| {relative_path} "
            f"| {report['owner']} "
            f"| {report['stability']} "
            f"| {report['last_reviewed']} "
            f"| {age} {age_marker} "
            f"| {report['status']} |"
        )

    print("\n---")
    print("**Legend**: 🔴 > 1 year old, 🟡 > 6 months old, ✅ Fresh")


if __name__ == "__main__":
    main()