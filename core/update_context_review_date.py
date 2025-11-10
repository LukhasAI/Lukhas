#!/usr/bin/env python3
"""
Surgically updates the 'last_reviewed' date in a context file's frontmatter.

Usage:
    python scripts/update_context_review_date.py <path_to_file>
"""

import sys
from pathlib import Path
from datetime import datetime
import re

def update_review_date(file_path: Path):
    """Finds and updates the last_reviewed field in the frontmatter."""
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    content = file_path.read_text()
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Regex to find and replace the last_reviewed line
    # This is safer than parsing/rewriting the whole YAML block
    new_content, count = re.subn(
        r"last_reviewed:.*",
        f"last_reviewed: {today_str}",
        content,
        count=1
    )

    if count > 0:
        file_path.write_text(new_content)
        print(f"✅ Updated 'last_reviewed' date in {file_path.name} to {today_str}.")
    else:
        print(f"⚠️ 'last_reviewed' field not found in {file_path.name}. No changes made.")
        print("   Please add 'last_reviewed: YYYY-MM-DD' to the frontmatter.")

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    update_review_date(file_path)

if __name__ == "__main__":
    main()