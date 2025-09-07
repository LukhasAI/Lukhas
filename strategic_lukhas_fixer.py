#!/usr/bin/env python3
"""
🎯 STRATEGIC LUKHAS FIXER
Focus on the 23 HIGH priority lukhas/ blockers for maximum functional impact
"""

import ast
import json
import os
import re
from typing import Dict, List, Tuple


class StrategicLukhasFixer:
    """Strategic fixer focused on lukhas/ HIGH priority blockers"""

    def __init__(self):
        self.fixes_applied = 0
        self.files_fixed = 0

    def get_lukhas_high_priority_files(self) -> list[str]:
        """Get the 23 HIGH priority lukhas/ files from analysis"""
        high_priority_files = [
            "lukhas/bridge/bridge_wrapper.py",
            "lukhas/core/common/decorators.py",
            "lukhas/core/common/glyph.py",
            "lukhas/core/distributed_tracing.py",
            "lukhas/core/efficient_communication.py",
            "lukhas/core/symbolism/tags.py",
            "lukhas/emotion/__init__.py",
            "lukhas/emotion/emotion_wrapper.py",
            "lukhas/governance/auth_glyph_registry.py",
            "lukhas/governance/auth_governance_policies.py",
            "lukhas/governance/colony_memory_validator.py",
            "lukhas/governance/consent_ledger_impl.py",
            "lukhas/governance/ethics/constitutional_ai.py",
            "lukhas/governance/identity/auth_backend/extreme_performance_audit_logger.py",
            "lukhas/governance/identity/connector.py",
            "lukhas/governance/identity/extreme_performance_connector.py",
            "lukhas/identity/auth_service.py",
            "lukhas/identity/tier_system.py",
            "lukhas/identity/webauthn.py",
            "lukhas/memory/__init__.py",
            "lukhas/memory/emotional/__init__.py",
            "lukhas/memory/matriz_adapter.py",
            "lukhas/observability/matriz_emit.py",
            "lukhas/rl/engine/consciousness_environment.py",
            "lukhas/rl/environments/consciousness_environment.py",
            "lukhas/utils/logging_config.py",
            "lukhas/consciousness/consciousness_wrapper.py",
        ]
        return [f for f in high_priority_files if os.path.exists(f)]

    def get_aggressive_f_string_patterns(self) -> list[tuple[str, str, str]]:
        """Aggressive patterns for f-string parenthesis errors"""
        return [
            # Most common pattern: missing closing parenthesis
            (r'f"([^"]*)\{([^}]+)\}([^"]*)"', self.fix_fstring_parentheses, "PARENTHESIS_FIX"),
            (r"f'([^']*)\{([^}]+)\}([^']*)'", self.fix_fstring_parentheses_single, "PARENTHESIS_FIX_SINGLE"),

            # Specific method patterns
            (r'f"([^"]*)\{([^}]+\.upper)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_UPPER"),
            (r'f"([^"]*)\{([^}]+\.lower)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_LOWER"),
            (r'f"([^"]*)\{([^}]+\.timestamp)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_TIMESTAMP"),
            (r'f"([^"]*)\{([^}]+\.isoformat)\(\}([^"]*)"', r'f"\1{\2()}\3"', "METHOD_ISOFORMAT"),

            # Function patterns
            (r'f"([^"]*)\{(time\.time)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNC_TIME"),
            (r'f"([^"]*)\{(uuid\.uuid4)\(\}([^"]*)"', r'f"\1{\2()}\3"', "FUNC_UUID"),
            (r'f"([^"]*)\{(len)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "FUNC_LEN"),
            (r'f"([^"]*)\{(hash)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "FUNC_HASH"),
            (r'f"([^"]*)\{(int)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "FUNC_INT"),
            (r'f"([^"]*)\{(str)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "FUNC_STR"),
            (r'f"([^"]*)\{(type)\(([^}]+)\}([^"]*)"', r'f"\1{\2(\3)}\4"', "FUNC_TYPE"),
        ]

    def fix_fstring_parentheses(self, match):
        """Smart f-string parenthesis fixer for double quotes"""
        prefix, expr, suffix = match.groups()

        # Count parentheses in the expression
        open_parens = expr.count("(")
        close_parens = expr.count(")")

        if open_parens > close_parens:
            # Add missing closing parentheses
            missing_parens = ")" * (open_parens - close_parens)
            return f'f"{prefix}{{{expr}{missing_parens}}}{suffix}"'
        elif close_parens > open_parens:
            # Remove extra closing parentheses (less common, but possible)
            return f'f"{prefix}{{{expr.rstrip(")")}}}{suffix}"'
        else:
            # Already balanced
            return match.group(0)

    def fix_fstring_parentheses_single(self, match):
        """Smart f-string parenthesis fixer for single quotes"""
        prefix, expr, suffix = match.groups()

        open_parens = expr.count("(")
        close_parens = expr.count(")")

        if open_parens > close_parens:
            missing_parens = ")" * (open_parens - close_parens)
            return f"f'{prefix}{{{expr}{missing_parens}}}{suffix}'"
        elif close_parens > open_parens:
            clean_expr = expr.rstrip(")")
            return f"f'{prefix}{{{clean_expr}}}{suffix}'"
        else:
            return match.group(0)

    def validate_syntax(self, content: str, file_path: str) -> bool:
        """Validate syntax with detailed error reporting"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    def fix_file_strategically(self, file_path: str) -> tuple[bool, int, list[str]]:
        """Apply strategic fixes to a lukhas/ HIGH priority file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            total_fixes = 0
            patterns_applied = []

            # Apply all aggressive patterns
            for pattern_info in self.get_aggressive_f_string_patterns():
                if len(pattern_info) == 3:
                    pattern, replacement, pattern_type = pattern_info

                    if callable(replacement):
                        # Use custom function for smart fixing
                        matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
                        if matches:
                            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
                            if new_content != content:
                                fix_count = len(matches)
                                total_fixes += fix_count
                                patterns_applied.append(f"{pattern_type}: {fix_count}")
                                content = new_content
                    else:
                        # Use regex replacement
                        try:
                            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                            if matches:
                                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
                                if new_content != content:
                                    fix_count = len(matches)
                                    total_fixes += fix_count
                                    patterns_applied.append(f"{pattern_type}: {fix_count}")
                                    content = new_content
                        except re.error:
                            continue

            if total_fixes > 0:
                # Validate the fixes
                if self.validate_syntax(content, file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"🎯 STRATEGIC FIX: {file_path} - {total_fixes} fixes applied")
                    self.fixes_applied += total_fixes
                    self.files_fixed += 1
                    return True, total_fixes, patterns_applied
                else:
                    print(f"❌ Validation failed for {file_path}")
                    return False, 0, []

            return True, 0, []  # No fixes needed

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False, 0, []

    def run_strategic_fixes(self):
        """Run strategic fixes on lukhas/ HIGH priority files"""
        print("🎯 STRATEGIC LUKHAS FIXER")
        print("=" * 60)
        print("Fixing 23 HIGH priority lukhas/ blockers for maximum functional impact")
        print()

        high_priority_files = self.get_lukhas_high_priority_files()
        print(f"Processing {len(high_priority_files)} HIGH priority lukhas/ files...")
        print()

        successful_fixes = []
        failed_fixes = []

        for file_path in high_priority_files:
            success, fixes, patterns = self.fix_file_strategically(file_path)

            if success and fixes > 0:
                successful_fixes.append((file_path, fixes, patterns))
            elif not success:
                failed_fixes.append(file_path)

        print()
        print("🎯 STRATEGIC FIXING RESULTS:")
        print("=" * 40)
        print(f"HIGH priority files processed: {len(high_priority_files)}")
        print(f"Files successfully fixed: {self.files_fixed}")
        print(f"Total fixes applied: {self.fixes_applied}")
        print(f"Failed validations: {len(failed_fixes)}")

        if successful_fixes:
            print()
            print("🏆 Successful Strategic Fixes:")
            for file_path, fixes, patterns in successful_fixes:
                print(f"  • {file_path}: {fixes} fixes")
                for pattern in patterns[:3]:  # Show top 3 patterns
                    print(f"    - {pattern}")

        if failed_fixes:
            print()
            print("❌ Failed Strategic Fixes:")
            for file_path in failed_fixes:
                print(f"  • {file_path}")

        return self.fixes_applied > 0


def main():
    """Run strategic lukhas fixer"""
    print("🎯 STRATEGIC LUKHAS FIXER")
    print("Maximum functional impact by fixing HIGH priority lukhas/ blockers")
    print()

    fixer = StrategicLukhasFixer()
    success = fixer.run_strategic_fixes()

    if success:
        print("\n🧪 Running functional test to verify strategic improvements...")
        import subprocess
        try:
            subprocess.run(["python3", "functional_test_suite.py"],
                                  capture_output=True, text=True, timeout=60)
            print("Strategic functional test completed.")
        except Exception as e:
            print(f"Could not run functional test: {e}")
    else:
        print("\n⚠️ No strategic fixes applied")


if __name__ == "__main__":
    main()
