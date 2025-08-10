#!/usr/bin/env python3
"""
Fix remaining specific import issues
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RemainingImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

    def fix_imports(self):
        """Fix remaining import issues"""
        logger.info("Fixing remaining import issues...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Fix bio.orchestration imports
        self._fix_bio_orchestration()

        # Fix core.memory remaining issues
        self._fix_core_memory_remaining()

        # Fix single imports
        self._fix_single_imports()

        # Report
        logger.info(f"\nTotal fixes applied: {self.fixes_applied}")
        logger.info(f"Files fixed: {self.files_fixed}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_bio_orchestration(self):
        """Fix bio.orchestration imports"""
        logger.info("\nFixing bio.orchestration imports...")

        mappings = {
            "from bio.orchestration.bio_orchestrator": "from bio.systems.orchestration.bio_orchestrator",
            "from bio.orchestration.base_orchestrator": "from bio.systems.orchestration.base_orchestrator",
            "from bio.orchestration.": "from bio.systems.orchestration.",
        }

        self._apply_fixes(mappings)

    def _fix_core_memory_remaining(self):
        """Fix remaining core.memory imports"""
        logger.info("\nFixing remaining core.memory imports...")

        mappings = {
            "from core.memory.dream_memory_fold": "from memory.systems.dream_memory_fold",
            "from core.memory_learning.memory_manager": "from memory.systems.memory_learning.memory_manager",
            "from core.memory.": "from memory.",
        }

        self._apply_fixes(mappings)

    def _fix_single_imports(self):
        """Fix single import statements"""
        logger.info("\nFixing single import statements...")

        specific_files = {
            "demo_documentation_update.py": [
                ("import Path", "from pathlib import Path")
            ],
            "memory_system_demo.py": [
                (
                    "import create_hybrid_memory_fold",
                    "from memory.systems.hybrid_memory_fold import create_hybrid_memory_fold",
                ),
                (
                    "import create_attention_orchestrator",
                    "from memory.systems.attention_memory_layer import create_attention_orchestrator",
                ),
                (
                    "import create_structural_conscience",
                    "from memory.structural_conscience import create_structural_conscience",
                ),
            ],
        }

        for filename, fixes in specific_files.items():
            file_path = self.root_path / filename
            if file_path.exists():
                self._fix_specific_file(file_path, fixes)

    def _fix_specific_file(self, file_path: Path, fixes: list):
        """Apply specific fixes to a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            for old, new in fixes:
                content = content.replace(old, new)

            if content != original_content:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                self.files_fixed += 1
                self.fixes_applied += len(fixes)
                logger.info(f"Fixed {file_path.name}")

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")

    def _apply_fixes(self, mappings: dict):
        """Apply import mappings to all Python files"""
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                file_fixes = 0

                for old_pattern, new_pattern in mappings.items():
                    count = content.count(old_pattern)
                    if count > 0:
                        content = content.replace(old_pattern, new_pattern)
                        file_fixes += count

                if content != original_content:
                    if not self.dry_run:
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(content)

                    self.files_fixed += 1
                    self.fixes_applied += file_fixes

                    relative_path = py_file.relative_to(self.root_path)
                    logger.debug(f"Fixed {file_fixes} imports in {relative_path}")

            except Exception as e:
                if "utf-8" not in str(e):
                    logger.error(f"Error processing {py_file}: {e}")

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
            "scripts",
        }

        return any(part in skip_dirs for part in path.parts)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix remaining import issues")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = RemainingImportFixer(root_path, dry_run=not args.fix)
    fixer.fix_imports()


if __name__ == "__main__":
    main()
