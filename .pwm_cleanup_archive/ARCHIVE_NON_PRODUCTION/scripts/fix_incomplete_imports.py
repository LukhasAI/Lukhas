#!/usr/bin/env python3
"""
Fix incomplete import statements
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IncompleteImportFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

    def fix_imports(self):
        """Fix incomplete import statements"""
        logger.info("Fixing incomplete import statements...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            self._fix_file(py_file)

        logger.info(f"\nTotal fixes applied: {self.fixes_applied}")
        logger.info(f"Files fixed: {self.files_fixed}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_file(self, file_path: Path):
        """Fix incomplete imports in a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []
            i = 0

            while i < len(lines):
                line = lines[i]

                # Check for incomplete from imports
                if re.match(r"^from\s+[\w.]+\s+import\s*$", line.strip()):
                    # This is incomplete, check next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        # If next line is indented or starts with (, it's a continuation
                        if next_line.startswith(" ") or next_line.strip().startswith(
                            "("
                        ):
                            # Keep both lines
                            new_lines.append(line)
                        else:
                            # Remove incomplete import
                            logger.debug(
                                f"Removing incomplete import in {file_path.name}: {line.strip()}"
                            )
                            modified = True
                            self.fixes_applied += 1
                            i += 1
                            continue
                    else:
                        # Last line is incomplete, remove it
                        logger.debug(
                            f"Removing incomplete import at EOF in {file_path.name}: {line.strip()}"
                        )
                        modified = True
                        self.fixes_applied += 1
                        i += 1
                        continue

                # Check for incomplete import statements
                elif re.match(r"^import\s+[\w.]+\s*,\s*$", line.strip()):
                    # Import ending with comma, check next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if re.match(r"^\s*[\w.]+", next_line):
                            # It's a continuation
                            new_lines.append(line)
                        else:
                            # Remove trailing comma
                            new_line = re.sub(r",\s*$", "", line)
                            new_lines.append(new_line)
                            modified = True
                            self.fixes_applied += 1
                    else:
                        # Remove trailing comma
                        new_line = re.sub(r",\s*$", "", line)
                        new_lines.append(new_line)
                        modified = True
                        self.fixes_applied += 1

                # Check for "from module import" with nothing after
                elif re.match(r"^from\s+[\w.]+\s+import$", line.strip()):
                    # Check if it's actually incomplete or has continuation
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("("):
                        # It's a multi-line import
                        new_lines.append(line)
                    else:
                        # Remove incomplete import
                        logger.debug(
                            f"Removing incomplete 'from X import' in {file_path.name}: {line.strip()}"
                        )
                        modified = True
                        self.fixes_applied += 1
                        i += 1
                        continue

                # Check for standalone "import" or "from"
                elif line.strip() in ["import", "from"]:
                    logger.debug(
                        f"Removing standalone '{line.strip()}' in {file_path.name}"
                    )
                    modified = True
                    self.fixes_applied += 1
                    i += 1
                    continue

                else:
                    new_lines.append(line)

                i += 1

            if modified:
                if not self.dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                self.files_fixed += 1
                relative_path = file_path.relative_to(self.root_path)
                logger.info(f"Fixed {relative_path}")

        except Exception as e:
            if "utf-8" not in str(e):
                logger.error(f"Error processing {file_path}: {e}")

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

    parser = argparse.ArgumentParser(description="Fix incomplete import statements")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = IncompleteImportFixer(root_path, dry_run=not args.fix)
    fixer.fix_imports()


if __name__ == "__main__":
    main()
