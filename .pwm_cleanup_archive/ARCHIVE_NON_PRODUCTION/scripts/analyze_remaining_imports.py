#!/usr/bin/env python3
"""
Analyze remaining broken imports to find patterns we can fix
"""

import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RemainingImportAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.broken_patterns = defaultdict(list)
        self.single_imports = defaultdict(list)
        self.missing_modules = Counter()

    def analyze(self):
        """Analyze remaining broken imports"""
        logger.info("Analyzing remaining broken imports...")

        # Load the broken imports report
        report_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "broken_imports_report.json"
        )
        if not report_path.exists():
            logger.error(
                "No broken imports report found. Run find_broken_imports.py first."
            )
            return

        with open(report_path) as f:
            report = json.load(f)

        # Analyze patterns
        self._analyze_patterns()

        # Generate actionable report
        self._generate_actionable_report()

    def _analyze_patterns(self):
        """Analyze import patterns in detail"""
        logger.info("Analyzing import patterns in Python files...")

        # Common external packages to skip
        external_packages = {
            "os",
            "sys",
            "json",
            "logging",
            "typing",
            "datetime",
            "pathlib",
            "collections",
            "re",
            "asyncio",
            "threading",
            "time",
            "math",
            "random",
            "numpy",
            "pandas",
            "torch",
            "tensorflow",
            "sklearn",
            "matplotlib",
            "requests",
            "urllib",
            "pytest",
            "unittest",
            "structlog",
            "abc",
            "dataclasses",
            "enum",
            "functools",
            "itertools",
            "hashlib",
            "uuid",
            "traceback",
            "inspect",
            "copy",
            "pickle",
            "base64",
            "warnings",
            "setuptools",
            "pkg_resources",
            "importlib",
            "subprocess",
            "shutil",
            "tempfile",
            "contextlib",
            "weakref",
            "socket",
            "ssl",
            "http",
            "email",
            "csv",
            "sqlite3",
            "multiprocessing",
            "queue",
            "signal",
        }

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Find all imports
                import_patterns = [
                    (r"^import\s+(\w+)$", "single"),
                    (r"^from\s+([\w.]+)\s+import\s+([^#\n]+)$", "from"),
                ]

                for pattern, import_type in import_patterns:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        if import_type == "single":
                            module = match.group(1)
                            if (
                                module not in external_packages
                                and not self._module_exists(module)
                            ):
                                self.single_imports[module].append(
                                    {
                                        "file": str(
                                            py_file.relative_to(self.root_path)
                                        ),
                                        "line": content[: match.start()].count("\n")
                                        + 1,
                                    }
                                )
                        else:
                            module = match.group(1)
                            imports = match.group(2)

                            # Check if it's a broken import
                            base_module = module.split(".")[0]
                            if (
                                base_module not in external_packages
                                and not self._module_exists(module)
                            ):
                                self.broken_patterns[module].append(
                                    {
                                        "file": str(
                                            py_file.relative_to(self.root_path)
                                        ),
                                        "imports": imports.strip(),
                                        "line": content[: match.start()].count("\n")
                                        + 1,
                                    }
                                )

            except Exception as e:
                logger.debug(f"Error analyzing {py_file}: {e}")

    def _module_exists(self, module_path: str) -> bool:
        """Check if a module exists in the codebase"""
        # Convert module path to file path
        parts = module_path.split(".")

        # Check as .py file
        py_path = self.root_path / Path(*parts[:-1]) / f"{parts[-1]}.py"
        if py_path.exists():
            return True

        # Check as directory with __init__.py
        dir_path = self.root_path / Path(*parts)
        if dir_path.exists() and dir_path.is_dir():
            return True

        # Check if it's a class or function in a module
        if len(parts) > 1:
            parent_module = ".".join(parts[:-1])
            return self._module_exists(parent_module)

        return False

    def _generate_actionable_report(self):
        """Generate report with actionable fixes"""
        logger.info("Generating actionable report...")

        # Sort single imports by frequency
        single_import_counts = Counter()
        for module, occurrences in self.single_imports.items():
            single_import_counts[module] = len(occurrences)

        # Sort broken patterns by frequency
        pattern_counts = Counter()
        for pattern, occurrences in self.broken_patterns.items():
            pattern_counts[pattern] = len(occurrences)

        # Generate fix mappings
        fix_mappings = {}

        # Analyze single imports
        logger.info("\nTop single imports to fix:")
        for module, count in single_import_counts.most_common(20):
            logger.info(f"  {module}: {count} occurrences")

            # Try to find where this might be
            possible_locations = self._find_possible_locations(module)
            if possible_locations:
                fix_mappings[f"import {module}"] = (
                    f"from {possible_locations[0]} import {module}"
                )
                logger.info(
                    f"    -> Suggested fix: from {possible_locations[0]} import {module}"
                )

        # Analyze broken from imports
        logger.info("\nTop broken 'from' imports:")
        for pattern, count in pattern_counts.most_common(20):
            logger.info(f"  {pattern}: {count} occurrences")

            # Look for similar patterns that might be the correct path
            possible_fixes = self._suggest_fixes(pattern)
            if possible_fixes:
                logger.info(f"    -> Possible fixes: {possible_fixes}")

        # Save detailed report
        report = {
            "single_imports": {
                module: {"count": len(occurrences), "examples": occurrences[:3]}
                for module, occurrences in self.single_imports.items()
            },
            "broken_patterns": {
                pattern: {"count": len(occurrences), "examples": occurrences[:3]}
                for pattern, occurrences in self.broken_patterns.items()
            },
            "fix_mappings": fix_mappings,
        }

        output_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "remaining_imports_analysis.json"
        )
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\nDetailed report saved to: {output_path}")

    def _find_possible_locations(self, name: str) -> list:
        """Find possible locations for a class or function"""
        locations = []

        # Search for files containing this class or function
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check if this file defines the name
                if (
                    re.search(rf"^class {name}\b", content, re.MULTILINE)
                    or re.search(rf"^def {name}\b", content, re.MULTILINE)
                    or re.search(rf"^{name} =", content, re.MULTILINE)
                ):
                    # Convert file path to module path
                    relative = py_file.relative_to(self.root_path)
                    module_parts = list(relative.parts[:-1]) + [relative.stem]
                    module_path = ".".join(module_parts)
                    locations.append(module_path)

            except:
                pass

        return locations

    def _suggest_fixes(self, broken_module: str) -> list:
        """Suggest possible fixes for a broken module path"""
        suggestions = []

        # Common transformations
        parts = broken_module.split(".")

        # Try without first part (like removing 'src' or 'lib')
        if len(parts) > 1:
            without_first = ".".join(parts[1:])
            if self._module_exists(without_first):
                suggestions.append(without_first)

        # Try looking for the last part as a file
        if len(parts) > 1:
            last_part = parts[-1]
            possible_locs = self._find_possible_locations(last_part)
            suggestions.extend(possible_locs)

        return suggestions

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

    parser = argparse.ArgumentParser(description="Analyze remaining broken imports")
    parser.add_argument("path", nargs="?", default=".", help="Root path")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    analyzer = RemainingImportAnalyzer(root_path)
    analyzer.analyze()


if __name__ == "__main__":
    main()
