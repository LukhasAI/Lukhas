#!/usr/bin/env python3
"""
Fix common import patterns based on codebase structure
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CommonPatternFixer:
    def __init__(self, root_path: Path, dry_run: bool = True):
        self.root_path = root_path
        self.dry_run = dry_run
        self.fixes_applied = 0
        self.files_fixed = 0

    def fix_imports(self):
        """Fix common import patterns"""
        logger.info("Fixing common import patterns...")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE RUN'}")

        # Fix OpenAI imports
        self._fix_openai_imports()

        # Fix __future__ imports (these should stay but be at top)
        self._fix_future_imports()

        # Fix common internal patterns
        self._fix_common_patterns()

        logger.info(f"\nTotal fixes applied: {self.fixes_applied}")
        logger.info(f"Files fixed: {self.files_fixed}")

        if self.dry_run:
            logger.info("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("To apply changes, run with --fix flag")

    def _fix_openai_imports(self):
        """Fix OpenAI import issues"""
        logger.info("\nFixing OpenAI imports...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Check if file uses OpenAI but doesn't import it properly
                if "openai." in content or "OpenAI" in content:
                    # Check if import is missing
                    if "import openai" not in content and "from openai" not in content:
                        # Add import at the top after other imports
                        lines = content.split("\n")
                        import_added = False

                        for i, line in enumerate(lines):
                            # Find a good place to add the import
                            if line.startswith("import ") or line.startswith("from "):
                                # Find the last import
                                j = i
                                while j < len(lines) - 1 and (
                                    lines[j + 1].startswith("import ")
                                    or lines[j + 1].startswith("from ")
                                ):
                                    j += 1
                                # Add OpenAI import after last import
                                lines.insert(j + 1, "import openai")
                                import_added = True
                                break

                        if import_added:
                            content = "\n".join(lines)

                if content != original_content:
                    if not self.dry_run:
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(content)

                    self.files_fixed += 1
                    self.fixes_applied += 1
                    logger.debug(f"Fixed OpenAI import in {py_file.name}")

            except Exception as e:
                if "utf-8" not in str(e):
                    logger.error(f"Error processing {py_file}: {e}")

    def _fix_future_imports(self):
        """Ensure __future__ imports are at the top of files"""
        logger.info("\nFixing __future__ import placement...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()

                # Find __future__ imports
                future_imports = []
                other_lines = []

                for line in lines:
                    if line.strip().startswith("from __future__ import"):
                        future_imports.append(line)
                    else:
                        other_lines.append(line)

                if future_imports:
                    # Reconstruct file with __future__ at top
                    new_lines = []

                    # Add shebang and docstring first if they exist
                    i = 0
                    while i < len(other_lines):
                        line = other_lines[i]
                        if i == 0 and line.startswith("#!"):
                            new_lines.append(line)
                            i += 1
                        elif line.strip().startswith('"""') or line.strip().startswith(
                            "'''"
                        ):
                            # Add docstring
                            new_lines.append(line)
                            i += 1
                            # Find end of docstring
                            if not (
                                line.strip().endswith('"""')
                                or line.strip().endswith("'''")
                            ):
                                while i < len(other_lines):
                                    new_lines.append(other_lines[i])
                                    if other_lines[i].strip().endswith(
                                        '"""'
                                    ) or other_lines[i].strip().endswith("'''"):
                                        i += 1
                                        break
                                    i += 1
                        else:
                            break

                    # Add blank line if needed
                    if new_lines and not new_lines[-1].strip() == "":
                        new_lines.append("\n")

                    # Add __future__ imports
                    new_lines.extend(future_imports)

                    # Add rest of file
                    new_lines.extend(other_lines[i:])

                    # Check if we changed anything
                    if new_lines != lines:
                        if not self.dry_run:
                            with open(py_file, "w", encoding="utf-8") as f:
                                f.writelines(new_lines)

                        self.files_fixed += 1
                        self.fixes_applied += 1
                        logger.debug(
                            f"Fixed __future__ import placement in {py_file.name}"
                        )

            except Exception as e:
                if "utf-8" not in str(e):
                    logger.error(f"Error processing {py_file}: {e}")

    def _fix_common_patterns(self):
        """Fix other common import patterns"""
        logger.info("\nFixing common import patterns...")

        mappings = {
            # Fix any remaining standalone function imports
            r"^import (create_\w+)$": r"# TODO: Fix import \1",
            # Fix common typos and patterns
            "from dream.systems.advanced_dream_engine": "from creativity.dream.engine.advanced_dream_engine",
            "from dream.quantum_dream_adapter": "from creativity.dream.quantum_dream_adapter",
            "from dream.core": "from creativity.dream.core",
            # Fix voice imports
            "from voice.voice_integrator": "from learning.systems.voice_duet",
            # Fix any remaining old patterns
            "from lukhas": "from core",
            "import lukhas": "import core",
        }

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
                    if old_pattern.startswith("^"):
                        # Regex pattern
                        new_content, count = re.subn(
                            old_pattern, new_pattern, content, flags=re.MULTILINE
                        )
                        if count > 0:
                            content = new_content
                            file_fixes += count
                    else:
                        # Simple string replacement
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

            except Exception as e:
                if "utf-8" not in str(e):
                    logger.error(f"Error processing {py_file}: {e}")

        if fixed_count > 0:
            logger.info(f"  Fixed {fixed_count} import patterns")

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

    parser = argparse.ArgumentParser(description="Fix common import patterns")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default is dry run)"
    )
    parser.add_argument(
        "--path", default=".", help="Root path (default: current directory)"
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    fixer = CommonPatternFixer(root_path, dry_run=not args.fix)
    fixer.fix_imports()


if __name__ == "__main__":
    main()
