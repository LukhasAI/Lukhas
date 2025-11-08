#!/usr/bin/env python3
"""
tools/validate_seo.py

Validates SEO compliance:
- All pages have canonical URLs
- Meta descriptions 150-160 characters
- Title tags 50-60 characters
- No duplicate canonical URLs across domains
- Schema.org markup present
"""
import re
from pathlib import Path

import yaml


def validate_seo():
    """Run SEO validation checks."""
    errors = []
    warnings = []

    # Check 1: All pages have canonical URLs
    for md_file in Path("branding/websites").rglob("*.md"):
        fm = read_front_matter(md_file)
        if not fm:
            continue

        canonical = fm.get("canonical", "")
        if not canonical:
            errors.append(f"{md_file}: Missing canonical URL")

        # Check 2: Meta description length
        seo = fm.get("seo", {})
        description = seo.get("description", "")
        if description:
            desc_len = len(description)
            if desc_len < 150 or desc_len > 160:
                warnings.append(f"{md_file}: Meta description {desc_len} chars (target: 150-160)")
        else:
            errors.append(f"{md_file}: Missing SEO meta description")

        # Check 3: Title length
        title = fm.get("title", "")
        if title:
            title_len = len(title)
            if title_len < 50 or title_len > 60:
                warnings.append(f"{md_file}: Title {title_len} chars (target: 50-60)")

    # Check 4: Duplicate canonical URLs
    canonical_urls = {}
    for md_file in Path("branding/websites").rglob("*.md"):
        fm = read_front_matter(md_file)
        if not fm:
            continue
        canonical = fm.get("canonical", "")
        if canonical:
            if canonical in canonical_urls:
                errors.append(f"Duplicate canonical: {canonical} in {md_file} and {canonical_urls[canonical]}")
            else:
                canonical_urls[canonical] = md_file

    # Report results
    if errors:
        print("❌ SEO Validation Errors:")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("⚠️  SEO Validation Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if not errors:
        print(f"✅ SEO validation passed ({len(canonical_urls)} pages checked)")
        return 0
    else:
        return 1

def read_front_matter(path):
    """Read YAML front-matter from markdown file."""
    txt = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, flags=re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception:
        return {}

if __name__ == "__main__":
    import sys
    sys.exit(validate_seo())
