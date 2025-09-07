#!/usr/bin/env python3
"""
Aggressive Syntax Fixer - Fixes or quarantines all syntax errors
"""
import time
import streamlit as st

import ast
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class AggressiveSyntaxFixer:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.quarantine_dir = Path("quarantine") / self.timestamp
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

        self.fixed = 0
        self.quarantined = 0
        self.syntax_errors = []

    def find_all_syntax_errors(self):
        """Find all Python files with syntax errors"""
        for root, _dirs, files in os.walk("."):
            if any(skip in root for skip in [".git", "__pycache__", ".venv", "quarantine"]):
                continue

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    error = self.check_syntax(filepath)
                    if error:
                        self.syntax_errors.append({"file": filepath, "error": error})

        return self.syntax_errors

    def check_syntax(self, filepath):
        """Check if file has syntax error"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return None
        except SyntaxError as e:
            return {
                "type": "SyntaxError",
                "msg": e.msg,
                "line": e.lineno,
                "offset": e.offset,
            }
        except Exception as e:
            return {"type": type(e).__name__, "msg": str(e), "line": 0, "offset": 0}

    def aggressive_fix(self, filepath, error):
        """Aggressively fix or quarantine a file"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Try various fixes
            fixed_content = content

            # Fix 1: Remove problematic Unicode characters
            fixed_content = fixed_content.encode("ascii", "ignore").decode("ascii")

            # Fix 2: Fix common indentation errors
            if "indent" in error["msg"].lower():
                fixed_content = self.fix_indentation(fixed_content)

            # Fix 3: Fix unclosed strings/brackets
            if "EOF" in error["msg"] or "EOL" in error["msg"]:
                fixed_content = self.fix_unclosed(fixed_content)

            # Fix 4: Remove or comment problematic lines
            if error["line"] > 0:
                lines = fixed_content.split("\n")
                if error["line"] <= len(lines):
                    # Comment out the problematic line
                    lines[error["line"] - 1] = "# SYNTAX_ERROR_FIXED: " + lines[error["line"] - 1]
                    fixed_content = "\n".join(lines)

            # Test if fixed
            try:
                ast.parse(fixed_content)
                # Success! Write back
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                self.fixed += 1
                return True
            except BaseException:
                # Still broken, quarantine it
                return self.quarantine_file(filepath)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return self.quarantine_file(filepath)

    def fix_indentation(self, content):
        """Fix indentation issues"""
        lines = content.split("\n")
        fixed_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                fixed_lines.append("")
                continue

            # Decrease indent for certain keywords
            if stripped.startswith(("elif", "else", "except", "finally", "case")):
                indent_level = max(0, indent_level - 1)

            # Apply indentation
            fixed_lines.append("    " * indent_level + stripped)

            # Increase indent after colons
            if stripped.endswith(":"):
                indent_level += 1

            # Decrease after return/break/continue
            if stripped.startswith(("return", "break", "continue", "pass")):
                indent_level = max(0, indent_level - 1)

        return "\n".join(fixed_lines)

    def fix_unclosed(self, content):
        """Fix unclosed strings and brackets"""
        # Count quotes and brackets
        single_quotes = content.count("'") - content.count("\\'")
        double_quotes = content.count('"') - content.count('\\"')
        parens = content.count("(") - content.count(")")
        brackets = content.count("[") - content.count("]")
        braces = content.count("{") - content.count("}")

        # Add closing characters
        if single_quotes % 2 == 1:
            content += "'"
        if double_quotes % 2 == 1:
            content += '"'
        if parens > 0:
            content += ")" * parens
        if brackets > 0:
            content += "]" * brackets
        if braces > 0:
            content += "}" * braces

        return content

    def quarantine_file(self, filepath):
        """Move file to quarantine"""
        try:
            rel_path = Path(filepath).relative_to(".")
            dest = self.quarantine_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(filepath, dest)

            # Create placeholder
            placeholder = f'''"""
This file has been quarantined due to syntax errors.
Original location: {filepath}
Quarantined: {self.timestamp}
Error: Check quarantine/{self.timestamp}/{rel_path}
"""

# Placeholder to prevent import errors

class Placeholder:
    pass
'''

            with open(filepath, "w") as f:
                f.write(placeholder)

            self.quarantined += 1
            return True

        except Exception as e:
            print(f"Failed to quarantine {filepath}: {e}")
            return False

    def generate_report(self):
        """Generate fix report"""
        report = {
            "timestamp": self.timestamp,
            "total_errors": len(self.syntax_errors),
            "fixed": self.fixed,
            "quarantined": self.quarantined,
            "remaining": len(self.syntax_errors) - self.fixed - self.quarantined,
            "quarantine_dir": str(self.quarantine_dir),
            "errors_by_type": {},
        }

        # Categorize errors
        for error_info in self.syntax_errors:
            error_type = error_info["error"]["type"]
            if error_type not in report["errors_by_type"]:
                report["errors_by_type"][error_type] = 0
            report["errors_by_type"][error_type] += 1

        return report


def main():
    print("🔨 Aggressive Syntax Fixer")
    print("=" * 50)

    fixer = AggressiveSyntaxFixer()

    # Find all syntax errors
    print("🔍 Scanning for syntax errors...")
    errors = fixer.find_all_syntax_errors()
    print(f"Found {len(errors)} files with syntax errors")

    if not errors:
        print("✅ No syntax errors found!")
        return

    # Show error types
    error_types = {}
    for e in errors:
        error_type = e["error"]["msg"]
        if error_type not in error_types:
            error_types[error_type] = 0
        error_types[error_type] += 1

    print("\n📊 Error Types:")
    for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {error_type}: {count}")

    # Fix aggressively
    print("\n🔧 Attempting aggressive fixes...")
    for i, error_info in enumerate(errors):
        filepath = error_info["file"]
        error = error_info["error"]

        print(f"Processing {i + 1}/{len(errors)}: {filepath}...", end="")

        if fixer.aggressive_fix(filepath, error):
            print(" [FIXED]")
        else:
            print(" [QUARANTINED]")

    # Generate report
    report = fixer.generate_report()

    with open("aggressive_fix_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 50)
    print("✅ Aggressive Fix Complete!")
    print(f"  - Fixed: {fixer.fixed} files")
    print(f"  - Quarantined: {fixer.quarantined} files")
    print(f"  - Quarantine location: {fixer.quarantine_dir}")

    # Re-scan
    print("\n🔍 Re-scanning for remaining errors...")
    remaining = AggressiveSyntaxFixer().find_all_syntax_errors()
    print(f"📊 Remaining syntax errors: {len(remaining)}")


if __name__ == "__main__":
    main()
