#!/usr/bin/env python3
"""Test TODO removal on a single file"""

import re
from pathlib import Path


def test_single_file():
    """Test on a single file"""

    test_file = Path("./candidate/core/notion_sync.py")

    if not test_file.exists():
        print(f"❌ Test file {test_file} not found")
        return

    # Read file
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"📄 Testing file: {test_file}")
    print(f"📊 File size: {len(content)} characters")

    # Test streamlit pattern
    pattern = r".*#\s*TODO:\s*Install or implement streamlit\s*\n"
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    print(f"🔍 Found {len(matches)} matches")

    for i, match in enumerate(matches):
        line = match.group(0)
        print(f"  Match {i+1}: {repr(line)}")

        # Test safety check
        safety_result = "install or implement streamlit" in line.lower()
        print(f"  Safety check: {safety_result}")

        # Show context
        start = max(0, match.start() - 100)
        end = min(len(content), match.end() + 100)
        context = content[start:end]
        print(f"  Context: ...{context}...")
        print()


if __name__ == "__main__":
    test_single_file()
