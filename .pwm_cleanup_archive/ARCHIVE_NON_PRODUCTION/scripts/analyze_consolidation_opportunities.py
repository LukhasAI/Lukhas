#!/usr/bin/env python3
"""
Analyze codebase for consolidation and modularization opportunities
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


class ConsolidationAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.module_imports = defaultdict(set)  # What each module imports
        self.module_importers = defaultdict(set)  # Who imports each module
        self.internal_modules = set()
        self.file_to_classes = defaultdict(list)
        self.class_to_file = {}
        self.similar_files = []
        self.consolidation_candidates = []

    def analyze(self):
        """Run complete consolidation analysis"""
        logger.info("Starting consolidation analysis...")

        # Map all internal modules
        self._map_internal_modules()

        # Analyze import relationships
        self._analyze_import_relationships()

        # Find consolidation opportunities
        self._find_consolidation_opportunities()

        # Generate report
        self._generate_report()

    def _map_internal_modules(self):
        """Map all internal Python modules"""
        logger.info("Mapping internal modules...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            # Get module path
            try:
                relative = py_file.relative_to(self.root_path)
                module_path = ".".join(relative.parts[:-1] + (relative.stem,))
                self.internal_modules.add(module_path)

                # Extract classes from file
                with open(py_file, encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                self.file_to_classes[str(relative)].append(node.name)
                                self.class_to_file[node.name] = str(relative)
                    except:
                        pass

            except Exception as e:
                logger.debug(f"Error processing {py_file}: {e}")

        logger.info(f"Found {len(self.internal_modules)} internal modules")

    def _analyze_import_relationships(self):
        """Analyze who imports whom"""
        logger.info("Analyzing import relationships...")

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                relative = py_file.relative_to(self.root_path)
                module_path = ".".join(relative.parts[:-1] + (relative.stem,))

                with open(py_file, encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_internal_module(alias.name):
                                self.module_imports[module_path].add(alias.name)
                                self.module_importers[alias.name].add(module_path)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module and self._is_internal_module(node.module):
                            self.module_imports[module_path].add(node.module)
                            self.module_importers[node.module].add(module_path)

            except Exception as e:
                logger.debug(f"Error analyzing {py_file}: {e}")

    def _find_consolidation_opportunities(self):
        """Find opportunities for consolidation"""
        logger.info("Finding consolidation opportunities...")

        # 1. Find tightly coupled modules (high bidirectional imports)
        self._find_tightly_coupled_modules()

        # 2. Find modules with similar names
        self._find_similar_named_modules()

        # 3. Find small modules that could be merged
        self._find_small_modules()

        # 4. Find modules with circular dependencies
        self._find_circular_dependencies()

        # 5. Find duplicate or near-duplicate files
        self._find_duplicate_files()

    def _find_tightly_coupled_modules(self):
        """Find modules that import each other frequently"""
        couples = []

        for module1 in self.module_imports:
            for module2 in self.module_imports[module1]:
                # Check if they import each other
                if module1 in self.module_imports.get(module2, set()):
                    if module1 < module2:  # Avoid duplicates
                        couples.append(
                            {
                                "type": "tightly_coupled",
                                "modules": [module1, module2],
                                "reason": "Bidirectional imports indicate tight coupling",
                            }
                        )

        self.consolidation_candidates.extend(couples)

    def _find_similar_named_modules(self):
        """Find modules with similar names that might be consolidated"""
        from difflib import SequenceMatcher

        module_names = list(self.internal_modules)
        similar = []

        for i, mod1 in enumerate(module_names):
            for mod2 in module_names[i + 1 :]:
                # Get base names
                base1 = mod1.split(".")[-1]
                base2 = mod2.split(".")[-1]

                # Check similarity
                ratio = SequenceMatcher(None, base1.lower(), base2.lower()).ratio()
                if ratio > 0.8:  # 80% similar
                    similar.append(
                        {
                            "type": "similar_names",
                            "modules": [mod1, mod2],
                            "similarity": ratio,
                            "reason": f"Names are {ratio*100:.0f}% similar",
                        }
                    )

        self.consolidation_candidates.extend(similar)

    def _find_small_modules(self):
        """Find small modules that could be consolidated"""
        small_modules = defaultdict(list)

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                size = py_file.stat().st_size
                if size < 1000:  # Less than 1KB
                    relative = py_file.relative_to(self.root_path)
                    parent = relative.parts[0] if relative.parts else "root"

                    # Count meaningful lines
                    with open(py_file, encoding="utf-8") as f:
                        lines = f.readlines()
                        meaningful_lines = sum(
                            1
                            for line in lines
                            if line.strip() and not line.strip().startswith("#")
                        )

                    if meaningful_lines < 50:  # Less than 50 meaningful lines
                        small_modules[parent].append(
                            {
                                "file": str(relative),
                                "size": size,
                                "lines": meaningful_lines,
                                "classes": self.file_to_classes.get(str(relative), []),
                            }
                        )

            except Exception as e:
                logger.debug(f"Error checking {py_file}: {e}")

        # Group small modules by directory
        for directory, modules in small_modules.items():
            if len(modules) > 1:
                self.consolidation_candidates.append(
                    {
                        "type": "small_modules",
                        "directory": directory,
                        "modules": modules,
                        "reason": f"{len(modules)} small modules in same directory could be consolidated",
                    }
                )

    def _find_circular_dependencies(self):
        """Find circular import dependencies"""
        visited = set()
        rec_stack = set()
        cycles = []

        def find_cycles(module, path=[]):
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for imported in self.module_imports.get(module, []):
                if imported not in visited:
                    find_cycles(imported, path.copy())
                elif imported in rec_stack:
                    # Found cycle
                    cycle_start = path.index(imported)
                    cycle = path[cycle_start:] + [imported]
                    cycles.append(cycle)

            rec_stack.remove(module)

        for module in self.internal_modules:
            if module not in visited:
                find_cycles(module)

        # Add unique cycles
        unique_cycles = []
        for cycle in cycles:
            sorted_cycle = tuple(sorted(cycle))
            if sorted_cycle not in [tuple(sorted(c["modules"])) for c in unique_cycles]:
                unique_cycles.append(
                    {
                        "type": "circular_dependency",
                        "modules": cycle,
                        "reason": "Circular import dependency - consider consolidating or refactoring",
                    }
                )

        self.consolidation_candidates.extend(unique_cycles[:10])  # Limit to 10

    def _find_duplicate_files(self):
        """Find files with very similar content"""
        file_hashes = defaultdict(list)

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    # Simple content hash (ignoring whitespace)
                    normalized = "".join(content.split())
                    content_hash = hash(normalized)

                relative = py_file.relative_to(self.root_path)
                file_hashes[content_hash].append(str(relative))

            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")

        # Find duplicates
        for content_hash, files in file_hashes.items():
            if len(files) > 1:
                self.consolidation_candidates.append(
                    {
                        "type": "duplicate_files",
                        "files": files,
                        "reason": "Files have identical or nearly identical content",
                    }
                )

    def _generate_report(self):
        """Generate consolidation opportunities report"""
        # Analyze import patterns for consolidation
        consolidation_report = {
            "total_modules": len(self.internal_modules),
            "total_imports": sum(
                len(imports) for imports in self.module_imports.values()
            ),
            "consolidation_opportunities": len(self.consolidation_candidates),
            "opportunities_by_type": defaultdict(int),
            "recommendations": [],
        }

        # Count by type
        for candidate in self.consolidation_candidates:
            consolidation_report["opportunities_by_type"][candidate["type"]] += 1

        # Generate specific recommendations
        self._generate_recommendations(consolidation_report)

        # Save report
        output_dir = self.root_path / "scripts" / "import_migration"
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "consolidation_report.json", "w") as f:
            json.dump(
                {
                    "report": consolidation_report,
                    "candidates": self.consolidation_candidates[:50],  # Top 50
                },
                f,
                indent=2,
            )

        # Generate summary
        summary = f"""
