#!/usr/bin/env python3
"""
Module: check_broken_links.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Check for broken relative links in markdown files.

Validates that all relative markdown links point to existing files.
Skips absolute URLs, anchors, and mailto links.
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

EXCLUDE_DIRS = {
    ".venv", ".venv_*", "venv", "__pycache__", ".pytest_cache",
    "node_modules", ".git", "dist", "build", "*.egg-info", "htmlcov"
}


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    import re as regex_module
    for part in path.parts:
        if any(regex_module.match(pattern.replace("*", ".*"), part) for pattern in EXCLUDE_DIRS):
            return True
    return False


def find_broken_links(md_path: Path) -> List[Tuple[str, str, Path]]:
    """Find broken relative links in a markdown file. Returns (text, link, resolved_path)."""
    broken = []

    try:
        content = md_path.read_text()

        # Find markdown links: [text](link)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for text, link in links:
            # Skip absolute URLs
            if link.startswith(('http://', 'https://', '#', 'mailto:', 'ftp://')):
                continue

            # Split anchor from path
            link_path = link.split('#')[0]

            # Skip empty paths (pure anchors)
            if not link_path:
                continue

            # Resolve relative path from markdown file location
            try:
                target = (md_path.parent / link_path).resolve()

                # Check if target exists
                if not target.exists():
                    broken.append((text, link, target))

            except Exception as e:
                # Invalid path syntax
                broken.append((text, link, Path(f"<invalid: {e}>")))

    except Exception as e:
        print(f"⚠️  Error reading {md_path}: {e}", file=sys.stderr)

    return broken


def main():
    print("🔍 Checking for broken relative links...")

    root = Path(".")
    all_broken = []
    checked_count = 0

    for md_path in root.rglob("*.md"):
        if should_exclude(md_path):
            continue

        checked_count += 1
        broken = find_broken_links(md_path)

        if broken:
            all_broken.append((md_path, broken))

    # Print results
    print(f"\n📊 Checked {checked_count} markdown files")

    if all_broken:
        total_broken = sum(len(links) for _, links in all_broken)
        print(f"\n❌ Found {total_broken} broken links in {len(all_broken)} files:\n")

        for md_path, broken_links in all_broken[:20]:  # Show first 20 files
            print(f"  {md_path}:")
            for text, link, target in broken_links[:5]:  # Show first 5 per file
                print(f"    - [{text}]({link}) → {target}")
            if len(broken_links) > 5:
                print(f"    ... and {len(broken_links) - 5} more broken links")

        if len(all_broken) > 20:
            print(f"\n  ... and {len(all_broken) - 20} more files with broken links")

        return 1
    else:
        print("✅ All relative links valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
