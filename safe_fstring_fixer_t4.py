#!/usr/bin/env python3
"""
🛡️ T4 SAFE F-STRING FIXER WITH VALIDATION SAFEGUARDS
Surgical fixes with pre/post validation to prevent cascading errors
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class SafeFStringFixer:
    """T4-style safe fixer with comprehensive validation"""

    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        self.validation_failures = 0
        self.backup_created = {}

    def validate_syntax(self, content: str, file_path: str) -> bool:
        """Pre/post validation to ensure syntax correctness"""
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            print(f"❌ Syntax validation failed for {file_path}: {e}")
            return False

    def create_backup(self, file_path: str, content: str):
        """Create backup before modification"""
        self.backup_created[file_path] = content

    def restore_backup(self, file_path: str):
        """Restore from backup if validation fails"""
        if file_path in self.backup_created:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.backup_created[file_path])
            print(f"🔄 Restored backup for {file_path}")

    def safe_fix_fstring_parentheses(self, content: str) -> tuple[str, int]:
        """Safe f-string parenthesis fixes with specific patterns"""
        fixes_count = 0

        # SAFE PATTERN 1: Missing closing parenthesis after function calls
        patterns = [
            # time.time() pattern
            (r'f"([^"]*)\{([^}]*time\.time)\(\}([^"]*)"', r'f"\1{\2()}\3"'),
            # uuid.uuid4() pattern
            (r'f"([^"]*)\{([^}]*uuid\.uuid4)\(\}([^"]*)"', r'f"\1{\2()}\3"'),
            # len() pattern
            (r'f"([^"]*)\{len\(([^}]+)\}([^"]*)"', r'f"\1{len(\2)}\3"'),
            # hash() pattern
            (r'f"([^"]*)\{hash\(([^}]+)\}([^"]*)"', r'f"\1{hash(\2)}\3"'),
            # int() pattern
            (r'f"([^"]*)\{int\(([^}]+)\}([^"]*)"', r'f"\1{int(\2)}\3"'),
            # str() pattern
            (r'f"([^"]*)\{str\(([^}]+)\}([^"]*)"', r'f"\1{str(\2)}\3"'),
            # .upper() pattern
            (r'f"([^"]*)\{([^}]+)\.upper\(\}([^"]*)"', r'f"\1{\2.upper()}\3"'),
            # .timestamp() pattern
            (r'f"([^"]*)\{([^}]+)\.timestamp\(\}([^"]*)"', r'f"\1{\2.timestamp()}\3"'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                fixes_count += len(re.findall(pattern, content))
                content = new_content

        return content, fixes_count

    def process_file(self, file_path: str) -> bool:
        """Process single file with full validation pipeline"""
        try:
            # Read original content
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Pre-validation: Skip if already has syntax errors we can't fix
            if not self.validate_syntax(original_content, file_path):
                return False

            # Create backup
            self.create_backup(file_path, original_content)

            # Apply safe fixes
            fixed_content, fixes_count = self.safe_fix_fstring_parentheses(original_content)

            # Skip if no fixes needed
            if fixes_count == 0:
                return True

            # Post-validation: Ensure fixes didn't break syntax
            if not self.validate_syntax(fixed_content, file_path):
                self.validation_failures += 1
                print(f"⚠️  Post-validation failed for {file_path}, skipping")
                return False

            # Write fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            self.fixes_applied += fixes_count
            print(f"✅ {file_path}: Applied {fixes_count} safe fixes")
            return True

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            self.restore_backup(file_path)
            return False

    def get_priority_files(self) -> list[str]:
        """Get files prioritized by impact on functionality"""
        priority_patterns = [
            "**/consciousness_wrapper.py",
            "**/matriz_adapter.py",
            "**/matriz_emit.py",
            "products/__init__.py",
            "business/__init__.py",
            "security/__init__.py",
            "**/actor_system.py",
            "lukhas/**/__init__.py",
        ]

        priority_files = []
        for pattern in priority_patterns:
            files = list(Path(".").glob(pattern))
            priority_files.extend([str(f) for f in files])

        return list(set(priority_files))  # Remove duplicates

    def run_safe_fixes(self, max_files: int = 50):
        """Run safe fixes on priority files with limits"""
        print("🛡️ T4 SAFE F-STRING FIXER")
        print("=" * 50)
        print("Safe fixes with pre/post validation safeguards")
        print()

        priority_files = self.get_priority_files()
        print(f"🎯 Processing {min(len(priority_files), max_files} priority files")
        print()

        success_count = 0
        for _i, file_path in enumerate(priority_files[:max_files]):
            if self.process_file(file_path):
                success_count += 1
            self.files_processed += 1

        print()
        print("📊 T4 SAFE FIXING RESULTS:")
        print("=" * 30)
        print(f"Files processed: {self.files_processed}")
        print(f"Files successfully fixed: {success_count}")
        print(f"Total fixes applied: {self.fixes_applied}")
        print(f"Validation failures: {self.validation_failures}")
        print(f"Success rate: {(success_count/self.files_processed*100}:.1f}%")

        return success_count > 0


def main():
    """Run T4 safe f-string fixes"""
    fixer = SafeFStringFixer()
    success = fixer.run_safe_fixes(max_files=30)  # Conservative limit

    if success:
        print("\n✅ Safe fixes completed successfully!")
        print("🧪 Recommend running functional tests to verify improvements")
    else:
        print("\n⚠️ No fixes applied - files may need manual intervention")


if __name__ == "__main__":
    main()
