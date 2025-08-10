#!/usr/bin/env python3
"""
Fix imports module by module with specific patterns
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModuleImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = {}

    def fix_module(self, module_name: str):
        """Fix imports for a specific module"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Fixing imports for module: {module_name}")
        logger.info(f"{'='*80}")

        if module_name == "core.memory":
            self._fix_core_memory()
        elif module_name == "bio.nested":
            self._fix_bio_nested()
        elif module_name == "single_imports":
            self._fix_single_imports()
        elif module_name == "lukhas":
            self._fix_lukhas_prefix()
        else:
            logger.error(f"Unknown module: {module_name}")

    def _fix_core_memory(self):
        """Fix core.memory imports"""
        logger.info("Fixing core.memory imports...")

        # These files were moved from core/memory to features/memory or memory/
        mappings = {
            "from core.memory.memory_fold": "from features.memory.memory_fold",
            "from core.memory.fold_engine": "from memory.fold_engine",
            "import core.memory.memory_fold": "import features.memory.memory_fold",
            "import core.memory.fold_engine": "import memory.fold_engine",
        }

        self._apply_mappings(mappings, "core.memory")

    def _fix_bio_nested(self):
        """Fix bio nested imports"""
        logger.info("Fixing bio nested imports...")

        # Bio files were flattened - remove nested paths
        mappings = {
            "from bio.awareness.quantum_bio_components": "from bio.quantum_bio_components",
            "from bio.systems.oscillator.quantum_inspired_layer": "from bio.quantum_inspired_layer",
            "import bio.awareness.": "import bio.",
            "import bio.systems.": "import bio.",
        }

        self._apply_mappings(mappings, "bio.nested")

    def _fix_single_imports(self):
        """Fix single module imports (missing pathlib, etc)"""
        logger.info("Fixing single module imports...")

        # Common missing imports
        mappings = {
            r"^import Path$": "from pathlib import Path",
            r"^import create_hybrid_memory_fold$": "from features.memory.memory_fold import create_hybrid_memory_fold",
            r"^import create_attention_orchestrator$": "from orchestration.orchestrator import create_attention_orchestrator",
            r"^import create_structural_conscience$": "from memory.structural_conscience import create_structural_conscience",
            r"^from setuptools import": "from setuptools import",  # This is actually correct, skip
        }

        # Special handling for single imports
        fixed_count = 0
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()

                modified = False
                new_lines = []

                for line in lines:
                    new_line = line

                    # Fix Path import
                    if line.strip() == "import Path":
                        new_line = "from pathlib import Path\n"
                        modified = True

                    # Fix standalone function imports
                    elif re.match(
                        r"^import (create_\w+|initialize_\w+)$", line.strip()
                    ):
                        # These need to be traced to their actual location
                        func_name = line.strip().split()[1]
                        new_line = f"# TODO: Fix import for {func_name}\n" + line
                        modified = True

                    new_lines.append(new_line)

                if modified and not self.dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    fixed_count += 1

            except Exception as e:
                logger.error(f"Error processing {py_file}: {e}")

        logger.info(f"Fixed {fixed_count} files with single imports")
        self.fixes_applied["single_imports"] = fixed_count

    def _fix_lukhas_prefix(self):
        """Fix lukhas prefix imports"""
        logger.info("Fixing lukhas prefix imports...")

        mappings = {
            "from lukhas.": "from ",
            "import lukhas.": "import ",
        }

        self._apply_mappings(mappings, "lukhas")

    def _apply_mappings(self, mappings: dict, module_name: str):
        """Apply import mappings to all Python files"""
        fixed_files = 0
        total_fixes = 0

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                file_fixes = 0

                for old_pattern, new_pattern in mappings.items():
                    if old_pattern.startswith("^"):
                        # Regex pattern
                        new_content, count = re.subn(
                            old_pattern, new_pattern, content, flags=re.MULTILINE
                        )
                    else:
                        # Simple string replacement
                        count = content.count(old_pattern)
                        new_content = content.replace(old_pattern, new_pattern)

                    if count > 0:
                        content = new_content
                        file_fixes += count

                if content != original_content:
                    if not self.dry_run:
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(content)

                    fixed_files += 1
                    total_fixes += file_fixes

                    relative_path = py_file.relative_to(self.root_path)
                    logger.debug(f"Fixed {file_fixes} imports in {relative_path}")

            except Exception as e:
                logger.error(f"Error processing {py_file}: {e}")

        logger.info(
            f"Module {module_name}: Fixed {total_fixes} imports in {fixed_files} files"
        )
        self.fixes_applied[module_name] = total_fixes

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

    def generate_report(self):
        """Generate final report"""
        logger.info("\n" + "=" * 80)
        logger.info("IMPORT FIX SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        for module, count in self.fixes_applied.items():
            logger.info(f"{module}: {count} fixes")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix imports module by module")
    parser.add_argument(
        "module",
        choices=["core.memory", "bio.nested", "single_imports", "lukhas", "all"],
        help="Module to fix",
    )
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = ModuleImportFixer(root_path, dry_run=not args.fix)

    if args.module == "all":
        modules = ["core.memory", "bio.nested", "single_imports", "lukhas"]
        for module in modules:
            fixer.fix_module(module)
    else:
        fixer.fix_module(args.module)

    fixer.generate_report()


if __name__ == "__main__":
    main()
