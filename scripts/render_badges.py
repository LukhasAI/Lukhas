#!/usr/bin/env python3
"""
LUKHAS Documentation Badge Renderer (T4/0.01%)

Synthesizes badges from front-matter (status + owner) and injects at top of docs.
Preserves H1 headings, adds badge legend to DOCUMENTATION_INDEX.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict

# Constants
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"
INDEX_PATH = DOCS_ROOT / "reference" / "DOCUMENTATION_INDEX.md"

# Badge styles (shields.io compatible)
BADGE_STYLES = {
    'status': {
        'wip': '![Status: WIP](https://img.shields.io/badge/status-wip-yellow)',
        'draft': '![Status: Draft](https://img.shields.io/badge/status-draft-orange)',
        'stable': '![Status: Stable](https://img.shields.io/badge/status-stable-green)',
        'deprecated': '![Status: Deprecated](https://img.shields.io/badge/status-deprecated-red)',
        'archived': '![Status: Archived](https://img.shields.io/badge/status-archived-gray)',
        'moved': '![Status: Moved](https://img.shields.io/badge/status-moved-blue)',
    },
    'owner_template': '![Owner: {owner}](https://img.shields.io/badge/owner-{owner_slug}-lightblue)',
}

FRONT_MATTER_PATTERN = re.compile(r'^---\n(.*?)\n---', re.DOTALL | re.MULTILINE)
H1_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)


def load_manifest() -> Dict:
    """Load the documentation manifest."""
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return json.load(f)


def slugify_owner(owner: str) -> str:
    """Convert owner to badge-safe slug."""
    # Remove @ symbol, spaces, special chars
    slug = owner.replace('@', '').replace(' ', '_')
    slug = re.sub(r'[^a-zA-Z0-9_-]', '', slug)
    return slug


def generate_badges(status: str, owner: str) -> list[str]:
    """Generate badge markdown for status and owner."""
    badges = []

    # Status badge
    if status in BADGE_STYLES['status']:
        badges.append(BADGE_STYLES['status'][status])

    # Owner badge
    if owner and owner != 'unknown':
        owner_slug = slugify_owner(owner)
        owner_badge = BADGE_STYLES['owner_template'].format(
            owner=owner,
            owner_slug=owner_slug
        )
        badges.append(owner_badge)

    return badges


def inject_badges(file_path: Path, status: str, owner: str, dry_run: bool = True) -> bool:
    """
    Inject badges at top of document, after front-matter but before H1.
    Returns True if modified.
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ⚠️  Failed to read {file_path}: {e}")
        return False

    # Check if badges already exist
    if '![Status:' in content or '![Owner:' in content:
        return False  # Already has badges

    # Find front-matter
    fm_match = FRONT_MATTER_PATTERN.match(content)
    if not fm_match:
        return False  # No front-matter

    fm_end = fm_match.end()

    # Find first H1
    h1_match = H1_PATTERN.search(content, fm_end)
    if not h1_match:
        return False  # No H1 heading

    h1_start = h1_match.start()

    # Generate badges
    badges = generate_badges(status, owner)
    if not badges:
        return False  # No badges to add

    # Build new content
    before_h1 = content[:h1_start].rstrip()
    at_and_after_h1 = content[h1_start:]

    badge_block = '\n'.join(badges) + '\n\n'
    new_content = before_h1 + '\n\n' + badge_block + at_and_after_h1

    if dry_run:
        return True  # Would modify

    # Write back
    try:
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        with open(backup_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

        # Write new content
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)

        # Remove backup on success
        backup_path.unlink()
        return True

    except Exception as e:
        print(f"   ❌ Failed to write {file_path}: {e}")
        # Restore from backup if exists
        if backup_path.exists():
            backup_path.rename(file_path)
        return False


def generate_badge_legend() -> str:
    """Generate badge legend markdown for DOCUMENTATION_INDEX.md."""
    lines = [
        "## Badge Legend",
        "",
        "Documentation status and ownership badges:",
        "",
        "### Status Badges",
        "",
    ]

    for status, badge_md in BADGE_STYLES['status'].items():
        lines.append(f"- {badge_md} - {status.upper()}")

    lines.extend([
        "",
        "### Owner Badges",
        "",
        "![Owner: @username](https://img.shields.io/badge/owner-username-lightblue) - Assigned owner (@username or team-name)",
        "",
        "### Badge Meanings",
        "",
        "- **WIP**: Work in progress, content incomplete",
        "- **Draft**: Content complete but under review",
        "- **Stable**: Production-ready, reviewed and approved",
        "- **Deprecated**: Obsolete, kept for reference",
        "- **Archived**: Historical record, no longer maintained",
        "- **Moved**: Content relocated (see redirect)",
        "",
    ])

    return '\n'.join(lines)


