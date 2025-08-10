#!/usr/bin/env python3
"""
Fix syntax errors in recently updated files
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SyntaxErrorFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.files_fixed = 0

    def fix_syntax_errors(self):
        """Fix known syntax errors"""
        logger.info("Fixing syntax errors...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Fix specific files with known issues
        fixes = {
            "demo_documentation_update.py": [
                ("from pathlib from pathlib import Path", "from pathlib import Path")
            ],
            "memory_system_demo.py": [
                (
                    "from memory.systems.hybrid_memory_fold from memory.systems.hybrid_memory_fold import create_hybrid_memory_fold",
                    "from memory.systems.hybrid_memory_fold import create_hybrid_memory_fold",
                ),
                (
                    "from memory.systems.attention_memory_layer from memory.systems.attention_memory_layer import create_attention_orchestrator",
                    "from memory.systems.attention_memory_layer import create_attention_orchestrator",
                ),
                (
                    "from memory.structural_conscience from memory.structural_conscience import create_structural_conscience",
                    "from memory.structural_conscience import create_structural_conscience",
                ),
            ],
        }

        for filename, replacements in fixes.items():
            file_path = self.root_path / filename
            if file_path.exists():
                self._fix_file(file_path, replacements)

        logger.info(f"\nFixed {self.files_fixed} files")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_file(self, file_path: Path, replacements: list):
        """Fix a specific file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            for old, new in replacements:
                content = content.replace(old, new)

            if content != original_content:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                self.files_fixed += 1
                logger.info(f"Fixed {file_path.name}")

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix syntax errors in Python files")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = SyntaxErrorFixer(root_path, dry_run=not args.fix)
    fixer.fix_syntax_errors()


if __name__ == "__main__":
    main()
