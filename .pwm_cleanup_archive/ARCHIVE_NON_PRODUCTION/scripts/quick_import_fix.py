#!/usr/bin/env python3
"""
Quick targeted import fix focusing on known patterns
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QuickImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixed_files = 0
        self.total_fixes = 0

        # Known problematic patterns from our analysis
        self.import_patterns = {
            # Remove lukhas prefix
            r"from lukhas\.(\w+)": r"from \1",
            r"import lukhas\.(\w+)": r"import \1",
            # Common renames we know about
            r"from core\.memory\.memory_fold": "from features.memory.memory_fold",
            r"from bio\.hippocampus\.": "from bio.",
            r"from memory\.episodic\.": "from memory.",
            r"from quantum\.quantum_": "from quantum.",
            # Remove redundant paths
            r"from (\w+)\.(\w+)\.\2": r"from \1.\2",  # e.g., bio.hippocampus.hippocampus -> bio.hippocampus
        }

    def run(self):
        """Run quick import fixes"""
        logger.info("=" * 80)
        logger.info("Quick Import Fixer - Targeted Approach")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Process Python files
        py_files = list(self.root_path.rglob("*.py"))
        logger.info(f"Processing {len(py_files)} Python files...")

        for i, py_file in enumerate(py_files):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(py_files)} files")

            if self._should_skip(py_file):
                continue

            self._fix_file(py_file)

        # Report results
        logger.info("\n" + "=" * 80)
        logger.info("RESULTS")
        logger.info("=" * 80)
        logger.info(f"Files modified: {self.fixed_files}")
        logger.info(f"Total import fixes: {self.total_fixes}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_file(self, file_path: Path):
        """Fix imports in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_fixes = 0

            # Apply each pattern
            for pattern, replacement in self.import_patterns.items():
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    file_fixes += count

            # Check for any imports that still have issues
            # Fix common patterns like "from x.y.Z import Z" where Z is the class
            content = self._fix_class_imports(content)

            # If content changed, save it
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                self.fixed_files += 1
                self.total_fixes += file_fixes

                relative_path = file_path.relative_to(self.root_path)
                logger.debug(f"Fixed {file_fixes} imports in {relative_path}")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def _fix_class_imports(self, content: str) -> str:
        """Fix imports where the module was renamed to match the class"""
        # Pattern: from x.y.some_module import SomeClass
        # Where some_module.py was renamed to SomeClass.py

        import_regex = r"from\s+([\w.]+)\.(\w+)\s+import\s+(\w+)"

        def fix_import(match):
            base_path = match.group(1)
            module_name = match.group(2)
            class_name = match.group(3)

            # Check if module name is snake_case version of class name
            if module_name == self._to_snake_case(class_name):
                # The file was likely renamed from snake_case to PascalCase
                return f"from {base_path}.{class_name} import {class_name}"

            return match.group(0)  # No change

        return re.sub(import_regex, fix_import, content)

    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        # Handle acronyms and numbers
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        skip_dirs = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "env",
            "build",
            "dist",
            "node_modules",
            ".pytest_cache",
            "visualizations",
            "analysis_output",
        }

        return any(part in skip_dirs for part in path.parts)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Quick targeted import fixes")
    parser.add_argument(
        "path", nargs="?", default=".", help="Root path (default: current directory)"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = QuickImportFixer(root_path, dry_run=not args.fix)
    fixer.run()


if __name__ == "__main__":
    main()
