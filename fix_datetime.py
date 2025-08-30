#!/usr/bin/env python3
"""Fix datetime.now() calls to include timezone.utc"""

import os
import re
import subprocess


def fix_datetime_files():
    """Fix datetime issues in lukhas/ files"""

    # Get files with DTZ005 errors
    result = subprocess.run(
        ["python3", "-m", "ruff", "check", "lukhas/", "--select", "DTZ005"], capture_output=True, text=True
    )

    files_to_fix = set()
    for line in result.stderr.split("\n"):
        if ".py:" in line and "DTZ005" in line:
            file_path = line.split(":")[0]
            if file_path.startswith("lukhas/"):
                files_to_fix.add(file_path)

    print(f"Found {len(files_to_fix)} files to fix")

    for file_path in files_to_fix:
        try:
            with open(file_path) as f:
                content = f.read()

            # Add timezone import if not present
            if "from datetime import" in content and "timezone" not in content:
                content = content.replace("from datetime import datetime", "from datetime import datetime, timezone")
            elif "import datetime" in content and "from datetime import" not in content:
                # Handle cases with just 'import datetime'
                pass  # Will handle datetime.now() -> datetime.now(timezone.utc)

            # Fix datetime.now() calls
            content = re.sub(r"datetime\.now\(\)", "datetime.now(timezone.utc)", content)
            content = re.sub(r"datetime\.utcnow\(\)", "datetime.now(timezone.utc)", content)

            with open(file_path, "w") as f:
                f.write(content)

            print(f"Fixed: {file_path}")

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")


if __name__ == "__main__":
    fix_datetime_files()
