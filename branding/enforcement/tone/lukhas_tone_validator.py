#!/usr/bin/env python3
"""
LUKHAS Tone Validator - Trinity Framework Compliance (⚛️🧠🛡️)
Basic tone validation for LUKHAS consciousness platform
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class LukhasToneValidator:
    """LUKHAS Trinity Framework tone validation"""

    def __init__(self):
        self.approved_terminology = {
            "lukhas_ai",
            "lukhas",
            "trinity_framework",
            "consciousness",
            "quantum_inspired",
            "bio_inspired",
            "symbolic",
            "guardian",
            "identity",
            "memory",
            "orchestration",
            "agent_army",
        }

        self.deprecated_terms = {
            "lukhas_pwm": "lukhas_ai",
            "pwm": "lukhas",
            "_pwm": "",
            "lukhas_agi": "lukhas_ai",
        }

        self.trinity_symbols = ["⚛️", "🧠", "🛡️"]

    def validate_content(
        self, content: str, filepath: str = ""
    ) -> Tuple[bool, List[str]]:
        """Validate content against LUKHAS tone requirements"""
        issues = []

        # Check for deprecated terminology
        for deprecated, replacement in self.deprecated_terms.items():
            if deprecated.lower() in content.lower():
                issues.append(
                    f"Deprecated term '{deprecated}' found. Consider '{replacement}'"
                )

        # Basic Trinity Framework check
        has_trinity = any(symbol in content for symbol in self.trinity_symbols)
        if filepath.endswith(".md") and len(content) > 1000 and not has_trinity:
            issues.append(
                "Large documentation file missing Trinity Framework symbols (⚛️🧠🛡️)"
            )

        # Success if no critical issues
        return len(issues) == 0, issues

    def validate_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """Validate a single file"""
        try:
            if filepath.suffix in [".py", ".md", ".yaml", ".yml", ".json"]:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                return self.validate_content(content, str(filepath))
            return True, []  # Skip non-text files
        except Exception as e:
            return False, [f"Error reading file: {e}"]

    def validate_files(self, filepaths: List[str]) -> Dict[str, Any]:
        """Validate multiple files and return summary"""
        results = {
            "total_files": len(filepaths),
            "passed": 0,
            "failed": 0,
            "issues": [],
            "files_with_issues": [],
        }

        for filepath_str in filepaths:
            filepath = Path(filepath_str)
            if not filepath.exists():
                continue

            passed, issues = self.validate_file(filepath)

            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["files_with_issues"].append(str(filepath))
                for issue in issues:
                    results["issues"].append(f"{filepath}: {issue}")

        return results


def main():
    """Main tone validation entry point"""
    if len(sys.argv) < 2:
        print("Usage: lukhas_tone_validator.py <file1> [file2] ...")
        sys.exit(1)

    validator = LukhasToneValidator()
    files = sys.argv[1:]

    # Filter to only text files to avoid binary issues
    text_files = []
    for file in files:
        filepath = Path(file)
        if filepath.exists() and filepath.suffix in [
            ".py",
            ".md",
            ".yaml",
            ".yml",
            ".json",
            ".txt",
        ]:
            text_files.append(file)

    if not text_files:
        print("✅ No text files to validate")
        sys.exit(0)

    results = validator.validate_files(text_files)

    # Output results
    print("LUKHAS Tone Validation Results:")
    print(f"Files checked: {results['total_files']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")

    if results["issues"]:
        print("\n⚠️  Issues found:")
        for issue in results["issues"][:10]:  # Limit to first 10
            print(f"  - {issue}")
        if len(results["issues"]) > 10:
            print(f"  ... and {len(results['issues']) - 10} more issues")

    # For git hooks, we'll be permissive during transition
    # Only fail on critical issues (none defined yet)
    if results["failed"] > 0:
        print(
            "\n⚡ Note: Issues found but allowing commit during PWM transition period"
        )

    print("✅ Tone validation complete")
    sys.exit(0)  # Always pass for now


if __name__ == "__main__":
    main()
