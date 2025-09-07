#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Simple Conflict Healer - Fixes merge conflicts
"""
import os
import re
import shutil
import time
from datetime import datetime, timezone

import streamlit as st


def find_conflicts():
    """Find all Python files with merge conflicts"""
    conflicts = []

    for root, _dirs, files in os.walk("."):
        if ".venv" in root or ".git" in root or "._cleanup_archive" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                    if "<<<<<<< HEAD" in content:
                        conflicts.append(filepath)
                except BaseException:
                    pass

    return conflicts


def heal_file(filepath):
    """Heal conflicts in a single file"""

    # Backup
    backup_dir = "healing/backups"
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, os.path.basename(filepath) + ".backup")
    shutil.copy2(filepath, backup_path)

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Pattern to find conflicts
        pattern = r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]+"

        def resolve_conflict(match):
            ours = match.group(1)
            theirs = match.group(2)

            # Smart resolution: prefer LUKHAS version or longer version
            if "lukhas" in ours.lower() or "LUKHAS" in ours:
                return ours
            elif "lukhas" in theirs.lower() or "LUKHAS" in theirs:
                return theirs
            elif len(ours) > len(theirs):
                return ours
            else:
                return theirs

        # Replace all conflicts
        healed = re.sub(pattern, resolve_conflict, content, flags=re.DOTALL)

        # Write healed content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(healed)

        return True

    except Exception as e:
        print(f"Error healing {filepath}: {e}")
        # Restore backup
        shutil.copy2(backup_path, filepath)
        return False


def main():
    print("Starting Simple Conflict Healer...")

    conflicts = find_conflicts()

    if not conflicts:
        print("No conflicts found!")
        return

    print(f"Found {len(conflicts)} files with conflicts")

    healed = 0
    for filepath in conflicts:
        print(f"Healing {filepath}...")
        if heal_file(filepath):
            healed += 1
            print("  [OK]")
        else:
            print("  [FAILED]")

    print(f"\nHealed {healed}/{len(conflicts)} files")

    # Save report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_conflicts": len(conflicts),
        "healed": healed,
        "failed": len(conflicts) - healed,
        "files": conflicts,
    }

    import json

    with open("healing/conflict_report.json", "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
