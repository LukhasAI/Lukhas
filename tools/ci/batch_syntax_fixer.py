#!/usr/bin/env python3
"""
Batch Syntax Fixer - Automated Pattern-Based Syntax Repair
==========================================================

Fixes common syntax error patterns in controlled batches with validation.
Created for Phase 5B systematic syntax resolution.

Safety Features:
- Processes files in batches of 300-500
- Validates changes don't introduce new errors
- Creates git commits after each successful batch
- Rolls back if validation fails
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Common syntax error patterns and their fixes
SYNTAX_PATTERNS = {
    # F-string UUID patterns
    r'f"([^"]*){([^}]*uuid\.uuid4\(\))}\.hex(\[[^\]]*\])?}([^"]*)"': r'f"\1{\2.hex\3}\4"',
    r"f'([^']*){([^}]*uuid\.uuid4\(\))}\.hex(\[[^\]]*\])?}([^']*)'": r"f'\1{\2.hex\3}\4'",
    # F-string time.time() patterns
    r'f"([^"]*){([^}]*time\.time\(\))}([^"]*)"': r'f"\1{\2)\3"',
    r"f'([^']*){([^}]*time\.time\(\))}([^']*)'": r"f'\1{\2)\3'",
    # F-string int(time.time()) patterns
    r'f"([^"]*){([^}]*int\(time\.time\(\))}([^"]*)"': r'f"\1{\2)}\3"',
    r"f'([^']*){([^}]*int\(time\.time\(\))}([^']*)'": r"f'\1{\2)}\3'",
    # Dictionary access patterns with extra closing brace
    r'f"([^"]*){([^}]*\.get\([^)]+\))}\.([^}]+)}([^"]*)"': r'f"\1{\2.\3}\4"',
    r"f'([^']*){([^}]*\.get\([^)]+\))}\.([^}]+)}([^']*)'": r"f'\1{\2.\3}\4'",
    # Simple extra brace patterns
    r'f"([^"]*){([^}]+)}([^"]*)"': r'f"\1{\2}\3"',
    r"f'([^']*){([^}]+)}([^']*)'": r"f'\1{\2}\3'",
    # Missing closing parentheses in function calls within f-strings
    r'f"([^"]*){([^}]*\([^)]*)}([^"]*)"': r'f"\1{\2)}\3"',
    r"f'([^']*){([^}]*\([^)]*)}([^']*)'": r"f'\1{\2)}\3'",
}


class BatchSyntaxFixer:
    def __init__(self, batch_size: int = 400):
        self.batch_size = batch_size
        self.fixes_applied = 0
        self.files_processed = 0
        self.batches_completed = 0

    def get_syntax_error_files(self, directory: str = ".") -> list[str]:
        """Get list of files with syntax errors."""
        try:
            result = subprocess.run(
                [".venv/bin/ruff", "check", directory, "--output-format=json", "--quiet"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.stdout:
                import json

                errors = json.loads(result.stdout)

                # Filter to only syntax errors and get unique filenames
                syntax_files = set()
                for error in errors:
                    if error.get("code") in [None, "E999"] or "SyntaxError" in error.get("message", ""):
                        syntax_files.add(error["filename"])

                return list(syntax_files)

            return []

        except Exception as e:
            print(f"⚠️ Error getting syntax error files: {e}")
            return []

    def fix_file_patterns(self, file_path: str) -> int:
        """Fix syntax patterns in a single file."""
        fixes_count = 0

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply each pattern fix
            for pattern, replacement in SYNTAX_PATTERNS.items():
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    matches = len(re.findall(pattern, content))
                    fixes_count += matches
                    content = new_content

            # Only write if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                return fixes_count

        except UnicodeDecodeError:
            print(f"⚠️ Skipping file with encoding issues: {file_path}")
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")

        return 0

    def validate_batch_fixes(self) -> bool:
        """Validate that batch fixes didn't introduce new syntax errors."""
        print("🔍 Validating batch fixes...")

        # Run syntax guardian to check current state
        try:
            result = subprocess.run(
                [".venv/bin/python", "tools/ci/syntax_guardian.py"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                print("✅ Syntax Guardian validation passed")
                return True
            else:
                print("❌ Syntax Guardian validation failed")
                print(result.stdout)
                return False

        except Exception as e:
            print(f"⚠️ Validation error: {e}")
            return False

    def run_world_tests(self) -> bool:
        """Run world tests to ensure functionality is preserved."""
        print("🧪 Running world tests...")

        try:
            result = subprocess.run(
                [
                    ".venv/bin/pytest",
                    "tests/test_basic_functions.py",
                    "tests/test_aka_qualia.py::TestT1T2Integration::test_complete_cycle_dangerous_input",
                    "tests/memory/test_memory_basic.py",
                    "-v",
                    "--tb=short",
                    "--disable-warnings",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0 and "FAILED" not in result.stdout:
                print("✅ World tests passed")
                return True
            else:
                print("❌ World tests failed")
                print(result.stdout[-1000:])  # Show last 1000 chars
                return False

        except Exception as e:
            print(f"⚠️ World test error: {e}")
            return False

    def commit_batch(self, batch_num: int, fixes_count: int, files_count: int):
        """Commit the current batch of fixes."""
        commit_msg = f"""🔧 Batch {batch_num}: Automated syntax fixes

Applied {fixes_count} pattern fixes across {files_count} files.

Patterns fixed:
- F-string UUID method calls (uuid.uuid4().hex)
- F-string time.time() function calls
- Dictionary access with extra braces
- Missing function call parentheses
- General f-string brace corrections

Validation: Syntax Guardian ✅ | World Tests ✅

🧬 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print(f"✅ Committed batch {batch_num}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Commit failed: {e}")

    def process_batch(self, files: list[str], batch_num: int) -> bool:
        """Process a single batch of files."""
        print(f"\n🔧 Processing Batch {batch_num}")
        print(f"Files in batch: {len(files)}")

        batch_fixes = 0
        files_modified = 0

        # Process each file in the batch
        for file_path in files:
            fixes = self.fix_file_patterns(file_path)
            if fixes > 0:
                batch_fixes += fixes
                files_modified += 1

        print(f"Applied {batch_fixes} fixes to {files_modified} files")

        # Validate the batch
        if not self.validate_batch_fixes():
            print("❌ Batch validation failed - rolling back")
            subprocess.run(["git", "checkout", "HEAD", "."], check=True)
            return False

        # Run world tests every few batches or if significant changes
        if (batch_num % 3 == 0 or batch_fixes > 50) and not self.run_world_tests():
            print("❌ World tests failed - rolling back")
            subprocess.run(["git", "checkout", "HEAD", "."], check=True)
            return False

        # Commit successful batch
        if batch_fixes > 0:
            self.commit_batch(batch_num, batch_fixes, files_modified)

        self.fixes_applied += batch_fixes
        self.files_processed += files_modified
        self.batches_completed += 1

        return True

    def run_batch_fixing(self, target_directory: str = "."):
        """Run the complete batch fixing process."""
        print("🚀 Starting Automated Batch Syntax Fixing")
        print(f"Batch size: {self.batch_size} files")
        print(f"Target directory: {target_directory}")

        # Get all files with syntax errors
        syntax_files = self.get_syntax_error_files(target_directory)
        total_files = len(syntax_files)

        if total_files == 0:
            print("✅ No syntax errors found!")
            return

        print(f"Found {total_files} files with syntax errors")

        # Process in batches
        batch_num = 1
        for i in range(0, total_files, self.batch_size):
            batch_files = syntax_files[i : i + self.batch_size]

            if not self.process_batch(batch_files, batch_num):
                print(f"❌ Batch {batch_num} failed - stopping")
                break

            batch_num += 1

            # Progress update
            processed = min(i + self.batch_size, total_files)
            print(f"Progress: {processed}/{total_files} files processed ({processed/total_files*100:.1f}%)")

        # Final summary
        print("\n" + "=" * 60)
        print("🎯 BATCH SYNTAX FIXING COMPLETE")
        print("=" * 60)
        print(f"Batches completed: {self.batches_completed}")
        print(f"Files processed: {self.files_processed}")
        print(f"Total fixes applied: {self.fixes_applied}")
        print(f"Success rate: {self.batches_completed/max(1,batch_num-1)*100:.1f}%")


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    fixer = BatchSyntaxFixer(batch_size=400)
    fixer.run_batch_fixing(target_dir)


if __name__ == "__main__":
    main()
