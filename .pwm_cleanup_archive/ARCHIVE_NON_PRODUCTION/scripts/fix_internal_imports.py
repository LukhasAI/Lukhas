#!/usr/bin/env python3
"""
Fix internal module imports based on analysis
"""

import ast
import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InternalImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

        # Build index of all classes and functions
        self.class_to_module = {}
        self.function_to_module = {}
        self._build_index()

    def _build_index(self):
        """Build index of all classes and functions in the codebase"""
        logger.info("Building index of classes and functions...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Get module path
                relative = py_file.relative_to(self.root_path)
                module_parts = list(relative.parts[:-1]) + [relative.stem]
                module_path = ".".join(module_parts)

                # Parse for classes and functions
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            self.class_to_module[node.name] = module_path
                        elif isinstance(node, ast.FunctionDef) and node.name.startswith(
                            "create_"
                        ):
                            # Focus on factory functions
                            self.function_to_module[node.name] = module_path
                except:
                    pass

            except Exception as e:
                logger.debug(f"Error indexing {py_file}: {e}")

        logger.info(
            f"Indexed {len(self.class_to_module)} classes and {len(self.function_to_module)} functions"
        )

    def fix_imports(self):
        """Fix internal imports"""
        logger.info("Fixing internal imports...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Fix patterns we discovered
        self._fix_specific_patterns()

        # Fix single imports that are actually internal
        self._fix_single_internal_imports()

        # Fix known problematic imports
        self._fix_known_issues()

        logger.info(f"\nTotal fixes applied: {self.fixes_applied}")
        logger.info(f"Files fixed: {self.files_fixed}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_specific_patterns(self):
        """Fix specific import patterns"""
        logger.info("\nFixing specific import patterns...")

        mappings = {
            # LUKHAS_AGENT_PLUGIN patterns
            "from core.common_AGENT_PLUGIN.core.lukhas_emotion_log": "from core.lukhas_emotion_log",
            "from core.common_AGENT_PLUGIN.": "from ",
            # Symbolic AI patterns
            "from symbolic_ai.trait_manager": "from orchestration.brain.spine.trait_manager",
            "from symbolic_ai.": "from symbolic.",
            # GlobalInstitutionalFramework
            "from GlobalInstitutionalFramework": "from identity.backend.app.institution_manager",
            "import GlobalInstitutionalFramework": "from identity.backend.app.institution_manager import GlobalInstitutionalFramework",
            # token_budget_controller
            "from token_budget_controller": "from core.budget.token_controller",
            "import token_budget_controller": "from core.budget.token_controller import token_budget_controller",
            # Fix remaining bio patterns
            "from bio.integration.bio_awareness.": "from bio.",
            # Fix any remaining core.memory
            "from core.memory import": "from memory import",
            "import core.memory": "import memory",
        }

        self._apply_mappings(mappings)

    def _fix_single_internal_imports(self):
        """Fix single import statements for internal modules"""
        logger.info("\nFixing single internal imports...")

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

                    # Check for single imports
                    match = re.match(r"^import (\w+)$", line.strip())
                    if match:
                        name = match.group(1)

                        # Check if it's an internal class
                        if name in self.class_to_module:
                            module = self.class_to_module[name]
                            new_line = f"from {module} import {name}\n"
                            modified = True
                            logger.debug(
                                f"Fixed: import {name} -> from {module} import {name}"
                            )

                        # Check if it's an internal function
                        elif name in self.function_to_module:
                            module = self.function_to_module[name]
                            new_line = f"from {module} import {name}\n"
                            modified = True
                            logger.debug(
                                f"Fixed: import {name} -> from {module} import {name}"
                            )

                    new_lines.append(new_line)

                if modified and not self.dry_run:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    self.files_fixed += 1

            except Exception as e:
                if "utf-8" not in str(e):
                    logger.error(f"Error processing {py_file}: {e}")

    def _fix_known_issues(self):
        """Fix known problematic imports"""
        logger.info("\nFixing known import issues...")

        # Specific files with known issues
        specific_fixes = {
            "tests/symbolic/test_symbolic_core.py": [
                ("from core.memory import (", "from memory import ("),
                (
                    "from core.memory import SYMBOLIC_INTEGRATION_ENABLED",
                    "from memory import SYMBOLIC_INTEGRATION_ENABLED",
                ),
                ("import core.memory", "import memory"),
            ],
            "quantum/quantum_bio_bulletproof_system.py": [
                (
                    "from bio.integration.bio_awareness.advanced_quantum_bio import EnhancedMitochondrialQuantumBridge",
                    "from bio.advanced_quantum_bio import EnhancedMitochondrialQuantumBridge",
                )
            ],
            "quantum/systems/bio_integration/bulletproof_system.py": [
                (
                    "from bio.integration.bio_awareness.advanced_quantum_bio import EnhancedMitochondrialQuantumBridge",
                    "from bio.advanced_quantum_bio import EnhancedMitochondrialQuantumBridge",
                )
            ],
        }

        for filename, fixes in specific_fixes.items():
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

    def _apply_mappings(self, mappings: dict):
        """Apply import mappings to all Python files"""
        fixed_count = 0

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
                    fixed_count += file_fixes

                    relative_path = py_file.relative_to(self.root_path)
                    logger.debug(f"Fixed {file_fixes} imports in {relative_path}")

            except Exception as e:
                if "utf-8" not in str(e):
                    logger.error(f"Error processing {py_file}: {e}")

        if fixed_count > 0:
            logger.info(f"  Fixed {fixed_count} occurrences")

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

    parser = argparse.ArgumentParser(description="Fix internal module imports")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = InternalImportFixer(root_path, dry_run=not args.fix)
    fixer.fix_imports()


if __name__ == "__main__":
    main()
