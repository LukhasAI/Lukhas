#!/usr/bin/env python3
"""
Fix timezone import issues across LUKHAS codebase
Resolves F821 violations for timezone usage
"""
import json
from pathlib import Path


def fix_timezone_imports():
    """Fix timezone import issues by updating datetime imports"""

    # Load F821 violations
    with open("/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/idx_F821.json") as f:
        data = json.load(f)

    # Find files with timezone F821 violations
    timezone_files = set()
    for violation in data["violations"]:
        if "timezone" in violation["message"]:
            timezone_files.add(violation["filename"])

    print(f"Found {len(timezone_files)} files with timezone F821 violations")

    fixes_applied = 0
    for file_path in timezone_files:
        abs_path = Path(f"/Users/agi_dev/LOCAL-REPOS/Lukhas/{file_path}")

        if not abs_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue

        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()

            # Check if file already imports timezone
            if "from datetime import timezone" in content or "import timezone" in content:
                continue

            # Check if file uses datetime.now(timezone.utc) or similar patterns
            if "timezone." in content:
                # Look for datetime import pattern and update it
                if "from datetime import datetime" in content:
                    new_content = content.replace(
                        "from datetime import datetime",
                        "from datetime import datetime, timezone"
                    )

                    # Write back the fixed content
                    with open(abs_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print(f"✅ Fixed timezone import in: {file_path}")
                    fixes_applied += 1

                elif "import datetime" in content:
                    # If using 'import datetime', the timezone usage should be datetime.timezone
                    # This is already correct, but let's check for incorrect usage
                    if "timezone.utc" in content and "datetime.timezone.utc" not in content:
                        # Need to replace timezone.utc with datetime.timezone.utc
                        new_content = content.replace("timezone.utc", "datetime.timezone.utc")

                        with open(abs_path, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        print(f"✅ Fixed timezone usage in: {file_path}")
                        fixes_applied += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(f"\n🎯 Applied {fixes_applied} timezone import fixes")
    return fixes_applied

if __name__ == "__main__":
    fix_timezone_imports()