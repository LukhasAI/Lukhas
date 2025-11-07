#!/usr/bin/env python3
"""
LUKHAS Documentation Link Rewriter

Rewrites internal links to canonical paths and validates anchors.
"""

import json
import re
from pathlib import Path
from typing import Dict, Set, Tuple

# Constants
DOCS_ROOT = Path(__file__).parent.parent / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"
DEDUPE_PLAN_PATH = INVENTORY_DIR / "dedupe_plan.json"

# Link patterns
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
HEADING_PATTERN = re.compile(r'^#+\s+(.+)$', re.MULTILINE)


def load_manifest() -> Dict:
    """Load the documentation manifest."""
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_dedupe_plan() -> Dict:
    """Load the deduplication plan."""
    if not DEDUPE_PLAN_PATH.exists():
        return {"redirects": []}

    with open(DEDUPE_PLAN_PATH, encoding='utf-8') as f:
        return json.load(f)


def build_redirect_map(dedupe_plan: Dict) -> Dict[str, str]:
    """Build map of old path -> canonical path."""
    redirect_map = {}

    for redirect in dedupe_plan.get('redirects', []):
        from_path = redirect['from']
        to_path = redirect['to']
        redirect_map[from_path] = to_path

    return redirect_map


def extract_headings(content: str) -> Set[str]:
    """Extract all heading anchors from content."""
    headings = set()

    for match in HEADING_PATTERN.finditer(content):
        heading_text = match.group(1).strip()
        # GitHub-style anchor: lowercase, replace spaces with -, remove special chars
        anchor = re.sub(r'[^\w\s-]', '', heading_text.lower())
        anchor = re.sub(r'[\s]+', '-', anchor)
        headings.add(anchor)

    return headings


def resolve_relative_link(source_file: Path, link: str, docs_root: Path) -> Path:
    """Resolve a relative link to absolute path."""
    if link.startswith('/'):
        # Absolute from repo root
        return Path(link.lstrip('/'))

    if link.startswith('http://') or link.startswith('https://'):
        # External link
        return None

    # Relative to source file
    source_dir = source_file.parent
    target = (source_dir / link).resolve()

    return target


def validate_link(source_file: Path, link_text: str, link_url: str,
                  docs_by_path: Dict, redirect_map: Dict, docs_root: Path) -> Tuple[bool, str, str]:
    """
    Validate a link and return (is_valid, error_msg, canonical_url).
    Returns canonical URL if redirect needed.
    """
    # Parse URL and anchor
    if '#' in link_url:
        url_path, anchor = link_url.split('#', 1)
    else:
        url_path = link_url
        anchor = None

    # Skip external links
    if url_path.startswith('http://') or url_path.startswith('https://'):
        return (True, "", link_url)

    # Skip anchors-only (same-page)
    if not url_path and anchor:
        return (True, "", link_url)

    # Resolve to absolute path
    target_path = resolve_relative_link(source_file, url_path, docs_root)

    if target_path is None:
        return (True, "", link_url)  # External

    # Check if path exists in docs
    target_str = str(target_path)

    # Try to find in docs
    matching_docs = [d for d in docs_by_path.values() if target_str in d['path']]

    if not matching_docs:
        return (False, f"Target not found: {url_path}", link_url)

    target_doc = matching_docs[0]

    # Check if target was moved (redirect)
    canonical_path = redirect_map.get(target_doc['path'], target_doc['path'])

    # Validate anchor if present
    if anchor:
        try:
            with open(target_doc['path'], encoding='utf-8') as f:
                content = f.read()
            headings = extract_headings(content)

            if anchor not in headings:
                return (False, f"Anchor not found: #{anchor}", link_url)
        except Exception as e:
            return (False, f"Cannot validate anchor: {e}", link_url)

    # Build canonical URL
    if canonical_path != target_doc['path']:
        # Need to redirect
        rel_canonical = canonical_path.replace('docs/', '')
        canonical_url = rel_canonical + (f"#{anchor}" if anchor else "")
        return (True, f"Redirect: {canonical_path}", canonical_url)

    return (True, "", link_url)


def rewrite_links_in_file(file_path: Path, docs_by_path: Dict, redirect_map: Dict,
                          docs_root: Path, dry_run: bool = True) -> Dict:
    """
    Rewrite links in a single file.
    Returns stats and changes.
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}

    changes = []
    broken_links = []
    rewrites = 0

    def replace_link(match):
        nonlocal rewrites
        link_text = match.group(1)
        link_url = match.group(2)

        is_valid, msg, canonical_url = validate_link(
            file_path, link_text, link_url, docs_by_path, redirect_map, docs_root
        )

        if not is_valid:
            broken_links.append({
                "text": link_text,
                "url": link_url,
                "error": msg,
            })
            return match.group(0)  # Keep original

        if canonical_url != link_url:
            changes.append({
                "original": link_url,
                "canonical": canonical_url,
                "reason": msg,
            })
            rewrites += 1
            return f"[{link_text}]({canonical_url})"

        return match.group(0)

    new_content = MARKDOWN_LINK_PATTERN.sub(replace_link, content)

    if not dry_run and rewrites > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return {
        "file": str(file_path),
        "rewrites": rewrites,
        "broken": len(broken_links),
        "changes": changes,
        "broken_links": broken_links,
    }


def main():
    """Main link rewriting workflow."""
    import sys

    dry_run = '--apply' not in sys.argv

    print("=" * 80)
    print("LUKHAS Documentation Link Rewriter")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}")
    print()

    # Load data
    print("📂 Loading manifest...")
    manifest = load_manifest()
    docs = manifest['documents']

    print("📂 Loading dedupe plan...")
    dedupe_plan = load_dedupe_plan()
    redirect_map = build_redirect_map(dedupe_plan)

    # Build lookup
    docs_by_path = {d['path']: d for d in docs}

    print(f"📝 Processing {len(docs)} documents...")
    print()

    total_rewrites = 0
    total_broken = 0
    files_with_changes = 0

    for doc in docs:
        if doc.get('redirect'):
            continue

        file_path = Path(doc['path'])
        result = rewrite_links_in_file(file_path, docs_by_path, redirect_map, DOCS_ROOT, dry_run)

        if 'error' in result:
            print(f"⚠️  {result['file']}: {result['error']}")
            continue

        if result['rewrites'] > 0:
            files_with_changes += 1
            total_rewrites += result['rewrites']
            print(f"✏️  {doc['path']}: {result['rewrites']} link(s) rewritten")

        if result['broken'] > 0:
            total_broken += result['broken']
            print(f"❌ {doc['path']}: {result['broken']} broken link(s)")
            for broken in result['broken_links'][:3]:  # Show first 3
                print(f"   - [{broken['text']}]({broken['url']}): {broken['error']}")

    print()
    print("=" * 80)
    print("LINK REWRITING SUMMARY")
    print("=" * 80)
    print(f"Files processed: {len(docs)}")
    print(f"Files with changes: {files_with_changes}")
    print(f"Total links rewritten: {total_rewrites}")
    print(f"Total broken links: {total_broken}")
    print()

    if dry_run:
        print("⚠️  This was a DRY RUN. No files were modified.")
        print("    Run with --apply to apply changes.")
    else:
        print("✅ Changes applied.")

    print()
    print("=" * 80)
    print("✅ Phase 4 Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
