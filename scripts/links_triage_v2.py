#!/usr/bin/env python3
"""
LUKHAS Broken Links Triage Bot v2 (T4/0.01%)

Enhanced link validation with:
- Anchor validation (#section-name in same file)
- External link checking (HEAD requests with timeout)
- Batch GitHub issues by 25 items
- 3 reports: summary, internal, external
"""

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests library not available - external link checking disabled")
    print("   Install with: pip install requests")

# Constants
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"
OUTPUT_DIR = DOCS_ROOT / "_generated" / "link_triage"

LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
ANCHOR_PATTERN = re.compile(r'^#([a-zA-Z0-9_-]+)$')
HEADING_PATTERN = re.compile(r'^#+\s+(.+)$', re.MULTILINE)

# External link check config
EXTERNAL_TIMEOUT = 5  # seconds
EXTERNAL_CHECK_LIMIT = 50  # max external links to check (avoid rate limits)


def load_manifest() -> Dict:
    """Load the documentation manifest."""
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def slugify_heading(heading: str) -> str:
    """Convert heading text to GitHub-style anchor slug."""
    # Remove emojis, special chars, convert to lowercase, replace spaces with hyphens
    slug = heading.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/hyphens with single hyphen
    return slug.strip('-')


def extract_anchors(content: str) -> set:
    """Extract all heading anchors from markdown content."""
    anchors = set()
    for match in HEADING_PATTERN.finditer(content):
        heading_text = match.group(1)
        anchor = slugify_heading(heading_text)
        anchors.add(anchor)
    return anchors


def check_external_link(url: str, timeout: int = EXTERNAL_TIMEOUT) -> Tuple[bool, Optional[str]]:
    """
    Check if external link is reachable (HEAD request).
    Returns (is_reachable, error_message).
    """
    if not REQUESTS_AVAILABLE:
        return True, None  # Skip if requests not available

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code >= 400:
            return False, f"HTTP {response.status_code}"
        return True, None
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection failed"
    except requests.exceptions.TooManyRedirects:
        return False, "Too many redirects"
    except Exception as e:
        return False, str(e)[:50]


def categorize_link(link_url: str, source_path: Path, docs_by_path: Dict) -> Tuple[str, Optional[str]]:
    """
    Categorize link and check validity.
    Returns (category, error_message).
    """
    # External links
    if link_url.startswith('http://') or link_url.startswith('https://'):
        return 'external', None

    # Anchors (same-file)
    if link_url.startswith('#'):
        anchor_match = ANCHOR_PATTERN.match(link_url)
        if anchor_match:
            return 'anchor', None  # Will validate separately
        return 'malformed', "Invalid anchor syntax"

    # Empty links
    if not link_url:
        return 'malformed', "Empty link"

    # Website paths (external, not in repo)
    if link_url.startswith('/docs/'):
        return 'external_path', "Website path, not in repo"

    # Malformed syntax patterns
    if '**' in link_url or link_url.count('(') > 0:
        return 'malformed', "Invalid markdown syntax"

    # Relative paths to .md files
    if link_url.endswith('.md'):
        # Resolve relative to source file
        target_path = (source_path.parent / link_url).resolve()

        # Check if target exists
        if not target_path.exists():
            # Try alternative: check if it appears in manifest
            found = any(link_url in d['path'] or link_url in d['path'].replace('docs/', '')
                       for d in docs_by_path.values())
            if not found:
                return 'missing_file', f"Target not found: {link_url}"

        return 'internal_valid', None

    # Other relative paths
    return 'other', None


