#!/usr/bin/env python3
"""
Pre-commit F-String Syntax Validator
====================================
AST-based validation to prevent f-string syntax errors from entering the codebase.
Integrates with T4 autofix pipeline and can auto-fix detected issues.

Usage:
- As pre-commit hook: validates staged files
- As standalone: validates specified files
- Auto-fix mode: applies fixes automatically

Features:
- AST parsing for comprehensive syntax validation
- Pattern-based f-string error detection
- Integration with EnhancedFStringFixer
- Detailed error reporting with line numbers
"""

import ast
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

# Import our enhanced fixer
sys.path.insert(0, str(ROOT / "tools" / "automation"))
try:
    from enhanced_fstring_fixer import F_STRING_PATTERNS, EnhancedFStringFixer
except ImportError:
    logger.warning("Enhanced f-string fixer not available")
    EnhancedFStringFixer = None
    F_STRING_PATTERNS = []


class FStringValidationError(Exception):
    """Exception for f-string validation failures"""

    def __init__(self, message: str, file_path: str, line_number: Optional[int] = None):
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(f"{file_path}:{line_number or '?'}: {message}")


class PrecommitFStringValidator:
    """Pre-commit f-string syntax validator"""

    def __init__(self, auto_fix: bool = False):
        self.auto_fix = auto_fix
        self.validation_errors = []
        self.fixes_applied = []

    def get_staged_python_files(self) -> list[Path]:
        """Get list of staged Python files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            if result.returncode != 0:
                logger.warning("Could not get staged files, checking all Python files")
                return list(ROOT.rglob("*.py"))

            staged_files = []
            for line in result.stdout.strip().split("\n"):
                if line and line.endswith(".py"):
                    file_path = ROOT / line
                    if file_path.exists():
                        staged_files.append(file_path)

            return staged_files

        except Exception as e:
            logger.error(f"Error getting staged files: {e}")
            return []

    def validate_ast_syntax(self, file_path: Path) -> list[FStringValidationError]:
        """Validate Python syntax using AST parsing"""
        errors = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            # Check if it's an f-string related error
            if any(
                keyword in str(e).lower()
                for keyword in ["f-string", "single '}'", "closing parenthesis", "opening parenthesis"]
            ):
                errors.append(FStringValidationError(f"F-string syntax error: {e.msg}", str(file_path), e.lineno))
            else:
                errors.append(FStringValidationError(f"Syntax error: {e.msg}", str(file_path), e.lineno))
        except Exception as e:
            errors.append(FStringValidationError(f"AST parsing failed: {e}", str(file_path)))

        return errors

    def validate_fstring_patterns(self, file_path: Path) -> list[FStringValidationError]:
        """Validate known problematic f-string patterns"""
        errors = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.split("\n")

            # Check for common f-string error patterns
            for i, line in enumerate(lines, 1):
                # Pattern 1: Extra closing brace after format spec
                if re.search(r'f["\'].*\{[^{}]*\}:[.\d]*[fFeEgGdiouxXbcrsa]\}', line):
                    errors.append(
                        FStringValidationError("Extra closing brace after format specification", str(file_path), i)
                    )

                # Pattern 2: Method call syntax error
                if re.search(r'f["\'].*\{[^{}]*\(\)\}\.\w+(?:\[.*?\])?\}', line):
                    errors.append(FStringValidationError("Method call syntax error in f-string", str(file_path), i))

                # Pattern 3: Bracket/brace mismatch
                if re.search(r'f["\'].*\{[^{}]*\}(?:\[[^\]]*\])?', line):
                    # Check for mismatched brackets
                    open_brackets = line.count("[") + line.count("{")
                    close_brackets = line.count("]") + line.count("}")
                    if open_brackets != close_brackets:
                        # More specific check for f-string context
                        f_string_match = re.search(r'f["\'][^"\']*["\']', line)
                        if f_string_match and ("}]" in f_string_match.group() or "}[" in f_string_match.group()):
                            errors.append(
                                FStringValidationError("Bracket/brace mismatch in f-string", str(file_path), i)
                            )

        except Exception as e:
            errors.append(FStringValidationError(f"Pattern validation failed: {e}", str(file_path)))

        return errors

    def validate_file(self, file_path: Path) -> list[FStringValidationError]:
        """Validate a single file for f-string issues"""
        errors = []

        # AST validation (catches actual syntax errors)
        errors.extend(self.validate_ast_syntax(file_path))

        # Pattern validation (catches potential issues)
        if not errors:  # Only check patterns if AST parsing succeeded
            errors.extend(self.validate_fstring_patterns(file_path))

        return errors

    def apply_auto_fixes(self, file_path: Path) -> bool:
        """Apply automatic fixes to file"""
        if not EnhancedFStringFixer:
            logger.warning("Auto-fix requested but fixer not available")
            return False

        try:
            fixer = EnhancedFStringFixer(validate_syntax=True)
            success = fixer.fix_file(file_path)

            if success:
                self.fixes_applied.append(str(file_path))
                logger.info(f"Auto-fixed f-string errors in: {file_path}")

            return success

        except Exception as e:
            logger.error(f"Auto-fix failed for {file_path}: {e}")
            return False

    def validate_files(self, files: list[Path]) -> bool:
        """Validate multiple files, return True if all pass"""
        all_valid = True

        for file_path in files:
            logger.debug(f"Validating: {file_path}")

            errors = self.validate_file(file_path)

            if errors:
                all_valid = False
                self.validation_errors.extend(errors)

                if self.auto_fix:
                    logger.info(f"Attempting auto-fix for: {file_path}")
                    if self.apply_auto_fixes(file_path):
                        # Re-validate after fixing
                        new_errors = self.validate_file(file_path)
                        if not new_errors:
                            logger.info(f"✅ Auto-fix successful for: {file_path}")
                            # Remove errors for this file from validation_errors
                            self.validation_errors = [
                                e for e in self.validation_errors if e.file_path != str(file_path)
                            ]
                            all_valid = True  # This file is now valid
                        else:
                            logger.warning(f"Auto-fix partially successful for: {file_path}")
                    else:
                        logger.warning(f"Auto-fix failed for: {file_path}")

        return all_valid and len(self.validation_errors) == 0

    def print_validation_report(self):
        """Print detailed validation report"""
        if not self.validation_errors and not self.fixes_applied:
            print("✅ All f-string validations passed")
            return

        if self.fixes_applied:
            print(f"\n🔧 AUTO-FIXES APPLIED ({len(self.fixes_applied)} files):")
            for file_path in self.fixes_applied:
                print(f"  ✅ {file_path}")

        if self.validation_errors:
            print(f"\n❌ F-STRING VALIDATION ERRORS ({len(self.validation_errors)}):")

            # Group errors by file
            by_file = {}
            for error in self.validation_errors:
                if error.file_path not in by_file:
                    by_file[error.file_path] = []
                by_file[error.file_path].append(error)

            for file_path, errors in by_file.items():
                print(f"\n  📁 {file_path}")
                for error in errors:
                    line_info = f":{error.line_number}" if error.line_number else ""
                    print(f"    ❌ Line{line_info}: {error.message}")

        print("\n📊 SUMMARY:")
        print(f"  - Files with fixes: {len(self.fixes_applied)}")
        print(f"  - Remaining errors: {len(self.validation_errors)}")
        print(f"  - Validation {'✅ PASSED' if not self.validation_errors else '❌ FAILED'}")


def main():
    """CLI interface for pre-commit validator"""
    import argparse

    parser = argparse.ArgumentParser(description="Pre-commit f-string validator")
    parser.add_argument("files", nargs="*", help="Files to validate (default: staged files)")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix detected issues")
    parser.add_argument("--all-files", action="store_true", help="Validate all Python files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    validator = PrecommitFStringValidator(auto_fix=args.auto_fix)

    # Determine files to validate
    if args.files:
        files = [Path(f) for f in args.files]
    elif args.all_files:
        files = list(ROOT.rglob("*.py"))
    else:
        files = validator.get_staged_python_files()

    if not files:
        print("No Python files to validate")
        return 0

    logger.info(f"Validating {len(files)} Python files...")

    # Run validation
    all_valid = validator.validate_files(files)

    # Print report
    validator.print_validation_report()

    # Exit with appropriate code
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
