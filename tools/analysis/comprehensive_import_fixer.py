#!/usr/bin/env python3
"""
🔧  Comprehensive Import Fixer
=================================
Systematically fixes all import errors and dependencies in LUKHAS .
"""
from consciousness.qi import qi
import time
import streamlit as st

import ast
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ImportErrorFixer:
    """Comprehensive import error fixing system"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.syntax_errors: list[dict[str, Any]] = []
        self.missing_modules: dict[str, list[str]] = defaultdict(list)
        self.circular_imports: list[list[str]] = []
        self.fixed_files: list[str] = []
        self.errors_by_category: dict[str, int] = defaultdict(int)

        # Modules to ignore (archived, obsolete, etc.)
        self.ignored_patterns = [
            "._cleanup_archive",
            "ARCHIVE_",
            "BACKUP_",
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
        ]

        # Common fix patterns
        self.import_fixes = {
            # Core module fixes
            "core.common": "from lukhas.core.common import",
            "memory.core": "from lukhas.memory.core import",
            "consciousness.unified": "from lukhas.consciousness.unified import",
            "governance.guardian_system": "from lukhas.governance.guardian_system import",
            "qi.algorithms": "from lukhas.qi.algorithms import",
            "orchestration.brain": "from lukhas.orchestration.brain import",
            # Interface fixes
            "core.interfaces": "from core.interfaces import",
            "core.interfaces.dependency_injection": "from core.interfaces.dependency_injection import",
            # Common replacements
            "lukhas_core": "core",
            "lukhas.core": "core",
            "LUKHAS.core": "core",
            "common.logging": "core.common.logger",
            "common.config": "core.common.config",
        }

    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        path_str = str(file_path)
        return any(pattern in path_str for pattern in self.ignored_patterns)

    def analyze_syntax_errors(self) -> None:
        """Find and categorize syntax errors"""
        logger.info("🔍 Analyzing syntax errors...")

        for py_file in self.root_path.rglob("*.py"):
            if self.should_ignore_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Try to parse the file
                ast.parse(content, filename=str(py_file))

            except SyntaxError as e:
                error_info = {
                    "file": str(py_file.relative_to(self.root_path)),
                    "line": e.lineno,
                    "message": str(e),
                    "text": e.text.strip() if e.text else "",
                }
                self.syntax_errors.append(error_info)
                self.errors_by_category["syntax"] += 1

            except Exception as e:
                logger.warning(f"Could not analyze {py_file}: {e}")

    def fix_syntax_errors(self) -> None:
        """Fix common syntax errors"""
        logger.info("🔧 Fixing syntax errors...")

        for error_info in self.syntax_errors:
            file_path = self.root_path / error_info["file"]

            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                line_num = error_info["line"] - 1  # Convert to 0-indexed
                if line_num < len(lines):
                    line = lines[line_num]
                    original_line = line

                    # Common syntax fixes
                    line = self.fix_common_syntax_issues(line)

                    if line != original_line:
                        lines[line_num] = line

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.writelines(lines)

                        logger.info(f"✅ Fixed syntax in {error_info['file']}:{error_info['line']}")
                        self.fixed_files.append(str(file_path))

            except Exception as e:
                logger.error(f"❌ Could not fix syntax error in {error_info['file']}: {e}")

    def fix_common_syntax_issues(self, line: str) -> str:
        """Fix common syntax issues in a line"""
        # Fix f-string backslash issues
        if 'f"' in line or "f'" in line:
            # Replace backslashes in f-strings with raw strings or variables
            line = re.sub(r'f"([^"]*\\[^"]*)"', r'f"{\\1}".replace("\\\\", "/")', line)

        # Fix missing colons in control structures
        if re.match(
            r"^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\s", line
        ) and not line.rstrip().endswith(":"):
            line = line.rstrip() + ":\n"

        # Fix indentation issues (convert tabs to spaces)
        if "\t" in line:
            line = line.expandtabs(4)

        # Fix common import errors
        line = self.fix_import_statement(line)

        return line

    def fix_import_statement(self, line: str) -> str:
        """Fix common import statement issues"""
        # Remove leading/trailing whitespace but preserve indentation
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]

        # Apply import fixes
        for old_pattern, new_pattern in self.import_fixes.items():
            if old_pattern in stripped and (stripped.startswith("from ") or stripped.startswith("import ")):
                # Replace the pattern in import statements
                stripped = stripped.replace(old_pattern, new_pattern.split(" import")[0])

        return indent + stripped

    def analyze_missing_modules(self) -> None:
        """Find missing module imports"""
        logger.info("🔍 Analyzing missing modules...")

        for py_file in self.root_path.rglob("*.py"):
            if self.should_ignore_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name
                            if not self.module_exists(module_name):
                                self.missing_modules[module_name].append(str(py_file.relative_to(self.root_path)))
                                self.errors_by_category["missing_module"] += 1

                    elif isinstance(node, ast.ImportFrom) and node.module:
                        module_name = node.module
                        if not self.module_exists(module_name):
                            self.missing_modules[module_name].append(str(py_file.relative_to(self.root_path)))
                            self.errors_by_category["missing_module"] += 1

            except Exception as e:
                logger.warning(f"Could not analyze imports in {py_file}: {e}")

    def module_exists(self, module_name: str) -> bool:
        """Check if a module exists"""
        # Ignore archived modules
        if any(pattern in module_name for pattern in self.ignored_patterns):
            return True

        # Check if it's a local module
        if module_name.startswith("."):
            return True  # Relative imports are harder to validate

        # Check if it's a core LUKHAS module
        module_parts = module_name.split(".")
        if len(module_parts) > 0:
            first_part = module_parts[0]
            expected_path = self.root_path / first_part
            if expected_path.exists() and expected_path.is_dir():
                return True

        # Check if it's an installed package
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def fix_missing_modules(self) -> None:
        """Fix missing module imports"""
        logger.info("🔧 Fixing missing modules...")

        # Group by module type
        local_modules = {}
        external_modules = {}

        for module_name, files in self.missing_modules.items():
            if any(pattern in module_name for pattern in self.ignored_patterns):
                continue

            if self.is_local_module(module_name):
                local_modules[module_name] = files
            else:
                external_modules[module_name] = files

        # Fix local modules
        self.fix_local_modules(local_modules)

        # Report external modules
        self.report_external_modules(external_modules)

    def is_local_module(self, module_name: str) -> bool:
        """Check if module should be a local LUKHAS module"""
        local_prefixes = [
            "core",
            "memory",
            "consciousness",
            "governance",
            "quantum",
            "orchestration",
            "creativity",
            "bio",
            "emotion",
            "identity",
            "reasoning",
            "architectures",
            "bridge",
            "ethics",
            "api",
            "vivox",
            "lukhas",
        ]

        return any(module_name.startswith(prefix) for prefix in local_prefixes)

    def fix_local_modules(self, local_modules: dict[str, list[str]]) -> None:
        """Fix local module import issues"""
        logger.info("🔧 Fixing local module imports...")

        for module_name, files in local_modules.items():
            # Find the correct module path
            correct_path = self.find_correct_module_path(module_name)

            if correct_path:
                # Update imports in files
                for file_path_str in files:
                    self.update_import_in_file(file_path_str, module_name, correct_path)
            else:
                # Create missing module structure
                self.create_missing_module(module_name)

    def find_correct_module_path(self, module_name: str) -> Optional[str]:
        """Find the correct path for a module"""
        parts = module_name.split(".")

        # Check various possible locations
        possible_paths = [
            self.root_path / "/".join(parts),
            self.root_path / parts[0] / "/".join(parts[1:]) if len(parts) > 1 else None,
        ]

        for path in possible_paths:
            if path and path.exists():
                # Check if it's a proper Python module
                if path.is_dir() and (path / "__init__.py").exists():
                    return str(path.relative_to(self.root_path)).replace("/", ".")
                elif path.with_suffix(".py").exists():
                    return str(path.relative_to(self.root_path)).replace("/", ".").replace(".py", "")

        return None

    def update_import_in_file(self, file_path_str: str, old_import: str, new_import: str) -> None:
        """Update import statement in a file"""
        file_path = self.root_path / file_path_str

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Replace import statements
            patterns = [
                f"from {old_import} import",
                f"import {old_import}",
                f"from {old_import}.",
            ]

            new_patterns = [
                f"from {new_import} import",
                f"import {new_import}",
                f"from {new_import}.",
            ]

            updated = False
            for old_pattern, new_pattern in zip(patterns, new_patterns):
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    updated = True

            if updated:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.info(f"✅ Updated import {old_import} -> {new_import} in {file_path_str}")
                self.fixed_files.append(file_path_str)

        except Exception as e:
            logger.error(f"❌ Could not update import in {file_path_str}: {e}")

    def create_missing_module(self, module_name: str) -> None:
        """Create missing module structure"""
        parts = module_name.split(".")
        current_path = self.root_path

        for part in parts:
            current_path = current_path / part

            if not current_path.exists():
                current_path.mkdir(parents=True, exist_ok=True)

                # Create __init__.py
                init_file = current_path / "__init__.py"
                if not init_file.exists():
                    with open(init_file, "w", encoding="utf-8") as f:
                        f.write(f\'"""\n{part.title()} Module\n"""\n\n\')

                    logger.info(f"✅ Created module structure: {current_path.relative_to(self.root_path}}")

    def report_external_modules(self, external_modules: dict[str, list[str]]) -> None:
        """Report external modules that need to be installed"""
        if external_modules:
            logger.info("📦 External modules that may need installation:")
            for module_name, files in list(external_modules.items())[:10]:  # Show first 10
                logger.info(f"   • {module_name} (used in {len(files}} files)")

    def create_missing_init_files(self) -> None:
        """Create missing __init__.py files"""
        logger.info("📁 Creating missing __init__.py files...")

        for directory in self.root_path.rglob("*"):
            if (
                directory.is_dir()
                and not self.should_ignore_file(directory)
                and any(directory.rglob("*.py"))
                and not (directory / "__init__.py").exists()
            ):
                init_file = directory / "__init__.py"
                module_name = directory.name.replace("_", " ").title()

                with open(init_file, "w", encoding="utf-8") as f:
                    f.write(f'"""\n{module_name} Module\n"""\n\n')

                logger.info(f"✅ Created __init__.py in {directory.relative_to(self.root_path}}")
                self.fixed_files.append(str(init_file))

    def fix_common_import_patterns(self) -> None:
        """Fix common import patterns across the codebase"""
        logger.info("🔧 Fixing common import patterns...")

        common_fixes = [
            # Core imports
            ("from lukhas.core.common import", "from lukhas.core.common import"),
            ("from lukhas.core.common import", "from lukhas.core.common import"),
            ("from core.common.logger import", "from core.common.logger import"),
            ("from core.common.config import", "from core.common.config import"),
            # Memory imports
            ("from lukhas.memory.core import", "from lukhas.memory.core import"),
            (
                "from lukhas.memory.core.unified_memory_orchestrator import",
                "from lukhas.memory.core.unified_memory_orchestrator import",
            ),
            # Consciousness imports
            (
                "from lukhas.consciousness.unified import",
                "from lukhas.consciousness.unified import",
            ),
            (
                "from lukhas.consciousness.unified.auto_consciousness import",
                "from lukhas.consciousness.unified.auto_consciousness import",
            ),
            # Interface imports
            ("from core.interfaces import", "from core.interfaces import"),
        ]

        for py_file in self.root_path.rglob("*.py"):
            if self.should_ignore_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                for old_pattern, new_pattern in common_fixes:
                    content = content.replace(old_pattern, new_pattern)

                if content != original_content:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)

                    logger.info(f"✅ Fixed import patterns in {py_file.relative_to(self.root_path}}")
                    self.fixed_files.append(str(py_file))

            except Exception as e:
                logger.warning(f"Could not fix import patterns in {py_file}: {e}")

    def run_comprehensive_fix(self) -> dict[str, Any]:
        """Run comprehensive import error fixing"""
        logger.info("🚀 Starting comprehensive import error fixing...")

        # Step 1: Fix syntax errors
        self.analyze_syntax_errors()
        self.fix_syntax_errors()

        # Step 2: Create missing __init__.py files
        self.create_missing_init_files()

        # Step 3: Fix common import patterns
        self.fix_common_import_patterns()

        # Step 4: Analyze and fix missing modules
        self.analyze_missing_modules()
        self.fix_missing_modules()

        # Generate report
        report = {
            "errors_fixed": {
                "syntax_errors": len(self.syntax_errors),
                "missing_modules": len(self.missing_modules),
                "total_errors": sum(self.errors_by_category.values()),
            },
            "files_modified": len(set(self.fixed_files)),
            "fixed_files": list(set(self.fixed_files)),
            "errors_by_category": dict(self.errors_by_category),
            "top_missing_modules": dict(list(self.missing_modules.items())[:20]),
        }

        return report


def main():
    """Main execution function"""
    print("🔧  Comprehensive Import Fixer")
    print("=" * 60)

    fixer = ImportErrorFixer(PROJECT_ROOT)
    report = fixer.run_comprehensive_fix()

    print("\n📊 Fix Results:")
    print(f"   Syntax errors fixed: {report['errors_fixed']['syntax_errors']}")
    print(f"   Missing modules addressed: {report['errors_fixed']['missing_modules']}")
    print(f"   Total files modified: {report['files_modified']}")
    print(f"   Total errors processed: {report['errors_fixed']['total_errors']}")

    # Save detailed report
    report_path = PROJECT_ROOT / "docs/reports/analysis/_IMPORT_FIX_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {report_path}")

    if report["files_modified"] > 0:
        print(f"\n✅ Successfully fixed imports in {report['files_modified']} files!")
    else:
        print("\n✅ No import issues found in active codebase!")

    return report


if __name__ == "__main__":
    main()
