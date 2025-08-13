#!/usr/bin/env python3
"""
CLAUDE ARMY - Syntax Fixer Agent
Automatically fixes common syntax errors in Python files
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple


class SyntaxFixerAgent:
    def __init__(self):
        self.fixed_count = 0
        self.failed_count = 0
        self.results = []

    def find_syntax_errors(self) -> List[Tuple[Path, int, str]]:
        """Find all Python files with syntax errors"""
        errors = []
        for p in Path(".").rglob("*.py"):
            if any(
                skip in str(p)
                for skip in [
                    ".git",
                    "__pycache__",
                    "._cleanup_archive",
                    ".agent_results",
                ]
            ):
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                ast.parse(content)
            except SyntaxError as e:
                errors.append((p, e.lineno, e.msg))
            except Exception:
                pass
        return errors

    def fix_file(self, file_path: Path, line_no: int, error_msg: str) -> bool:
        """Attempt to fix a syntax error in a file"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")

            if line_no > len(lines):
                return False

            error_line = lines[line_no - 1] if line_no > 0 else ""

            # Common fixes
            fixed = False

            # Fix 1: EOL while scanning string literal
            if "EOL while scanning string literal" in error_msg:
                # Add missing quote
                if error_line.count('"') % 2 == 1:
                    lines[line_no - 1] = error_line + '"'
                    fixed = True
                elif error_line.count("'") % 2 == 1:
                    lines[line_no - 1] = error_line + "'"
                    fixed = True

            # Fix 2: Unmatched parenthesis
            elif "unmatched" in error_msg or "does not match" in error_msg:
                # Count parentheses
                open_count = (
                    error_line.count("(")
                    + error_line.count("[")
                    + error_line.count("{")
                )
                close_count = (
                    error_line.count(")")
                    + error_line.count("]")
                    + error_line.count("}")
                )

                if open_count > close_count:
                    lines[line_no - 1] = error_line + ")" * (open_count - close_count)
                    fixed = True
                elif close_count > open_count and line_no > 1:
                    # Remove extra closing
                    lines[line_no - 1] = re.sub(r"[)\]}]$", "", error_line)
                    fixed = True

            # Fix 3: Invalid syntax - missing colon
            elif "invalid syntax" in error_msg:
                # Check for missing colon in def/class/if/for/while
                if re.match(
                    r"^\s*(def|class|if|for|while|elif|else|try|except|finally|with)\s+.*[^:]$",
                    error_line,
                ):
                    lines[line_no - 1] = error_line + ":"
                    fixed = True
                # Check for malformed function definition
                elif "def " in error_line and "(" in error_line:
                    # Fix malformed method definitions like "def function(:"
                    lines[line_no - 1] = re.sub(
                        r"def\s+(\w+)\(:$", r"def \1(self):", error_line
                    )
                    if (
                        lines[line_no - 1] == error_line
                    ):  # If no change, try without self
                        lines[line_no - 1] = re.sub(
                            r"def\s+(\w+)\(:$", r"def \1():", error_line
                        )
                    if lines[line_no - 1] != error_line:
                        fixed = True

            # Fix 4: Unexpected indent
            elif "unexpected indent" in error_msg or "IndentationError" in error_msg:
                # Remove leading whitespace
                lines[line_no - 1] = error_line.lstrip()
                fixed = True

            if fixed:
                # Write the fixed content
                file_path.write_text("\n".join(lines), encoding="utf-8")

                # Verify the fix
                try:
                    ast.parse("\n".join(lines))
                    self.fixed_count += 1
                    self.results.append(f"✅ Fixed {file_path}:{line_no} - {error_msg}")
                    return True
                except:
                    # Revert if fix didn't work
                    file_path.write_text(content, encoding="utf-8")
                    self.failed_count += 1
                    self.results.append(
                        f"❌ Failed to fix {file_path}:{line_no} - {error_msg}"
                    )
                    return False
            else:
                self.failed_count += 1
                self.results.append(
                    f"⚠️ No fix available for {file_path}:{line_no} - {error_msg}"
                )
                return False

        except Exception as e:
            self.failed_count += 1
            self.results.append(f"❌ Error processing {file_path}: {str(e)}")
            return False

    def run(self, max_fixes: int = 20):
        """Run the syntax fixer agent"""
        print("🤖 SYNTAX FIXER AGENT ACTIVATED")
        print("=" * 50)

        # Find all syntax errors
        errors = self.find_syntax_errors()
        print(f"📊 Found {len(errors)} files with syntax errors")

        if not errors:
            print("✨ No syntax errors found!")
            return

        # Fix errors (limit to max_fixes for safety)
        fixes_attempted = 0
        for file_path, line_no, error_msg in errors[:max_fixes]:
            print(f"\n🔧 Attempting to fix {file_path}:{line_no}")
            print(f"   Error: {error_msg}")

            if self.fix_file(file_path, line_no, error_msg):
                print(f"   ✅ Fixed!")
            else:
                print(f"   ❌ Could not fix automatically")

            fixes_attempted += 1

        # Report results
        print("\n" + "=" * 50)
        print("📊 SYNTAX FIXER AGENT REPORT")
        print(f"   Fixes attempted: {fixes_attempted}")
        print(f"   ✅ Successfully fixed: {self.fixed_count}")
        print(f"   ❌ Failed to fix: {self.failed_count}")

        # Save results
        results_dir = Path(".agent_results/Syntax_Fixer")
        results_dir.mkdir(parents=True, exist_ok=True)

        with open(results_dir / "syntax_fixes.txt", "w") as f:
            f.write("\n".join(self.results))

        # Update status
        status_dir = Path(".agent_status")
        status_dir.mkdir(exist_ok=True)

        with open(status_dir / "Syntax_Fixer.status", "a") as f:
            f.write(f"COMPLETED: Fixed {self.fixed_count} errors\n")

        print(f"\n📄 Results saved to {results_dir / 'syntax_fixes.txt'}")


if __name__ == "__main__":
    agent = SyntaxFixerAgent()
    agent.run(max_fixes=20)  # Fix up to 20 files as a start