def scan_broken_links(docs: List[Dict], check_external: bool = False) -> Dict[str, List[Dict]]:
    """
    Scan all docs for broken links and categorize.

    Categories:
    - missing_file: .md files that don't exist
    - broken_anchor: #anchors in same file that don't match headings
    - malformed: Invalid markdown syntax
    - external_path: /docs/ website paths
    - external_broken: External links that return 4xx/5xx (if check_external=True)
    - internal_valid: Valid internal links (not reported)
    """
    broken_by_category = defaultdict(list)
    docs_by_path = {Path(d['path']): d for d in docs}

    external_checked = 0

    for doc in docs:
        if doc.get('redirect'):
            continue

        file_path = Path(doc['path'])
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        # Extract anchors for this file
        file_anchors = extract_anchors(content)

        for match in LINK_PATTERN.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2)
            line_num = content[:match.start()].count('\n') + 1

            # Categorize
            category, error_msg = categorize_link(link_url, file_path, docs_by_path)

            # Special handling for anchors
            if category == 'anchor':
                anchor_name = link_url[1:]  # Remove leading #
                if anchor_name not in file_anchors:
                    broken_by_category['broken_anchor'].append({
                        'source': str(file_path),
                        'text': link_text,
                        'url': link_url,
                        'line': line_num,
                        'error': f"Anchor not found in file (expected heading for '{anchor_name}')",
                    })

            # External link checking (if enabled and not too many)
            elif category == 'external' and check_external and external_checked < EXTERNAL_CHECK_LIMIT:
                is_reachable, error = check_external_link(link_url)
                external_checked += 1

                if not is_reachable:
                    broken_by_category['external_broken'].append({
                        'source': str(file_path),
                        'text': link_text,
                        'url': link_url,
                        'line': line_num,
                        'error': error or "Unreachable",
                    })

                # Rate limiting
                if external_checked % 10 == 0:
                    time.sleep(1)  # Sleep 1s every 10 requests

            # Report other broken categories
            elif category in ['missing_file', 'malformed', 'external_path']:
                broken_by_category[category].append({
                    'source': str(file_path),
                    'text': link_text,
                    'url': link_url,
                    'line': line_num,
                    'error': error_msg or "",
                })

    return broken_by_category


def generate_summary_report(broken_by_category: Dict[str, List[Dict]]) -> str:
    """Generate executive summary of all broken links."""
    total = sum(len(links) for links in broken_by_category.values())

    lines = [
        "# Broken Links Summary Report",
        "",
        f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total broken links**: {total}",
        "",
        "## Breakdown by Category",
        "",
        "| Category | Count | Description |",
        "|----------|-------|-------------|",
    ]

    descriptions = {
        'missing_file': 'Internal .md files that do not exist',
        'broken_anchor': 'Anchors (#section) with no matching heading',
        'malformed': 'Invalid markdown link syntax',
        'external_path': 'Website paths (/docs/) not in repo',
        'external_broken': 'External URLs returning errors',
    }

    for category in sorted(broken_by_category.keys(), key=lambda c: -len(broken_by_category[c])):
        count = len(broken_by_category[category])
        desc = descriptions.get(category, "Other broken links")
        lines.append(f"| {category} | {count} | {desc} |")

    lines.extend([
        "",
        "## Recommended Actions",
        "",
        "1. **missing_file** (Highest Priority): Create missing files or update links",
        "2. **broken_anchor**: Fix heading names or anchor links",
        "3. **malformed**: Fix markdown syntax errors",
        "4. **external_path**: Verify website content or remove obsolete links",
        "5. **external_broken**: Update or remove dead external links",
        "",
        "## Detailed Reports",
        "",
        "- [Internal Broken Links](internal_broken.md) - missing_file, broken_anchor, malformed",
        "- [External Broken Links](external_broken.md) - external_path, external_broken",
        "",
        "---",
        "",
        "*Auto-generated by `scripts/links_triage_v2.py`*",
    ])

    return '\n'.join(lines)


def generate_internal_report(broken_by_category: Dict[str, List[Dict]]) -> str:
    """Generate detailed report for internal broken links."""
    internal_categories = ['missing_file', 'broken_anchor', 'malformed']
    internal_links = {k: v for k, v in broken_by_category.items() if k in internal_categories}

    total = sum(len(links) for links in internal_links.values())

    lines = [
        "# Internal Broken Links Report",
        "",
        f"**Total**: {total} broken internal links",
        "",
        "## Categories",
        "",
    ]

    for category in internal_categories:
        if category not in internal_links:
            continue

        links = internal_links[category]
        lines.append(f"### {category} ({len(links)} links)")
        lines.append("")

        # Group by source file
        by_source = defaultdict(list)
        for link in links:
            by_source[link['source']].append(link)

        # Batch in groups of 25
        for idx, (source, source_links) in enumerate(sorted(by_source.items())):
            if idx >= 25:  # Limit to 25 files per category
                lines.append(f"*... and {len(by_source) - 25} more files*")
                break

            lines.append(f"#### {source.replace('docs/', '')}")
            lines.append("")

            for link in source_links[:5]:  # Limit to 5 links per file
                lines.append(f"- Line {link['line']}: `[{link['text']}]({link['url']})`")
                if link.get('error'):
                    lines.append(f"  - Error: {link['error']}")

            if len(source_links) > 5:
                lines.append(f"  - *... and {len(source_links) - 5} more*")

            lines.append("")

    lines.extend([
        "---",
        "",
        "*See [summary.md](summary.md) for complete breakdown*",
    ])

    return '\n'.join(lines)


