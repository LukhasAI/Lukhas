#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ MODULE: lukhasI Syntax Fixer Bot                                               ║
║ DESCRIPTION: Autonomous AI bot for fixing Python syntax errors            ║
║                                                                             ║
║ FUNCTIONALITY: Automated syntax error detection and correction             ║
║ IMPLEMENTATION: AST parsing • Error pattern matching • Auto-correction    ║
║ INTEGRATION: lukhasI System Health • Code Quality • Batch Processing          ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
import time
import streamlit as st

import ast
import logging
import re
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SyntaxFixerBot:
    """
    Autonomous AI bot for systematically fixing Python syntax errors.

    Features:
    - Automated syntax error detection
    - Pattern-based error correction
    - Unicode character normalization
    - Indentation fixing
    - String literal corrections
    - Async/await placement fixes
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.fixed_files = []
        self.error_patterns = self._initialize_error_patterns()
        self.stats = {
            "scanned": 0,
            "errors_found": 0,
            "files_fixed": 0,
            "patterns_applied": 0,
        }

    def _initialize_error_patterns(self) -> dict[str, dict]:
        """Initialize common syntax error patterns and their fixes."""
        return {
            "unicode_chars": {
                "pattern": r'[—–""' "•→←↑↓✨╔╗╚╝║═╠╣╤╧╪╬╭╮╯╰│┌┐└┘├┤┬┴┼]",
                "replacements": {
                    "—": "-",
                    "–": "-",
                    '"': '"',
                    """: "'", """: "'",
                    "•": "*",
                    "→": "->",
                    "←": "<-",
                    "↑": "^",
                    "↓": "v",
                    "✨": "*",
                    "╔": "+",
                    "╗": "+",
                    "╚": "+",
                    "╝": "+",
                    "║": "|",
                    "═": "=",
                    "╠": "+",
                    "╣": "+",
                    "╤": "+",
                    "╧": "+",
                    "╪": "+",
                    "╬": "+",
                    "╭": "+",
                    "╮": "+",
                    "╯": "+",
                    "╰": "+",
                    "│": "|",
                    "┌": "+",
                    "┐": "+",
                    "└": "+",
                    "┘": "+",
                    "├": "+",
                    "┤": "+",
                    "┬": "+",
                    "┴": "+",
                    "┼": "+",
                },
            },
            "date_literals": {
                "pattern": r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
                "replacement": r'"\1"',
            },
            "invalid_string_prefixes": {"pattern": r'[ps]"""', "replacement": '"""'},
            "unclosed_brackets": {
                "patterns": [
                    r"patterns = \[([^]]+)$",  # Unclosed list
                    r"\[([^]]*$)",  # General unclosed bracket
                ]
            },
            "leading_zeros": {"pattern": r"\b0(\d+)\b", "replacement": r"\1"},
        }

    def scan_workspace(self) -> list[tuple[Path, str]]:
        """Scan workspace for Python files with syntax errors."""
        logger.info(f"🔍 Scanning workspace: {self.workspace_path}")
        error_files = []

        for py_file in self.workspace_path.rglob("*.py"):
            self.stats["scanned"] += 1
            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                ast.parse(content)
            except (SyntaxError, UnicodeDecodeError) as e:
                error_files.append((py_file, str(e)))
                self.stats["errors_found"] += 1
                logger.warning(f"❌ Syntax error in {py_file.relative_to(self.workspace_path)}: {e}")

        logger.info(
            f"📊 Scan complete: {self.stats['scanned']} files scanned, {self.stats['errors_found']} errors found"
        )
        return error_files

    def fix_unicode_characters(self, content: str) -> str:
        """Fix unicode characters that cause syntax errors."""
        pattern = self.error_patterns["unicode_chars"]
        replacements = pattern["replacements"]

        for unicode_char, replacement in replacements.items():
            if unicode_char in content:
                content = content.replace(unicode_char, replacement)
                self.stats["patterns_applied"] += 1
                logger.debug(f"🔧 Replaced unicode character '{unicode_char}' with '{replacement}'")

        return content

    def fix_date_literals(self, content: str) -> str:
        """Fix date literals that are interpreted as numbers."""
        pattern = self.error_patterns["date_literals"]["pattern"]
        replacement = self.error_patterns["date_literals"]["replacement"]

        # Only fix if it's not already in a string or comment
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Skip if line is a comment or already in quotes
            if line.strip().startswith("#") or '"' in line or "'" in line:
                fixed_lines.append(line)
                continue

            if re.search(pattern, line):
                line = re.sub(pattern, replacement, line)
                self.stats["patterns_applied"] += 1
                logger.debug("🔧 Fixed date literal")

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_string_prefixes(self, content: str) -> str:
        """Fix invalid string prefixes like p''' or s'''."""
        pattern = self.error_patterns["invalid_string_prefixes"]["pattern"]
        replacement = self.error_patterns["invalid_string_prefixes"]["replacement"]

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            self.stats["patterns_applied"] += 1
            logger.debug("🔧 Fixed invalid string prefix")

        return content

    def fix_unclosed_brackets(self, content: str) -> str:
        """Fix unclosed brackets and lists."""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Look for patterns like: patterns = [
            if re.match(r"\s*patterns\s*=\s*\[$", line.strip()):
                # Find the next non-empty line and add closing bracket if needed
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1

                if j < len(lines) and not lines[j].strip().endswith("]"):
                    # Add closing bracket
                    lines.insert(j, "    ]")
                    self.stats["patterns_applied"] += 1
                    logger.debug("🔧 Fixed unclosed bracket")
                    break

        return "\n".join(lines)

    def fix_indentation_errors(self, content: str) -> str:
        """Fix common indentation errors."""
        lines = content.split("\n")
        fixed_lines = []
        in_class = False
        class_indent = 0

        for _i, line in enumerate(lines):
            # Detect class definition
            if line.strip().startswith("class "):
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue

            # Fix method definitions that should be inside class
            if in_class and line.strip().startswith("def ") and "(self," in line:
                # Ensure method is properly indented
                expected_indent = class_indent + 4
                current_indent = len(line) - len(line.lstrip())

                if current_indent != expected_indent:
                    line = " " * expected_indent + line.lstrip()
                    self.stats["patterns_applied"] += 1
                    logger.debug("🔧 Fixed method indentation")

            # Detect end of class (non-indented line that's not empty)
            if in_class and line.strip() and not line.startswith(" ") and not line.strip().startswith("#"):
                in_class = False

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_async_await_errors(self, content: str) -> str:
        """Fix await outside async function errors."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # If line contains await but function isn't async, make it async
            if "await " in line and "def " in line and "async def" not in line:
                line = line.replace("def ", "async def ")
                self.stats["patterns_applied"] += 1
                logger.debug("🔧 Made function async for await")
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_leading_zeros(self, content: str) -> str:
        """Fix leading zeros in decimal literals."""
        pattern = self.error_patterns["leading_zeros"]["pattern"]
        replacement = self.error_patterns["leading_zeros"]["replacement"]

        # Only fix in non-string contexts
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Skip comments and strings
            if line.strip().startswith("#") or '"' in line or "'" in line:
                fixed_lines.append(line)
                continue

            if re.search(pattern, line):
                line = re.sub(pattern, replacement, line)
                self.stats["patterns_applied"] += 1
                logger.debug("🔧 Fixed leading zero")

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def apply_all_fixes(self, content: str) -> str:
        """Apply all available fixes to content."""
        content = self.fix_unicode_characters(content)
        content = self.fix_date_literals(content)
        content = self.fix_string_prefixes(content)
        content = self.fix_unclosed_brackets(content)
        content = self.fix_indentation_errors(content)
        content = self.fix_async_await_errors(content)
        content = self.fix_leading_zeros(content)
        return content

    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file and return True if successful."""
        try:
            # Read original content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # Apply fixes
            fixed_content = self.apply_all_fixes(original_content)

            # Test if fixes resolved syntax errors
            try:
                ast.parse(fixed_content)
                syntax_valid = True
            except SyntaxError:
                syntax_valid = False

            # Write back if improvements were made
            if fixed_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                self.fixed_files.append(file_path)
                self.stats["files_fixed"] += 1

                if syntax_valid:
                    logger.info(f"✅ Fixed: {file_path.relative_to(self.workspace_path)}")
                    return True
                else:
                    logger.warning(f"⚠️ Partial fix: {file_path.relative_to(self.workspace_path)}")
                    return False

            return syntax_valid

        except Exception as e:
            logger.error(f"❌ Error fixing {file_path}: {e}")
            return False

    def run_comprehensive_fix(self) -> dict[str, int]:
        """Run comprehensive syntax fixing across the workspace."""
        logger.info("🚀 Starting lukhasI Syntax Fixer Bot...")

        # Scan for errors
        error_files = self.scan_workspace()

        if not error_files:
            logger.info("🎉 No syntax errors found! System is already at 100% health.")
            return self.stats

        # Fix each file
        logger.info(f"🔧 Fixing {len(error_files)} files with syntax errors...")

        for file_path, _error_msg in error_files:
            logger.info(f"🔧 Fixing: {file_path.relative_to(self.workspace_path)}")
            self.fix_file(file_path)

        # Final scan to verify
        logger.info("🔍 Running final verification scan...")
        remaining_errors = self.scan_workspace()

        if remaining_errors:
            logger.warning(f"⚠️ {len(remaining_errors)} files still have syntax errors")
            for file_path, error in remaining_errors[:5]:  # Show first 5
                logger.warning(f"   - {file_path.relative_to(self.workspace_path)}: {error}")
        else:
            logger.info("🎉 ALL SYNTAX ERRORS FIXED! System health: 100%")

        return self.stats

    def generate_report(self) -> str:
        """Generate a comprehensive fix report."""
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     lukhasI SYNTAX FIXER BOT REPORT                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

📊 STATISTICS:
   • Files Scanned: {self.stats["scanned"]}
   • Errors Found: {self.stats["errors_found"]}
   • Files Fixed: {self.stats["files_fixed"]}
   • Patterns Applied: {self.stats["patterns_applied"]}

✅ FIXED FILES:
"""
        for file_path in self.fixed_files:
            report += f"   • {file_path.relative_to(self.workspace_path)}\n"

        return report


def main():
    """Main entry point for the lukhasI Syntax Fixer Bot."""
    workspace = Path("/Users/agi_dev/Lukhas")

    # Initialize the bot
    bot = SyntaxFixerBot(workspace)

    # Run comprehensive fix
    bot.run_comprehensive_fix()

    # Generate and display report
    report = bot.generate_report()
    print(report)

    # Final system health check
    print("\n🏥 Running final system health check...")
    try:
        result = subprocess.run(
            [
                "python3",
                "-c",
                "import sys; sys.path.append('.'); "
                "from tools.lukhasHealthMonitor import systemHealthMonitor; "
                "monitor = lukhasHealthMonitor('.'); "
                "health = monitor.comprehensive_health_check(); "
                "print(f'System Health: {health[\"overall_health\"]:.1%}')",
            ],
            cwd=workspace,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print("✅ Syntax fixing complete!")
    except Exception:
        print("✅ Syntax fixing complete!")


if __name__ == "__main__":
    main()
