#!/usr/bin/env python3
"""
Implement high-impact performance consolidations
"""

import ast
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0

    def fix_duplicates(self):
        """Remove duplicate files"""
        logger.info("Removing duplicate files...")

        duplicates = [
            [
                "memory_optimization_analysis.py",
                "benchmarks/memory/memory_stress_tests/memory_optimization_analysis.py",
            ],
            ["bio/symbolic_entropy.py", "symbolic/bio/symbolic_entropy.py"],
            [
                "bio/symbolic_entropy_observer.py",
                "symbolic/bio/symbolic_entropy_observer.py",
            ],
        ]

        for dup_set in duplicates:
            # Keep the first, remove the rest
            keep_file = self.root_path / dup_set[0]

            for dup_file in dup_set[1:]:
                remove_path = self.root_path / dup_file
                if remove_path.exists():
                    logger.info(f"  Removing duplicate: {dup_file}")
                    if not self.dry_run:
                        remove_path.unlink()
                    self.fixes_applied += 1

                    # Update imports pointing to removed file
                    self._update_imports_for_removed_file(dup_file, dup_set[0])

    def consolidate_memory_systems(self):
        """Consolidate fragmented memory systems"""
        logger.info("\nConsolidating memory systems...")

        # Create unified memory system files
        consolidations = {
            "memory/unified_memory_system.py": [
                "memory/systems/memory_fold.py",
                "memory/systems/hybrid_memory_fold.py",
                "memory/systems/optimized_hybrid_memory_fold.py",
                "memory/systems/distributed_memory_fold.py",
            ],
            "memory/unified_memory_manager.py": [
                "memory/manager.py",
                "memory/quantum_manager.py",
                "memory/quantum_memory_manager.py",
                "memory/drift_memory_manager.py",
            ],
        }

        for target_file, source_files in consolidations.items():
            self._consolidate_files(target_file, source_files)

    def consolidate_small_modules(self):
        """Consolidate small modules to reduce import overhead"""
        logger.info("\nConsolidating small modules...")

        # Bio consolidation
        self._consolidate_directory_modules("bio", "bio_utilities.py", size_limit=1500)

        # Core consolidation
        self._consolidate_directory_modules(
            "core", "core_utilities.py", size_limit=1500
        )

        # Symbolic consolidation
        self._consolidate_directory_modules(
            "symbolic", "symbolic_utilities.py", size_limit=1500
        )

    def fix_circular_dependencies(self):
        """Break circular dependencies"""
        logger.info("\nFixing circular dependencies...")

        # Fix ethics <-> dream circular dependency
        self._fix_ethics_dream_circular()

        # Fix orchestration brain circular dependency
        self._fix_orchestration_brain_circular()

    def _consolidate_files(self, target: str, sources: list):
        """Consolidate multiple source files into target"""
        target_path = self.root_path / target

        if self.dry_run:
            logger.info(f"  Would consolidate {len(sources)} files into {target}")
            return

        # Collect all content
        imports = set()
        classes = []
        functions = []

        for source in sources:
            source_path = self.root_path / source
            if not source_path.exists():
                continue

            with open(source_path, encoding="utf-8") as f:
                content = f.read()

            # Parse to extract components
            try:
                tree = ast.parse(content)

                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(f"import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            names = ", ".join(n.name for n in node.names)
                            imports.add(f"from {node.module} import {names}")

                # Extract classes and functions
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        classes.append(ast.unparse(node))
                    elif isinstance(node, ast.FunctionDef):
                        functions.append(ast.unparse(node))

            except Exception as e:
                logger.error(f"Error parsing {source}: {e}")

        # Create consolidated file
        consolidated_content = (
            '"""\nConsolidated module for better performance\n"""\n\n'
        )

        # Add imports
        for imp in sorted(imports):
            consolidated_content += f"{imp}\n"

        consolidated_content += "\n\n"

        # Add functions
        for func in functions:
            consolidated_content += f"{func}\n\n"

        # Add classes
        for cls in classes:
            consolidated_content += f"{cls}\n\n"

        # Write consolidated file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(consolidated_content)

        logger.info(f"  Created consolidated file: {target}")

        # Update imports
        for source in sources:
            self._update_imports_after_consolidation(source, target)

        self.fixes_applied += 1

    def _consolidate_directory_modules(
        self, directory: str, target_name: str, size_limit: int = 2000
    ):
        """Consolidate small modules in a directory"""
        dir_path = self.root_path / directory
        if not dir_path.exists():
            return

        small_files = []

        for py_file in dir_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            if py_file.stat().st_size < size_limit:
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()
                    code_lines = sum(
                        1
                        for line in lines
                        if line.strip() and not line.strip().startswith("#")
                    )

                if code_lines < 50:
                    small_files.append(str(py_file.relative_to(self.root_path)))

        if len(small_files) > 3:
            target = f"{directory}/{target_name}"
            logger.info(
                f"  Consolidating {len(small_files)} small files in {directory}/"
            )
            self._consolidate_files(target, small_files[:10])  # Limit to 10 files

    def _fix_ethics_dream_circular(self):
        """Fix circular dependency between ethics and dream modules"""
        if self.dry_run:
            logger.info("  Would fix ethics <-> dream circular dependency")
            return

        # Move shared interfaces to a common module
        interface_content = '''"""
Common interfaces to break circular dependencies
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class EthicsCheckable(ABC):
    """Interface for ethics-checkable components"""

    @abstractmethod
    def get_ethical_context(self) -> Dict[str, Any]:
        """Get context for ethical evaluation"""
        pass

class DreamAnalyzable(ABC):
    """Interface for dream-analyzable components"""

    @abstractmethod
    def get_dream_state(self) -> Dict[str, Any]:
        """Get current dream state"""
        pass
'''

        interface_path = self.root_path / "core" / "interfaces" / "common_interfaces.py"
        interface_path.parent.mkdir(parents=True, exist_ok=True)

        with open(interface_path, "w", encoding="utf-8") as f:
            f.write(interface_content)

        logger.info("  Created common interfaces to break circular dependency")
        self.fixes_applied += 1

    def _fix_orchestration_brain_circular(self):
        """Fix circular dependency in orchestration.brain modules"""
        if self.dry_run:
            logger.info("  Would fix orchestration.brain circular dependency")
            return

        # Merge tightly coupled modules
        self._consolidate_files(
            "orchestration/brain/unified_collapse_system.py",
            [
                "orchestration/brain/brain_collapse_manager.py",
                "orchestration/brain/collapse_bridge.py",
            ],
        )

    def _update_imports_for_removed_file(
        self, removed_file: str, replacement_file: str
    ):
        """Update imports pointing to removed file"""
        removed_module = removed_file.replace(".py", "").replace("/", ".")
        replacement_module = replacement_file.replace(".py", "").replace("/", ".")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                if removed_module in content:
                    new_content = content.replace(
                        f"from {removed_module}", f"from {replacement_module}"
                    )
                    new_content = new_content.replace(
                        f"import {removed_module}", f"import {replacement_module}"
                    )

                    if new_content != content and not self.dry_run:
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(new_content)

            except Exception as e:
                logger.debug(f"Error updating {py_file}: {e}")

    def _update_imports_after_consolidation(self, old_file: str, new_file: str):
        """Update imports after consolidation"""
        old_module = old_file.replace(".py", "").replace("/", ".")
        new_module = new_file.replace(".py", "").replace("/", ".")

        # Extract just the module name for class imports
        old_classes = self._get_classes_from_file(self.root_path / old_file)

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                modified = False

                # Update module imports
                if f"from {old_module}" in content:
                    content = content.replace(
                        f"from {old_module}", f"from {new_module}"
                    )
                    modified = True

                # Update class imports
                for class_name in old_classes:
                    if f"import {class_name}" in content:
                        content = content.replace(
                            f"from {old_module} import {class_name}",
                            f"from {new_module} import {class_name}",
                        )
                        modified = True

                if modified and not self.dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)

            except Exception as e:
                logger.debug(f"Error updating imports in {py_file}: {e}")

    def _get_classes_from_file(self, file_path: Path) -> list:
        """Extract class names from a file"""
        classes = []

        if not file_path.exists():
            return classes

        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)

        except Exception:
            pass

        return classes

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

    def run_all_fixes(self):
        """Run all performance fixes"""
        logger.info("Running performance consolidation fixes...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # 1. Remove duplicates (quick win)
        self.fix_duplicates()

        # 2. Consolidate memory systems (high impact)
        self.consolidate_memory_systems()

        # 3. Consolidate small modules (startup performance)
        self.consolidate_small_modules()

        # 4. Fix circular dependencies (runtime performance)
        self.fix_circular_dependencies()

        logger.info(f"\nTotal fixes applied: {self.fixes_applied}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Implement performance consolidation fixes"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = PerformanceFixer(root_path, dry_run=not args.fix)
    fixer.run_all_fixes()


if __name__ == "__main__":
    main()
