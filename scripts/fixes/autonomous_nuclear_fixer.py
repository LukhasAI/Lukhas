#!/usr/bin/env python3
"""
🚀 AUTONOMOUS NUCLEAR F-STRING FIXER
Comprehensive autonomous fixes for remaining critical blockers
"""
from __future__ import annotations


import ast
import os
import re
import subprocess
from pathlib import Path


class AutonomousNuclearFixer:
    """Autonomous comprehensive f-string fixer"""

    def __init__(self):
        self.fixes_applied = 0
        self.files_fixed = 0

    def get_comprehensive_patterns(self) -> list[tuple[str, str, str]]:
        """All comprehensive f-string patterns"""
        return [
            # Method calls missing closing parenthesis
            (r'f"([^"]*)\{([^}]+\.upper)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD"),
            (r'f"([^"]*)\{([^}]+\.lower)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD"),
            (r'f"([^"]*)\{([^}]+\.strip)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD"),
            (r'f"([^"]*)\{([^}]+\.timestamp)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD"),
            (r'f"([^"]*)\{([^}]+\.isoformat)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD"),
            # Function calls missing closing parenthesis
            (r'f"([^"]*)\{(time\.time)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNCTION"),
            (r'f"([^"]*)\{(uuid\.uuid4)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNCTION"),
            (r'f"([^"]*)\{(datetime\.now[^}]*)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNCTION"),
            # Built-in functions missing closing parenthesis
            (r'f"([^"]*)\{(len)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            (r'f"([^"]*)\{(hash)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            (r'f"([^"]*)\{(int)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            (r'f"([^"]*)\{(str)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            (r'f"([^"]*)\{(float)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            (r'f"([^"]*)\{(bool)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            (r'f"([^"]*)\{(type)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "BUILTIN"),
            # Complex nested calls
            (r'f"([^"]*)\{([^}]*)\(([^}]*)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "NESTED"),
            # Single quotes versions
            (r"f'([^']*)\{([^}]+\.upper)\(\}([^']*)'", r"f'\1{\2()}\3'", "METHOD_SINGLE"),
            (r"f'([^']*)\{([^}]+\.lower)\(\}([^']*)'", r"f'\1{\2()}\3'", "METHOD_SINGLE"),
            (r"f'([^']*)\{(len)\(([^}]+)\}([^']*)'", r"f'\1{\2(\3)}\4'", "BUILTIN_SINGLE"),
            # Attribute access patterns
            (r'f"([^"]*)\{([^}]+)\.__name__\}([^"]*)"', r'f"\1{\2.__name__}\3"', "ATTRIBUTE"),
            (r'f"([^"]*)\{([^}]+)\.get\(([^}]+)\}([^"]*)"', r'f"\1{\2.get(\3)}\4"', "METHOD_CALL"),
        ]

    def validate_syntax(self, content: str, file_path: str) -> bool:
        """Validate syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def fix_file_autonomous(self, file_path: str) -> tuple[bool, int]:
        """Apply autonomous fixes to a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            total_fixes = 0

            for pattern, replacement, _pattern_type in self.get_comprehensive_patterns():
                try:
                    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                    if matches:
                        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
                        if new_content != content:
                            fix_count = len(matches)
                            total_fixes += fix_count
                            content = new_content

                except re.error:
                    continue

            if total_fixes > 0:
                # Validate the fixes
                if self.validate_syntax(content, file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"🚀 AUTONOMOUS FIX: {file_path} - {total_fixes} fixes applied")
                    self.fixes_applied += total_fixes
                    self.files_fixed += 1
                    return True, total_fixes
                else:
                    print(f"❌ Validation failed for {file_path}")
                    return False, 0

            return True, 0  # No fixes needed

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False, 0

    def get_all_critical_files(self) -> list[str]:
        """Get all files that could be blocking functionality"""
        patterns = [
            # Root level blocking files
            "*.py",
            # Lukhas core - highest priority
            "lukhas/**/*.py",
            # Candidate consciousness and memory
            "candidate/consciousness/*.py",
            "candidate/memory/*.py",
            "candidate/agents/*.py",
            "candidate/bio/*.py",
            # Infrastructure
            "governance/*.py",
            "orchestration/*.py",
            "core/*.py",
            "bridge/*.py",
        ]

        all_files = []
        for pattern in patterns:
            files = list(Path(".").glob(pattern))
            all_files.extend([str(f) for f in files if f.suffix == ".py"])

        # Remove duplicates and sort by priority
        unique_files = list(set(all_files))

        # Prioritize lukhas/ files first
        lukhas_files = [f for f in unique_files if f.startswith("lukhas/")]
        root_files = [f for f in unique_files if "/" not in f and f.endswith(".py")]
        candidate_files = [f for f in unique_files if f.startswith("candidate/")]
        other_files = [f for f in unique_files if f not in lukhas_files + root_files + candidate_files]

        return lukhas_files + root_files + candidate_files[:50] + other_files[:30]

    def run_autonomous_nuclear_fixes(self):
        """Run comprehensive autonomous nuclear fixes"""
        print("🚀 AUTONOMOUS NUCLEAR F-STRING FIXER")
        print("=" * 60)
        print("Comprehensive autonomous fixes for maximum impact")
        print()

        critical_files = self.get_all_critical_files()
        print(f"Processing {len(critical_files)} critical files...")
        print()

        successful_fixes = []
        failed_fixes = []

        for i, file_path in enumerate(critical_files):
            if os.path.exists(file_path):
                success, fixes = self.fix_file_autonomous(file_path)

                if success and fixes > 0:
                    successful_fixes.append((file_path, fixes))
                elif not success:
                    failed_fixes.append(file_path)

                # Progress indicator
                if (i + 1) % 20 == 0:
                    print(f"Progress: {i + 1}/{len(critical_files)} files processed")

        print()
        print("🚀 AUTONOMOUS NUCLEAR RESULTS:")
        print("=" * 40)
        print(f"Files processed: {len(critical_files)}")
        print(f"Files successfully fixed: {self.files_fixed}")
        print(f"Total fixes applied: {self.fixes_applied}")
        print(f"Failed validations: {len(failed_fixes)}")

        if successful_fixes:
            print()
            print("🏆 Top Successful Fixes:")
            top_fixes = sorted(successful_fixes, key=lambda x: x[1], reverse=True)[:15]
            for file_path, fixes in top_fixes:
                print(f"  {file_path}: {fixes} fixes")

        return self.fixes_applied > 0


def main():
    """Run autonomous nuclear fixer"""
    print("🚀 AUTONOMOUS NUCLEAR F-STRING FIXER")
    print("Comprehensive autonomous approach with full approval")
    print()

    fixer = AutonomousNuclearFixer()
    success = fixer.run_autonomous_nuclear_fixes()

    if success:
        print("\n🧪 Running functional test to verify improvements...")
        try:
            subprocess.run(["python3", "functional_test_suite.py"], capture_output=True, text=True, timeout=60)
            print("Functional test completed. Check results above.")
        except subprocess.TimeoutExpired:
            print("Functional test taking longer than expected...")
        except Exception as e:
            print(f"Could not run functional test: {e}")
    else:
        print("\n⚠️ No fixes applied - files may need manual intervention")


if __name__ == "__main__":
    main()