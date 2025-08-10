#!/usr/bin/env python3
"""
Comprehensive import fix based on actual file locations
"""

import ast
import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.function_to_module = {}
        self.class_to_module = {}
        self.fixes_applied = 0
        self.files_fixed = 0

    def run(self):
        """Run comprehensive import fix"""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE IMPORT FIXER")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Step 1: Build complete index of functions and classes
        logger.info("\n[Step 1/3] Building function and class index...")
        self._build_index()

        # Step 2: Fix imports based on actual locations
        logger.info("\n[Step 2/3] Fixing imports...")
        self._fix_all_imports()

        # Step 3: Report results
        logger.info("\n[Step 3/3] Generating report...")
        self._generate_report()

    def _build_index(self):
        """Build index of all functions and classes"""
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Get module path
                relative_path = py_file.relative_to(self.root_path)
                module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
                module_path = ".".join(module_parts)

                # Parse AST
                try:
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            self.function_to_module[node.name] = module_path
                        elif isinstance(node, ast.ClassDef):
                            self.class_to_module[node.name] = module_path

                except SyntaxError:
                    pass

            except Exception as e:
                logger.debug(f"Error indexing {py_file}: {e}")

        logger.info(
            f"Indexed {len(self.function_to_module)} functions and {len(self.class_to_module)} classes"
        )

    def _fix_all_imports(self):
        """Fix all imports in the codebase"""
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            self._fix_file_imports(py_file)

    def _fix_file_imports(self, file_path: Path):
        """Fix imports in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            for i, line in enumerate(lines):
                new_line = line

                # Fix standalone function imports
                match = re.match(r"^from ([\w.]+) import ([\w, ]+)$", line.strip())
                if match:
                    module = match.group(1)
                    imports = [imp.strip() for imp in match.group(2).split(",")]

                    # Check each import
                    fixed_imports = []
                    for imp in imports:
                        if imp in self.function_to_module:
                            correct_module = self.function_to_module[imp]
                            if correct_module != module:
                                # Need to fix this import
                                new_line = f"from {correct_module} import {imp}\n"
                                modified = True
                                logger.debug(
                                    f"Fixed: {line.strip()} -> {new_line.strip()}"
                                )
                        elif imp in self.class_to_module:
                            correct_module = self.class_to_module[imp]
                            if correct_module != module:
                                # Need to fix this import
                                new_line = f"from {correct_module} import {imp}\n"
                                modified = True
                                logger.debug(
                                    f"Fixed: {line.strip()} -> {new_line.strip()}"
                                )

                # Fix core.memory imports
                if "from core.memory" in line:
                    new_line = line.replace("from core.memory", "from memory")
                    if new_line != line:
                        modified = True

                # Fix bio nested imports
                if re.search(r"from bio\.\w+\.\w+", line):
                    # Flatten bio imports
                    match = re.search(r"from bio\.[\w.]+\.(\w+) import", line)
                    if match:
                        module_name = match.group(1)
                        if module_name in self.class_to_module:
                            correct_path = self.class_to_module[module_name]
                            if correct_path.startswith("bio."):
                                new_line = (
                                    f"from {correct_path} import"
                                    + line.split("import", 1)[1]
                                )
                                modified = True

                # Remove lukhas prefix
                if "lukhas." in line:
                    new_line = line.replace("lukhas.", "")
                    if new_line != line:
                        modified = True

                new_lines.append(new_line)

            if modified:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                self.files_fixed += 1
                relative_path = file_path.relative_to(self.root_path)
                logger.info(f"Fixed imports in: {relative_path}")

        except Exception as e:
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

        # Skip non-UTF8 files
        if path.name == "__init__.py" and "symbolic_diagnostics" in str(path):
            return True

        return any(part in skip_dirs for part in path.parts)

    def _generate_report(self):
        """Generate final report"""
        logger.info("\n" + "=" * 80)
        logger.info("IMPORT FIX SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")
        logger.info(f"Files fixed: {self.files_fixed}")

        # Show example fixes
        logger.info("\nExample function locations found:")
        for func, module in list(self.function_to_module.items())[:5]:
            if func.startswith("create_"):
                logger.info(f"  {func} -> {module}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive import fix")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = ComprehensiveImportFixer(root_path, dry_run=not args.fix)
    fixer.run()


if __name__ == "__main__":
    main()
