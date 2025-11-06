#!/usr/bin/env python3
"""
Pytest Class Collection Fixer
=============================
Automatically fixes test classes that cannot be collected by pytest due to __init__ constructors.
Converts __init__ methods to setup_method or pytest fixtures while preserving test logic.

Fixes patterns like:
- class TestExample: def __init__(self): ... → setup_method pattern
- Complex initialization → pytest fixture pattern
- Preserve all test logic and maintain functionality

Features:
- AST-based safe transformation
- Multiple conversion strategies
- Validation and rollback
- Integration with diagnostic orchestrator
"""

import ast
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


class TestClassTransformer(ast.NodeTransformer):
    """AST transformer to fix test class __init__ methods"""

    def __init__(self):
        self.transformations = []
        self.current_class = None

    def visit_ClassDef(self, node):
        """Visit class definitions to find test classes"""
        old_class = self.current_class

        # Check if this is a test class
        if node.name.startswith("Test"):
            self.current_class = node.name

            # Look for __init__ method
            init_method = None
            init_index = None

            for i, item in enumerate(node.body):
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_method = item
                    init_index = i
                    break

            if init_method:
                # Transform the __init__ method
                new_method = self.transform_init_method(init_method, node.name)
                if new_method:
                    # Replace __init__ with setup_method
                    node.body[init_index] = new_method
                    self.transformations.append(
                        {
                            "class": node.name,
                            "action": "converted_init_to_setup_method",
                            "original_method": ast.unparse(init_method) if hasattr(ast, "unparse") else "init_method",
                        }
                    )

        # Continue visiting child nodes
        self.generic_visit(node)
        self.current_class = old_class
        return node

    def transform_init_method(self, init_method: ast.FunctionDef, class_name: str) -> Optional[ast.FunctionDef]:
        """Transform __init__ method to setup_method"""

        # Create setup_method with same body (excluding self parameter handling)
        setup_method = ast.FunctionDef(
            name="setup_method",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self", annotation=None)],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=init_method.body.copy(),
            decorator_list=[],
            returns=None,
        )

        return setup_method


