#!/usr/bin/env python3
"""
Safe Batch F-String Syntax Fixer for LUKHAS

Fixes common f-string syntax errors in a safe, batched approach:
1. f"text-{uuid.uuid4()}.hex}" → f"text-{uuid.uuid4().hex}"
2. f"text {var}" → f"text {var}"
3. Missing closing braces in f-strings

Safety measures:
- Dry-run mode by default
- File-by-file processing with validation
- Backup creation
- Pattern-specific fixes only
- Preserves git history
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SafeFStringFixer:
    def __init__(self, dry_run: bool = True, create_backups: bool = True):
        self.dry_run = dry_run
        self.create_backups = create_backups
        self.fixes_applied = []

        # Safe patterns to fix (order matters - most specific first)
        self.patterns = [
            # Pattern 1: uuid.uuid4()}.hex} → uuid.uuid4().hex
            (r"(\buuid\.uuid4\(\))\.hex\}", r"\1.hex", "Fix uuid.hex brace mismatch"),
            # Pattern 2: time.time()}  → time.time())
            (r"(\btime\.time\(\))\}", r"\1)", "Fix time.time() brace mismatch"),
            # Pattern 3: Double closing braces }} → }
            (r'([^{}\s])\}\}(["\'])', r"\1}\2", "Fix double closing braces in f-strings"),
            # Pattern 4: Missing closing parenthesis in f-strings
            (r'(\{[^}]*\([^}]*)\}(["\'])', r"\1)}\2", "Fix missing closing parenthesis in f-strings"),
        ]

    def find_python_files(self, root_dir: str) -> list[Path]:
        """Find all Python files, excluding virtual environments."""
        exclude_patterns = [".venv", ".cleanenv", "__pycache__", ".git", "node_modules", ".pytest_cache", ".mypy_cache"]

        python_files = []
        for root, dirs, files in os.walk(root_dir):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return python_files

    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        shutil.copy2(file_path, backup_path)
        return backup_path

    def validate_syntax(self, file_path: Path) -> bool:
        """Validate Python syntax of file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            compile(content, str(file_path), "exec")
            return True
        except SyntaxError:
            return False
        except Exception:
            # Other errors (encoding, etc.) - be conservative
            return False

    def fix_file(self, file_path: Path) -> tuple[bool, list[str], str]:
        """Fix f-string patterns in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            fixes = []

            # Apply each pattern
            for pattern, replacement, description in self.patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    fixes.append(f"{description}: {len(matches)} fixes")

            if not fixes:
                return False, [], "No fixes needed"

            # Validate syntax after fixes
            try:
                compile(content, str(file_path), "exec")
            except SyntaxError as e:
                return False, fixes, f"Syntax error after fixes: {e}"

            if not self.dry_run:
                # Create backup if requested
                if self.create_backups:
                    self.backup_file(file_path)

                # Write fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            return True, fixes, "Success"

        except Exception as e:
            return False, [], f"Error processing file: {e}"

    def process_files(self, files: list[Path], batch_size: int = 50) -> dict:
        """Process files in batches."""
        results = {"total_files": len(files), "processed": 0, "fixed": 0, "failed": 0, "fixes": []}

        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1}: files {i+1}-{min(i+batch_size, len(files))}")

            for file_path in batch:
                try:
                    # Skip files that already have syntax errors
                    if not self.validate_syntax(file_path):
                        print(f"⚠️  Skipping {file_path}: Pre-existing syntax errors")
                        results["failed"] += 1
                        continue

                    success, fixes, message = self.fix_file(file_path)
                    results["processed"] += 1

                    if success and fixes:
                        results["fixed"] += 1
                        results["fixes"].append({"file": str(file_path), "fixes": fixes})
                        status = "✅" if not self.dry_run else "🔍"
                        print(f"{status} {file_path}: {'; '.join(fixes)}")

                    elif not success:
                        results["failed"] += 1
                        print(f"❌ {file_path}: {message}")

                except KeyboardInterrupt:
                    print("\n⚠️  Process interrupted by user")
                    return results
                except Exception as e:
                    print(f"❌ {file_path}: Unexpected error: {e}")
                    results["failed"] += 1

        return results

    def run_batch_fix(self, root_dir: str = ".", file_patterns: Optional[list[str]] = None, batch_size: int = 50):
        """Run the batch fixing process."""
        print("🔧 LUKHAS F-String Batch Fixer")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE FIX'}")
        print(f"Root directory: {root_dir}")
        print(f"Backup files: {self.create_backups}")

        # Find files
        if file_patterns:
            files = []
            for pattern in file_patterns:
                files.extend(Path(root_dir).glob(pattern))
        else:
            files = self.find_python_files(root_dir)

        print(f"Found {len(files)} Python files")

        if not files:
            print("No files to process")
            return

        # Process files
        results = self.process_files(files, batch_size)

        # Summary
        print("\n📊 Summary:")
        print(f"   Total files: {results['total_files']}")
        print(f"   Processed: {results['processed']}")
        print(f"   Fixed: {results['fixed']}")
        print(f"   Failed: {results['failed']}")

        if results["fixes"]:
            print("\n🔧 Fixes applied:")
            for fix in results["fixes"][:10]:  # Show first 10
                print(f"   {fix['file']}: {len(fix['fixes'])} fixes")
            if len(results["fixes"]) > 10:
                print(f"   ... and {len(results['fixes']) - 10} more files")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Safe batch f-string syntax fixer for LUKHAS")
    parser.add_argument("--live", action="store_true", help="Apply fixes (default is dry-run)")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup files")
    parser.add_argument("--batch-size", type=int, default=50, help="Files per batch")
    parser.add_argument("--dir", default=".", help="Root directory to process")
    parser.add_argument("--files", nargs="*", help="Specific file patterns to fix")

    args = parser.parse_args()

    fixer = SafeFStringFixer(dry_run=not args.live, create_backups=not args.no_backup)

    fixer.run_batch_fix(root_dir=args.dir, file_patterns=args.files, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
