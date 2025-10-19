#!/usr/bin/env python3
"""
Module: rapid_cascade_chaser.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
🏃‍♂️ RAPID CASCADE CHASER
Follow and fix the cascade blockers in real-time as they move
"""

import ast
import os
import re
import subprocess
from typing import Optional


class RapidCascadeChaser:
    """Chase the cascade and fix blockers in real-time"""

    def __init__(self):
        self.fixes_applied = 0
        self.chases = 0

    def get_current_blocker(self) -> Optional[tuple[str, int, str]]:
        """Get the current cascade blocker from functional test"""
        try:
            result = subprocess.run(["python3", "functional_test_suite.py"], capture_output=True, text=True, timeout=30)

            output = result.stdout

            # Parse for f-string errors
            pattern = r"f-string: closing parenthesis '\}' does not match opening parenthesis '\(' \(([^)]+\.py), line (\d+)\)"
            matches = re.findall(pattern, output)

            if matches:
                filename, line_num = matches[0]  # Take first blocker
                return filename, int(line_num), "f-string-parenthesis"

            # Parse for other syntax errors
            pattern = r"SyntaxError.*\(([^)]+\.py), line (\d+)\)"
            matches = re.findall(pattern, output)

            if matches:
                filename, line_num = matches[0]
                return filename, int(line_num), "syntax-error"

            return None

        except Exception as e:
            print(f"❌ Error getting blocker: {e}")
            return None

    def fix_f_string_line(self, file_path: str, line_num: int) -> bool:
        """Fix specific f-string issue at given line"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_num > len(lines) or line_num < 1:
                return False

            original_line = lines[line_num - 1]  # Convert to 0-based indexing
            fixed_line = original_line

            # Aggressive f-string parenthesis fixes
            patterns = [
                # Pattern 1: Missing closing parenthesis in method calls
                (r"\.(\w+)\(\}", r".\1()}"),
                # Pattern 2: Missing closing parenthesis in function calls
                (r"(\w+)\(([^}]*)\}", r"\1(\2)}"),
                # Pattern 3: Fix uuid.uuid4( patterns
                (r"uuid\.uuid4\(\}", r"uuid.uuid4()}"),
                # Pattern 4: Fix datetime patterns
                (r"datetime\.now\([^}]*\)\(\}", r"datetime.now().timestamp()}"),
                # Pattern 5: Fix len patterns
                (r"len\(([^}]+)\}", r"len(\1)}"),
                # Pattern 6: Fix hash patterns
                (r"hash\(([^}]+)\}", r"hash(\1)}"),
                # Pattern 7: Fix int patterns
                (r"int\(([^}]+)\}", r"int(\1)}"),
                # Pattern 8: Fix type patterns
                (r"type\(([^}]+)\}", r"type(\1)}"),
            ]

            for pattern, replacement in patterns:
                if re.search(pattern, fixed_line):
                    fixed_line = re.sub(pattern, replacement, fixed_line)
                    break

            if fixed_line != original_line:
                lines[line_num - 1] = fixed_line

                # Write back and validate
                content = "".join(lines)

                try:
                    ast.parse(content)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    print(f"🏃‍♂️ CHASED & FIXED: {file_path}:{line_num}")
                    print(f"   Before: {original_line.strip()}")
                    print(f"   After:  {fixed_line.strip()}")

                    self.fixes_applied += 1
                    return True

                except SyntaxError:
                    print(f"❌ Fix broke syntax for {file_path}:{line_num}")
                    return False

            return False

        except Exception as e:
            print(f"❌ Error fixing {file_path}:{line_num}: {e}")
            return False

    def chase_cascade(self, max_chases: int = 20):
        """Chase the cascade blockers in real-time"""
        print("🏃‍♂️ RAPID CASCADE CHASER")
        print("=" * 60)
        print("Chasing cascade blockers in real-time")
        print()

        for chase in range(max_chases):
            self.chases += 1

            print(f"\n🔍 CHASE #{chase + 1}: Finding current blocker...")

            # Get current blocker
            blocker = self.get_current_blocker()

            if not blocker:
                print("🎉 NO MORE BLOCKERS FOUND!")
                print("Running final functional test...")
                os.system("python3 functional_test_suite.py")
                return True

            filename, line_num, error_type = blocker

            # Try to find the actual file
            possible_paths = [
                filename,
                f"lukhas/{filename}",
                f"candidate/{filename}",
                f"lukhas/core/{filename}",
                f"lukhas/core/common/{filename}",
            ]

            actual_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    actual_path = path
                    break

            if not actual_path:
                print(f"❌ Could not find file: {filename}")
                continue

            print(f"🎯 FOUND BLOCKER: {actual_path}:{line_num} ({error_type})")

            # Fix the blocker
            if error_type == "f-string-parenthesis":
                success = self.fix_f_string_line(actual_path, line_num)

                if not success:
                    print(f"❌ Could not fix {actual_path}:{line_num}")
                    break
            else:
                print(f"⚠️  Non-f-string error, skipping: {error_type}")
                break

        print("\n🏃‍♂️ CHASE RESULTS:")
        print("=" * 30)
        print(f"Chases performed: {self.chases}")
        print(f"Fixes applied: {self.fixes_applied}")

        if self.fixes_applied > 0:
            print("\n🧪 Running functional test to check progress...")
            os.system("python3 functional_test_suite.py")

        return self.fixes_applied > 0


def main():
    chaser = RapidCascadeChaser()
    chaser.chase_cascade()


if __name__ == "__main__":
    main()
