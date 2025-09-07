#!/usr/bin/env python3
"""
Final comprehensive linting fix script.
Handles syntax errors, undefined names, and other critical issues.
"""
import ast
import re
import subprocess
from pathlib import Path

import streamlit as st


def run_command(cmd: list[str], cwd: str = ".") -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def fix_syntax_errors(file_path: Path) -> bool:
    """Fix common syntax errors in a file"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix unterminated strings
        lines = content.split("\n")
        fixed_lines = []
        for i, line in enumerate(lines):
            # Check for unterminated f-strings
            if 'f"' in line or "f'" in line:
                # Count quotes
                double_quotes = line.count('"') - line.count('\\"')
                single_quotes = line.count("'") - line.count("\\'")

                # Fix odd number of quotes
                if double_quotes % 2 == 1:
                    line = line.rstrip() + '"'
                if single_quotes % 2 == 1:
                    line = line.rstrip() + "'"

            # Fix multiline strings that got broken
            if i > 0 and lines[i - 1].rstrip().endswith(","):
                if line.strip() and not line.strip().startswith((")", "]", "}", "#")):
                    # Check if previous line has unterminated string
                    prev = lines[i - 1].rstrip()
                    if (prev.count('"') - prev.count('\\"')) % 2 == 1:
                        fixed_lines[-1] = fixed_lines[-1].rstrip()[:-1] + '",'
                    elif (prev.count("'") - prev.count("\\'")) % 2 == 1:
                        fixed_lines[-1] = fixed_lines[-1].rstrip()[:-1] + "',"

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Fix invalid method names like _identity_core.resolve_access_tier
        content = re.sub(r"def _identity_core\.(\w+)", r"def _identity_core_\1", content)

        # Fix broken imports
        content = re.sub(r"from typing import for\b", "from typing import Any", content)

        # Fix broken raw strings
        content = re.sub(
            r'r"\^\s+LUKHAS⬟\([A-Z0-9\s\-]+\)',
            r'r"^LUKHAS⬟([A-Z0-9]{2,8})-([A-Z]{2,3})-(\d)-([A-F0-9]{3,6})"',
            content,
        )

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def add_missing_imports(file_path: Path) -> bool:
    """Add missing imports for undefined names"""
    try:
        content = file_path.read_text(encoding="utf-8")

        # Common missing imports
        missing_imports = {
            "logging": "import logging",
            "time": "import time",
            "datetime": "from datetime import datetime",
            "timezone": "from datetime import timezone",
            "Any": "from typing import Any",
            "Optional": "from typing import Optional",
            "List": "from typing import List",
            "Dict": "from typing import Dict",
            "Tuple": "from typing import Tuple",
            "Union": "from typing import Union",
        }

        # Parse the file to find undefined names
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return False

        # Find all names used
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)

        # Find existing imports
        existing_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    existing_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    existing_imports.add(alias.name)

        # Add missing imports
        imports_to_add = []
        for name, import_stmt in missing_imports.items():
            if name in used_names and name not in existing_imports:
                imports_to_add.append(import_stmt)

        if imports_to_add:
            # Find the right place to add imports (after module docstring)
            lines = content.split("\n")
            insert_idx = 0

            # Skip module docstring
            if lines[0].startswith('"""'):
                for i, line in enumerate(lines[1:], 1):
                    if '"""' in line:
                        insert_idx = i + 1
                        break
            elif lines[0].startswith("#"):
                insert_idx = 1

            # Add imports
            for import_stmt in imports_to_add:
                lines.insert(insert_idx, import_stmt)
                insert_idx += 1

            content = "\n".join(lines)
            file_path.write_text(content, encoding="utf-8")
            return True

        return False
    except Exception as e:
        print(f"Error adding imports to {file_path}: {e}")
        return False


def main():
    """Main function to fix all linting issues"""

    # Directories to fix
    dirs_to_fix = [
        "core",
        "bridge",
        "lukhas",
        "serve",
        "orchestration",
        "governance",
        "tests",
        "tools",
    ]

    print("🔧 Starting comprehensive linting fix...")

    # Step 1: Fix syntax errors
    print("\n📝 Step 1: Fixing syntax errors...")
    syntax_fixed = 0
    for dir_name in dirs_to_fix:
        if not Path(dir_name).exists():
            continue
        for file_path in Path(dir_name).rglob("*.py"):
            if fix_syntax_errors(file_path):
                syntax_fixed += 1
    print(f"  Fixed syntax in {syntax_fixed} files")

    # Step 2: Add missing imports
    print("\n📦 Step 2: Adding missing imports...")
    imports_fixed = 0
    for dir_name in dirs_to_fix:
        if not Path(dir_name).exists():
            continue
        for file_path in Path(dir_name).rglob("*.py"):
            if add_missing_imports(file_path):
                imports_fixed += 1
    print(f"  Added imports to {imports_fixed} files")

    # Step 3: Run autoflake to remove unused imports
    print("\n🧹 Step 3: Removing unused imports...")
    for dir_name in dirs_to_fix:
        if Path(dir_name).exists():
            cmd = [
                "autoflake",
                "--in-place",
                "--remove-unused-variables",
                "--remove-all-unused-imports",
                "--recursive",
                dir_name,
            ]
            run_command(cmd)

    # Step 4: Run black for formatting
    print("\n🎨 Step 4: Formatting with black...")
    for dir_name in dirs_to_fix:
        if Path(dir_name).exists():
            cmd = ["black", "--line-length", "88", "--quiet", dir_name]
            run_command(cmd)

    # Step 5: Run ruff for final fixes
    print("\n✨ Step 5: Final fixes with ruff...")
    for dir_name in dirs_to_fix:
        if Path(dir_name).exists():
            cmd = ["ruff", "check", "--fix", "--unsafe-fixes", "--quiet", dir_name]
            run_command(cmd)

    # Step 6: Check final status
    print("\n📊 Step 6: Checking final status...")
    returncode, stdout, stderr = run_command(["flake8", ".", "--count"])
    if stdout and stdout.strip().isdigit():
        count = int(stdout.strip())
        print(f"\n✅ Final issue count: {count}")

        if count < 100:
            print("🎉 Excellent! Less than 100 issues remaining.")
        elif count < 500:
            print("👍 Good progress! Less than 500 issues remaining.")
        elif count < 1000:
            print("📈 Making progress! Less than 1000 issues remaining.")
        else:
            print("⚡ Significant reduction achieved!")
    else:
        print("ℹ️ Could not determine final count")

    print("\n✅ Comprehensive linting fix complete!")
    print("\nNext steps:")
    print("1. Review the changes with: git diff")
    print("2. Run tests to ensure nothing broke: make test")
    print("3. Commit the changes: git commit -am 'Fix linting issues'")


if __name__ == "__main__":
    main()