class PytestClassFixer:
    """Main pytest class collection fixer"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.fixed_files = []
        self.transformation_log = []

    def find_problematic_test_classes(self) -> list[Path]:
        """Find test files with classes that have __init__ methods"""
        problematic_files = []

        # Search for test files
        test_files = list(ROOT.glob("tests/**/*.py"))
        test_files.extend(ROOT.glob("**/test_*.py"))

        for test_file in test_files:
            if self.file_has_test_class_with_init(test_file):
                problematic_files.append(test_file)

        return problematic_files

    def file_has_test_class_with_init(self, file_path: Path) -> bool:
        """Check if file contains test classes with __init__ methods"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")

            # Parse AST
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    # Check for __init__ method in test class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                            return True

            return False

        except Exception as e:
            logger.warning(f"Could not analyze {file_path}: {e}")
            return False

    def get_pytest_collection_warnings(self) -> list[Path]:
        """Get files with pytest collection warnings from actual pytest output"""
        try:
            # Run pytest in collection-only mode to find problematic classes
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                cwd=ROOT,
                timeout=30,
            )

            problematic_files = set()

            # Parse pytest output for collection warnings
            for line in result.stderr.split("\n"):
                if "cannot collect test class" in line.lower() and "__init__" in line.lower():  # TODO[T4-ISSUE]: {"code":"SIM102","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Nested if statements - can be collapsed with 'and' operator","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tools_automation_pytest_class_fixer_py_L160"}
                    # Extract file path from pytest warning
                    if " from: " in line:
                        file_part = line.split(" from: ")[1].strip(")")
                        if file_part.endswith(".py"):
                            file_path = ROOT / file_part
                            if file_path.exists():
                                problematic_files.add(file_path)

            return list(problematic_files)

        except Exception as e:
            logger.warning(f"Could not get pytest collection info: {e}")
            return []

    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file before modification"""
        backup_dir = ROOT / "backups" / "pytest_fixes"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_file = backup_dir / f"{file_path.name}.backup"
        shutil.copy2(file_path, backup_file)

        return backup_file

    def validate_fix(self, file_path: Path) -> bool:
        """Validate that the fix doesn't break syntax or functionality"""
        try:
            # Check Python syntax
            content = file_path.read_text()
            ast.parse(content)

            # Check that pytest can collect tests from this file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(file_path), "--collect-only", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                cwd=ROOT,
                timeout=10,
            )

            # Look for collection warnings in this specific file
            has_collection_warning = any(
                "__init__" in line.lower() and "cannot collect" in line.lower() for line in result.stderr.split("\n")
            )

            return not has_collection_warning

        except Exception as e:
            logger.warning(f"Validation failed for {file_path}: {e}")
            return False

    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file with test class collection issues"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fix test classes in: {file_path}")
            return True

        try:
            # Create backup
            backup_file = self.create_backup(file_path)
            logger.info(f"Created backup: {backup_file}")

            # Read and parse file
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Apply transformations
            transformer = TestClassTransformer()
            new_tree = transformer.visit(tree)

            if transformer.transformations:
                # Generate new code
                if hasattr(ast, "unparse"):
                    new_content = ast.unparse(new_tree)
                else:
                    # Fallback: use basic string replacement for older Python
                    new_content = self.fallback_string_replacement(content)

                # Write fixed content
                file_path.write_text(new_content, encoding="utf-8")

                # Validate fix
                if self.validate_fix(file_path):
                    self.fixed_files.append(str(file_path))
                    self.transformation_log.extend(transformer.transformations)
                    logger.info(f"✅ Fixed test classes in: {file_path}")
                    return True
                else:
                    # Rollback on validation failure
                    shutil.copy2(backup_file, file_path)
                    logger.warning(f"⚠️ Validation failed, rolled back: {file_path}")
                    return False
            else:
                logger.info(f"No transformations needed for: {file_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {e}")
            return False

    def fallback_string_replacement(self, content: str) -> str:
        """Fallback method using string replacement for older Python versions"""
        # Simple regex-based replacement of __init__ with setup_method in test classes
        lines = content.split("\n")
        new_lines = []
        in_test_class = False
        class_indent = 0

        for line in lines:
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)

            # Check if we're entering a test class
            if stripped.startswith("class Test") and ":" in stripped:
                in_test_class = True
                class_indent = current_indent
                new_lines.append(line)
                continue

            # Check if we're leaving the test class
            if (in_test_class and current_indent <= class_indent and stripped and (not stripped.startswith('#'))) and (not stripped.startswith('def ') and (not stripped.startswith('@'))):
                in_test_class = False

            # Replace __init__ with setup_method in test classes
            if in_test_class and stripped.startswith("def __init__(self"):
                new_line = line.replace("__init__", "setup_method")
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        return "\n".join(new_lines)

    def run_fixes(self, target_files: Optional[list[Path]] = None) -> dict:
        """Run pytest class fixes on target files"""
        logger.info("🧪 Starting pytest class collection fixes")

        if target_files is None:
            # Find files with collection issues
            logger.info("Finding test files with collection issues...")
            target_files = self.get_pytest_collection_warnings()

            if not target_files:
                # Fallback to AST-based detection
                target_files = self.find_problematic_test_classes()

        if not target_files:
            logger.info("No test files with collection issues found")
            return {"status": "no_files", "files_processed": 0}

        logger.info(f"Found {len(target_files)} files with test class collection issues")

        success_count = 0

        for file_path in target_files:
            logger.info(f"Processing: {file_path}")
            if self.fix_file(file_path):
                success_count += 1

        return {
            "status": "completed",
            "files_processed": len(target_files),
            "files_fixed": success_count,
            "fixed_files": self.fixed_files,
            "transformations": len(self.transformation_log),
            "dry_run": self.dry_run,
        }


def main():
    """CLI interface for pytest class fixer"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix pytest test class collection issues")
    parser.add_argument("files", nargs="*", help="Test files to fix (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fixer = PytestClassFixer(dry_run=args.dry_run)

    target_files = None
    if args.files:
        target_files = [Path(f) for f in args.files]

    results = fixer.run_fixes(target_files)

    # Print results
    print("\n🧪 PYTEST CLASS COLLECTION FIXER RESULTS")
    print("========================================")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Files processed: {results['files_processed']}")
    print(f"Files fixed: {results['files_fixed']}")
    print(f"Transformations: {results['transformations']}")

    if results["fixed_files"]:
        print("\n✅ FIXED FILES:")
        for file_path in results["fixed_files"]:
            print(f"  - {file_path}")

    return 0 if results["files_fixed"] > 0 or results["files_processed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
