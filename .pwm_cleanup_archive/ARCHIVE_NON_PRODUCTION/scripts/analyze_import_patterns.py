#!/usr/bin/env python3
"""
Analyze import patterns in the codebase to understand migration needs
"""

import ast
import json
import logging
from collections import defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ImportAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.import_patterns = defaultdict(set)
        self.file_imports = defaultdict(list)
        self.potential_old_imports = []
        self.module_locations = {}

    def analyze(self):
        """Run complete import analysis"""
        logger.info("Starting import pattern analysis...")

        # First, map all current module locations
        self._map_current_modules()

        # Then analyze all imports
        self._analyze_all_imports()

        # Identify potential old import patterns
        self._identify_old_patterns()

        # Generate report
        self._generate_report()

    def _map_current_modules(self):
        """Map all current Python modules and their locations"""
        logger.info("Mapping current module locations...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            # Get module name from file
            module_name = self._get_module_from_file(py_file)
            if module_name:
                relative_path = py_file.relative_to(self.root_path)
                self.module_locations[module_name] = str(relative_path)

        logger.info(f"Found {len(self.module_locations)} modules")

    def _get_module_from_file(self, file_path: Path) -> str:
        """Extract main class/module name from file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            # Look for classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    return node.name

            # If no class, use filename
            return file_path.stem

        except:
            return file_path.stem

    def _analyze_all_imports(self):
        """Analyze all import statements in the codebase"""
        logger.info("Analyzing import statements...")

        py_files = list(self.root_path.rglob("*.py"))

        for i, py_file in enumerate(py_files):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(py_files)} files")

            if self._should_skip(py_file):
                continue

            self._analyze_file_imports(py_file)

    def _analyze_file_imports(self, file_path: Path):
        """Analyze imports in a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            relative_path = file_path.relative_to(self.root_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = {
                            "type": "import",
                            "module": alias.name,
                            "line": node.lineno,
                            "file": str(relative_path),
                        }
                        self.import_patterns[alias.name].add(str(relative_path))
                        self.file_imports[str(relative_path)].append(import_info)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_info = {
                            "type": "from",
                            "module": node.module,
                            "names": [n.name for n in node.names],
                            "line": node.lineno,
                            "file": str(relative_path),
                        }
                        self.import_patterns[node.module].add(str(relative_path))
                        self.file_imports[str(relative_path)].append(import_info)

        except Exception as e:
            logger.debug(f"Error analyzing {file_path}: {e}")

    def _identify_old_patterns(self):
        """Identify imports that might be using old paths"""
        logger.info("Identifying potential old import patterns...")

        # Common old patterns
        old_prefixes = ["lukhas.", "src.", "lib.", "modules."]

        for module, files in self.import_patterns.items():
            # Check if import doesn't resolve to current module
            is_external = any(
                module.startswith(ext)
                for ext in [
                    "numpy",
                    "pandas",
                    "torch",
                    "tensorflow",
                    "sklearn",
                    "matplotlib",
                    "os",
                    "sys",
                    "json",
                    "logging",
                ]
            )

            if is_external:
                continue

            # Check if module path doesn't exist
            module_file = module.replace(".", "/") + ".py"
            if not (self.root_path / module_file).exists():
                # Check without .py
                module_dir = module.replace(".", "/")
                if not (self.root_path / module_dir).exists():
                    # This might be an old import
                    self.potential_old_imports.append(
                        {"module": module, "used_in": list(files), "count": len(files)}
                    )

            # Check for old prefixes
            for prefix in old_prefixes:
                if module.startswith(prefix):
                    self.potential_old_imports.append(
                        {
                            "module": module,
                            "used_in": list(files),
                            "count": len(files),
                            "pattern": prefix,
                        }
                    )
                    break

    def _generate_report(self):
        """Generate analysis report"""
        report = {
            "total_files_analyzed": len(self.file_imports),
            "total_import_statements": sum(
                len(imports) for imports in self.file_imports.values()
            ),
            "unique_modules_imported": len(self.import_patterns),
            "potential_old_imports": len(self.potential_old_imports),
            "old_import_details": sorted(
                self.potential_old_imports, key=lambda x: x["count"], reverse=True
            )[:50],
            "module_locations": self.module_locations,
        }

        # Save report
        output_dir = self.root_path / "scripts" / "import_migration"
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "import_analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Generate human-readable summary
        summary = f"""
Import Pattern Analysis Summary
==============================

Total Files Analyzed: {report['total_files_analyzed']}
Total Import Statements: {report['total_import_statements']}
Unique Modules Imported: {report['unique_modules_imported']}
Potential Old Imports: {report['potential_old_imports']}

Top Old Import Patterns Found:
"""

        for old_import in report["old_import_details"][:20]:
            summary += (
                f"\n- {old_import['module']} (used in {old_import['count']} files)"
            )
            if "pattern" in old_import:
                summary += f" [Pattern: {old_import['pattern']}]"

        with open(output_dir / "import_analysis_summary.txt", "w") as f:
            f.write(summary)

        logger.info(f"Analysis complete! Reports saved to {output_dir}")
        print(summary)

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
            "scripts",
            "visualizations",
            "analysis_output",
        }

        return any(part in skip_dirs for part in path.parts)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze import patterns in Python codebase"
    )
    parser.add_argument("path", nargs="?", default=".", help="Root path to analyze")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    analyzer = ImportAnalyzer(root_path)
    analyzer.analyze()


if __name__ == "__main__":
    main()
