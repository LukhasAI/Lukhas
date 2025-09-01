#!/usr/bin/env python3
"""
Syntax Doctor - Automatically fixes common Python syntax errors
"""

import ast
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


class SyntaxDoctor:
    """Heals syntax errors in Python files"""

    def __init__(self):
        self.fixed_count = 0
        self.failed_count = 0
        self.backup_dir = Path("healing/syntax_backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Common syntax patterns to fix
        self.fix_patterns = [
            # Fix unclosed brackets/parentheses
            (r"(\w+)\s*\(\s*$", r"\1()"),
            (r"(\w+)\s*\[\s*$", r"\1[]"),
            (r"(\w+)\s*\{\s*$", r"\1{}"),
            # Fix missing colons
            (
                r"^(\s*)(if|elif|else|while|for|try|except|finally|with|def|class)\s+(.+[^:])\s*$",
                r"\1\2 \3:",
            ),
            # Fix invalid f-string syntax
            (r'f"([^"]*)\{([^}]*)\$([^}]*)\}"', r'f"\1{\2}{\3}"'),
            # Fix trailing commas in function definitions
            (r"def\s+(\w+)\s*\([^)]*,\s*\)\s*:", r"def \1():"),
            # Fix async syntax
            (r"async\s+def\s+async\s+", r"async def "),
            # Fix duplicate keywords
            (r"\bimport\s+import\b", r"import"),
            (r"\bfrom\s+from\b", r"from"),
            (r"\breturn\s+return\b", r"return"),
            # Fix common typos
            (r"\bpritn\b", r"print"),
            (r"\bslef\b", r"self"),
            (r"\btreu\b", r"True"),
            (r"\bflase\b", r"False"),
            (r"\bnoen\b", r"None"),
        ]

    def find_syntax_errors(self):
        """Find all Python files with syntax errors"""
        errors = []

        for root, _dirs, files in os.walk("."):
            # Skip virtual environments and git
            if any(skip in root for skip in [".venv", ".git", "__pycache__", "._cleanup_archive"]):
                continue

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    if self.has_syntax_error(filepath):
                        errors.append(filepath)

        return errors

    def has_syntax_error(self, filepath):
        """Check if file has syntax errors"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Try to parse with AST
            ast.parse(content)
            return False
        except SyntaxError:
            return True
        except Exception:
            # Other errors (encoding, etc) - skip
            return False

    def get_syntax_error_details(self, filepath):
        """Get detailed syntax error information"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            ast.parse(content)
            return None
        except SyntaxError as e:
            return {"msg": e.msg, "line": e.lineno, "offset": e.offset, "text": e.text}
        except Exception as e:
            return {"msg": str(e), "line": 0, "offset": 0, "text": ""}

    def fix_file(self, filepath):
        """Attempt to fix syntax errors in a file"""
        # Create backup
        backup_path = self.backup_dir / (Path(filepath).name + f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup")
        shutil.copy2(filepath, backup_path)

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Get error details
            error = self.get_syntax_error_details(filepath)
            if not error:
                return True  # No error

            # Apply regex fixes
            for pattern, replacement in self.fix_patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            # Specific fixes based on error type
            if error["msg"]:
                content = self.apply_specific_fixes(content, error)

            # Try to fix unclosed strings
            content = self.fix_unclosed_strings(content)

            # Fix indentation issues
            content = self.fix_indentation(content)

            # Write fixed content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Verify fix
            if not self.has_syntax_error(filepath):
                self.fixed_count += 1
                return True
            else:
                # Restore backup if still broken
                shutil.copy2(backup_path, filepath)
                self.failed_count += 1
                return False

        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
            # Restore backup
            shutil.copy2(backup_path, filepath)
            self.failed_count += 1
            return False

    def apply_specific_fixes(self, content, error):
        """Apply fixes based on specific error messages"""
        lines = content.split("\n")

        if "invalid syntax" in error["msg"]:
            # Common invalid syntax fixes
            if error["line"] and error["line"] <= len(lines):
                line_idx = error["line"] - 1
                line = lines[line_idx]

                # Fix missing colons
                if any(
                    keyword in line
                    for keyword in [
                        "if",
                        "elif",
                        "else",
                        "while",
                        "for",
                        "def",
                        "class",
                    ]
                ) and not line.rstrip().endswith(":"):
                    lines[line_idx] = line.rstrip() + ":"

                # Fix unclosed parentheses
                if line.count("(") > line.count(")"):
                    lines[line_idx] = line + ")" * (line.count("(") - line.count(")"))
                elif line.count("[") > line.count("]"):
                    lines[line_idx] = line + "]" * (line.count("[") - line.count("]"))
                elif line.count("{") > line.count("}"):
                    lines[line_idx] = line + "}" * (line.count("{") - line.count("}"))

        elif "unexpected EOF" in error["msg"]:
            # Add missing closing brackets at end
            open_parens = content.count("(") - content.count(")")
            open_brackets = content.count("[") - content.count("]")
            open_braces = content.count("{") - content.count("}")

            closing = ")" * open_parens + "]" * open_brackets + "}" * open_braces
            if closing:
                lines.append(closing)

        elif "unindent does not match" in error["msg"]:
            # Fix indentation on error line
            if error["line"] and error["line"] <= len(lines):
                line_idx = error["line"] - 1
                # Find previous line's indentation
                for i in range(line_idx - 1, -1, -1):
                    if lines[i].strip():
                        prev_indent = len(lines[i]) - len(lines[i].lstrip())
                        lines[line_idx] = " " * prev_indent + lines[line_idx].lstrip()
                        break

        return "\n".join(lines)

    def fix_unclosed_strings(self, content):
        """Fix unclosed string literals"""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Count quotes
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')

            # Fix odd number of quotes
            if single_quotes % 2 == 1:
                lines[i] = line + "'"
            if double_quotes % 2 == 1:
                lines[i] = line + '"'

        return "\n".join(lines)

    def fix_indentation(self, content):
        """Fix common indentation issues"""
        lines = content.split("\n")
        fixed_lines = []
        current_indent = 0

        for line in lines:
            stripped = line.strip()

            if not stripped:
                fixed_lines.append("")
                continue

            # Decrease indent for certain keywords
            if stripped.startswith(("elif", "else", "except", "finally")):
                current_indent = max(0, current_indent - 4)

            # Apply current indentation
            if stripped.startswith(("return", "break", "continue", "pass")):
                fixed_lines.append(" " * current_indent + stripped)
            else:
                # Preserve existing indentation if valid
                orig_indent = len(line) - len(line.lstrip())
                if orig_indent % 4 == 0:  # Valid indentation
                    fixed_lines.append(line)
                    current_indent = orig_indent
                else:
                    fixed_lines.append(" " * current_indent + stripped)

            # Increase indent after certain keywords
            if stripped.endswith(":"):
                current_indent += 4

        return "\n".join(fixed_lines)

    def generate_report(self, errors_found, errors_fixed):
        """Generate healing report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(errors_found),
            "fixed": self.fixed_count,
            "failed": self.failed_count,
            "success_rate": ((self.fixed_count / len(errors_found) * 100) if errors_found else 0),
            "files": {
                "fixed": [f for f in errors_fixed if errors_fixed[f]],
                "failed": [f for f in errors_fixed if not errors_fixed[f]],
            },
        }

        return report


def main():
    """Run the syntax doctor"""
    print("[Syntax Doctor] Starting...")
    print("=" * 50)

    doctor = SyntaxDoctor()

    # Find all syntax errors
    print("[Scanning] Looking for syntax errors...")
    errors = doctor.find_syntax_errors()

    if not errors:
        print("[OK] No syntax errors found!")
        return

    print(f"Found {len(errors)} files with syntax errors")

    # Show first few errors
    print("\n[Sample Errors]")
    for filepath in errors[:5]:
        error = doctor.get_syntax_error_details(filepath)
        if error:
            print(f"\n{filepath}:")
            print(f"  Line {error['line']}: {error['msg']}")
            if error["text"]:
                print(f"  >>> {error['text'].strip()}")

    # Fix errors
    print(f"\n[Fixing] Attempting to fix {len(errors)} files...")
    errors_fixed = {}

    for i, filepath in enumerate(errors):
        print(f"Fixing {i + 1}/{len(errors)}: {filepath}...", end="")
        success = doctor.fix_file(filepath)
        errors_fixed[filepath] = success
        print(" [OK]" if success else " [FAILED]")

    # Generate report
    report = doctor.generate_report(errors, errors_fixed)

    # Save report
    import json

    report_path = Path("healing/syntax_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Summary
    print("\n" + "=" * 50)
    print("[SYNTAX HEALING COMPLETE]")
    print("=" * 50)
    print(f"[Fixed] {doctor.fixed_count}/{len(errors)} files ({report['success_rate']:.1f}%)")
    print(f"[Failed] {doctor.failed_count} files")

    if doctor.failed_count > 0:
        print("\n[Warning] Some files could not be automatically fixed.")
        print("These may require manual intervention.")
        print(f"Check the report at: {report_path}")

    # Rescan to confirm
    print("\n[Rescanning] Verifying fixes...")
    remaining = doctor.find_syntax_errors()
    print(f"[Status] Remaining syntax errors: {len(remaining)}")

    if remaining:
        print("\n[Files Still With Errors]")
        for f in remaining[:10]:
            print(f"  - {f}")
        if len(remaining) > 10:
            print(f"  ... and {len(remaining) - 10} more")


if __name__ == "__main__":
    main()
