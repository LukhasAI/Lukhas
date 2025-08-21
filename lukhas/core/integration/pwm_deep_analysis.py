#!/usr/bin/env python3
"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

LUKHAS  Deep Module Connectivity Analysis
Identifies critical files vs isolated orphans for aggressive archiving
"""

import ast
import json
from collections import defaultdict
from pathlib import Path


class ConnectivityAnalyzer:

    def __init__(self, root_path="."):
        self.root_path = Path(root_path)
        self.python_files = []
        self.import_graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        self.file_metrics = {}
        self.isolated_files = []
        self.critical_hubs = []

    def scan_python_files(self):
        """Find all Python files excluding archives"""
        self.python_files = list(self.root_path.rglob("*.py"))
        self.python_files = [
            f
            for f in self.python_files
            if "._cleanup_archive" not in str(f) and ".git" not in str(f)
        ]
        print(f"📊 Found {len(self.python_files)} Python files to analyze")

    def analyze_imports(self, file_path):
        """Extract imports from a Python file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)

            return imports
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
            return set()

    def build_connectivity_graph(self):
        """Build the import connectivity graph"""
        print("🔗 Building connectivity graph...")

        for file_path in self.python_files:
            imports = self.analyze_imports(file_path)
            relative_path = str(file_path.relative_to(self.root_path))

            # Convert file path to module name
            module_name = relative_path.replace("/", ".").replace(".py", "")

            self.import_graph[module_name] = imports

            # Build reverse graph
            for imp in imports:
                self.reverse_graph[imp].add(module_name)

    def calculate_file_metrics(self):
        """Calculate connectivity metrics for each file"""
        print("📈 Calculating file metrics...")

        for file_path in self.python_files:
            relative_path = str(file_path.relative_to(self.root_path))
            module_name = relative_path.replace("/", ".").replace(".py", "")

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                lines_of_code = len(
                    [
                        line
                        for line in content.split("\n")
                        if line.strip() and not line.strip().startswith("#")
                    ]
                )
                imports_out = len(self.import_graph.get(module_name, set()))
                imports_in = len(self.reverse_graph.get(module_name, set()))

                # Check for key indicators
                has_main = 'if __name__ == "__main__"' in content
                has_class = "class " in content
                has_function = "def " in content
                is_init = file_path.name == "__init__.py"
                is_hub = (
                    "hub" in file_path.name.lower()
                    or "manager" in file_path.name.lower()
                )

                connectivity_score = imports_in + imports_out
                isolation_score = max(0, 10 - connectivity_score)

                self.file_metrics[relative_path] = {
                    "module_name": module_name,
                    "lines_of_code": lines_of_code,
                    "imports_out": imports_out,
                    "imports_in": imports_in,
                    "connectivity_score": connectivity_score,
                    "isolation_score": isolation_score,
                    "has_main": has_main,
                    "has_class": has_class,
                    "has_function": has_function,
                    "is_init": is_init,
                    "is_hub": is_hub,
                    "file_size": file_path.stat().st_size,
                }

            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")

    def identify_critical_vs_isolated(self):
        """Identify critical files vs isolated orphans"""
        print("🎯 Identifying critical vs isolated files...")

        # Sort by connectivity and importance
        sorted_files = sorted(
            self.file_metrics.items(),
            key=lambda x: (
                x[1]["connectivity_score"],
                x[1]["lines_of_code"],
                x[1]["is_hub"],
                x[1]["is_init"],
            ),
            reverse=True,
        )

        # Identify critical hubs (top 10% by connectivity)
        top_10_percent = max(1, len(sorted_files) // 10)
        self.critical_hubs = [f[0] for f in sorted_files[:top_10_percent]]

        # Identify isolated files (bottom 50% by connectivity + low code)
        isolated_candidates = [
            f
            for f in sorted_files
            if f[1]["connectivity_score"] <= 2
            and f[1]["lines_of_code"] <= 50
            and not f[1]["is_hub"]
            and not f[1]["is_init"]
            and not f[1]["has_main"]
        ]

        self.isolated_files = [f[0] for f in isolated_candidates]

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("📋 Generating analysis report...")

        report = {
            "analysis_summary": {
                "total_python_files": len(self.python_files),
                "critical_hubs": len(self.critical_hubs),
                "isolated_files": len(self.isolated_files),
                "archive_candidates": len(self.isolated_files),
                "keep_files": len(self.python_files) - len(self.isolated_files),
            },
            "critical_hubs": [
                {"file": f, "metrics": self.file_metrics[f]}
                for f in self.critical_hubs[:20]  # Top 20
            ],
            "isolated_files": [
                {"file": f, "metrics": self.file_metrics[f]}
                for f in self.isolated_files
            ],
            "directory_analysis": self.analyze_directories(),
        }

        return report

    def analyze_directories(self):
        """Analyze directories by connectivity"""
        dir_stats = defaultdict(
            lambda: {
                "total_files": 0,
                "critical_files": 0,
                "isolated_files": 0,
                "connectivity_sum": 0,
            }
        )

        for file_path, metrics in self.file_metrics.items():
            directory = str(Path(file_path).parent)
            dir_stats[directory]["total_files"] += 1
            dir_stats[directory]["connectivity_sum"] += metrics["connectivity_score"]

            if file_path in self.critical_hubs:
                dir_stats[directory]["critical_files"] += 1
            elif file_path in self.isolated_files:
                dir_stats[directory]["isolated_files"] += 1

        # Calculate directory scores
        for directory, stats in dir_stats.items():
            stats["avg_connectivity"] = stats["connectivity_sum"] / max(
                1, stats["total_files"]
            )
            stats["isolation_ratio"] = stats["isolated_files"] / max(
                1, stats["total_files"]
            )

        return dict(dir_stats)


def main():
    print("🚀 LUKHAS  Deep Connectivity Analysis")
    print("=" * 50)

    analyzer = ConnectivityAnalyzer()

    # Run analysis
    analyzer.scan_python_files()
    analyzer.build_connectivity_graph()
    analyzer.calculate_file_metrics()
    analyzer.identify_critical_vs_isolated()

    # Generate report
    report = analyzer.generate_report()

    # Save report
    with open("_CONNECTIVITY_ANALYSIS.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n🎯 ANALYSIS COMPLETE!")
    print(f"📊 Total Python Files: {report['analysis_summary']['total_python_files']}")
    print(f"🔗 Critical Hubs: {report['analysis_summary']['critical_hubs']}")
    print(f"🏝️ Isolated Files: {report['analysis_summary']['isolated_files']}")
    print(f"📦 Archive Candidates: {report['analysis_summary']['archive_candidates']}")
    print(f"✅ Keep Files: {report['analysis_summary']['keep_files']}")

    print("\n📋 Top Critical Hubs:")
    for hub in report["critical_hubs"][:10]:
        metrics = hub["metrics"]
        print(f"  📁 {hub['file']}")
        print(
            f"     🔗 Connectivity: {metrics['connectivity_score']} | 📏 LOC: {metrics['lines_of_code']}"
        )

    print("\n🏝️ Isolated Files to Archive (Sample):")
    for isolated in report["isolated_files"][:10]:
        metrics = isolated["metrics"]
        print(f"  🗑️ {isolated['file']}")
        print(
            f"     🔗 Connectivity: {metrics['connectivity_score']} | 📏 LOC: {metrics['lines_of_code']}"
        )

    print("\n📄 Full report saved to: _CONNECTIVITY_ANALYSIS.json")


if __name__ == "__main__":
    main()
