#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
Fix common syntax errors in the LUKHAS codebase
"""

import ast
import os
import re
from pathlib import Path


def fix_broken_strings(content: str) -> str:
    """Fix broken string literals with newlines"""

    # Fix multiline string literals that are broken
    patterns = [
        # Pattern: logger.info("
        # Next line: some text")
        (r'logger\.info\("[\n\r]', 'logger.info("'),
        (r'logger\.debug\("[\n\r]', 'logger.debug("'),
        (r'logger\.warning\("[\n\r]', 'logger.warning("'),
        (r'logger\.error\("[\n\r]', 'logger.error("'),
        (r'print\("[\n\r]', 'print("'),
        # Fix lines that start with emojis and close quote
        (r'^([🎯🔐🛡️✅❌⚡🧠⚛️🌟🔧📊💡🎭🚀]+[^"]*")\)', r'logger.info("\1)'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    return content


def fix_unclosed_parentheses(content: str) -> str:
    """Fix obvious unclosed parentheses"""

    lines = content.split("\n")
    fixed_lines = []

    for _i, line in enumerate(lines):
        # If line starts with emoji and ends with "), probably should be a string
        if re.match(r'^\s*[🎯🔐🛡️✅❌⚡🧠⚛️🌟🔧📊💡🎭🚀].*"\)$', line.strip()):
            # Convert to proper logger statement
            stripped = line.strip()
            if not stripped.startswith("logger."):
                line = line.replace(stripped, f'        logger.info("{stripped.rstrip("}")}")')

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_file_syntax(filepath: Path) -> bool:
    """Fix syntax errors in a single file"""

    try:
        with open(filepath, encoding="utf-8") as f:
            original_content = f.read()
    except UnicodeDecodeError:
        print(f"⚠️ Skipping {filepath} - encoding issue")
        return False

    # Try to parse original
    try:
        ast.parse(original_content)
        return True  # Already valid
    except SyntaxError:
        pass  # Expected, we'll try to fix

    content = original_content

    # Apply fixes
    content = fix_broken_strings(content)
    content = fix_unclosed_parentheses(content)

    # Test if fixed
    try:
        ast.parse(content)
        print(f"✅ Fixed: {filepath}")

        # Write back
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    except SyntaxError as e:
        print(f"❌ Could not fix {filepath}: {e}")
        return False


def main():
    """Fix syntax errors in Python files"""

    fixed = 0
    failed = 0

    # Find Python files with syntax errors
    for root, _dirs, files in os.walk("."):
        # Skip problematic directories
        if any(skip in root for skip in [".venv", ".git", "__pycache__", ".pytest_cache", "node_modules"]):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file

                try:
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                    ast.parse(content)
                    # File is already valid
                    continue
                except SyntaxError:
                    # Try to fix it
                    if fix_file_syntax(filepath):
                        fixed += 1
                    else:
                        failed += 1
                except (UnicodeDecodeError, Exception):
                    continue

    print(f"\n📊 Results: {fixed} files fixed, {failed} files could not be fixed")


if __name__ == "__main__":
    main()