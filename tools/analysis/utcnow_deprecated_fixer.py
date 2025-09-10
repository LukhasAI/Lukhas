#!/usr/bin/env python3
"""
Phase 5C continuation: Fix deprecated datetime.utcnow() and fromtimestamp() calls
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def get_dtz_violations() -> list[dict]:
    """Get DTZ006/DTZ007 violations (deprecated datetime methods)."""
    try:
        result = subprocess.run(
            [
                ".venv/bin/ruff",
                "check",
                ".",
                "--select=DTZ006,DTZ007",
                "--output-format=json",
                "--quiet",
                "--exclude=archive/",
                "--exclude=website_v1/",
                "--exclude=products/shared/gpt_oss_integration/",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        if result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error getting DTZ violations: {e}")
        return []


def create_deprecated_datetime_patterns() -> dict[str, str]:
    """Create patterns for fixing deprecated datetime methods."""
    return {
        # datetime.utcnow() -> datetime.now(timezone.utc)
        r"datetime\.utcnow\(\)": "datetime.now(timezone.utc)",
        r"datetime\.datetime\.utcnow\(\)": "datetime.now(timezone.utc)",
        # With assignments
        r"(\w+)\s*=\s*datetime\.utcnow\(\)": r"\1 = datetime.now(timezone.utc)",
        r"(\w+)\s*=\s*datetime\.datetime\.utcnow\(\)": r"\1 = datetime.now(timezone.utc)",
        # datetime.fromtimestamp(x) -> datetime.fromtimestamp(x, tz=timezone.utc)
        r"datetime\.fromtimestamp\(([^)]+)\)": r"datetime.fromtimestamp(\1, tz=timezone.utc)",
        r"datetime\.datetime\.fromtimestamp\(([^)]+)\)": r"datetime.fromtimestamp(\1, tz=timezone.utc)",
        # strptime without timezone info - add timezone.utc context
        r"datetime\.strptime\(([^)]+)\)": r"datetime.strptime(\1).replace(tzinfo=timezone.utc)",
        r"datetime\.datetime\.strptime\(([^)]+)\)": r"datetime.strptime(\1).replace(tzinfo=timezone.utc)",
    }


def ensure_timezone_import(content: str) -> str:
    """Ensure timezone import is present when needed."""
    if "timezone.utc" in content:
        # Check if timezone is already imported
        if "from datetime import" in content and "timezone" not in content:
            # Replace existing datetime import to include timezone
            content = re.sub(r"from datetime import ([^;\n]+)", r"from datetime import \1, timezone", content)
        elif "import datetime" in content and "from datetime import" not in content:
            # Add specific timezone import
            content = re.sub(r"import datetime", "import datetime\nfrom datetime import timezone", content)
        elif "from datetime import" not in content and "import datetime" not in content:
            # Add full import at top
            lines = content.split("\n")
            import_line = "from datetime import datetime, timezone"

            # Find insertion point
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1
                elif line.strip().startswith('"""') and i < 10:
                    # Skip docstring
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip().endswith('"""'):
                            insert_idx = j + 1
                            break

            lines.insert(insert_idx, import_line)
            content = "\n".join(lines)

    return content


def fix_file_deprecated_datetime(file_path: str, patterns: dict[str, str]) -> tuple[bool, int]:
    """Fix deprecated datetime issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        fixes_applied = 0

        # Apply deprecated datetime fixing patterns
        for pattern, replacement in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_applied += len(matches)

        # Ensure timezone import if needed
        if fixes_applied > 0:
            content = ensure_timezone_import(content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, fixes_applied

        return False, 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0


def run_world_tests() -> bool:
    """Run world tests to validate changes."""
    try:
        result = subprocess.run(
            [
                ".venv/bin/pytest",
                "tests/test_basic_functions.py",
                "tests/memory/test_memory_basic.py",
                "tests/test_aka_qualia.py::TestT1T2Integration::test_complete_cycle_dangerous_input",
                "-q",
                "--disable-warnings",
            ],
            capture_output=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        return result.returncode == 0
    except Exception as e:
        print(f"World test error: {e}")
        return False


def main():
    """Fix deprecated datetime methods."""
    print("🕐 Phase 5C: Deprecated datetime method fixes")
    print("🎯 Converting utcnow(), fromtimestamp(), strptime() to UTC")
    print()

    violations = get_dtz_violations()
    if not violations:
        print("✅ No deprecated datetime violations found!")
        return

    print(f"📊 Found {len(violations)} deprecated datetime violations")

    # Group by file
    files_to_fix = {}
    for violation in violations:
        filename = violation["filename"]
        if filename not in files_to_fix:
            files_to_fix[filename] = []
        files_to_fix[filename].append(violation)

    print(f"📁 Files to process: {len(files_to_fix)}")

    # Get fixing patterns
    patterns = create_deprecated_datetime_patterns()

    total_fixes = 0
    files_processed = 0

    for file_path in files_to_fix:
        rel_path = file_path.replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
        print(f"📝 {rel_path}")

        fixed, fixes = fix_file_deprecated_datetime(file_path, patterns)
        if fixed:
            total_fixes += fixes
            files_processed += 1
            print(f"   ✅ {fixes} deprecated datetime fixes applied")
        else:
            print("   ⚪ No changes needed")

    print("\n🎯 Deprecated datetime fixes:")
    print(f"   📁 Files processed: {files_processed}")
    print(f"   🔧 Total fixes: {total_fixes}")

    # Validate
    if run_world_tests():
        print("   ✅ World tests PASSED")
        print("\n🎉 Deprecated datetime fixes COMPLETE!")
    else:
        print("   ❌ World tests FAILED")


if __name__ == "__main__":
    main()
