#!/usr/bin/env python3
"""
Find and report broken imports in the codebase
"""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BrokenImportFinder:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.broken_imports = defaultdict(list)
        self.import_errors = defaultdict(int)

        # Common external packages to skip
        self.external_packages = {
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
        }

    def find_broken_imports(self):
        """Find all broken imports in the codebase"""
        logger.info("Searching for broken imports...")

        py_files = list(self.root_path.rglob("*.py"))
        logger.info(f"Checking {len(py_files)} Python files...")

        for i, py_file in enumerate(py_files):
            if i % 200 == 0:
                logger.info(f"Progress: {i}/{len(py_files)}")

            if self._should_skip(py_file):
                continue

            self._check_file_imports(py_file)

        # Generate report
        self._generate_report()

    def _check_file_imports(self, file_path: Path):
        """Check imports in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Use regex to find imports (more reliable than AST for broken files)
            import_patterns = [
                (r"from\s+([\w.]+)\s+import\s+([^#\n]+)", "from"),
                (r"import\s+([\w.]+)(?:\s+as\s+\w+)?", "import"),
            ]

            relative_path = str(file_path.relative_to(self.root_path))

            for pattern, import_type in import_patterns:
                for match in re.finditer(pattern, content):
                    module = match.group(1)

                    # Skip external modules
                    if module.split(".")[0] in self.external_packages:
                        continue

                    # Check if import is broken
                    if not self._module_exists(module):
                        line_no = content[: match.start()].count("\n") + 1

                        self.broken_imports[relative_path].append(
                            {
                                "module": module,
                                "type": import_type,
                                "line": line_no,
                                "statement": match.group(0).strip(),
                            }
                        )

                        # Track error patterns
                        if module.startswith("lukhas."):
                            self.import_errors["lukhas_prefix"] += 1
                        elif "." not in module:
                            self.import_errors["single_module"] += 1
                        else:
                            self.import_errors["other"] += 1

        except Exception as e:
            logger.debug(f"Error checking {file_path}: {e}")

    def _module_exists(self, module_path: str) -> bool:
        """Check if a module path exists"""
        # Convert module path to file path
        path_parts = module_path.split(".")

        # Check as a .py file
        py_path = self.root_path / Path(*path_parts[:-1]) / f"{path_parts[-1]}.py"
        if py_path.exists():
            return True

        # Check as a directory with __init__.py
        dir_path = self.root_path / Path(*path_parts)
        if dir_path.exists() and (dir_path / "__init__.py").exists():
            return True

        # Check as just a directory (for namespace packages)
        if dir_path.exists() and dir_path.is_dir():
            return True

        return False

    def _generate_report(self):
        """Generate detailed report of broken imports"""
        # Calculate statistics
        total_broken = sum(len(imports) for imports in self.broken_imports.values())
        files_affected = len(self.broken_imports)

        # Group by module pattern
        pattern_groups = defaultdict(list)
        for file_path, imports in self.broken_imports.items():
            for imp in imports:
                module = imp["module"]
                if module.startswith("lukhas."):
                    pattern_groups["lukhas_prefix"].append((file_path, imp))
                elif module.startswith("core.memory"):
                    pattern_groups["core_memory"].append((file_path, imp))
                elif module.startswith("bio.") and module.count(".") > 1:
                    pattern_groups["bio_nested"].append((file_path, imp))
                else:
                    pattern_groups["other"].append((file_path, imp))

        # Save detailed report
        report = {
            "summary": {
                "total_broken_imports": total_broken,
                "files_affected": files_affected,
                "error_patterns": dict(self.import_errors),
            },
            "pattern_groups": {
                pattern: len(imports) for pattern, imports in pattern_groups.items()
            },
            "examples": {},
        }

        # Add examples from each pattern
        for pattern, imports in pattern_groups.items():
            report["examples"][pattern] = [
                {"file": imp[0], "import": imp[1]["statement"], "line": imp[1]["line"]}
                for imp in imports[:5]  # First 5 examples
            ]

        # Save report
        output_dir = self.root_path / "scripts" / "import_migration"
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "broken_imports_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 80)
        print("BROKEN IMPORTS ANALYSIS")
        print("=" * 80)
        print(f"Total broken imports: {total_broken}")
        print(f"Files affected: {files_affected}")
        print("\nPattern breakdown:")
        for pattern, count in report["pattern_groups"].items():
            print(f"  {pattern}: {count}")

        print("\nExample broken imports:")
        for pattern, examples in report["examples"].items():
            if examples:
                print(f"\n{pattern}:")
                for ex in examples[:2]:
                    print(f"  {ex['file']}:{ex['line']}")
                    print(f"    {ex['import']}")

        print(f"\nFull report saved to: {output_dir / 'broken_imports_report.json'}")

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

    parser = argparse.ArgumentParser(description="Find broken imports")
    parser.add_argument("path", nargs="?", default=".", help="Root path")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    finder = BrokenImportFinder(root_path)
    finder.find_broken_imports()


if __name__ == "__main__":
    main()
