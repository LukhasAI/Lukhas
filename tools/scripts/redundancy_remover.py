#!/usr/bin/env python3
from typing import Dict
from typing import List
from typing import Optional
"""
 Redundancy Remover
=====================
Safely removes identified redundant code while preserving functionality.
"""

import ast
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class RedundancyRemover:
    """Safely removes redundant code"""

    def __init__(self, dry_run: bool = True):
        self.root_path = Path("/Users/agi_dev/Lukhas")
        self.dry_run = dry_run
        self.backup_dir = self.root_path / ".redundancy_backup" / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.removed_count = 0
        self.modified_files = set()

    def remove_duplicate_logger_setup(self):
        """Replace redundant logger setup with common utility"""
        logger.info("\n🔧 Removing duplicate logger setup code...")

        pattern_variations = [
            # Pattern 1: Direct getLogger
            (
                r"logger = logging\.getLogger\(__name__\)",
                "logger = get_logger(__name__)",
            ),
            # Pattern 2: With handler setup
            (
                r"logger = logging\.getLogger\(__name__\)\s*\n\s*handler = \
    logging\.StreamHandler.*\n.*formatter.*\n.*setFormatter.*\n.*addHandler.*",
                "logger = get_logger(__name__)",
            ),
            # Pattern 3: get_logger function definitions
            (
                r"def get_logger\(.*?\):\s*\n(?:.*\n)*?.*return logger",
                None,  # Remove entirely, use common version
            ),
        ]

        files_to_update = []

        # Find files with logger setup
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                if "getLogger" in content or "get_logger" in content:
                    files_to_update.append(py_file)

            except Exception:
                pass

        logger.info(f"   Found {len(files_to_update)} files with logger setup")

        # Process each file
        import re

        modified = 0
        for py_file in files_to_update[:50]:  # Limit for safety
            try:
                with open(py_file, encoding="utf-8") as f:
                    original_content = f.read()

                content = original_content
                needs_import = False

                # Apply patterns
                for pattern, replacement in pattern_variations:
                    if re.search(pattern, content):
                        if replacement:
                            content = re.sub(pattern, replacement, content)
                            needs_import = True
                        else:
                            # Remove the function definition
                            content = re.sub(pattern, "", content)

                # Add import if needed
                if needs_import and "from system.common.utils import get_logger" not in content:
                    # Add import after other imports
                    lines = content.split("\n")
                    import_added = False

                    for i, line in enumerate(lines):
                        if (line.startswith("import ") or line.startswith("from ")) and not import_added:
                            # Find end of import block
                            j = i
                            while j < len(lines) and (
                                lines[j].startswith(("import ", "from ")) or lines[j].strip() == ""
                            ):
                                j += 1
                            lines.insert(j, "from system.common.utils import get_logger")
                            import_added = True
                            break

                    if not import_added and len(lines) > 3:
                        # Add after docstring
                        lines.insert(3, "from system.common.utils import get_logger\n")

                    content = "\n".join(lines)

                # Save if changed
                if content != original_content:
                    if not self.dry_run:
                        self._backup_file(py_file)
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(content)

                    self.modified_files.add(py_file)
                    modified += 1
                    logger.info(
                        f"   {'Would modify' if self.dry_run else 'Modified'}: {py_file.relative_to(self.root_path)}"
                    )

            except Exception as e:
                logger.warning(f"   Error processing {py_file}: {e}")

        logger.info(f"   {'Would modify' if self.dry_run else 'Modified'} {modified} files")
        self.removed_count += modified

    def remove_duplicate_functions(self):
        """Remove exact duplicate function definitions"""
        logger.info("\n🔧 Removing exact duplicate functions...")

        # Load streamline report
        report_path = self.root_path / "docs" / "reports" / "_STREAMLINE_REPORT.json"
        if not report_path.exists():
            logger.warning("   Streamline report not found")
            return

        with open(report_path) as f:
            report = json.load(f)

        duplicate_functions = report["findings"]["duplicate_functions"]

        # Process duplicates by module
        removed = 0
        for dup_group in duplicate_functions[:20]:  # Limit for safety
            occurrences = dup_group["occurrences"]
            if len(occurrences) < 2:
                continue

            # Keep the first occurrence, remove others
            occurrences[0]

            for dup in occurrences[1:]:
                file_path = self.root_path / dup["file"]
                if self._remove_function_from_file(file_path, dup["name"], dup["lines"]):
                    removed += 1
                    logger.info(f"   {'Would remove' if self.dry_run else 'Removed'} {dup['name']} from {dup['file']}")

        logger.info(f"   {'Would remove' if self.dry_run else 'Removed'} {removed} duplicate functions")
        self.removed_count += removed

    def consolidate_imports(self):
        """Consolidate common imports"""
        logger.info("\n🔧 Consolidating common imports...")

        # Common imports to consolidate
        common_imports = {
            "typing": ["Dict", "List", "Optional", "Any", "Tuple", "Set"],
            "pathlib": ["Path"],
            "datetime": ["datetime", "timezone"],
            "dataclasses": ["dataclass", "field"],
            "abc": ["ABC", "abstractmethod"],
            "asyncio": ["asyncio"],
            "json": ["json"],
            "logging": ["logging"],
        }

        consolidated = 0
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                new_lines = []
                import_section = []
                in_imports = False
                imports_dict = {}

                for line in lines:
                    if line.startswith(("import ", "from ")):
                        in_imports = True
                        # Parse import
                        if line.startswith("from"):
                            parts = line.split()
                            if len(parts) >= 4 and parts[2] == "import":
                                module = parts[1]
                                imports = " ".join(parts[3:])
                                if module not in imports_dict:
                                    imports_dict[module] = []
                                imports_dict[module].append(imports)
                        else:
                            import_section.append(line)
                    else:
                        if in_imports and line.strip() and not line.startswith(("import ", "from ")):
                            # End of import section
                            in_imports = False
                            # Write consolidated imports
                            for module, imports in sorted(imports_dict.items()):
                                if module in common_imports:
                                    # Consolidate
                                    all_imports = set()
                                    for imp_line in imports:
                                        all_imports.update(imp.strip() for imp in imp_line.split(","))
                                    if all_imports:
                                        new_lines.append(f"from {module} import {', '.join(sorted(all_imports))}")
                                else:
                                    for imp in imports:
                                        new_lines.append(f"from {module} import {imp}")
                            new_lines.extend(import_section)
                            new_lines.append(line)
                        else:
                            if not in_imports:
                                new_lines.append(line)

                new_content = "\n".join(new_lines)
                if new_content != content:
                    if not self.dry_run:
                        self._backup_file(py_file)
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(new_content)

                    self.modified_files.add(py_file)
                    consolidated += 1

            except Exception:
                pass

        logger.info(f"   {'Would consolidate' if self.dry_run else 'Consolidated'} imports in {consolidated} files")

    def remove_unused_imports(self):
        """Remove unused imports"""
        logger.info("\n🔧 Removing unused imports...")

        cleaned = 0
        for py_file in list(self.root_path.rglob("*.py"))[:100]:  # Limit for safety
            if self._should_skip_file(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST
                tree = ast.parse(content)

                # Find all imports
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split(".")[0])

                # Find all names used
                used_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)

                # Check which imports are unused
                unused = imports - used_names

                if unused and len(unused) < len(imports):  # Don't remove all imports
                    logger.info(f"   Found {len(unused)} unused imports in {py_file.relative_to(self.root_path)}")
                    cleaned += 1

            except Exception:
                pass

        logger.info(f"   Found {cleaned} files with unused imports")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            "__pycache__",
            ".git",
            "archive",
            "backup",
            ".streamline_backup",
            ".redundancy_backup",
            "test_",
            "tests/",
            "examples/",
            "docs/",
        ]

        str_path = str(file_path)
        return any(pattern in str_path for pattern in skip_patterns)

    def _backup_file(self, file_path: Path):
        """Backup a file before modification"""
        if self.dry_run:
            return

        relative_path = file_path.relative_to(self.root_path)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)

    def _remove_function_from_file(self, file_path: Path, func_name: str, lines: tuple[int, int]) -> bool:
        """Remove a function from a file"""
        if not file_path.exists():
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                content_lines = f.readlines()

            # Remove the function lines
            start_line = lines[0] - 1  # Convert to 0-based
            end_line = lines[1] if lines[1] else lines[0]

            # Find the actual end of the function (including any trailing whitespace)
            while end_line < len(content_lines) and content_lines[end_line].strip() == "":
                end_line += 1

            # Remove the lines
            new_content_lines = content_lines[:start_line] + content_lines[end_line:]

            if not self.dry_run:
                self._backup_file(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_content_lines)

            self.modified_files.add(file_path)
            return True

        except Exception as e:
            logger.warning(f"   Error removing function from {file_path}: {e}")
            return False

    def generate_report(self):
        """Generate removal report"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": self.dry_run,
            "removed_count": self.removed_count,
            "modified_files": len(self.modified_files),
            "backup_location": str(self.backup_dir) if not self.dry_run else None,
            "files_modified": [str(f.relative_to(self.root_path)) for f in sorted(self.modified_files)][:50],
        }

        report_path = self.root_path / "docs" / "reports" / "redundancy_removal_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def run(self):
        """Run redundancy removal"""
        logger.info(f"🧹 Starting Redundancy Removal {'(DRY RUN)' if self.dry_run else ''}")
        logger.info("=" * 80)

        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Backup directory: {self.backup_dir}")

        # Run removal operations
        self.remove_duplicate_logger_setup()
        self.remove_duplicate_functions()
        self.consolidate_imports()
        self.remove_unused_imports()

        # Generate report
        self.generate_report()

        logger.info("\n" + "=" * 80)
        logger.info("📊 REMOVAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'ACTUAL REMOVAL'}")
        logger.info(f"Total removals: {self.removed_count}")
        logger.info(f"Files modified: {len(self.modified_files)}")
        if not self.dry_run:
            logger.info(f"Backup location: {self.backup_dir}")
        logger.info("Report saved: docs/reports/redundancy_removal_report.json")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were actually modified.")
            logger.info("   To perform actual removal, run with: --no-dry-run")

        logger.info("=" * 80)


def main():
    """Run redundancy remover"""
    import sys

    dry_run = "--no-dry-run" not in sys.argv

    if not dry_run:
        response = input("⚠️  This will modify files. Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    remover = RedundancyRemover(dry_run=dry_run)
    remover.run()


if __name__ == "__main__":
    main()