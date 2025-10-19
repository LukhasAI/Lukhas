#!/usr/bin/env python3
"""
Module: brand_validator.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
LUKHAS Brand Validator - Ensures consistent naming across the codebase
Prevents deprecated terminology and enforces Lambda (Λ) usage rules
"""

import sys
from pathlib import Path

# Define brand rules
DEPRECATED_TERMS = {
    "MATADA": "MΛTRIZ",  # Display form
    "matada": "matriz",  # Plain text form
    "Matada": "Matriz",  # Capitalized form
}

DISPLAY_TERMS = {
    "LUKHΛS": "Display form - use in logos, headings, marketing",
    "ΛI": "Display form for AI - use in promotional content",
    "ΛiD": "Display form for identity system",
    "MΛTRIZ": "Display form for MATRIZ product",
}

PLAIN_TERMS = {
    "Lukhas": "Plain text form - use in body copy, SEO, accessibility",
    "Lukhas AI": "Plain text for AI product",
    "Lukhas ID": "Plain text for identity system",
    "Matriz": "Plain text for MATRIZ product",
}

# File patterns to check
INCLUDE_PATTERNS = [
    "**/*.py",
    "**/*.js",
    "**/*.ts",
    "**/*.tsx",
    "**/*.jsx",
    "**/*.md",
    "**/*.json",
    "**/*.yaml",
    "**/*.yml",
    "**/*.html",
    "**/*.css",
    "**/*.scss",
]

# Directories to exclude
EXCLUDE_DIRS = [
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
]


class BrandValidator:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.violations = []
        self.warnings = []

    def validate_file(self, filepath: Path) -> list[tuple[int, str, str]]:
        """Check a single file for brand violations"""
        violations = []

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Check for deprecated terms
                for deprecated, replacement in DEPRECATED_TERMS.items():
                    if deprecated in line:
                        violations.append(
                            (
                                line_num,
                                f"Deprecated term '{deprecated}' found",
                                f"Replace with '{replacement}'",
                            )
                        )

                # Check for incorrect Lambda usage in URLs
                if "Λ" in line and ("href=" in line or "url" in line.lower() or "path" in line.lower()):
                    if "aria-label" not in line and "display" not in line.lower():
                        violations.append(
                            (
                                line_num,
                                "Lambda (Λ) found in URL/path context",
                                "Use plain text form in URLs and paths",
                            )
                        )

        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)

        return violations

    def validate_directory(self) -> dict[str, list]:
        """Validate entire directory tree"""
        results = {"violations": [], "warnings": [], "files_checked": 0, "files_with_issues": 0}

        for pattern in INCLUDE_PATTERNS:
            for filepath in self.root_dir.glob(pattern):
                # Skip excluded directories
                if any(excluded in filepath.parts for excluded in EXCLUDE_DIRS):
                    continue

                results["files_checked"] += 1
                violations = self.validate_file(filepath)

                if violations:
                    results["files_with_issues"] += 1
                    relative_path = filepath.relative_to(self.root_dir)

                    for line_num, issue, suggestion in violations:
                        results["violations"].append(
                            {
                                "file": str(relative_path),
                                "line": line_num,
                                "issue": issue,
                                "suggestion": suggestion,
                            }
                        )

        return results

    def print_report(self, results: dict) -> bool:
        """Print validation report and return success status"""
        print("\n" + "=" * 60)
        print("LUKHAS BRAND VALIDATION REPORT")
        print("=" * 60)

        print(f"\nFiles checked: {results['files_checked']}")
        print(f"Files with issues: {results['files_with_issues']}")
        print(f"Total violations: {len(results['violations'])}")

        if results["violations"]:
            print("\n" + "-" * 60)
            print("VIOLATIONS FOUND:")
            print("-" * 60)

            # Group by file
            by_file = {}
            for violation in results["violations"]:
                file = violation["file"]
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(violation)

            for file, violations in by_file.items():
                print(f"\n📁 {file}:")
                for v in violations:
                    print(f"  Line {v['line']}: {v['issue']}")
                    print(f"    → {v['suggestion']}")

        if results["warnings"]:
            print("\n" + "-" * 60)
            print("WARNINGS:")
            print("-" * 60)
            for warning in results["warnings"]:
                print(f"  ⚠️  {warning}")

        if not results["violations"]:
            print("\n✅ All brand guidelines are being followed!")
            return True
        else:
            print("\n❌ Brand violations found. Please fix the issues above.")
            print("\nBrand Guidelines:")
            print("  • MATADA → MΛTRIZ (display) or Matriz (plain)")
            print("  • Use Lambda (Λ) only in display contexts, not URLs")
            print("  • Always provide aria-label for accessibility")
            return False


def main():
    """Main entry point"""
    # Get the repository root (parent of scripts directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print(f"🔍 Validating brand compliance in: {repo_root}")

    validator = BrandValidator(repo_root)
    results = validator.validate_directory()

    success = validator.print_report(results)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
