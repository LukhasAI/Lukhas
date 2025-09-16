#!/usr/bin/env python3
"""
Limited TODO removal for testing - processes just a few files
"""

import re
from pathlib import Path


def limited_removal():
    """Remove TODOs from just a few test files"""

    # Test files
    test_files = [
        "./candidate/core/notion_sync.py",
        "./candidate/core/orchestration/brain/config/settings_editor.py",
        "./candidate/governance/ethics_legacy/safety/compliance_dashboard_visual.py",
    ]

    # Streamlit pattern only for safety
    pattern = r".*#\s*TODO:\s*Install or implement streamlit\s*\n"

    print("🧪 LIMITED TODO REMOVAL TEST")
    print("=" * 50)

    for file_path_str in test_files:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"\n📄 Processing: {file_path}")

        # Read file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            continue

        # Find matches
        matches = list(re.finditer(pattern, original_content, re.MULTILINE))

        if not matches:
            print("  ✅ No TODOs to remove")
            continue

        print(f"  🔍 Found {len(matches)} TODO(s) to remove")

        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
        print(f"  💾 Backup created: {backup_path}")

        # Remove matches (in reverse order)
        new_content = original_content
        for match in reversed(matches):
            line = match.group(0)

            # Safety check
            if "install or implement streamlit" in line.lower():
                print(f"  ✂️  Removing: {line.strip()}")
                new_content = new_content[: match.start()] + new_content[match.end() :]
            else:
                print(f"  ⚠️  Safety check failed: {line.strip()}")

        # Write new content
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ File updated successfully")
        except Exception as e:
            print(f"  ❌ Error writing file: {e}")
            # Restore from backup
            with open(backup_path, "r", encoding="utf-8") as f:
                restore_content = f.read()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(restore_content)
            print(f"  🔄 File restored from backup")

    print("\n" + "=" * 50)
    print("✅ Limited removal test completed")
    print("🔍 Check the files and backups to verify results")


if __name__ == "__main__":
    limited_removal()