def update_index_legend(dry_run: bool = True) -> bool:
    """Add badge legend to DOCUMENTATION_INDEX.md if not present."""
    if not INDEX_PATH.exists():
        print(f"   ⚠️  {INDEX_PATH} not found")
        return False

    try:
        with open(INDEX_PATH, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Failed to read {INDEX_PATH}: {e}")
        return False

    # Check if legend already exists
    if '## Badge Legend' in content:
        return False  # Already has legend

    legend = generate_badge_legend()

    # Append to end of file
    new_content = content.rstrip() + '\n\n' + legend + '\n'

    if dry_run:
        return True  # Would modify

    try:
        # Backup
        backup_path = INDEX_PATH.with_suffix(INDEX_PATH.suffix + '.bak')
        with open(backup_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

        # Write
        with open(INDEX_PATH, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)

        backup_path.unlink()
        return True

    except Exception as e:
        print(f"   ❌ Failed to write {INDEX_PATH}: {e}")
        if backup_path.exists():
            backup_path.rename(INDEX_PATH)
        return False


def main():
    """Main workflow."""
    print("=" * 80)
    print("LUKHAS Documentation Badge Renderer (T4/0.01%)")
    print("=" * 80)
    print()

    # Parse flags
    dry_run = '--dry-run' not in sys.argv and '--apply' not in sys.argv
    if '--apply' in sys.argv:
        dry_run = False

    if dry_run:
        print("🔍 DRY-RUN MODE (use --apply to modify files)")
    else:
        print("⚠️  APPLY MODE - Will inject badges into docs")
    print()

    # Load manifest
    print("📂 Loading manifest...")
    manifest = load_manifest()
    docs = manifest['documents']
    print(f"   ✅ {len(docs)} documents")
    print()

    # Inject badges
    print("🏷️  Injecting badges...")
    modified_count = 0
    skipped_count = 0

    for doc in docs:
        if doc.get('redirect'):
            continue  # Skip redirects

        status = doc.get('status', 'unknown')
        owner = doc.get('owner', 'unknown')

        # Skip if no valid badges
        if status == 'unknown' and owner == 'unknown':
            continue

        file_path = Path(doc['path'])
        # Ensure absolute path
        if not file_path.is_absolute():
            file_path = REPO_ROOT / file_path
        if not file_path.exists():
            continue

        was_modified = inject_badges(file_path, status, owner, dry_run=dry_run)
        if was_modified:
            modified_count += 1
            if not dry_run:
                # Handle relative paths
                try:
                    rel_path = file_path.relative_to(REPO_ROOT)
                except ValueError:
                    rel_path = file_path
                print(f"   ✅ {rel_path}")
        else:
            skipped_count += 1

    print()
    print("📊 Summary:")
    if dry_run:
        print(f"   Would modify: {modified_count} files")
    else:
        print(f"   Modified: {modified_count} files")
    print(f"   Skipped: {skipped_count} files (already have badges or no valid data)")
    print()

    # Update index legend
    print("📖 Updating badge legend in DOCUMENTATION_INDEX.md...")
    legend_added = update_index_legend(dry_run=dry_run)
    if legend_added:
        if dry_run:
            print("   Would add badge legend")
        else:
            print("   ✅ Badge legend added")
    else:
        print("   ℹ️  Legend already present or index not found")
    print()

    # Calculate coverage
    total_eligible = len([d for d in docs if not d.get('redirect')])
    coverage_pct = (modified_count / total_eligible) * 100 if total_eligible > 0 else 0

    print("=" * 80)
    print("BADGE COVERAGE")
    print("=" * 80)
    print(f"Eligible docs: {total_eligible}")
    print(f"With badges: {modified_count}")
    print(f"Coverage: {coverage_pct:.1f}%")
    print()

    if coverage_pct >= 95:
        print("✅ Target coverage (≥95%) achieved!")
    else:
        print(f"⚠️  Coverage below target (need {int(total_eligible * 0.95 - modified_count)} more)")

    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
