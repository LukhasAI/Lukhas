#!/usr/bin/env python3
"""
Precise TODO cleanup - removes only the TODO comments, not the actual code
"""

import re
from pathlib import Path


def precise_cleanup():
    """Remove only the TODO comment part, preserve the actual code"""

    print("🎯 PRECISE TODO CLEANUP")
    print("=" * 40)

    # Pattern to match only the "# TODO: ..." part while preserving the rest
    patterns = [
        # Pattern: # import streamlit as st  # TODO: Install or implement streamlit
        # Replace with: import streamlit as st
        (r"^(\s*)#\s*(import streamlit as st)\s*#\s*TODO: Install or implement streamlit\s*$", r"\1\2"),
        # Pattern: # some code  # TODO: Install or implement streamlit
        # Replace with: # some code
        (r"^(.+?)\s*#\s*TODO: Install or implement streamlit\s*$", r"\1"),
        # Pattern: # TODO: Implement actual consolidation logic (whole line)
        # Replace with: (remove line)
        (r"^\s*#\s*TODO: Implement actual consolidation logic\s*\n", ""),
    ]

    # Files that need fixing
    broken_files = [
        "./candidate/core/interfaces/as_agent/streamlit/app.py",
        "./candidate/core/interfaces/as_agent/streamlit/components/dream_export_streamlit.py",
        "./candidate/core/interfaces/as_agent/streamlit/components/tier_visualizer.py",
        "./candidate/core/interfaces/as_agent/streamlit/components/voice_preview_streamlit.py",
    ]

    for file_path_str in broken_files:
        file_path = Path(file_path_str)

        if not file_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue

        print(f"\n📄 Processing: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_lines = content.count("\n")
            new_content = content

            # Apply patterns
            for pattern, replacement in patterns:
                old_content = new_content
                new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE)
                if new_content != old_content:
                    print(f"  ✂️ Applied pattern: {pattern[:50]}...")

            if new_content != content:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + ".precise_backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Write fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                new_lines = new_content.count("\n")
                print(f"  ✅ Fixed file (lines: {original_lines} -> {new_lines})")
                print(f"  💾 Backup: {backup_path}")
            else:
                print(f"  ℹ️ No changes needed")

        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    precise_cleanup()
