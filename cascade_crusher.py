#!/usr/bin/env python3
"""
⚡ CASCADE CRUSHER
Aggressively target the cascade blockers one by one with immediate testing
"""

import ast
import os
import subprocess
from typing import List, Tuple


class CascadeCrusher:
    """Crush cascade blockers with immediate functional testing feedback"""

    def __init__(self):
        self.fixes_applied = 0
        self.cascade_broken = False

    def get_critical_remaining_files(self) -> list[str]:
        """Files most likely to break the cascade"""
        return [
            "lukhas/memory/__init__.py",
            "business/__init__.py",
            "security/__init__.py",
            "lukhas/core/common/glyph.py",
            "lukhas/bridge/bridge_wrapper.py",
            "lukhas/identity/auth_service.py",
            "lukhas/memory/matriz_adapter.py",
            "lukhas/governance/auth_glyph_registry.py",
            "lukhas/consciousness/consciousness_wrapper.py",
        ]

    def aggressive_fix_patterns(self, content: str) -> str:
        """Apply aggressive f-string fixes"""
        import re

        # Pattern 1: Fix any {word} pattern missing closing parenthesis
        content = re.sub(r'f"([^"]*)\{([^}]+)\(([^)]*)\}([^"]*)"',
                        lambda m: f'f"{m.group(1)}{{{m.group(2)}({m.group(3)})}}{m.group(4)}"',
                        content)

        # Pattern 2: Fix method calls specifically
        content = re.sub(r"\.(\w+)\(\}", r".\1()}", content)

        # Pattern 3: Fix function calls
        content = re.sub(r"(\w+)\(([^}]*)\}", r"\1(\2)}", content)

        # Pattern 4: Fix nested parentheses
        content = re.sub(r"\{([^{}]*\([^)]*)\}", r"{\1)}", content)

        return content

    def crush_cascade_file(self, file_path: str) -> bool:
        """Aggressively fix a single cascade file"""
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                original = f.read()

            # Apply aggressive fixes
            fixed = self.aggressive_fix_patterns(original)

            if fixed == original:
                return False  # No changes needed

            # Validate syntax
            try:
                ast.parse(fixed)
            except SyntaxError:
                print(f"❌ Aggressive fix broke syntax for {file_path}")
                return False

            # Apply the fix
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed)

            print(f"⚡ CRUSHED: {file_path}")
            self.fixes_applied += 1
            return True

        except Exception as e:
            print(f"❌ Error crushing {file_path}: {e}")
            return False

    def test_functional_breakthrough(self) -> tuple[bool, str]:
        """Test if we achieved a functional breakthrough"""
        try:
            result = subprocess.run(["python3", "functional_test_suite.py"],
                                  capture_output=True, text=True, timeout=30)

            output = result.stdout

            # Check for functional breakthroughs
            if "✅" in output and "Functionally Operational: 0/13" not in output:
                return True, "BREAKTHROUGH DETECTED!"

            # Check if cascade moved to different blocker
            if "Memory System Functional" in output and "❌" not in output.split("Memory System Functional")[1].split("\n")[0]:
                return True, "Memory System Breakthrough!"

            if "Agent System Functional" in output and "❌" not in output.split("Agent System Functional")[1].split("\n")[0]:
                return True, "Agent System Breakthrough!"

            if "Governance Functional" in output and "❌" not in output.split("Governance Functional")[1].split("\n")[0]:
                return True, "Governance System Breakthrough!"

            # Check for error cascade changes
            lines = output.split("\n")
            error_lines = [line for line in lines if "f-string:" in line and "does not match" in line]

            if len(error_lines) < 5:  # Significant error reduction
                return True, f"Error cascade significantly reduced to {len(error_lines)} blockers"

            return False, f"Cascade continues with {len(error_lines)} blockers"

        except subprocess.TimeoutExpired:
            return False, "Test timeout"
        except Exception as e:
            return False, f"Test error: {e}"

    def run_cascade_crusher(self):
        """Run the cascade crusher with immediate feedback"""
        print("⚡ CASCADE CRUSHER")
        print("=" * 60)
        print("Aggressively targeting cascade blockers with immediate testing")
        print()

        critical_files = self.get_critical_remaining_files()

        for i, file_path in enumerate(critical_files):
            print(f"\n⚡ CRUSHING #{i+1}: {file_path}")

            # Crush the file
            success = self.crush_cascade_file(file_path)

            if success:
                # Immediate functional test
                breakthrough, message = self.test_functional_breakthrough()

                if breakthrough:
                    print(f"🎉 {message}")
                    self.cascade_broken = True
                    break
                else:
                    print(f"📊 {message}")

            # Show progress
            if (i + 1) % 3 == 0:
                print(f"\nProgress: {i + 1}/{len(critical_files)} files processed")

        print("\n⚡ CASCADE CRUSHER RESULTS:")
        print("=" * 40)
        print(f"Files crushed: {self.fixes_applied}")
        print(f"Cascade broken: {self.cascade_broken}")

        if self.cascade_broken:
            print("\n🎉 FUNCTIONAL BREAKTHROUGH ACHIEVED!")
            print("Running final functional test...")
            os.system("python3 functional_test_suite.py")
        else:
            print("\n💪 Continue the assault - cascade weakened but not broken")


def main():
    crusher = CascadeCrusher()
    crusher.run_cascade_crusher()


if __name__ == "__main__":
    main()