def generate_external_report(broken_by_category: Dict[str, List[Dict]]) -> str:
    """Generate detailed report for external broken links."""
    external_categories = ['external_path', 'external_broken']
    external_links = {k: v for k, v in broken_by_category.items() if k in external_categories}

    total = sum(len(links) for links in external_links.values())

    lines = [
        "# External Broken Links Report",
        "",
        f"**Total**: {total} broken external links",
        "",
    ]

    for category in external_categories:
        if category not in external_links:
            continue

        links = external_links[category]
        lines.append(f"## {category} ({len(links)} links)")
        lines.append("")

        # Batch in groups of 25
        for idx, link in enumerate(sorted(links, key=lambda l: l['source'])[:25]):
            lines.append(f"### {idx + 1}. {link['source'].replace('docs/', '')}")
            lines.append(f"- Line {link['line']}: `[{link['text']}]({link['url']})`")
            if link.get('error'):
                lines.append(f"- Error: {link['error']}")
            lines.append("")

        if len(links) > 25:
            lines.append(f"*... and {len(links) - 25} more*")
            lines.append("")

    lines.extend([
        "---",
        "",
        "*See [summary.md](summary.md) for complete breakdown*",
    ])

    return '\n'.join(lines)


def main():
    """Main workflow."""
    print("=" * 80)
    print("LUKHAS Broken Links Triage Bot v2 (T4/0.01%)")
    print("=" * 80)
    print()

    # Parse flags
    check_external = '--check-external' in sys.argv

    if check_external and not REQUESTS_AVAILABLE:
        print("❌ --check-external requires 'requests' library")
        print("   Install with: pip install requests")
        sys.exit(1)

    # Load manifest
    print(f"📂 Loading manifest...")
    manifest = load_manifest()
    docs = manifest['documents']
    print(f"   ✅ {len(docs)} documents")
    print()

    # Scan for broken links
    print(f"🔍 Scanning for broken links...")
    if check_external:
        print(f"   ⚠️  External link checking enabled (limit: {EXTERNAL_CHECK_LIMIT})")
    broken_by_category = scan_broken_links(docs, check_external=check_external)

    total_broken = sum(len(links) for links in broken_by_category.values())
    print(f"📊 Found {total_broken} broken links across {len(broken_by_category)} categories")
    print()

    for category, links in sorted(broken_by_category.items(), key=lambda x: -len(x[1])):
        print(f"  {category:20s}: {len(links):4d}")
    print()

    if not broken_by_category:
        print("✅ No broken links found!")
        return 0

    # Generate reports
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📝 Generating reports...")

    # 1. Summary
    summary_md = generate_summary_report(broken_by_category)
    summary_path = OUTPUT_DIR / "summary.md"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_md)
    print(f"   ✅ {summary_path}")

    # 2. Internal
    internal_md = generate_internal_report(broken_by_category)
    internal_path = OUTPUT_DIR / "internal_broken.md"
    with open(internal_path, 'w', encoding='utf-8') as f:
        f.write(internal_md)
    print(f"   ✅ {internal_path}")

    # 3. External
    external_md = generate_external_report(broken_by_category)
    external_path = OUTPUT_DIR / "external_broken.md"
    with open(external_path, 'w', encoding='utf-8') as f:
        f.write(external_md)
    print(f"   ✅ {external_path}")

    print()
    print("=" * 80)
    print("USAGE")
    print("=" * 80)
    print()
    print("# Create GitHub issues:")
    print(f"gh issue create --title 'Broken Links: Internal' --body-file '{internal_path}' --label 'docs:broken-links'")
    print(f"gh issue create --title 'Broken Links: External' --body-file '{external_path}' --label 'docs:broken-links'")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
