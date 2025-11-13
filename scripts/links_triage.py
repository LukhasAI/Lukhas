#!/usr/bin/env python3
"""
LUKHAS Broken Links Triage Bot

Categorizes broken links by type and generates batched GitHub issues.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict

# Constants
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"

LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def load_manifest() -> Dict:
    """Load the documentation manifest."""
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return json.load(f)


def categorize_link(link_url: str) -> str:
    """Categorize link by type."""
    if link_url.startswith('http://') or link_url.startswith('https://'):
        return 'external'

    if not link_url or link_url.startswith('#'):
        return 'anchor'

    if link_url.startswith('/docs/'):
        return 'external_path'  # Website paths, not repo

    if '**' in link_url or link_url.count('(') > 0:
        return 'malformed'

    # Check if it looks like a valid relative path
    if link_url.endswith('.md'):
        return 'missing_file'

    return 'other'


def scan_broken_links(docs: list[Dict]) -> dict[str, list[Dict]]:
    """Scan all docs for broken links and categorize."""
    broken_by_category = defaultdict(list)
    docs_by_path = {d['path']: d for d in docs}

    for doc in docs:
        if doc.get('redirect'):
            continue

        file_path = Path(doc['path'])
        if not file_path.exists():
            continue

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        for match in LINK_PATTERN.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2)

            # Categorize
            category = categorize_link(link_url)

            # Check if target exists (for relative links)
            if category == 'missing_file':
                # Simple check: does it appear in any doc path?
                found = any(link_url in d['path'] or link_url in d['path'].replace('docs/', '')
                           for d in docs_by_path.values())

                if not found:
                    broken_by_category[category].append({
                        'source': doc['path'],
                        'text': link_text,
                        'url': link_url,
                        'line': content[:match.start()].count('\n') + 1,
                    })

            elif category in ['malformed', 'external_path']:
                broken_by_category[category].append({
                    'source': doc['path'],
                    'text': link_text,
                    'url': link_url,
                    'line': content[:match.start()].count('\n') + 1,
                })

    return broken_by_category


def generate_issue_for_category(category: str, links: list[Dict]) -> str:
    """Generate GitHub issue markdown for a category of broken links."""
    titles = {
        'missing_file': 'Broken Links: Missing Files',
        'malformed': 'Broken Links: Malformed Syntax',
        'external_path': 'Broken Links: External Website Paths',
    }

    descriptions = {
        'missing_file': 'Links pointing to .md files that do not exist in the repository.',
        'malformed': 'Links with invalid markdown syntax (e.g., `**kwargs`, extra parentheses).',
        'external_path': 'Links pointing to website paths (/docs/intro/...) that are not in the repo.',
    }

    issue = [
        f"# {titles.get(category, f'Broken Links: {category}')}",
        "",
        f"**Category**: `{category}`",
        f"**Total broken links**: {len(links)}",
        "",
        "## Description",
        "",
        descriptions.get(category, "Links that need review and fixing."),
        "",
        "## Broken Links",
        "",
    ]

    # Group by source file
    by_source = defaultdict(list)
    for link in links:
        by_source[link['source']].append(link)

    for source in sorted(by_source.keys())[:50]:  # Limit to 50 files
        source_links = by_source[source]
        issue.append(f"### {source.replace('docs/', '')}")
        issue.append("")

        for link in source_links[:10]:  # Limit to 10 links per file
            issue.append(f"- Line {link['line']}: `[{link['text']}]({link['url']})`")

        if len(source_links) > 10:
            issue.append(f"  - ... and {len(source_links) - 10} more")

        issue.append("")

    if len(by_source) > 50:
        issue.append(f"*... and {len(by_source) - 50} more files*")
        issue.append("")

    issue.extend([
        "## Resolution Steps",
        "",
        "### For Missing Files",
        "1. Create the missing file if content exists elsewhere",
        "2. Update link to point to correct location",
        "3. Remove link if content is obsolete",
        "",
        "### For Malformed Syntax",
        "1. Fix markdown syntax",
        "2. Escape special characters if needed",
        "3. Use code blocks for non-link content",
        "",
        "### For External Paths",
        "1. Verify if content exists on website",
        "2. Update to correct URL if moved",
        "3. Remove if obsolete",
        "",
        "---",
        "",
        "*Auto-generated by `scripts/links_triage.py`*",
    ])

    return '\n'.join(issue)


def main():
    """Main workflow."""

    print("=" * 80)
    print("LUKHAS Broken Links Triage Bot")
    print("=" * 80)
    print()

    # Load manifest
    print(f"📂 Loading manifest from {MANIFEST_PATH}...")
    manifest = load_manifest()
    docs = manifest['documents']

    # Scan for broken links
    print(f"🔍 Scanning {len(docs)} documents for broken links...")
    broken_by_category = scan_broken_links(docs)

    total_broken = sum(len(links) for links in broken_by_category.values())
    print(f"📊 Found {total_broken} broken links across {len(broken_by_category)} categories")
    print()

    for category, links in sorted(broken_by_category.items(), key=lambda x: -len(x[1])):
        print(f"  {category:20s}: {len(links):4d}")

    print()

    if not broken_by_category:
        print("✅ No broken links found!")
        return

    # Generate issues
    output_dir = DOCS_ROOT / "_generated" / "link_triage"
    output_dir.mkdir(parents=True, exist_ok=True)

    for category, links in broken_by_category.items():
        issue_md = generate_issue_for_category(category, links)
        output_path = output_dir / f"{category}.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(issue_md)

        print(f"✅ Generated: {output_path}")

    print()
    print("=" * 80)
    print("USAGE")
    print("=" * 80)
    print()
    print("# Create GitHub issues:")
    for category in broken_by_category:
        print(f"gh issue create --title 'Broken Links: {category}' --body-file 'docs/_generated/link_triage/{category}.md' --label 'docs:{category}'")

    print()


if __name__ == "__main__":
    main()
