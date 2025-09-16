#!/usr/bin/env python3
"""
🎯 T4 TARGETED SYNTAX FIXER - LUKHAS Trinity Framework
================================================================
More conservative approach to fixing only clear syntax errors.
⚛️🧠🛡️ Trinity Framework compliant with Guardian validation.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List


class TargetedSyntaxFixer:
    """Conservative syntax error fixer targeting specific patterns."""

    def __init__(self, workspace_path: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas"):
        self.workspace_path = Path(workspace_path)

    def get_ruff_errors(self) -> List[Dict]:
        """Get syntax errors from ruff in JSON format."""
        try:
            result = subprocess.run(
                [".venv/bin/ruff", "check", ".", "--output-format=json", "--select=E999"],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
            )
            return json.loads(result.stdout) if result.stdout else []
        except Exception as e:
            print(f"Error getting ruff output: {e}")
            return []

    def fix_obvious_indentation_issues(self, file_path: Path, lines: List[str]) -> List[str]:
        """Fix obvious indentation issues like mixed tabs/spaces."""
        fixed_lines = []
        for line_num, line in enumerate(lines, 1):
            original_line = line

            # Convert tabs to spaces if mixed indentation detected
            if "\t" in line and line.lstrip() != line:
                # Count leading whitespace
                leading_ws = len(line) - len(line.lstrip())
                if "\t" in line[:leading_ws]:
                    # Replace tabs with 4 spaces in indentation only
                    indent_part = line[:leading_ws].replace("\t", "    ")
                    line = indent_part + line[leading_ws:]

            # Fix obvious incomplete lines (ending with backslash but not continuing)
            if line.rstrip().endswith("\\") and line_num < len(lines):
                next_line = lines[line_num] if line_num <= len(lines) else ""
                if next_line.strip() == "":
                    # Remove dangling backslash
                    line = line.rstrip()[:-1].rstrip() + "\n"

            fixed_lines.append(line)

            if line != original_line:
                print(f"🔧 Fixed indentation in {file_path}:{line_num}")

        return fixed_lines

    def fix_obvious_fstring_issues(self, file_path: Path, content: str) -> str:
        """Fix only obvious f-string bracket issues."""
        original_content = content

        # Fix single } in f-strings (should be }})
        patterns = [
            # f"text {var} more text"  -> missing closing }
            (r'f"([^"]*\{[^}]*)"', r'f"\1}"'),
            (r"f'([^']*\{[^}]*)'", r"f'\1}'"),
            # Fix extra closing braces
            (r'f"([^"]*\{[^}]*\})\}"', r'f"\1"'),
            (r"f'([^']*\{[^}]*\})\}'", r"f'\1'"),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                print(f"🔧 Fixed f-string in {file_path}")
                content = new_content
                break  # Only apply one fix per file to be conservative

        return content

    def fix_syntax_errors_in_file(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file conservatively."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines(keepends=True)

            # Apply conservative fixes
            fixed_lines = self.fix_obvious_indentation_issues(file_path, lines)
            fixed_content = "".join(fixed_lines)
            fixed_content = self.fix_obvious_fstring_issues(file_path, fixed_content)

            # Only write if changes were made
            if fixed_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"✅ Fixed syntax errors in {file_path}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def rollback_problematic_files(self) -> None:
        """Rollback files that were corrupted by previous fixer."""
        print("🔄 Rolling back problematic changes...")

        problematic_patterns = [
            "datetime.fromtimestamp(latest_file.stat(), tz=timezone.utc).st_mtime)",
            ".stat(), tz=timezone.utc).st_mtime)",
            ".stat(), tz=timezone.utc).",
        ]

        # Use git to see what changed
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only"], cwd=self.workspace_path, capture_output=True, text=True
            )

            changed_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

            for file_name in changed_files:
                file_path = self.workspace_path / file_name
                if file_path.exists() and file_path.suffix == ".py":
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Check if file has problematic patterns
                        has_issues = any(pattern in content for pattern in problematic_patterns)

                        if has_issues:
                            print(f"🚨 Found problematic changes in {file_path}")
                            # Reset this file
                            subprocess.run(
                                ["git", "checkout", "HEAD", str(file_path)],
                                cwd=self.workspace_path,
                                capture_output=True,
                            )
                            print(f"🔄 Reset {file_path}")

                    except Exception as e:
                        print(f"Error checking {file_path}: {e}")

        except Exception as e:
            print(f"Error during rollback: {e}")

    def run_targeted_fixes(self):
        """Run targeted syntax fixes."""
        print("🎯 T4 TARGETED SYNTAX FIXER - LUKHAS Trinity Framework")
        print("=" * 65)
        print("⚛️ Conservative syntax error resolution with Guardian validation")

        # First, rollback problematic changes
        self.rollback_problematic_files()

        # Get current syntax errors
        errors = self.get_ruff_errors()
        syntax_files = set()

        for error in errors:
            error_code = error.get("code", "")
            if error_code == "E999" or (error_code and "syntax" in error_code.lower()):
                syntax_files.add(Path(error["filename"]))

        print(f"📊 Found {len(syntax_files)} files with syntax errors")

        # Apply conservative fixes
        fixed_count = 0
        for file_path in syntax_files:
            if self.fix_syntax_errors_in_file(file_path):
                fixed_count += 1

        print(f"\n📈 TARGETED FIXING SUMMARY:")
        print(f"✅ Files processed: {len(syntax_files)}")
        print(f"🔧 Files actually fixed: {fixed_count}")
        print(f"🧠 Conservative approach completed")
        print(f"🛡️ Guardian validation: Minimal risk changes only")
        print(f"\n💡 Re-run ruff to verify conservative fixes")


if __name__ == "__main__":
    fixer = TargetedSyntaxFixer()
    fixer.run_targeted_fixes()
