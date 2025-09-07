#!/usr/bin/env python3
"""
🎯 TARGETED NUCLEAR F-STRING FIXER
Fixes the specific "unmatched )" pattern found in the codebase
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class TargetedNuclearFixer:
    """Targeted fixes for the specific f-string patterns causing issues"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

    def get_targeted_patterns(self) -> list[tuple[str, str, str]]:
        """Specific patterns causing the 'unmatched )' errors"""
        return [
            # Pattern 1: Missing ) before _ in method calls
            (r'f"([^"]*)\{([^}]+\.upper)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_CALL"),
            (r'f"([^"]*)\{([^}]+\.lower)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_CALL"),
            (r'f"([^"]*)\{([^}]+\.strip)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_CALL"),
            (r'f"([^"]*)\{([^}]+\.timestamp)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_CALL"),

            # Pattern 2: Missing ) in function calls
            (r'f"([^"]*)\{(time\.time)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNCTION_CALL"),
            (r'f"([^"]*)\{(uuid\.uuid4)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNCTION_CALL"),

            # Pattern 3: Missing ) in nested function calls
            (r'f"([^"]*)\{([^}]*\([^}]*)\}([^"]*)"', r'f"\1{\2)}\3"', "NESTED_CALL"),

            # Pattern 4: The specific upper()_ pattern we found
            (r"\.upper\(\}_", r".upper()}_", "UPPER_UNDERSCORE"),
            (r"\.lower\(\}_", r".lower()}_", "LOWER_UNDERSCORE"),
            (r"\.strip\(\}_", r".strip()}_", "STRIP_UNDERSCORE"),

            # Pattern 5: Missing ) in hash/int/str calls
            (r'f"([^"]*)\{hash\(([^}]*)\}([^"]*)"', r'f"\1{hash(\2)}\3"', "HASH_CALL"),
            (r'f"([^"]*)\{int\(([^}]*)\}([^"]*)"', r'f"\1{int(\2)}\3"', "INT_CALL"),
            (r'f"([^"]*)\{str\(([^}]*)\}([^"]*)"', r'f"\1{str(\2)}\3"', "STR_CALL"),
        ]

    def validate_fix(self, original: str, fixed: str) -> bool:
        """Validate that the fix improves syntax"""
        try:
            # Try to parse the fixed content
            ast.parse(fixed)
            return True
        except SyntaxError:
            try:
                # Check if original was also invalid (we're not making it worse)
                ast.parse(original)
                return False  # Original was valid, fix broke it
            except SyntaxError:
                # Both are invalid, but let's see if we're getting closer
                original_errors = str(sys.exc_info()[1])
                try:
                    ast.parse(fixed)
                except SyntaxError:
                    fixed_errors = str(sys.exc_info()[1])
                    # If error messages changed, we might be making progress
                    return "unmatched" not in fixed_errors and "unmatched" in original_errors
                return True

    def fix_file_targeted(self, file_path: str) -> tuple[bool, int, list[str]]:
        """Apply targeted fixes to a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            total_fixes = 0
            patterns_applied = []

            for pattern, replacement, pattern_type in self.get_targeted_patterns():
                try:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    if matches:
                        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                        if new_content != content:
                            fix_count = len(matches)
                            total_fixes += fix_count
                            patterns_applied.append(f"{pattern_type}: {fix_count}")
                            content = new_content

                except re.error:
                    continue

            if total_fixes > 0:
                # Validate the fixes improve things
                if self.validate_fix(original_content, content):
                    if not self.dry_run:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"🎯 FIXED: {file_path} - {total_fixes} fixes applied")
                    else:
                        print(f"🔍 WOULD FIX: {file_path} - {total_fixes} fixes identified")

                    self.fixes_applied += total_fixes
                    self.files_fixed += 1
                    return True, total_fixes, patterns_applied
                else:
                    print(f"❌ Fix validation failed for {file_path}")
                    return False, 0, []

            return True, 0, []  # No fixes needed

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False, 0, []

    def get_priority_files(self) -> list[str]:
        """Get files with highest blocking impact"""
        patterns = [
            # Core blocking files
            "lukhas/core/common/config.py",
            "business/__init__.py",
            "security/__init__.py",
            "products/__init__.py",

            # Lukhas core namespace
            "lukhas/**/__init__.py",
            "lukhas/**/config.py",
            "lukhas/**/*service.py",
            "lukhas/**/*adapter.py",

            # Critical candidate files
            "candidate/consciousness/*.py",
            "candidate/memory/*.py",
        ]

        files = []
        for pattern in patterns:
            matches = list(Path(".").glob(pattern))
            files.extend([str(f) for f in matches if f.suffix == ".py"])

        return list(set(files))

    def run_targeted_fixes(self, max_files: int = 100):
        """Run targeted nuclear fixes"""
        print("🎯 TARGETED NUCLEAR F-STRING FIXER")
        print("=" * 50)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print()

        priority_files = self.get_priority_files()[:max_files]

        print(f"Processing {len(priority_files)} priority files...")
        print()

        results = []
        for file_path in priority_files:
            if os.path.exists(file_path):
                success, fixes, patterns = self.fix_file_targeted(file_path)
                results.append({
                    "file": file_path,
                    "success": success,
                    "fixes": fixes,
                    "patterns": patterns
                })

        print()
        print("📊 TARGETED FIXING RESULTS:")
        print("=" * 30)
        print(f"Files processed: {len(results)}")
        print(f"Files fixed: {self.files_fixed}")
        print(f"Total fixes applied: {self.fixes_applied}")

        # Show top fixes
        if results:
            top_fixes = sorted(results, key=lambda x: x["fixes"], reverse=True)[:10]
            print()
            print("🏆 Top Fixes:")
            for result in top_fixes:
                if result["fixes"] > 0:
                    print(f"  {result['file']}: {result['fixes']} fixes")

        return len([r for r in results if r["fixes"] > 0]) > 0


def main():
    """Main targeted nuclear fixer"""
    import sys

    dry_run = "--live" not in sys.argv

    if not dry_run:
        print("⚠️  LIVE MODE - Files will be modified!")
        response = input("Continue with live fixes? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    fixer = TargetedNuclearFixer(dry_run=dry_run)
    success = fixer.run_targeted_fixes(max_files=150)

    if success and not dry_run:
        print("\n🧪 Recommend running functional tests to verify improvements")
        print("Command: python3 functional_test_suite.py")


if __name__ == "__main__":
    main()
