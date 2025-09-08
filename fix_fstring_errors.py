#!/usr/bin/env python3
"""
Custom F-String Error Fixer
Targets the most common f-string syntax errors in the LUKHAS codebase
"""
import re
import sys
from pathlib import Path


class FStringFixer:
    def __init__(self):
        self.fixed_count = 0
        self.failed_count = 0

    def fix_single_brace(self, line: str) -> str:
        """Fix single '}' without matching '{' in f-strings"""
        if 'f"' in line or "f'" in line:
            # Pattern to find single } that should be escaped
            # Look for } not preceded by { and not already escaped
            pattern = r"(?<![{])}(?!})"
            # Replace with escaped version
            line = re.sub(pattern, "}}", line)
        return line

    def fix_mismatched_parens_in_fstring(self, line: str) -> str:
        """Fix f-string: closing parenthesis '}' does not match opening parenthesis '('"""
        # Pattern: f"...{expression(...)}"
        # Common issue: f"...{len(something} - 10}"
        pattern = r'(f["\'].*?\{[^}]*\([^)]*)(})'

        def replacer(match):
            content = match.group(1)
            # Count unmatched opening parens
            open_parens = content.count("(") - content.count(")")
            if open_parens > 0:
                return content + ")" * open_parens + "}"
            return match.group(0)

        return re.sub(pattern, replacer, line)

    def fix_unterminated_fstring(self, line: str) -> str:
        """Fix unterminated f-strings"""
        # Check if line has f" or f' but no closing quote
        if 'f"' in line:
            if line.count('"') % 2 != 0:
                line = line.rstrip() + '"\n'
        elif "f'" in line:
            if line.count("'") % 2 != 0:
                line = line.rstrip() + "'\n"
        return line

    def fix_file(self, filepath: Path) -> bool:
        """Fix all f-string errors in a file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            fixed_lines = []
            changed = False

            for line in lines:
                original = line

                # Apply fixes in order
                line = self.fix_mismatched_parens_in_fstring(line)
                line = self.fix_single_brace(line)
                line = self.fix_unterminated_fstring(line)

                if line != original:
                    changed = True

                fixed_lines.append(line)

            if changed:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(fixed_lines)
                self.fixed_count += 1
                return True

            return False

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            self.failed_count += 1
            return False

    def fix_directory(self, directory: str) -> None:
        """Fix all Python files in a directory"""
        path = Path(directory)
        python_files = list(path.rglob("*.py"))

        print(f"Found {len(python_files)} Python files in {directory}")

        for i, filepath in enumerate(python_files, 1):
            if i % 100 == 0:
                print(f"Processing file {i}/{len(python_files)}...")

            self.fix_file(filepath)

        print("\nResults:")
        print(f"  Fixed: {self.fixed_count} files")
        print(f"  Failed: {self.failed_count} files")
        print(f"  Unchanged: {len(python_files) - self.fixed_count - self.failed_count} files")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_fstring_errors.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    fixer = FStringFixer()
    fixer.fix_directory(directory)


if __name__ == "__main__":
    main()
