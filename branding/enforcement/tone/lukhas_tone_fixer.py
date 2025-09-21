#!/usr/bin/env python3
"""
LUKHAS Tone Fixer - Constellation Framework Auto-correction (⚛️🧠🛡️)
Automatic tone fixing for LUKHAS consciousness platform
"""

import sys
from pathlib import Path
from typing import Any


class LukhasToneFixer:
    """LUKHAS Constellation Framework tone auto-fixer"""

    def __init__(self):
        self.replacements = {
            "LUKHAS_PWM": "LUKHAS",
            "lukhas_pwm": "lukhas",
            "Lukhas_PWM": "Lukhas",
            "_PWM": "",
            "_pwm": "",
            "pwm_": "",
            "PWM_": "",
        }

    def fix_content(self, content: str, filepath: str = "") -> tuple[str, list[str]]:
        """Fix content tone issues automatically"""
        fixes_applied = []
        fixed_content = content

        # Apply replacements
        for old_term, new_term in self.replacements.items():
            if old_term in fixed_content:
                fixed_content = fixed_content.replace(old_term, new_term)
                fixes_applied.append(f"Replaced '{old_term}' with '{new_term}'")

        return fixed_content, fixes_applied

    def fix_file(self, filepath: Path) -> tuple[bool, list[str]]:
        """Fix a single file"""
        try:
            if filepath.suffix in [".py", ".md", ".yaml", ".yml", ".json", ".txt"]:
                original_content = filepath.read_text(encoding="utf-8", errors="ignore")
                fixed_content, fixes = self.fix_content(original_content, str(filepath))

                if fixes:
                    # Write back the fixed content
                    filepath.write_text(fixed_content, encoding="utf-8")
                    return True, fixes
                else:
                    return True, []  # No fixes needed
            return True, []  # Skip non-text files
        except Exception as e:
            return False, [f"Error fixing file: {e}"]

    def fix_files(self, filepaths: list[str]) -> dict[str, Any]:
        """Fix multiple files and return summary"""
        results = {
            "total_files": len(filepaths),
            "fixed": 0,
            "failed": 0,
            "fixes_applied": [],
            "files_fixed": [],
        }

        for filepath_str in filepaths:
            filepath = Path(filepath_str)
            if not filepath.exists():
                continue

            success, fixes = self.fix_file(filepath)

            if success:
                if fixes:
                    results["fixed"] += 1
                    results["files_fixed"].append(str(filepath))
                    for fix in fixes:
                        results["fixes_applied"].append(fix)
            else:
                results["failed"] += 1
                for error in fixes:  # fixes contains errors when success=False
                    results["fixes_applied"].append(error)

        return results


def main():
    """Main tone fixer entry point"""
    if len(sys.argv) < 2:
        print("Usage: lukhas_tone_fixer.py <file1> [file2] ...")
        sys.exit(1)

    fixer = LukhasToneFixer()
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
        print("✅ No text files to fix")
        sys.exit(0)

    results = fixer.fix_files(text_files)

    # Output results
    print("LUKHAS Tone Auto-Fix Results:")
    print(f"Files processed: {results['total_files']}")
    print(f"Files fixed: {results['fixed']}")
    print(f"Failures: {results['failed']}")

    if results["fixes_applied"]:
        print("\n⚡ Fixes applied:")
        for fix in results["fixes_applied"][:10]:  # Limit to first 10
            print(f"  - {fix}")
        if len(results["fixes_applied"]) > 10:
            print(f"  ... and {len(results['fixes_applied']) - 10} more fixes")

    print("✅ Tone auto-fix complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
