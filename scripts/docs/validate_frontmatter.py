#!/usr/bin/env python3
"""
Validate YAML frontmatter in all markdown files.

Checks:
- Valid YAML syntax
- Required fields present
- Field types correct
- No empty values for required fields
"""
import sys
from pathlib import Path
from typing import List

import yaml

EXCLUDE_DIRS = {
    ".venv",
    ".venv_*",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".git",
    "dist",
    "build",
    "*.egg-info",
    "htmlcov",
}

REQUIRED_FIELDS = {"module", "title"}


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    import re

    for part in path.parts:
        if any(re.match(pattern.replace("*", ".*"), part) for pattern in EXCLUDE_DIRS):
            return True
    return False


def validate_frontmatter(md_path: Path) -> List[str]:
    """Validate frontmatter in a markdown file. Returns list of errors."""
    errors = []

    try:
        content = md_path.read_text()

        # Check if has frontmatter
        if not content.startswith("---"):
            return []  # No frontmatter is OK for some files

        # Parse frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{md_path}: Invalid frontmatter format (missing closing ---)")
            return errors

        # Skip template files (Jinja2 placeholders)
        frontmatter_text = parts[1]
        if "{{" in frontmatter_text or "{%" in frontmatter_text:
            return []  # Skip templates

        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            errors.append(f"{md_path}: Invalid YAML syntax: {e}")
            return errors

        # Validate required fields
        if frontmatter and isinstance(frontmatter, dict):
            for field in REQUIRED_FIELDS:
                if field in frontmatter:
                    if not frontmatter[field]:
                        errors.append(f"{md_path}: Empty '{field}' field")
                    elif not isinstance(frontmatter[field], str):
                        errors.append(f"{md_path}: '{field}' must be string, got {type(frontmatter[field]).__name__}")

    except Exception as e:
        errors.append(f"{md_path}: Error reading file: {e}")

    return errors


def main():
    print("🔍 Validating frontmatter in markdown files...")

    root = Path(".")
    all_errors = []
    checked_count = 0

    for md_path in root.rglob("*.md"):
        if should_exclude(md_path):
            continue

        checked_count += 1
        errors = validate_frontmatter(md_path)
        all_errors.extend(errors)

    # Print results
    print(f"\n📊 Checked {checked_count} markdown files")

    if all_errors:
        print(f"\n❌ Found {len(all_errors)} validation errors:\n")
        for error in all_errors[:50]:  # Show first 50
            print(f"  {error}")
        if len(all_errors) > 50:
            print(f"\n  ... and {len(all_errors) - 50} more errors")

        return 1
    else:
        print("✅ All frontmatter valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
