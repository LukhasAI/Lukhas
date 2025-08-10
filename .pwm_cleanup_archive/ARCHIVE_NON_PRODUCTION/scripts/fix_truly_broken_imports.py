#!/usr/bin/env python3
"""
Fix truly broken imports based on validated report
"""

import json
import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TrulyBrokenImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

    def fix_imports(self):
        """Fix truly broken imports from validated report"""
        logger.info("Fixing truly broken imports...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Load the validated broken imports report
        report_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "validated_broken_imports.json"
        )
        if not report_path.exists():
            logger.error(
                "No validated broken imports report found. Run validate_real_broken_imports.py first."
            )
            return

        with open(report_path) as f:
            report = json.load(f)

        broken_imports = report.get("truly_broken", {})

        # Fix each file
        for file_path, imports in broken_imports.items():
            full_path = self.root_path / file_path
            if full_path.exists():
                self._fix_file(full_path, imports)

        logger.info(f"\nTotal fixes applied: {self.fixes_applied}")
        logger.info(f"Files fixed: {self.files_fixed}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_file(self, file_path: Path, broken_imports: list):
        """Fix broken imports in a specific file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            lines_to_remove = set()

            for imp in broken_imports:
                line_no = imp["line"] - 1  # Convert to 0-based index
                if 0 <= line_no < len(lines):
                    statement = imp["statement"]

                    # Handle different cases
                    if statement.endswith(" import"):
                        # Incomplete import, check context
                        module = imp["module"]

                        # Special handling for common patterns
                        if module == "dataclasses":
                            # Replace with complete import
                            lines[line_no] = (
                                "from dataclasses import dataclass, field\n"
                            )
                            modified = True
                            self.fixes_applied += 1
                            logger.debug(
                                f"Fixed dataclasses import in {file_path.name}"
                            )

                        elif module.startswith("."):
                            # Relative import - try to fix based on file location
                            if line_no + 1 < len(lines):
                                next_line = lines[line_no + 1].strip()
                                if next_line and not next_line.startswith(
                                    ("from", "import", "#", '"""', "'''")
                                ):
                                    # Next line might contain what to import
                                    if re.match(r"^[A-Z]\w*", next_line):
                                        # Looks like a class name
                                        lines[line_no] = (
                                            f"{statement} {next_line.split()[0]}\n"
                                        )
                                        modified = True
                                        self.fixes_applied += 1
                                    else:
                                        # Can't determine, comment it out
                                        lines[line_no] = (
                                            f"# {statement} # TODO: Fix incomplete import\n"
                                        )
                                        modified = True
                                        self.fixes_applied += 1
                                else:
                                    # Remove the incomplete import
                                    lines_to_remove.add(line_no)
                                    modified = True
                                    self.fixes_applied += 1
                            else:
                                # Last line, remove it
                                lines_to_remove.add(line_no)
                                modified = True
                                self.fixes_applied += 1

                        elif module == "core_documentation_updater":
                            # Fix known pattern
                            lines[line_no] = (
                                "from docs.documentation_updater import DocumentationUpdater\n"
                            )
                            modified = True
                            self.fixes_applied += 1

                        else:
                            # Comment out unclear imports
                            lines[line_no] = (
                                f"# {statement} # TODO: Fix incomplete import\n"
                            )
                            modified = True
                            self.fixes_applied += 1

            # Remove lines marked for removal (in reverse order to maintain indices)
            for line_no in sorted(lines_to_remove, reverse=True):
                del lines[line_no]

            if modified:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)

                self.files_fixed += 1
                relative_path = file_path.relative_to(self.root_path)
                logger.info(f"Fixed {relative_path}")

        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix truly broken imports")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = TrulyBrokenImportFixer(root_path, dry_run=not args.fix)
    fixer.fix_imports()


if __name__ == "__main__":
    main()