Consolidation Analysis Report
============================

Total Internal Modules: {consolidation_report['total_modules']}
Total Internal Imports: {consolidation_report['total_imports']}
Consolidation Opportunities: {consolidation_report['consolidation_opportunities']}

Opportunities by Type:
"""

        for opp_type, count in consolidation_report["opportunities_by_type"].items():
            summary += f"- {opp_type.replace('_', ' ').title()}: {count}\n"

        summary += "\nTop Recommendations:\n"
        for i, rec in enumerate(consolidation_report["recommendations"][:10], 1):
            summary += f"\n{i}. {rec['title']}\n"
            summary += f"   Action: {rec['action']}\n"
            summary += f"   Impact: {rec['impact']}\n"

        with open(output_dir / "consolidation_summary.txt", "w") as f:
            f.write(summary)

        print(summary)
        logger.info(f"Consolidation analysis complete! Reports saved to {output_dir}")

    def _generate_recommendations(self, report):
        """Generate specific consolidation recommendations"""
        recommendations = []

        # Recommendation 1: Merge tightly coupled modules
        coupled = [
            c for c in self.consolidation_candidates if c["type"] == "tightly_coupled"
        ]
        if coupled:
            recommendations.append(
                {
                    "title": "Merge Tightly Coupled Modules",
                    "action": f"Consider merging {len(coupled)} pairs of modules with bidirectional imports",
                    "impact": "Reduce complexity and circular dependencies",
                    "examples": [c["modules"] for c in coupled[:3]],
                }
            )

        # Recommendation 2: Consolidate small modules
        small = [
            c for c in self.consolidation_candidates if c["type"] == "small_modules"
        ]
        if small:
            total_small = sum(len(s["modules"]) for s in small)
            recommendations.append(
                {
                    "title": "Consolidate Small Modules",
                    "action": f"Merge {total_small} small modules into larger, cohesive modules",
                    "impact": "Reduce file sprawl and improve organization",
                    "examples": [s["directory"] for s in small[:3]],
                }
            )

        # Recommendation 3: Remove duplicates
        duplicates = [
            c for c in self.consolidation_candidates if c["type"] == "duplicate_files"
        ]
        if duplicates:
            recommendations.append(
                {
                    "title": "Remove Duplicate Files",
                    "action": f"Remove or merge {len(duplicates)} sets of duplicate files",
                    "impact": "Eliminate redundancy and confusion",
                    "examples": [d["files"] for d in duplicates[:3]],
                }
            )

        # Recommendation 4: Fix circular dependencies
        circular = [
            c
            for c in self.consolidation_candidates
            if c["type"] == "circular_dependency"
        ]
        if circular:
            recommendations.append(
                {
                    "title": "Resolve Circular Dependencies",
                    "action": f"Refactor {len(circular)} circular dependency chains",
                    "impact": "Improve architecture and testability",
                    "examples": [c["modules"] for c in circular[:3]],
                }
            )

        report["recommendations"] = recommendations

    def _is_internal_module(self, module: str) -> bool:
        """Check if module is internal to project"""
        # Check against known external modules
        external_prefixes = [
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
            "typing",
            "datetime",
            "asyncio",
            "collections",
            "pathlib",
            "unittest",
            "pytest",
            "re",
            "math",
            "random",
            "time",
            "functools",
        ]

        for prefix in external_prefixes:
            if module.startswith(prefix):
                return False

        # Check if it's one of our modules
        return any(module.startswith(m.split(".")[0]) for m in self.internal_modules)

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

    parser = argparse.ArgumentParser(description="Analyze consolidation opportunities")
    parser.add_argument("path", nargs="?", default=".", help="Root path to analyze")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    analyzer = ConsolidationAnalyzer(root_path)
    analyzer.analyze()


if __name__ == "__main__":
    main()
