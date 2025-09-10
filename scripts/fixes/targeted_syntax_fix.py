#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Targeted syntax fixer for LUKHAS repository
Focus on common fixable patterns while avoiding complex issues
"""

import ast
import os
import re


def fix_simple_patterns(content):
    """Fix simple, predictable syntax patterns"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Fix 1: Function definition with colon at start: "def add_connection(:"
        if re.match(r"^(\s*def\s+\w+)\(:$", line):
            line = re.sub(r"^(\s*def\s+\w+)\(:$", r"\1(self:", line)

        # Fix 2: Broken logger statements ending with quote and paren
        if re.match(r'^\s*self\.logger\.(info|debug|warning|error|critical)\(".*"\)$', line) and '")"' in line:
            line = line.replace('")"', '")')

        # Fix 3: Simple unmatched quotes in logger statements
        if "logger." in line and line.count('"') % 2 != 0 and line.strip().endswith(","):
            line = line.rstrip(",") + '",'

        # Fix 4: Generator expressions that need parentheses
        if "for " in line and " if " in line and not line.strip().startswith("(") and "lambda" not in line:
            # Check if it's a generator expression that needs parens
            if re.search(r"\w+\s+for\s+\w+\s+in\s+\w+\s+if\s+", line) and not re.search(r"[\[\(].*for.*[\]\)]", line):
                # Add parentheses around generator expression
                match = re.search(r"(\w+\s+for\s+\w+\s+in\s+\w+\s+if\s+[^,\n]+)", line)
                if match:
                    expr = match.group(1)
                    line = line.replace(expr, f"({expr})")

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def can_fix_file(filepath):
    """Check if file has fixable syntax errors"""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Try to parse - if it works, no syntax error
        try:
            ast.parse(content)
            return False, "No syntax error"
        except SyntaxError as e:
            error_msg = str(e)

            # Check for patterns we can fix
            fixable_patterns = [
                "invalid syntax",
                "EOL while scanning string literal",
                "Generator expression must be parenthesized",
                "unmatched",
                "closing parenthesis",
                "unexpected indent",
            ]

            if any(pattern in error_msg for pattern in fixable_patterns):
                return True, error_msg
            else:
                return False, f"Complex error: {error_msg}"

    except Exception as e:
        return False, f"Read error: {e}"


def fix_file(filepath):
    """Fix a single file"""
    try:
        with open(filepath, encoding="utf-8") as f:
            original_content = f.read()

        # Apply fixes
        fixed_content = fix_simple_patterns(original_content)

        # Test if fix worked
        try:
            ast.parse(fixed_content)
            # Success - write back
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            return True, "Fixed successfully"
        except SyntaxError as e:
            return False, f"Fix didn't work: {e}"

    except Exception as e:
        return False, f"Error processing file: {e}"


def main():
    """Main execution"""
    print("🔧 Targeted Syntax Fixer for LUKHAS")
    print("=" * 50)

    fixed_count = 0
    failed_count = 0
    skipped_count = 0

    # Walk through Python files
    for root, _dirs, files in os.walk("."):
        # Skip problematic directories
        if any(skip in root for skip in [".venv", ".git", "__pycache__", ".pytest_cache", "node_modules"]):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                can_fix, reason = can_fix_file(filepath)

                if can_fix:
                    success, message = fix_file(filepath)
                    if success:
                        print(f"✅ Fixed: {filepath}")
                        fixed_count += 1
                    else:
                        print(f"❌ Failed to fix {filepath}: {message}")
                        failed_count += 1
                else:
                    if "No syntax error" not in reason:
                        print(f"⏭️  Skipped {filepath}: {reason}")
                        skipped_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Results: {fixed_count} fixed, {failed_count} failed, {skipped_count} skipped")


if __name__ == "__main__":
    main()
