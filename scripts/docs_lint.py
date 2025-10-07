#!/usr/bin/env python3
"""
LUKHAS Documentation Linter (CI-Ready)

Validates front-matter, regenerates site map, and checks internal links.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Constants
DOCS_ROOT = Path(__file__).parent.parent / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"
OUTPUT_DIR = DOCS_ROOT / "_generated"
SITEMAP_PATH = OUTPUT_DIR / "SITE_MAP.md"

# Required front-matter keys
REQUIRED_KEYS = ['status', 'type', 'owner', 'module']

# Front-matter status values
VALID_STATUSES = {
    'wip', 'draft', 'stable', 'deprecated', 'archived',
    'moved', 'converted', 'tracked', 'baseline-freeze'
}

# Front-matter type values
VALID_TYPES = {
    'architecture', 'api', 'guide', 'report', 'adr', 'index',
    'misc', 'documentation', 'runbook', 'operations', 'transcript',
    'health-report', 'sprint-plan', 'redirect'
}


def load_manifest() -> Dict:
    """Load the documentation manifest."""
    if not MANIFEST_PATH.exists():
        print(f"❌ Manifest not found: {MANIFEST_PATH}")
        print("   Run: python3 scripts/docs_inventory.py")
        sys.exit(1)

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_front_matter(manifest: Dict) -> tuple[List[Dict], List[Dict]]:
    """Validate front-matter on all documents. Returns (errors, warnings)."""
    errors = []
    warnings = []

    for doc in manifest['documents']:
        if doc.get('redirect'):
            continue  # Skip redirect stubs

        doc_path = doc['path']

        # Check if has front-matter
        if not doc.get('has_front_matter'):
            errors.append({
                "file": doc_path,
                "error": "missing_front_matter",
                "message": "Document lacks YAML front-matter block",
            })
            continue

        # Check required keys (except owner - warn separately)
        for key in REQUIRED_KEYS:
            if key == 'owner':
                continue  # Handle owner separately below
            if key not in doc or doc[key] == 'unknown':
                errors.append({
                    "file": doc_path,
                    "error": f"missing_key_{key}",
                    "message": f"Front-matter missing required key: {key}",
                })

        # Warn on owner: unknown (don't fail CI yet - grace period until 2025-10-13)
        if doc.get('owner') in ['unknown', '', None]:
            warnings.append({
                "file": doc_path,
                "warning": "owner_unknown",
                "message": "Owner is 'unknown' - assignment recommended (see OWNERS_BACKLOG.md)",
            })

        # Validate status value
        if doc.get('status') and doc['status'] not in VALID_STATUSES:
            errors.append({
                "file": doc_path,
                "error": "invalid_status",
                "message": f"Invalid status: {doc['status']} (must be one of {VALID_STATUSES})",
            })

        # Validate type value
        if doc.get('type') and doc['type'] not in VALID_TYPES:
            errors.append({
                "file": doc_path,
                "error": "invalid_type",
                "message": f"Invalid type: {doc['type']} (must be one of {VALID_TYPES})",
            })

    return errors, warnings


def check_manifest_completeness(manifest: Dict) -> List[Dict]:
    """Check that all .md files are in manifest."""
    errors = []

    manifest_paths = {doc['path'] for doc in manifest['documents']}

    # Scan filesystem
    for md_file in DOCS_ROOT.rglob("*.md"):
        # Skip excluded directories
        if any(excluded in md_file.parts for excluded in
               {'.git', '__pycache__', 'node_modules', 'venv'}):
            continue

        if '_generated' in md_file.parts or '_inventory' in md_file.parts:
            continue

        rel_path = str(md_file.relative_to(DOCS_ROOT.parent))

        if rel_path not in manifest_paths:
            errors.append({
                "file": rel_path,
                "error": "not_in_manifest",
                "message": "File exists but not in manifest (orphan?)",
            })

    return errors


def check_sitemap_fresh(manifest: Dict) -> bool:
    """Check if SITE_MAP.md is up to date."""
    if not SITEMAP_PATH.exists():
        print(f"⚠️  Site map missing: {SITEMAP_PATH}")
        return False

    # Check if generated date matches
    with open(SITEMAP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple check: does it contain all doc count?
    expected_count = str(manifest['total_documents'])
    if expected_count not in content:
        print(f"⚠️  Site map appears stale (doc count mismatch)")
        return False

    return True


def check_internal_links(manifest: Dict) -> List[Dict]:
    """
    Quick internal link validation.
    Returns list of broken links (sample only for performance).
    """
    import re

    errors = []
    checked = 0
    max_check = 50  # Limit for CI performance

    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    docs_by_path = {doc['path']: doc for doc in manifest['documents']}

    for doc in manifest['documents'][:max_check]:
        if doc.get('redirect'):
            continue

        checked += 1

        try:
            with open(doc['path'], 'r', encoding='utf-8') as f:
                content = f.read()

            for match in LINK_PATTERN.finditer(content):
                link_text = match.group(1)
                link_url = match.group(2)

                # Skip external
                if link_url.startswith('http://') or link_url.startswith('https://'):
                    continue

                # Skip anchors only
                if not link_url or link_url.startswith('#'):
                    continue

                # Simple check: does target exist in manifest?
                # This is a simplified check for CI performance
                found = any(link_url in d['path'] or link_url in d['path'].replace('docs/', '')
                           for d in docs_by_path.values())

                if not found:
                    errors.append({
                        "file": doc['path'],
                        "link_text": link_text,
                        "link_url": link_url,
                        "error": "broken_link",
                        "message": f"Link target not found: {link_url}",
                    })

                    # Limit errors per file
                    if len([e for e in errors if e['file'] == doc['path']]) >= 3:
                        break

        except Exception as e:
            continue

    return errors


def main():
    """Main CI lint workflow."""
    print("=" * 80)
    print("LUKHAS Documentation Linter")
    print("=" * 80)
    print()

    exit_code = 0

    # Load manifest
    print("📂 Loading manifest...")
    manifest = load_manifest()
    print(f"   ✅ {manifest['total_documents']} documents")
    print()

    # 1. Check front-matter
    print("1️⃣  Checking front-matter...")
    fm_errors, fm_warnings = check_front_matter(manifest)
    if fm_errors:
        print(f"   ❌ {len(fm_errors)} front-matter error(s)")
        for error in fm_errors[:10]:  # Show first 10
            print(f"      - {error['file']}: {error['message']}")
        if len(fm_errors) > 10:
            print(f"      ... and {len(fm_errors) - 10} more")
        exit_code = 1
    else:
        print(f"   ✅ All documents have valid front-matter")

    if fm_warnings:
        print(f"   ⚠️  {len(fm_warnings)} warning(s) (owner: unknown)")
        print(f"      See: docs/_generated/OWNERS_BACKLOG.md")
        print(f"      Grace period until 2025-10-13")
    print()

    # 2. Check manifest completeness
    print("2️⃣  Checking manifest completeness...")
    manifest_errors = check_manifest_completeness(manifest)
    if manifest_errors:
        print(f"   ⚠️  {len(manifest_errors)} orphan file(s) not in manifest")
        for error in manifest_errors[:5]:
            print(f"      - {error['file']}")
        # Warn only, don't fail
    else:
        print(f"   ✅ All markdown files in manifest")
    print()

    # 3. Check site map freshness
    print("3️⃣  Checking site map freshness...")
    if check_sitemap_fresh(manifest):
        print(f"   ✅ Site map is up to date")
    else:
        print(f"   ❌ Site map is stale or missing")
        print(f"      Run: python3 scripts/docs_generate.py")
        exit_code = 1
    print()

    # 4. Check internal links (sample)
    print("4️⃣  Checking internal links (sample)...")
    link_errors = check_internal_links(manifest)
    if link_errors:
        print(f"   ⚠️  {len(link_errors)} broken link(s) found in sample")
        # Group by file
        by_file = {}
        for error in link_errors:
            f = error['file']
            if f not in by_file:
                by_file[f] = []
            by_file[f].append(error)

        for file, errors in list(by_file.items())[:5]:
            print(f"      {file}:")
            for error in errors[:2]:
                print(f"         - [{error['link_text']}]({error['link_url']})")

        print(f"      Run full check: python3 scripts/docs_rewrite_links.py")
        # Warn only for now
    else:
        print(f"   ✅ No broken links in sample")
    print()

    # Summary
    print("=" * 80)
    print("LINT SUMMARY")
    print("=" * 80)
    print(f"Front-matter errors: {len(fm_errors)}")
    print(f"Owner warnings: {len(fm_warnings)} (grace period until 2025-10-13)")
    print(f"Orphan files: {len(manifest_errors)}")
    print(f"Broken links (sample): {len(link_errors)}")
    print()

    if exit_code == 0:
        print("✅ All critical checks passed")
    else:
        print("❌ Some checks failed - see errors above")

    print("=" * 80)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
