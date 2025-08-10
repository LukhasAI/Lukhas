#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Path Validation Tool

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

This tool validates import paths, detects circular dependencies, and checks
module integrity.
"""

import ast
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

# Using built-in collections instead of networkx for dependency management

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportAnalyzer:
    """Analyzes Python imports and dependencies."""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.imports = defaultdict(set)
        self.errors = []
        self.dependency_graph = defaultdict(set)  # module -> set of dependencies

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze imports in a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

            return {"file": str(file_path), "imports": list(imports), "valid": True}

        except Exception as e:
            error = f"Error analyzing {file_path}: {e}"
            self.errors.append(error)
            logger.warning(error)
            return {
                "file": str(file_path),
                "imports": [],
                "valid": False,
                "error": str(e),
            }

    def build_dependency_graph(self) -> Dict:
        """Build dependency graph from all Python files."""
        logger.info("Building dependency graph...")

        # Find all Python files
        python_files = list(self.root_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")

        all_imports = {}

        for py_file in python_files:
            # Skip __pycache__ and .git directories
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue

            # Get relative path for module identification
            try:
                rel_path = py_file.relative_to(self.root_path)
                module_name = str(rel_path).replace("/", ".").replace(".py", "")

                # Analyze imports
                file_analysis = self.analyze_file(py_file)
                all_imports[module_name] = file_analysis

                # Add to dependency graph
                for imp in file_analysis["imports"]:
                    # Filter for local imports (lukhas.*)
                    if imp.startswith("lukhas") or imp.startswith("."):
                        self.dependency_graph[module_name].add(imp)

            except Exception as e:
                self.errors.append(f"Error processing {py_file}: {e}")

        return all_imports

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle - extract it
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor in self.dependency_graph:  # Only follow local modules
                    dfs(neighbor, path + [node])

            rec_stack.remove(node)

        # Check all nodes
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def validate_import_paths(self, imports_data: Dict) -> Dict:
        """Validate that all import paths exist and are accessible."""
        validation_results = {
            "valid_imports": 0,
            "invalid_imports": 0,
            "missing_modules": [],
            "broken_imports": [],
        }

        for module, data in imports_data.items():
            if not data["valid"]:
                continue

            for imp in data["imports"]:
                # Check if import path exists for local modules
                if imp.startswith("lukhas"):
                    # Convert import to file path
                    imp_path = self.root_path / (imp.replace(".", "/") + ".py")

                    if imp_path.exists():
                        validation_results["valid_imports"] += 1
                    else:
                        validation_results["invalid_imports"] += 1
                        validation_results["missing_modules"].append(
                            {
                                "module": module,
                                "missing_import": imp,
                                "expected_path": str(imp_path),
                            }
                        )
                else:
                    # External import - assume valid
                    validation_results["valid_imports"] += 1

        return validation_results


class PathValidator:
    """Main path validation orchestrator."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.analyzer = ImportAnalyzer(self.root_path)

    def run_validation(self) -> Dict:
        """Run complete path validation suite."""
        logger.info("Starting LUKHAS path validation...")

        results = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "root_path": str(self.root_path),
            "validation_status": "running",
        }

        try:
            # 1. Build dependency graph
            imports_data = self.analyzer.build_dependency_graph()
            results["total_modules"] = len(imports_data)

            # 2. Find circular dependencies
            cycles = self.analyzer.find_circular_dependencies()
            results["circular_dependencies"] = {
                "count": len(cycles),
                "cycles": cycles[:10],  # Limit to first 10 for readability
            }

            # 3. Validate import paths
            path_validation = self.analyzer.validate_import_paths(imports_data)
            results["path_validation"] = path_validation

            # 4. Error summary
            results["errors"] = {
                "count": len(self.analyzer.errors),
                "details": self.analyzer.errors[:20],  # Limit for readability
            }

            # 5. Overall status
            if cycles:
                results["validation_status"] = "warning_circular_deps"
            elif path_validation["invalid_imports"] > 0:
                results["validation_status"] = "warning_broken_imports"
            elif self.analyzer.errors:
                results["validation_status"] = "warning_parse_errors"
            else:
                results["validation_status"] = "passed"

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            results["validation_status"] = "failed"
            results["error"] = str(e)

        return results

    def generate_report(self, output_path: str = None) -> str:
        """Generate human-readable validation report."""
        results = self.run_validation()

        report = f"""# LUKHAS Path Validation Report

**Generated**: {results.get('timestamp', 'unknown')}
**Status**: {results['validation_status'].upper()}

## Summary

- **Total Modules**: {results.get('total_modules', 0)}
- **Circular Dependencies**: {results.get('circular_dependencies', {}).get('count', 0)}
- **Import Errors**: {results.get('errors', {}).get('count', 0)}

## Path Validation Results

"""

        if "path_validation" in results:
            pv = results["path_validation"]
            report += f"""- **Valid Imports**: {pv.get('valid_imports', 0)}
- **Invalid Imports**: {pv.get('invalid_imports', 0)}
- **Missing Modules**: {len(pv.get('missing_modules', []))}

"""

        # Circular dependencies section
        cycles = results.get("circular_dependencies", {}).get("cycles", [])
        if cycles:
            report += f"""## ⚠️ Circular Dependencies Found

{len(cycles)} circular dependency cycles detected:

"""
            for i, cycle in enumerate(cycles[:5]):  # Show first 5
                report += f"{i+1}. {' → '.join(cycle)}\n"

            if len(cycles) > 5:
                report += f"\n... and {len(cycles) - 5} more cycles.\n"
        else:
            report += (
                "## ✅ No Circular Dependencies\n\nAll import paths are acyclic.\n"
            )

        # Missing imports section
        missing = results.get("path_validation", {}).get("missing_modules", [])
        if missing:
            report += "\n## ❌ Missing Import Paths\n\n"
            for miss in missing[:10]:  # Show first 10
                report += f"- **{miss['module']}** imports `{miss['missing_import']}` (expected: {miss['expected_path']})\n"

            if len(missing) > 10:
                report += f"\n... and {len(missing) - 10} more missing imports.\n"

        # Errors section
        errors = results.get("errors", {}).get("details", [])
        if errors:
            report += "\n## 🔍 Parse Errors\n\n"
            for error in errors[:5]:  # Show first 5
                report += f"- {error}\n"

            if len(errors) > 5:
                report += f"\n... and {len(errors) - 5} more errors.\n"

        # Recommendations
        report += """
## Recommendations

"""
        if cycles:
            report += (
                "1. **Resolve circular dependencies** by refactoring import structure\n"
            )
        if missing:
            report += "2. **Fix missing import paths** or update import statements\n"
        if errors:
            report += "3. **Review syntax errors** in files that failed to parse\n"

        if results["validation_status"] == "passed":
            report += "✅ All validation checks passed! The codebase has healthy import structure.\n"

        # Save report if output path provided
        if output_path:
            with open(output_path, "w") as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")

        return report


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate LUKHAS import paths and dependencies"
    )
    parser.add_argument("--root", default=".", help="Root directory to analyze")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--json", help="Output JSON results to file")

    args = parser.parse_args()

    validator = PathValidator(args.root)

    if args.json:
        results = validator.run_validation()
        with open(args.json, "w") as f:
            json.dump(results, f, indent=2)
        print(f"JSON results saved to {args.json}")

    report = validator.generate_report(args.output)

    if not args.output:
        print(report)


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
