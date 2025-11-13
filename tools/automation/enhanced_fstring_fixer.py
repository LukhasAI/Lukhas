#!/usr/bin/env python3
"""
Enhanced F-String Syntax Fixer
==============================
Automated fixer for comprehensive f-string syntax errors based on LUKHAS diagnostic patterns.
Handles all patterns identified in the diagnostic report:
- Extra closing braces in format specifications
- Method call syntax errors in f-strings
- Mismatched parentheses in expressions
- Bracket mismatches

T4 Autofix compliant - integrates with existing .t4autofix.toml policy.
"""

import ast
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Diagnostic error patterns from DIAGNOSTIC_REPORT.md
F_STRING_PATTERNS = [
    # Pattern 1: Extra closing brace after format spec
    # Example: {obj.get('key', 0)}:.3f} -> {obj.get('key', 0):.3f}
    {
        "name": "extra_closing_brace_format_spec",
        "pattern": r"(\{[^{}]*\}):(\.?\d*[fFeEgGdiouxXbcrsa])\}",
        "replacement": r"\1:\2",
        "description": "Remove extra } after format specification",
    },
    # Pattern 2: Method call syntax in f-string
    # Example: {uuid.uuid4()}.hex[:8]} -> {uuid.uuid4().hex[:8]}
    {
        "name": "method_call_syntax",
        "pattern": r"(\{[^{}]*\(\))\}\.(\w+(?:\[.*?\])?)\}",
        "replacement": r"\1.\2}",
        "description": "Fix method chaining syntax in f-strings",
    },
    # Pattern 3: Mismatched parentheses
    # Example: {(total / max(total_discovered, 1)} -> {(total / max(total_discovered, 1))}
    {
        "name": "mismatched_parentheses",
        "pattern": r"\{(\([^)]*\([^)]*\)[^)]*)\}",
        "replacement": r"{\1)}",
        "description": "Balance parentheses in f-string expressions",
    },
    # Pattern 4: General extra closing brace
    # Example: f"Value: {value}" extra } -> f"Value: {value}"
    {
        "name": "general_extra_brace",
        "pattern": r'(\{[^{}]*\})\}(?=\s*["\'])',
        "replacement": r"\1",
        "description": "Remove extra closing brace",
    },
    # Pattern 5: Bracket mismatch (] vs })
    # Example: violations]} -> violations}]
    {
        "name": "bracket_mismatch",
        "pattern": r"(\w+)\]\}",
        "replacement": r"\1}]",
        "description": "Fix bracket vs brace mismatch",
    },
]


class EnhancedFStringFixer:
    """Enhanced F-String syntax fixer using pattern matching"""

    def __init__(self, validate_syntax: bool = True):
        self.validate_syntax = validate_syntax
        self.stats = {
            "files_processed": 0,
            "files_changed": 0,
            "patterns_fixed": {},
            "syntax_errors_found": 0,
            "syntax_errors_fixed": 0,
        }

    def fix_content(self, content: str) -> tuple[str, bool]:
        """Fix f-string syntax errors in content"""
        original_content = content
        changed = False

        for pattern_def in F_STRING_PATTERNS:
            pattern = pattern_def["pattern"]
            replacement = pattern_def["replacement"]
            name = pattern_def["name"]

            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                self.stats["patterns_fixed"][name] = self.stats["patterns_fixed"].get(name, 0) + len(matches)
                changed = True
                logger.debug(f"Applied pattern '{name}': {len(matches)} fixes")

        # Validate syntax if requested
        if self.validate_syntax and changed:
            if self._validate_python_syntax(content):
                self.stats["syntax_errors_fixed"] += 1
                logger.debug("Syntax validation passed")
            else:
                # Rollback if syntax is broken
                logger.warning("Syntax validation failed, rolling back changes")
                content = original_content
                changed = False
                self.stats["syntax_errors_found"] += 1

        return content, changed

    def _validate_python_syntax(self, content: str) -> bool:
        """Validate Python syntax using AST parsing"""
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            logger.debug(f"Syntax error detected: {e}")
            return False

    def fix_file(self, file_path: Path) -> bool:
        """Fix f-string errors in a single file"""
        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Apply fixes
            fixed_content, changed = self.fix_content(content)

            self.stats["files_processed"] += 1

            if changed:
                # Write back fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                self.stats["files_changed"] += 1
                logger.info(f"Fixed f-string errors in: {file_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False

    def fix_files(self, file_paths: list[Path]) -> dict:
        """Fix f-string errors in multiple files"""
        logger.info(f"Processing {len(file_paths)} files for f-string fixes...")

        for file_path in file_paths:
            self.fix_file(file_path)

        return self.get_stats()

    def get_stats(self) -> dict:
        """Get fixing statistics"""
        return self.stats.copy()


def get_problematic_files() -> list[Path]:
    """Get list of files with known f-string syntax errors from diagnostic"""
    base_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    # Files identified in DIAGNOSTIC_REPORT.md with syntax errors
    problematic_files = [
        "tests/test_advanced_suite_standalone.py",
        "tests/test_comprehensive_all_systems.py",
        "tests/test_consciousness_direct.py",
        "tests/test_core_systems_comprehensive.py",
        "tests/test_memory_integration_validation.py",
        "tests/test_priority4_systems_functional.py",
        "tests/test_real_consciousness_emergence.py",
    ]

    existing_files = []
    for file_path in problematic_files:
        full_path = base_path / file_path
        if full_path.exists():
            existing_files.append(full_path)
        else:
            logger.warning(f"File not found: {full_path}")

    return existing_files


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced F-String Syntax Fixer")
    parser.add_argument("files", nargs="*", help="Files to fix (default: diagnostic problem files)")
    parser.add_argument("--no-validate", action="store_true", help="Skip syntax validation")
    parser.add_argument("--pattern", help="Test specific pattern name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")

    args = parser.parse_args()

    # Initialize fixer
    fixer = EnhancedFStringFixer(validate_syntax=not args.no_validate)

    # Get files to process
    file_paths = [Path(f) for f in args.files] if args.files else get_problematic_files()

    if not file_paths:
        logger.error("No files to process")
        return 1

    # Pattern testing mode
    if args.pattern:
        logger.info(f"Testing pattern: {args.pattern}")
        pattern_def = next((p for p in F_STRING_PATTERNS if p["name"] == args.pattern), None)
        if not pattern_def:
            logger.error(f"Pattern not found: {args.pattern}")
            return 1

        for file_path in file_paths:
            content = file_path.read_text()
            matches = re.findall(pattern_def["pattern"], content)
            if matches:
                logger.info(f"{file_path}: {len(matches)} matches for pattern '{args.pattern}'")
        return 0

    # Dry run mode
    if args.dry_run:
        logger.info("DRY RUN MODE - no changes will be made")
        for file_path in file_paths:
            content = file_path.read_text()
            _fixed_content, changed = fixer.fix_content(content)
            if changed:
                logger.info(f"Would fix: {file_path}")
        return 0

    # Execute fixes
    stats = fixer.fix_files(file_paths)

    # Report results
    logger.info("=== F-String Fixer Results ===")
    logger.info(f"Files processed: {stats['files_processed']}")
    logger.info(f"Files changed: {stats['files_changed']}")
    logger.info(f"Syntax errors fixed: {stats['syntax_errors_fixed']}")
    logger.info(f"Syntax errors found: {stats['syntax_errors_found']}")

    if stats["patterns_fixed"]:
        logger.info("Pattern fixes applied:")
        for pattern, count in stats["patterns_fixed"].items():
            logger.info(f"  {pattern}: {count} fixes")

    return 0 if stats["syntax_errors_found"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
