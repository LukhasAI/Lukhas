#!/usr/bin/env python3
"""
Analyze consolidation opportunities for performance impact
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


class PerformanceOpportunityAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.performance_opportunities = []

    def analyze(self):
        """Analyze consolidation opportunities for performance impact"""
        logger.info("Analyzing consolidation opportunities for performance...")

        # 1. Analyze duplicate files (immediate performance gain)
        self._analyze_duplicate_files()

        # 2. Analyze small modules (import overhead reduction)
        self._analyze_small_modules()

        # 3. Analyze circular dependencies (runtime performance)
        self._analyze_circular_dependencies()

        # 4. Analyze memory system consolidation
        self._analyze_memory_systems()

        # 5. Generate performance impact report
        self._generate_report()

    def _analyze_duplicate_files(self):
        """Analyze duplicate files for removal"""
        logger.info("\n1. Analyzing duplicate files...")

        # Load consolidation report
        report_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "consolidation_report.json"
        )
        if report_path.exists():
            with open(report_path) as f:
                data = json.load(f)

            duplicates = [
                c for c in data["candidates"] if c["type"] == "duplicate_files"
            ]

            for dup in duplicates:
                files = dup["files"]
                # Calculate size impact
                total_size = 0
                for file in files[1:]:  # Skip first file (keep it)
                    file_path = self.root_path / file
                    if file_path.exists():
                        total_size += file_path.stat().st_size

                self.performance_opportunities.append(
                    {
                        "type": "duplicate_removal",
                        "files": files,
                        "impact": {
                            "disk_space_saved": total_size,
                            "import_time_saved": "HIGH",  # No duplicate parsing
                            "memory_saved": total_size,  # Approximate
                            "complexity_reduction": "HIGH",
                        },
                        "priority": 1,  # Highest priority
                    }
                )

    def _analyze_small_modules(self):
        """Analyze small modules that cause import overhead"""
        logger.info("\n2. Analyzing small modules for consolidation...")

        small_modules = defaultdict(list)

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            try:
                size = py_file.stat().st_size
                if size < 2000:  # Less than 2KB
                    with open(py_file, encoding="utf-8") as f:
                        lines = f.readlines()

                    # Count imports
                    import_count = sum(
                        1
                        for line in lines
                        if line.strip().startswith(("import ", "from "))
                    )
                    code_lines = sum(
                        1
                        for line in lines
                        if line.strip() and not line.strip().startswith("#")
                    )

                    if code_lines < 50:  # Small file
                        parent = py_file.parent.name
                        small_modules[parent].append(
                            {
                                "file": str(py_file.relative_to(self.root_path)),
                                "size": size,
                                "imports": import_count,
                                "code_lines": code_lines,
                            }
                        )

            except Exception as e:
                logger.debug(f"Error analyzing {py_file}: {e}")

        # Find directories with many small modules
        for directory, modules in small_modules.items():
            if len(modules) > 3:  # Multiple small files
                total_imports = sum(m["imports"] for m in modules)
                total_size = sum(m["size"] for m in modules)

                self.performance_opportunities.append(
                    {
                        "type": "small_module_consolidation",
                        "directory": directory,
                        "modules": modules,
                        "impact": {
                            "import_overhead_reduction": f"{total_imports} imports eliminated",
                            "startup_time_improvement": "MEDIUM",
                            "files_reduced": len(modules) - 1,
                            "maintainability": "HIGH",
                        },
                        "priority": 2,
                    }
                )

    def _analyze_circular_dependencies(self):
        """Analyze circular dependencies impact"""
        logger.info("\n3. Analyzing circular dependencies...")

        # Load from consolidation report
        report_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "consolidation_report.json"
        )
        if report_path.exists():
            with open(report_path) as f:
                data = json.load(f)

            circulars = [
                c for c in data["candidates"] if c["type"] == "circular_dependency"
            ]

            for circular in circulars:
                modules = circular["modules"]

                self.performance_opportunities.append(
                    {
                        "type": "circular_dependency_fix",
                        "modules": modules,
                        "impact": {
                            "import_time": "HIGH",  # Circular imports slow down startup
                            "memory_usage": "MEDIUM",  # Potential memory leaks
                            "testability": "HIGH",  # Hard to test circular deps
                            "runtime_performance": "MEDIUM",
                        },
                        "priority": 1,  # High priority
                    }
                )

    def _analyze_memory_systems(self):
        """Analyze memory system consolidation opportunities"""
        logger.info("\n4. Analyzing memory system consolidation...")

        memory_files = list(self.root_path.glob("memory/**/*.py"))
        memory_systems = defaultdict(list)

        for file in memory_files:
            if self._should_skip(file):
                continue

            try:
                with open(file, encoding="utf-8") as f:
                    content = f.read()

                # Look for memory-related classes
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "memory" in node.name.lower() or "fold" in node.name.lower():
                            memory_systems[file.parent.name].append(
                                {
                                    "file": str(file.relative_to(self.root_path)),
                                    "class": node.name,
                                    "size": file.stat().st_size,
                                }
                            )

            except Exception as e:
                logger.debug(f"Error analyzing {file}: {e}")

        # Find fragmented memory systems
        for system, files in memory_systems.items():
            if len(files) > 2:
                total_size = sum(f["size"] for f in files)

                self.performance_opportunities.append(
                    {
                        "type": "memory_system_consolidation",
                        "system": system,
                        "files": files,
                        "impact": {
                            "memory_efficiency": "HIGH",  # Unified memory management
                            "cache_performance": "HIGH",  # Better locality
                            "api_simplification": "HIGH",
                            "startup_time": "MEDIUM",
                        },
                        "priority": 1,  # Memory is critical
                    }
                )

    def _generate_report(self):
        """Generate performance opportunity report"""
        logger.info("\n5. Generating performance report...")

        # Sort by priority
        self.performance_opportunities.sort(key=lambda x: x["priority"])

        report = {
            "total_opportunities": len(self.performance_opportunities),
            "by_type": defaultdict(int),
            "high_impact": [],
            "quick_wins": [],
        }

        for opp in self.performance_opportunities:
            report["by_type"][opp["type"]] += 1

            # Identify high impact
            if opp["priority"] == 1:
                report["high_impact"].append(opp)

            # Identify quick wins
            if opp["type"] == "duplicate_removal":
                report["quick_wins"].append(opp)

        # Save detailed report
        output_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "performance_opportunities.json"
        )
        with open(output_path, "w") as f:
            json.dump(
                {
                    "summary": report,
                    "opportunities": self.performance_opportunities[:20],  # Top 20
                },
                f,
                indent=2,
            )

        # Print summary
        print("\n" + "=" * 80)
        print("PERFORMANCE CONSOLIDATION OPPORTUNITIES")
        print("=" * 80)
        print(f"\nTotal opportunities: {report['total_opportunities']}")
        print(f"High impact opportunities: {len(report['high_impact'])}")
        print(f"Quick wins: {len(report['quick_wins'])}")

        print("\n🎯 TOP PERFORMANCE IMPROVEMENTS:")

        print("\n1. IMMEDIATE WINS (Duplicate Removal):")
        for opp in report["quick_wins"][:3]:
            print(f"   - Remove: {opp['files'][1:]}")
            print(f"     Impact: {opp['impact']['disk_space_saved']} bytes saved")

        print("\n2. HIGH IMPACT (Memory Systems):")
        memory_opps = [
            o
            for o in self.performance_opportunities
            if o["type"] == "memory_system_consolidation"
        ]
        for opp in memory_opps[:3]:
            print(
                f"   - Consolidate {len(opp['files'])} files in memory/{opp['system']}"
            )
            print("     Impact: Better cache performance, unified API")

        print("\n3. STARTUP PERFORMANCE (Small Modules):")
        small_opps = [
            o
            for o in self.performance_opportunities
            if o["type"] == "small_module_consolidation"
        ]
        for opp in small_opps[:3]:
            print(
                f"   - Merge {len(opp['modules'])} small files in {opp['directory']}/"
            )
            print(f"     Impact: {opp['impact']['import_overhead_reduction']}")

        print(f"\nDetailed report saved to: {output_path}")

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

    parser = argparse.ArgumentParser(
        description="Analyze performance consolidation opportunities"
    )
    parser.add_argument("path", nargs="?", default=".", help="Root path")
    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    analyzer = PerformanceOpportunityAnalyzer(root_path)
    analyzer.analyze()


if __name__ == "__main__":
    main()
