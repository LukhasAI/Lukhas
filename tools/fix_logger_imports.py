#!/usr/bin/env python3
"""
Fix logger/logging import issues across LUKHAS codebase
Resolves F821 violations for logger and logging usage
"""
import json
import os
from pathlib import Path


def fix_logger_imports():
    """Fix logger import issues by adding proper import statements"""

    # Load F821 violations
    with open("/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/idx_F821.json") as f:
        data = json.load(f)

    # Find files with logger/logging F821 violations
    logger_files = set()
    for violation in data["violations"]:
        if violation["message"] in ["Undefined name `logger`", "Undefined name `logging`"]:
            logger_files.add(violation["filename"])

    print(f"Found {len(logger_files)} files with logger/logging F821 violations")

    fixes_applied = 0
    for file_path in logger_files:
        abs_path = Path(f"/Users/agi_dev/LOCAL-REPOS/Lukhas/{file_path}")

        if not abs_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue

        try:
            with open(abs_path, encoding="utf-8") as f:
                content = f.read()

            needs_logging_import = False
            needs_logger_setup = False

            # Check what's needed
            if "logging." in content and "import logging" not in content:
                needs_logging_import = True

            if "logger." in content and "logger =" not in content and "get_logger" not in content:
                needs_logger_setup = True

            if not needs_logging_import and not needs_logger_setup:
                continue

            lines = content.split("\n")
            import_insertion_index = 0

            # Find the best place to add imports (after existing imports)
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    import_insertion_index = i + 1
                elif stripped and not stripped.startswith("#") and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    break

            # Add logging import if needed
            if needs_logging_import:
                lines.insert(import_insertion_index, "import logging")
                import_insertion_index += 1

            # Add logger setup if needed (common LUKHAS pattern)
            if needs_logger_setup:
                # Check if file uses LUKHAS logger pattern
                if "ΛTRACE" in content or "LUKHAS" in content:
                    lines.insert(import_insertion_index, "logger = logging.getLogger(__name__)")
                else:
                    lines.insert(import_insertion_index, "logger = logging.getLogger(__name__)")
                import_insertion_index += 1

            new_content = "\n".join(lines)

            # Write back the fixed content
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"✅ Fixed logger imports in: {file_path}")
            fixes_applied += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(f"\n🎯 Applied {fixes_applied} logger import fixes")
    return fixes_applied

if __name__ == "__main__":
    fix_logger_imports()
