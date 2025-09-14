#!/usr/bin/env python3
"""
Quick datetime UTC fixer for ruff DTZ005/DTZ003 violations.
Applies surgical fixes with minimal disruption.
"""

import json
import re
import subprocess


def fix_datetime_in_file(file_path):
    """Fix datetime issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Add timezone import if needed
        if "datetime.now(" in content or "datetime.utcnow(" in content:
            # Check if timezone is already imported
            if "from datetime import" in content and "timezone" not in content:
                content = re.sub(
                    r"from datetime import ([^)]+)",
                    lambda m: f"from datetime import {m.group(1).rstrip()}, timezone",
                    content,
                    count=1,
                )
            elif "import datetime" in content and "timezone" not in content:
                # For "import datetime" style, we'll use datetime.timezone.utc
                pass

        # Fix datetime.now(timezone.utc) -> datetime.now(timezone.utc)
        content = re.sub(r"datetime\.now\(\)", "datetime.now(timezone.utc)", content)

        # Fix datetime.now(timezone.utc) -> datetime.now(timezone.utc)
        content = re.sub(r"datetime\.utcnow\(\)", "datetime.now(timezone.utc)", content)

        # For "import datetime" style
        content = re.sub(r"datetime\.datetime\.now\(\)", "datetime.datetime.now(datetime.timezone.utc)", content)
        content = re.sub(r"datetime\.datetime\.utcnow\(\)", "datetime.datetime.now(datetime.timezone.utc)", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def get_files_with_datetime_issues():
    """Get files that have DTZ005/DTZ003 violations."""
    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", ".", "--select", "DTZ005,DTZ003", "--output-format=json"],
            capture_output=True,
            text=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        if result.stdout:
            violations = json.loads(result.stdout)
            files = set()
            for violation in violations:
                if violation.get("filename"):
                    files.add(violation["filename"])
            return list(files)
    except Exception as e:
        print(f"Error getting datetime issues: {e}")

    return []


def main():
    print("🕒 Fixing datetime UTC compliance issues...")

    files_to_fix = get_files_with_datetime_issues()
    print(f"Found {len(files_to_fix)} files with datetime issues")

    fixed_count = 0
    for file_path in files_to_fix[:100]:  # Limit to first 100 for safety
        if fix_datetime_in_file(file_path):
            fixed_count += 1
            print(f"✅ Fixed: {file_path}")

    print(f"\n🎉 Fixed {fixed_count}/{min(len(files_to_fix), 100)} files")

    # Check remaining issues
    remaining = get_files_with_datetime_issues()
    print(f"📊 Remaining files with datetime issues: {len(remaining)}")


if __name__ == "__main__":
    main()
