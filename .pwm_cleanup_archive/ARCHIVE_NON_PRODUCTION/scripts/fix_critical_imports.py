#!/usr/bin/env python3
"""
Fix critical imports in a targeted way
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CriticalImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

        # Critical import fixes based on our analysis
        self.critical_fixes = {
            # Fix core.memory imports
            "from core.memory.memory_fold": "from memory.systems.memory_fold",
            "from core.memory.fold_engine": "from memory.fold_engine",
            "import core.memory.": "import memory.",
            # Fix bio nested imports
            "from bio.awareness.": "from bio.",
            "from bio.systems.oscillator.": "from bio.",
            "from bio.systems.": "from bio.",
            # Remove lukhas prefix
            "from lukhas.": "from ",
            "import lukhas.": "import ",
            # Fix common missing imports
            r"\nimport Path\n": "\nfrom pathlib import Path\n",
            r"\nimport create_hybrid_memory_fold\n": "\nfrom memory.systems.hybrid_memory_fold import create_hybrid_memory_fold\n",
            r"\nimport create_attention_orchestrator\n": "\nfrom memory.systems.attention_memory_layer import create_attention_orchestrator\n",
            r"\nimport create_structural_conscience\n": "\nfrom memory.structural_conscience import create_structural_conscience\n",
        }

    def fix_imports(self):
        """Fix critical imports across the codebase"""
        logger.info("Starting critical import fixes...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Process Python files
        py_files = list(self.root_path.rglob("*.py"))
        total_files = len(py_files)

        for i, py_file in enumerate(py_files):
            if i % 100 == 0:
                logger.info(
                    f"Progress: {i}/{total_files} files ({i/total_files*100:.1f}%)"
                )

            if self._should_skip(py_file):
                continue

            self._fix_file(py_file)

        # Final report
        logger.info("\n" + "=" * 80)
        logger.info("CRITICAL IMPORT FIX SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Files processed: {total_files}")
        logger.info(f"Files fixed: {self.files_fixed}")
        logger.info(f"Total fixes applied: {self.fixes_applied}")

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

            # Apply critical fixes
            for pattern, replacement in self.critical_fixes.items():
                if pattern.startswith(r"\n"):
                    # Regex pattern
                    new_content, count = re.subn(
                        pattern, replacement, content, flags=re.MULTILINE
                    )
                else:
                    # Simple string replacement
                    count = content.count(pattern)
                    new_content = content.replace(pattern, replacement)

                if count > 0:
                    content = new_content
                    file_fixes += count

            # If content changed, save it
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                self.files_fixed += 1
                self.fixes_applied += file_fixes

                relative_path = file_path.relative_to(self.root_path)
                logger.debug(f"Fixed {file_fixes} imports in {relative_path}")

        except Exception as e:
            if "utf-8" not in str(e):
                logger.error(f"Error fixing {file_path}: {e}")

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

    parser = argparse.ArgumentParser(description="Fix critical imports in Python files")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = CriticalImportFixer(root_path, dry_run=not args.fix)
    fixer.fix_imports()


if __name__ == "__main__":
    main()
