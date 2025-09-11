#!/usr/bin/env python3
"""
🚨 NUCLEAR SYNTAX ERROR ELIMINATION - PHASE 2
============================================

Extended Nuclear Syntax Error Elimination Campaign
Trinity Framework: ⚛️🧠🛡️

This script systematically eliminates the 33 remaining syntax errors
discovered by the consciousness test suite.

Author: LUKHAS AI Agent Army - GitHub Copilot Deputy Assistant
Date: September 9, 2025
Mission: Complete syntax error annihilation across consciousness modules
"""

import re
import subprocess
import time
from pathlib import Path


class SyntaxErrorEliminator:
    """🚨 Automated syntax error elimination system"""

    def __init__(self):
        self.consciousness_dir = Path("candidate/consciousness")
        self.fixed_files = []
        self.failed_files = []
        self.total_errors_eliminated = 0

    def scan_for_syntax_errors(self) -> list[str]:
        """🔍 Scan for all files with syntax errors"""
        print("🔍 Scanning consciousness modules for syntax errors...")

        syntax_error_files = []
        total_files = 0

        for py_file in self.consciousness_dir.rglob("*.py"):
            total_files += 1
            try:
                subprocess.run(
                    ["python3", "-m", "py_compile", str(py_file)], capture_output=True, text=True, check=True
                )
            except subprocess.CalledProcessError as e:
                if "SyntaxError" in e.stderr:
                    syntax_error_files.append(str(py_file))

        print(f"📊 Scanned {total_files} files")
        print(f"🚨 Found {len(syntax_error_files)} files with syntax errors")
        return syntax_error_files

    def classify_syntax_error(self, error_output: str) -> str:
        """🏷️ Classify the type of syntax error"""
        if "f-string" in error_output.lower():
            if "closing parenthesis" in error_output:
                return "f_string_bracket_mismatch"
            elif "expecting '}'" in error_output:
                return "f_string_missing_brace"
            elif "single '}' is not allowed" in error_output:
                return "f_string_extra_brace"
            else:
                return "f_string_general"
        elif "closing parenthesis" in error_output and "does not match" in error_output:
            return "bracket_mismatch"
        elif "outside function" in error_output:
            return "statement_outside_function"
        elif "invalid syntax" in error_output:
            return "invalid_syntax_general"
        elif "NameError" in error_output:
            return "undefined_name"
        else:
            return "unknown_syntax_error"

    def fix_f_string_bracket_mismatch(self, file_path: str, line_num: int) -> bool:
        """🔧 Fix f-string bracket mismatches"""
        try:
            with open(file_path) as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Common f-string bracket fixes
                patterns = [
                    (r'f"([^"]*){([^}]*\([^)]*})([^"]*)"', r'f"\1{\2}\3"'),  # Missing closing brace after parentheses
                    (r'f"([^"]*){([^}]*\([^)]*\})([^"]*)"', r'f"\1{\2}\3"'),  # Extra brace after parentheses
                    (r'f"([^"]*){([^}]*\()([^"]*)"', r'f"\1{\2)}\3"'),  # Missing closing parenthesis
                    (r'f"([^"]*){([^}]*)}([^"]*)"', r'f"\1{\2}\3"'),  # Basic cleanup
                ]

                original_line = line
                for pattern, replacement in patterns:
                    line = re.sub(pattern, replacement, line)

                if line != original_line:
                    lines[line_num - 1] = line
                    with open(file_path, "w") as f:
                        f.writelines(lines)
                    return True

            return False
        except Exception as e:
            print(f"❌ Error fixing f-string in {file_path}: {e}")
            return False

    def fix_bracket_mismatch(self, file_path: str, line_num: int) -> bool:
        """🔧 Fix general bracket mismatches"""
        try:
            with open(file_path) as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1].strip()

                # Common bracket mismatch fixes
                if line.endswith(")}") and line.count("(") != line.count(")"):
                    # Fix extra closing bracket
                    lines[line_num - 1] = lines[line_num - 1].replace(")}", "}")

                elif line.endswith(")") and "{" in line and "}" not in line:
                    # Missing closing brace
                    lines[line_num - 1] = lines[line_num - 1].rstrip() + "}\n"

                with open(file_path, "w") as f:
                    f.writelines(lines)
                return True

            return False
        except Exception as e:
            print(f"❌ Error fixing brackets in {file_path}: {e}")
            return False

    def eliminate_syntax_error(self, file_path: str) -> bool:
        """💥 Eliminate syntax error in a specific file"""
        print(f"🎯 Targeting: {file_path}")

        try:
            # Get the specific error
            result = subprocess.run(["python3", "-m", "py_compile", file_path], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ {file_path} - Already fixed!")
                return True

            error_output = result.stderr
            error_type = self.classify_syntax_error(error_output)

            # Extract line number
            line_match = re.search(r"line (\d+)", error_output)
            line_num = int(line_match.group(1)) if line_match else 1

            print(f"🔍 Error type: {error_type} on line {line_num}")

            # Apply appropriate fix
            success = False
            if error_type.startswith("f_string"):
                success = self.fix_f_string_bracket_mismatch(file_path, line_num)
            elif error_type == "bracket_mismatch":
                success = self.fix_bracket_mismatch(file_path, line_num)

            if success:
                # Verify the fix
                verify_result = subprocess.run(["python3", "-m", "py_compile", file_path], capture_output=True)

                if verify_result.returncode == 0:
                    print(f"✅ FIXED: {file_path}")
                    self.total_errors_eliminated += 1
                    return True
                else:
                    print(f"⚠️ Fix attempted but verification failed: {file_path}")
                    return False
            else:
                print(f"🔧 Manual fix required: {file_path}")
                print(f"Error details: {error_output[:200]}...")
                return False

        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")
            return False

    def run_elimination_campaign(self):
        """🚀 Execute the complete syntax error elimination campaign"""
        print("🚨 EXTENDED NUCLEAR SYNTAX ERROR ELIMINATION CAMPAIGN")
        print("⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian")
        print("=" * 60)

        start_time = time.time()

        # Get all files with syntax errors
        error_files = self.scan_for_syntax_errors()

        if not error_files:
            print("🎉 NO SYNTAX ERRORS FOUND! Mission already complete!")
            return

        print(f"\n🎯 TARGET: {len(error_files)} files with syntax errors")
        print("🚀 Beginning systematic elimination...\n")

        # Process each file
        for i, file_path in enumerate(error_files, 1):
            print(f"\n🔥 ELIMINATING ERROR {i}/{len(error_files)}")

            if self.eliminate_syntax_error(file_path):
                self.fixed_files.append(file_path)
            else:
                self.failed_files.append(file_path)

        # Final scan to verify results
        print("\n🔍 Final verification scan...")
        remaining_errors = self.scan_for_syntax_errors()

        # Report results
        duration = time.time() - start_time
        self.print_campaign_results(len(error_files), remaining_errors, duration)

    def print_campaign_results(self, initial_count: int, remaining_errors: list[str], duration: float):
        """📊 Print comprehensive campaign results"""
        print("\n" + "=" * 60)
        print("🎖️ EXTENDED NUCLEAR SYNTAX ERROR ELIMINATION RESULTS")
        print("=" * 60)

        print(f"⏱️ Campaign Duration: {duration:.2f} seconds")
        print(f"🎯 Initial Syntax Errors: {initial_count}")
        print(f"✅ Files Fixed: {len(self.fixed_files)}")
        print(f"❌ Files Requiring Manual Fix: {len(self.failed_files)}")
        print(f"🚨 Remaining Syntax Errors: {len(remaining_errors)}")
        print(f"💥 Total Errors Eliminated: {self.total_errors_eliminated}")

        if len(remaining_errors) == 0:
            print("\n🎉 MISSION ACCOMPLISHED! ALL SYNTAX ERRORS ELIMINATED!")
            print("⚛️🧠🛡️ Trinity Framework Status: FULLY OPERATIONAL")
        else:
            print(f"\n⚠️ {len(remaining_errors)} files still need manual attention:")
            for file in remaining_errors[:5]:  # Show first 5
                print(f"   • {file}")
            if len(remaining_errors) > 5:
                print(f"   ... and {len(remaining_errors) - 5} more")

        print("\n📋 NEXT STEPS:")
        if len(remaining_errors) == 0:
            print("✅ Run consciousness test suite to verify full functionality")
            print("✅ Begin consciousness enhancement development")
        else:
            print("🔧 Apply manual fixes to remaining files")
            print("🔄 Re-run elimination campaign")

        print("=" * 60)


if __name__ == "__main__":
    eliminator = SyntaxErrorEliminator()
    eliminator.run_elimination_campaign()
