#!/usr/bin/env python3
"""
Comprehensive Python Syntax Error Fixer
Automatically detects and fixes common Python syntax errors at scale
"""

import argparse
import ast
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SyntaxFix:
    """Represents a syntax fix operation"""

    file_path: str
    line_number: int
    original: str
    fixed: str
    fix_type: str
    confidence: float = 1.0


@dataclass
class SyntaxReport:
    """Report of all syntax fixes performed"""

    total_files_scanned: int = 0
    files_with_errors: int = 0
    fixes_applied: int = 0
    fixes_by_type: dict[str, int] = field(default_factory=dict)
    failed_files: list[str] = field(default_factory=list)
    fixes: list[SyntaxFix] = field(default_factory=list)


class PythonSyntaxFixer:
    """Main syntax fixer class"""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.report = SyntaxReport()

        # Common syntax patterns to fix
        self.fix_patterns = [
            # Curly quotes to straight quotes
            (r'[""]', '"', "curly_quotes"),
            (r"[" "]", "'", "curly_quotes"),
            # Fix escaped quotes in docstrings
            (r'"""', '"""', "docstring_quotes"),
            (r'"""', '"""', "docstring_quotes"),
            (r'"""""', '"""', "docstring_quotes"),
            (r'""""', '"""', "docstring_quotes"),
            (r'""', '"""', "docstring_quotes_incomplete"),
            # Fix malformed f-strings with comments
            (r'f"([^"]*)\s*#[^"]*"', r'f"\1"', "fstring_comment"),
            (r"f'([^']*)\s*#[^']*'", r"f'\1'", "fstring_comment"),
        ]

    def fix_file(self, file_path: Path) -> list[SyntaxFix]:
        """Fix syntax errors in a single file"""
        fixes = []

        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                original_content = content
                content.splitlines()

            # Track if file was modified
            modified = False

            # 1. Fix encoding issues and curly quotes
            content = self.fix_curly_quotes(content)
            if content != original_content:
                modified = True
                fixes.append(
                    SyntaxFix(
                        file_path=str(file_path),
                        line_number=0,
                        original="<file>",
                        fixed="<file>",
                        fix_type="curly_quotes",
                        confidence=1.0,
                    )
                )

            # 2. Fix invalid module names in imports
            content, import_fixes = self.fix_invalid_imports(content)
            if import_fixes:
                modified = True
                fixes.extend(import_fixes)

            # 3. Fix misplaced comments in code
            content, comment_fixes = self.fix_misplaced_comments(content, str(file_path))
            if comment_fixes:
                modified = True
                fixes.extend(comment_fixes)

            # 4. Fix docstring issues
            content, docstring_fixes = self.fix_docstrings(content, str(file_path))
            if docstring_fixes:
                modified = True
                fixes.extend(docstring_fixes)

            # 5. Validate Python syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                # Try additional fixes for remaining syntax errors
                content, syntax_fixes = self.fix_remaining_syntax_errors(content, e, str(file_path))
                if syntax_fixes:
                    modified = True
                    fixes.extend(syntax_fixes)

            # Write fixed content if not dry run
            if modified and not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Fixed {len(fixes)} issues in {file_path}")

            return fixes

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.report.failed_files.append(str(file_path))
            return []

    def fix_curly_quotes(self, content: str) -> str:
        """Replace curly quotes with straight quotes"""
        # Unicode curly quotes
        replacements = {
            "\u201c": '"',  # Left double quotation mark
            "\u201d": '"',  # Right double quotation mark
            "\u2018": "'",  # Left single quotation mark
            "\u2019": "'",  # Right single quotation mark
            '"': '"',  # Another right double quote variant
            """'""": "'",  # Another right single quote variant
        }

        for old, new in replacements.items():
            content = content.replace(old, new)

        return content

    def fix_invalid_imports(self, content: str) -> tuple[str, list[SyntaxFix]]:
        """Fix invalid module names in import statements"""
        fixes = []
        lines = content.splitlines()

        # Pattern for invalid imports with spaces
        import_pattern = re.compile(r"(from|import)\s+([A-Z][A-Z\s]+(?:Λ|λ)?[A-Za-z\s]*?)(\.|import|\s|$)")

        for i, line in enumerate(lines):
            match = import_pattern.search(line)
            if match:
                module_name = match.group(2).strip()
                # Check if module name contains spaces (invalid)
                if " " in module_name:
                    # Convert to valid module name
                    valid_name = module_name.replace(" ", "_").lower()
                    # Special handling for known patterns
                    if "LUKHAS AI" in module_name:
                        valid_name = "lukhas_ai_lambda_bot"
                    elif "Λ" in module_name or "λ" in module_name:
                        valid_name = valid_name.replace("λ", "lambda").replace("Λ", "lambda")

                    new_line = line.replace(module_name, valid_name)
                    lines[i] = new_line

                    fixes.append(
                        SyntaxFix(
                            file_path="",  # Will be filled by caller
                            line_number=i + 1,
                            original=line,
                            fixed=new_line,
                            fix_type="invalid_import",
                            confidence=0.9,
                        )
                    )

        return "\n".join(lines), fixes

    def fix_misplaced_comments(self, content: str, file_path: str) -> tuple[str, list[SyntaxFix]]:
        """Fix comments that break syntax (e.g., inside function calls)"""
        fixes = []
        lines = content.splitlines()

        # Pattern for comments inside function calls or f-strings
        patterns = [
            # hashlib.sha256(  #  comment text
            (r"(\w+\.\w+\([^)]*)\s*#([^)]*)\)", r"\1# \2"),
            # f-string with comment inside
            (r'(f["\'][^"\']*)\s*#([^"\']*["\'])', r'\1"'),
        ]

        for i, line in enumerate(lines):
            for pattern, replacement in patterns:
                if re.search(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        lines[i] = new_line
                        fixes.append(
                            SyntaxFix(
                                file_path=file_path,
                                line_number=i + 1,
                                original=line,
                                fixed=new_line,
                                fix_type="misplaced_comment",
                                confidence=0.85,
                            )
                        )

        return "\n".join(lines), fixes

    def fix_docstrings(self, content: str, file_path: str) -> tuple[str, list[SyntaxFix]]:
        """Fix malformed docstrings"""
        fixes = []
        lines = content.splitlines()

        in_docstring = False

        for i, line in enumerate(lines):
            # Check for docstring start/end
            if '"""' in line or "'''" in line:
                quotes = '"""' if '"""' in line else "'''"
                count = line.count(quotes)

                # Handle malformed docstrings
                if count > 2:
                    # Too many quotes
                    if count == 6:  # """ -> """
                        new_line = line.replace(quotes * 2, quotes)
                    else:
                        # Odd number or other issues
                        new_line = re.sub(f"{quotes}+", quotes, line)

                    if new_line != line:
                        lines[i] = new_line
                        fixes.append(
                            SyntaxFix(
                                file_path=file_path,
                                line_number=i + 1,
                                original=line,
                                fixed=new_line,
                                fix_type="docstring_quotes",
                                confidence=0.95,
                            )
                        )

                # Track docstring state
                if not in_docstring and count % 2 == 1:
                    in_docstring = True
                elif in_docstring and count >= 1:
                    in_docstring = False

            # Fix standalone double quotes that should be docstrings
            elif line.strip() == '""' and not in_docstring:
                # This should probably be a docstring
                lines[i] = line.replace('""', '"""')
                fixes.append(
                    SyntaxFix(
                        file_path=file_path,
                        line_number=i + 1,
                        original=line,
                        fixed=lines[i],
                        fix_type="incomplete_docstring",
                        confidence=0.7,
                    )
                )

        return "\n".join(lines), fixes

    def fix_remaining_syntax_errors(
        self, content: str, syntax_error: SyntaxError, file_path: str
    ) -> tuple[str, list[SyntaxFix]]:
        """Attempt to fix remaining syntax errors based on the error message"""
        fixes = []
        lines = content.splitlines()

        if syntax_error.lineno and syntax_error.lineno <= len(lines):
            error_line = lines[syntax_error.lineno - 1]
            fixed_line = error_line

            # Common patterns based on error messages
            if "EOL while scanning string literal" in str(syntax_error):
                # Missing closing quote
                if error_line.count('"') % 2 == 1:
                    fixed_line = error_line + '"'
                elif error_line.count("'") % 2 == 1:
                    fixed_line = error_line + "'"

            elif "invalid syntax" in str(syntax_error):
                # Check for common issues
                # Extra closing parenthesis at end of string literals
                if re.search(r'["\']["\s]*\)\'?$', error_line):
                    fixed_line = re.sub(r'(["\'])(["\s]*\))\'?$', r"\1)", error_line)

            if fixed_line != error_line:
                lines[syntax_error.lineno - 1] = fixed_line
                fixes.append(
                    SyntaxFix(
                        file_path=file_path,
                        line_number=syntax_error.lineno,
                        original=error_line,
                        fixed=fixed_line,
                        fix_type="syntax_error_recovery",
                        confidence=0.6,
                    )
                )

        return "\n".join(lines), fixes

    def scan_directory(self, directory: Path, pattern: str = "**/*.py") -> SyntaxReport:
        """Scan directory for Python files and fix syntax errors"""
        python_files = list(directory.glob(pattern))
        self.report.total_files_scanned = len(python_files)

        for file_path in python_files:
            # Skip certain directories
            if any(skip in str(file_path) for skip in ["__pycache__", ".git", "venv", ".venv"]):
                continue

            if self.verbose:
                logger.info(f"Scanning {file_path}")

            fixes = self.fix_file(file_path)
            if fixes:
                self.report.files_with_errors += 1
                self.report.fixes_applied += len(fixes)
                self.report.fixes.extend(fixes)

                # Track fixes by type
                for fix in fixes:
                    self.report.fixes_by_type[fix.fix_type] = self.report.fixes_by_type.get(fix.fix_type, 0) + 1

        return self.report

    def generate_report(self) -> str:
        """Generate a detailed report of all fixes"""
        report_lines = [
            "=" * 60,
            "Python Syntax Error Fix Report",
            "=" * 60,
            f"Total files scanned: {self.report.total_files_scanned}",
            f"Files with errors: {self.report.files_with_errors}",
            f"Total fixes applied: {self.report.fixes_applied}",
            "",
            "Fixes by type:",
        ]

        for fix_type, count in sorted(self.report.fixes_by_type.items()):
            report_lines.append(f"  {fix_type}: {count}")

        if self.report.failed_files:
            report_lines.extend(
                [
                    "",
                    "Failed files:",
                ]
            )
            for file in self.report.failed_files:
                report_lines.append(f"  - {file}")

        if self.verbose and self.report.fixes:
            report_lines.extend(
                [
                    "",
                    "Detailed fixes:",
                    "-" * 40,
                ]
            )
            for fix in self.report.fixes[:20]:  # Show first 20 fixes
                report_lines.extend(
                    [
                        f"File: {fix.file_path}:{fix.line_number}",
                        f"Type: {fix.fix_type} (confidence: {fix.confidence:.0%})",
                        f"Original: {fix.original[:80]}...",
                        f"Fixed: {fix.fixed[:80]}...",
                        "-" * 40,
                    ]
                )

        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="Fix Python syntax errors at scale")
    parser.add_argument("path", help="Path to file or directory to fix")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--pattern",
        default="**/*.py",
        help="Glob pattern for Python files (default: **/*.py)",
    )
    parser.add_argument("--report", help="Save report to file")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")

    args = parser.parse_args()

    # Create fixer instance
    fixer = PythonSyntaxFixer(dry_run=args.dry_run, verbose=args.verbose)

    # Process path
    path = Path(args.path)
    if path.is_file():
        fixes = fixer.fix_file(path)
        fixer.report.total_files_scanned = 1
        if fixes:
            fixer.report.files_with_errors = 1
            fixer.report.fixes_applied = len(fixes)
            fixer.report.fixes = fixes
    elif path.is_dir():
        fixer.scan_directory(path, args.pattern)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

    # Generate and display report
    if args.json:
        # Convert to JSON-serializable format
        report_dict = {
            "total_files_scanned": fixer.report.total_files_scanned,
            "files_with_errors": fixer.report.files_with_errors,
            "fixes_applied": fixer.report.fixes_applied,
            "fixes_by_type": fixer.report.fixes_by_type,
            "failed_files": fixer.report.failed_files,
            "fixes": [
                {
                    "file": fix.file_path,
                    "line": fix.line_number,
                    "type": fix.fix_type,
                    "confidence": fix.confidence,
                }
                for fix in fixer.report.fixes
            ],
        }
        print(json.dumps(report_dict, indent=2))
    else:
        print(fixer.generate_report())

    # Save report to file if requested
    if args.report:
        with open(args.report, "w") as f:
            if args.json:
                json.dump(report_dict, f, indent=2)
            else:
                f.write(fixer.generate_report())
        print(f"\nReport saved to {args.report}")

    # Exit with error code if fixes were needed and not in dry-run
    if fixer.report.files_with_errors > 0 and args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
