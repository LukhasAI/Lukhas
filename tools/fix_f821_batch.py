#!/usr/bin/env python3
"""
F821 undefined-name batch fixer for LUKHAS codebase.
Fixes common undefined name patterns systematically.
"""

import json
import re
import subprocess
from collections import defaultdict


def get_f821_violations():
    """Get F821 undefined-name violations from ruff."""
    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", ".", "--select", "F821", "--output-format=json"],
            capture_output=True,
            text=True,
            cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
        )

        if result.stdout:
            violations = json.loads(result.stdout)
            return violations
    except Exception as e:
        print(f"Error getting F821 violations: {e}")

    return []


def analyze_undefined_patterns(violations):
    """Analyze patterns in undefined names."""
    patterns = defaultdict(list)

    for violation in violations:
        filename = violation.get("filename", "")
        message = violation.get("message", "")

        # Skip archive files to focus on active code
        if "archive/" in filename or ".git/" in filename:
            continue

        # Extract undefined name
        if "Undefined name" in message and "'" in message:
            name = message.split("'")[1]
            patterns[name].append(filename)

    return patterns


def fix_timezone_imports(file_path):
    """Fix missing timezone imports."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Check if timezone is used but not imported
        if "timezone.utc" in content or "datetime.now(timezone" in content:
            # Check if timezone is already imported
            if "from datetime import" in content and "timezone" not in content:
                # Add timezone to existing datetime import
                content = re.sub(
                    r"from datetime import ([^)]+)",
                    lambda m: f"from datetime import {m.group(1).rstrip()}, timezone",
                    content,
                    count=1,
                )
            elif "import datetime" in content and "from datetime import" not in content:
                # For import datetime style, use datetime.timezone.utc
                content = re.sub(r"timezone\.utc", "datetime.timezone.utc", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing timezone in {file_path}: {e}")
        return False


def fix_logger_declarations(file_path):
    """Fix missing logger declarations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Check if logger is used but not declared
        if "logger." in content:
            # Check if logger is already imported/declared
            if (
                ("import logging" not in content
                and "logger = " not in content
                and "from" not in content)
                or "logger" not in content
            ):
                # Add basic logger setup at the top after imports
                lines = content.split("\n")
                import_end = 0

                for i, line in enumerate(lines):
                    if (
                        line.startswith("import ")
                        or line.startswith("from ")
                        or line.strip() == ""
                        or line.strip().startswith("#")
                    ):
                        import_end = i + 1
                    else:
                        break

                # Insert logger setup
                logger_setup = ["", "# Logger setup", "import logging", "logger = logging.getLogger(__name__)", ""]

                lines[import_end:import_end] = logger_setup
                content = "\n".join(lines)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing logger in {file_path}: {e}")
        return False


def fix_typing_imports(file_path):
    """Fix missing typing imports."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Common typing imports that might be missing
        typing_needs = []

        if re.search(r"\bSet\b", content):
            typing_needs.append("Set")
        if re.search(r"\bDict\b", content):
            typing_needs.append("Dict")
        if re.search(r"\bList\b", content):
            typing_needs.append("List")
        if re.search(r"\bOptional\b", content):
            typing_needs.append("Optional")
        if re.search(r"\bUnion\b", content):
            typing_needs.append("Union")
        if re.search(r"\bAny\b", content):
            typing_needs.append("Any")

        if typing_needs:
            # Check if typing is already imported
            has_typing_import = False
            typing_imports = set()

            for line in content.split("\n"):
                if "from typing import" in line:
                    has_typing_import = True
                    # Extract existing imports
                    match = re.search(r"from typing import (.+)", line)
                    if match:
                        existing = match.group(1).split(",")
                        typing_imports.update(imp.strip() for imp in existing)
                    break

            # Add missing typing imports
            missing = [t for t in typing_needs if t not in typing_imports]

            if missing:
                if has_typing_import:
                    # Add to existing import
                    all_imports = sorted(list(typing_imports) + missing)
                    content = re.sub(
                        r"from typing import .+", f'from typing import {", ".join(all_imports)}', content, count=1
                    )
                else:
                    # Add new typing import
                    lines = content.split("\n")
                    import_line = f'from typing import {", ".join(missing)}'

                    # Find where to insert
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            insert_pos = i + 1

                    lines.insert(insert_pos, import_line)
                    content = "\n".join(lines)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing typing in {file_path}: {e}")
        return False


def main():
    """Main F821 fixing routine."""
    print("🔧 Fixing F821 undefined-name violations...")

    violations = get_f821_violations()
    patterns = analyze_undefined_patterns(violations)

    print(f"Found F821 violations for {len(patterns)} undefined names")
    for name, files in list(patterns.items())[:10]:
        print(f"  {name}: {len(files)} files")

    # Focus on most common issues
    fixed_files = set()
    total_fixed = 0

    # Fix timezone issues
    if "timezone" in patterns:
        print(f"\n🕒 Fixing timezone issues in {len(patterns['timezone'])} files...")
        for file_path in patterns["timezone"][:50]:  # Limit batch size
            if fix_timezone_imports(file_path):
                fixed_files.add(file_path)
                total_fixed += 1

    # Fix logger issues
    if "logger" in patterns:
        print(f"\n📝 Fixing logger issues in {len(patterns['logger'])} files...")
        for file_path in patterns["logger"][:30]:  # Smaller batch
            if fix_logger_declarations(file_path):
                fixed_files.add(file_path)
                total_fixed += 1

    # Fix typing issues
    typing_names = ["Set", "Dict", "List", "Optional", "Union", "Any"]
    for name in typing_names:
        if name in patterns:
            print(f"\n🔤 Fixing {name} typing issues in {len(patterns[name])} files...")
            for file_path in patterns[name][:20]:  # Small batch
                if fix_typing_imports(file_path):
                    fixed_files.add(file_path)
                    total_fixed += 1

    print(f"\n🎉 Fixed F821 issues in {len(fixed_files)} unique files")

    # Show sample of fixed files
    for file_path in list(fixed_files)[:10]:
        short_path = file_path.replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
        print(f"  ✅ {short_path}")

    return len(fixed_files)


if __name__ == "__main__":
    main()
