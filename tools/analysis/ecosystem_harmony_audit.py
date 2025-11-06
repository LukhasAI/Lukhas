#!/usr/bin/env python3
"""
LUKHAS  Ecosystem Harmony Audit
Comprehensive analysis to ensure all systems are pulling their weight
and working in harmonious synchrony
"""

import ast
import json
import os
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


class EcosystemHarmonyAuditor:
    def __init__(self):
        self.modules = [
            "core",
            "consciousness",
            "memory",
            "qim",
            "emotion",
            "governance",
            "bridge",
        ]
        self.audit_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "module_health": {},
            "weak_links": [],
            "underperformers": [],
            "missing_integrations": [],
            "circular_dependencies": [],
            "orphaned_components": [],
            "harmony_score": 0.0,
        }

    def audit_module_health(self, module):
        """Deep health check for each module"""
        health_metrics = {
            "name": module,
            "file_count": 0,
            "test_coverage": 0,
            "documentation_score": 0,
            "connectivity_score": 0,
            "code_quality_issues": [],
            "missing_components": [],
            "integration_points": 0,
            "imports_in": 0,
            "imports_out": 0,
            "cyclomatic_complexity": 0,
            "lines_of_code": 0,
            "comment_ratio": 0,
            "test_file_ratio": 0,
            "example_count": 0,
            "submodule_balance": {},
            "hybrid_component_health": {},
        }

        module_path = Path(module)
        if not module_path.exists():
            health_metrics["status"] = "MISSING"
            return health_metrics

        # Count files and analyze structure
        py_files = list(module_path.rglob("*.py"))
        health_metrics["file_count"] = len(py_files)

        # Check for tests
        test_files = [f for f in py_files if "test" in f.name or f.parts[-2] == "tests"]
        health_metrics["test_file_ratio"] = len(test_files) / max(len(py_files), 1)

        # Check documentation
        module_path / "docs"
        module_path / "README.md"
        health_metrics["documentation_score"] = self.calculate_doc_score(module_path)

        # Check examples
        examples_path = module_path / "examples"
        if examples_path.exists():
            health_metrics["example_count"] = len(list(examples_path.rglob("*.py")))

        # Analyze code quality
        total_lines = 0
        total_comments = 0
        imports_in = 0
        imports_out = 0

        for py_file in py_files:
            if "test" not in str(py_file):
                metrics = self.analyze_file(py_file, module)
                total_lines += metrics["lines"]
                total_comments += metrics["comments"]
                imports_out += metrics["imports_out"]
                imports_in += metrics["imports_in"]

                if metrics["issues"]:
                    health_metrics["code_quality_issues"].extend(metrics["issues"])

        health_metrics["lines_of_code"] = total_lines
        health_metrics["comment_ratio"] = total_comments / max(total_lines, 1)
        health_metrics["imports_in"] = imports_in
        health_metrics["imports_out"] = imports_out
        health_metrics["connectivity_score"] = (imports_in + imports_out) / max(len(py_files), 1)

        # Check submodule balance
        health_metrics["submodule_balance"] = self.analyze_submodule_balance(module_path)

        # Check hybrid components
        health_metrics["hybrid_component_health"] = self.check_hybrid_components(module_path)

        # Calculate overall health score
        health_metrics["health_score"] = self.calculate_module_health_score(health_metrics)

        return health_metrics

    def analyze_file(self, filepath, module):
        """Analyze a single Python file"""
        metrics = {
            "lines": 0,
            "comments": 0,
            "imports_out": 0,
            "imports_in": 0,
            "issues": [],
        }

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                metrics["lines"] = len(lines)

                # Count comments
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith('"""'):
                        metrics["comments"] += 1

                # Analyze imports
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if any(m in alias.name for m in self.modules if m != module):
                                metrics["imports_out"] += 1
                    elif (
                        isinstance(node, ast.ImportFrom)
                        and node.module
                        and any(m in node.module for m in self.modules if m != module)
                    ):
                        metrics["imports_out"] += 1

                # Check for common issues
                if len(lines) > 500:
                    metrics["issues"].append(f"{filepath.name}: File too long ({len(lines)} lines)")

                if metrics["comments"] / max(len(lines), 1) < 0.1:
                    metrics["issues"].append(f"{filepath.name}: Low comment ratio")

        except Exception as e:
            metrics["issues"].append(f"{filepath.name}: Parse error - {e!s}")

        return metrics

    def calculate_doc_score(self, module_path):
        """Calculate documentation score for a module"""
        score = 0

        # Check for README
        if (module_path / "README.md").exists():
            score += 25

        # Check for docs directory
        docs_path = module_path / "docs"
        if docs_path.exists():
            score += 25

            # Check for specific docs
            if (docs_path / "api").exists():
                score += 15
            if (docs_path / "guides").exists():
                score += 15

        # Check for docstrings in __init__.py
        init_path = module_path / "__init__.py"
        if init_path.exists():
            try:
                with open(init_path) as f:
                    if '"""' in f.read():
                        score += 20
            except BaseException:
                pass

        return score

    def analyze_submodule_balance(self, module_path):
        """Analyze balance between submodules"""
        submodules = {}

        for item in module_path.iterdir():
            if item.is_dir() and not item.name.startswith(".") and not item.name.startswith("_"):
                py_files = list(item.rglob("*.py"))
                submodules[item.name] = {
                    "file_count": len(py_files),
                    "has_init": (item / "__init__.py").exists(),
                }

        # Calculate balance score
        if submodules:
            file_counts = [s["file_count"] for s in submodules.values()]
            avg = statistics.mean(file_counts)
            std_dev = statistics.stdev(file_counts) if len(file_counts) > 1 else 0
            balance_score = 1 - (std_dev / max(avg, 1)) if avg > 0 else 0
        else:
            balance_score = 0

        return {"submodules": submodules, "balance_score": balance_score}

    def check_hybrid_components(self, module_path):
        """Check health of hybrid components"""
        hybrid_health = {}

        # Look for HYBRID_COMPONENT.json files
        for hybrid_marker in module_path.rglob("HYBRID_COMPONENT.json"):
            try:
                with open(hybrid_marker) as f:
                    hybrid_info = json.load(f)
                    component_name = hybrid_info.get("component", "unknown")

                    # Check if component directory has files
                    component_dir = hybrid_marker.parent
                    py_files = list(component_dir.glob("*.py"))

                    hybrid_health[component_name] = {
                        "exists": True,
                        "file_count": len(py_files),
                        "primary_module": hybrid_info.get("primary_module"),
                        "also_in": hybrid_info.get("also_exists_in", []),
                    }
            except BaseException:
                pass

        return hybrid_health

    def calculate_module_health_score(self, metrics):
        """Calculate overall health score for a module"""
        scores = []

        # File count score (normalized)
        if metrics["file_count"] > 0:
            scores.append(min(metrics["file_count"] / 100, 1.0))
        else:
            scores.append(0)

        # Test coverage score
        scores.append(metrics["test_file_ratio"])

        # Documentation score
        scores.append(metrics["documentation_score"] / 100)

        # Connectivity score (normalized)
        scores.append(min(metrics["connectivity_score"] / 10, 1.0))

        # Comment ratio score
        scores.append(min(metrics["comment_ratio"] * 5, 1.0))

        # Example score
        scores.append(min(metrics["example_count"] / 5, 1.0))

        # Submodule balance
        if metrics.get("submodule_balance"):
            scores.append(metrics["submodule_balance"].get("balance_score", 0))

        # Quality issues penalty
        quality_penalty = len(metrics["code_quality_issues"]) * 0.05

        final_score = max(0, statistics.mean(scores) - quality_penalty)
        return round(final_score, 3)

    def find_weak_links(self):
        """Identify weak connections between modules"""
        weak_links = []

        # Check each module pair
        for i, module1 in enumerate(self.modules):
            for module2 in self.modules[i + 1 :]:
                connection_strength = self.measure_connection_strength(module1, module2)
                if connection_strength < 0.1:  # Threshold for weak connection
                    weak_links.append(
                        {
                            "modules": [module1, module2],
                            "strength": connection_strength,
                            "issue": "Weak or no connection between modules",
                        }
                    )

        return weak_links

    def measure_connection_strength(self, module1, module2):
        """Measure connection strength between two modules"""
        imports_1_to_2 = 0
        imports_2_to_1 = 0

        # Count imports from module1 to module2
        for py_file in Path(module1).rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    if f"from {module2}" in content or f"import {module2}" in content:
                        imports_1_to_2 += content.count(f"from {module2}") + content.count(f"import {module2}")
            except BaseException:
                pass

        # Count imports from module2 to module1
        for py_file in Path(module2).rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    if f"from {module1}" in content or f"import {module1}" in content:
                        imports_2_to_1 += content.count(f"from {module1}") + content.count(f"import {module1}")
            except BaseException:
                pass

        # Calculate normalized strength
        total_imports = imports_1_to_2 + imports_2_to_1
        return min(total_imports / 100, 1.0)  # Normalize to 0-1

    def identify_underperformers(self):
        """Identify modules not pulling their weight"""
        underperformers = []

        # Calculate average health score
        health_scores = [m["health_score"] for m in self.audit_results["module_health"].values()]
        avg_health = statistics.mean(health_scores) if health_scores else 0

        for module, metrics in self.audit_results["module_health"].items():
            if metrics["health_score"] < avg_health * 0.7:  # 70% of average
                underperformers.append(
                    {
                        "module": module,
                        "health_score": metrics["health_score"],
                        "issues": metrics["code_quality_issues"][:5],  # Top 5 issues
                        "missing": self.identify_missing_components(module, metrics),
                    }
                )

        return underperformers

    def identify_missing_components(self, module, metrics):
        """Identify what's missing from a module"""
        missing = []

        if metrics["test_file_ratio"] < 0.1:
            missing.append("Adequate test coverage")

        if metrics["documentation_score"] < 50:
            missing.append("Comprehensive documentation")

        if metrics["example_count"] == 0:
            missing.append("Usage examples")

        if metrics["connectivity_score"] < 1:
            missing.append("Strong inter-module connections")

        return missing

    def check_circular_dependencies(self):
        """Check for circular dependencies between modules"""
        circular_deps = []

        # Build dependency graph
        dep_graph = defaultdict(set)

        for module in self.modules:
            for py_file in Path(module).rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ImportFrom) and node.module:
                                for other_module in self.modules:
                                    if other_module != module and other_module in node.module:
                                        dep_graph[module].add(other_module)
                except BaseException:
                    pass

        # Check for cycles
        for module in self.modules:
            visited = set()
            if self._has_cycle(module, dep_graph, visited, [module]):
                circular_deps.append(module)

        return list(set(circular_deps))

    def _has_cycle(self, node, graph, visited, path):
        """DFS to detect cycles"""
        visited.add(node)

        for neighbor in graph.get(node, []):
            if neighbor in path:
                return True
            if neighbor not in visited and self._has_cycle(neighbor, graph, visited, [*path, neighbor]):
                return True

        return False

    def calculate_harmony_score(self):
        """Calculate overall ecosystem harmony score"""
        scores = []

        # Module health scores
        module_health_scores = [m["health_score"] for m in self.audit_results["module_health"].values()]
        if module_health_scores:
            scores.append(statistics.mean(module_health_scores))

        # Connection strength score
        weak_link_penalty = len(self.audit_results["weak_links"]) * 0.05
        scores.append(max(0, 1 - weak_link_penalty))

        # Underperformer penalty
        underperformer_penalty = len(self.audit_results["underperformers"]) * 0.1
        scores.append(max(0, 1 - underperformer_penalty))

        # Circular dependency penalty
        circular_penalty = len(self.audit_results["circular_dependencies"]) * 0.15
        scores.append(max(0, 1 - circular_penalty))

        return round(statistics.mean(scores), 3)

    def generate_recommendations(self):
        """Generate specific recommendations for improvement"""
        recommendations = []

        # Module-specific recommendations
        for module, metrics in self.audit_results["module_health"].items():
            if metrics["health_score"] < 0.7:
                recs = []

                if metrics["test_file_ratio"] < 0.2:
                    recs.append(f"Add comprehensive tests to {module}/tests/")

                if metrics["documentation_score"] < 50:
                    recs.append(f"Create proper documentation in {module}/docs/")

                if metrics["example_count"] == 0:
                    recs.append(f"Add usage examples to {module}/examples/")

                if metrics["connectivity_score"] < 2:
                    recs.append("Increase integration with other modules")

                recommendations.append(
                    {
                        "module": module,
                        "priority": ("HIGH" if metrics["health_score"] < 0.5 else "MEDIUM"),
                        "actions": recs,
                    }
                )

        # Weak link recommendations
        for weak_link in self.audit_results["weak_links"]:
            recommendations.append(
                {
                    "modules": weak_link["modules"],
                    "priority": "MEDIUM",
                    "actions": [
                        f"Create bridge components between {weak_link['modules'][0]} and {weak_link['modules'][1]}"
                    ],
                }
            )

        return recommendations

    def run_audit(self):
        """Run the complete ecosystem harmony audit"""
        print("🔍 Starting LUKHAS Ecosystem Harmony Audit...")
        print("=" * 60)

        # Audit each module
        print("\n📊 Auditing Module Health...")
        for module in self.modules:
            print(f"  Analyzing {module}...", end="", flush=True)
            health = self.audit_module_health(module)
            self.audit_results["module_health"][module] = health
            print(f" Health Score: {health['health_score']:.2f}")

        # Find weak links
        print("\n🔗 Analyzing Inter-Module Connections...")
        self.audit_results["weak_links"] = self.find_weak_links()
        print(f"  Found {len(self.audit_results['weak_links'])} weak connections")

        # Identify underperformers
        print("\n📉 Identifying Underperforming Modules...")
        self.audit_results["underperformers"] = self.identify_underperformers()
        print(f"  Found {len(self.audit_results['underperformers'])} underperformers")

        # Check circular dependencies
        print("\n🔄 Checking for Circular Dependencies...")
        self.audit_results["circular_dependencies"] = self.check_circular_dependencies()
        print(f"  Found {len(self.audit_results['circular_dependencies'])} circular dependencies")

        # Calculate harmony score
        self.audit_results["harmony_score"] = self.calculate_harmony_score()

        # Generate recommendations
        self.audit_results["recommendations"] = self.generate_recommendations()

        return self.audit_results


def generate_harmony_report(audit_results):
    """Generate a detailed harmony report"""
    report = f"""
# 🎵 LUKHAS Ecosystem Harmony Report
Generated: {audit_results["timestamp"]}

## Overall Harmony Score: {audit_results["harmony_score"]:.1%}

## 📊 Module Health Summary
"""

    # Sort modules by health score
    modules_by_health = sorted(
        audit_results["module_health"].items(),
        key=lambda x: x[1]["health_score"],
        reverse=True,
    )

    for module, metrics in modules_by_health:
        status = "🟢" if metrics["health_score"] >= 0.7 else "🟡" if metrics["health_score"] >= 0.5 else "🔴"
        report += f"\n## {status} {module} - Health: {metrics['health_score']:.1%}\n"
        report += f"- Files: {metrics['file_count']}\n"
        report += f"- Test Coverage: {metrics['test_file_ratio']:.1%}\n"
        report += f"- Documentation: {metrics['documentation_score']}%\n"
        report += f"- Connectivity: {metrics['connectivity_score']:.1f} avg connections/file\n"
        report += f"- Lines of Code: {metrics['lines_of_code']:,}\n"

        if metrics["code_quality_issues"]:
            report += f"- Issues: {len(metrics['code_quality_issues'])}\n"

    # Weak links
    if audit_results["weak_links"]:
        report += "\n## 🔗 Weak Connections\n"
        for link in audit_results["weak_links"]:
            report += f"- {link['modules'][0]} ↔ {link['modules'][1]}: strength {link['strength']:.1%}\n"

    # Underperformers
    if audit_results["underperformers"]:
        report += "\n## 📉 Underperforming Modules\n"
        for up in audit_results["underperformers"]:
            report += f"\n## {up['module']} (Score: {up['health_score']:.1%})\n"
            report += "Missing:\n"
            for missing in up["missing"]:
                report += f"- {missing}\n"

    # Circular dependencies
    if audit_results["circular_dependencies"]:
        report += "\n## 🔄 Circular Dependencies\n"
        for dep in audit_results["circular_dependencies"]:
            report += f"- {dep}\n"

    # Recommendations
    if audit_results["recommendations"]:
        report += "\n## 🎯 Recommendations\n"

        high_priority = [r for r in audit_results["recommendations"] if r.get("priority") == "HIGH"]
        medium_priority = [r for r in audit_results["recommendations"] if r.get("priority") == "MEDIUM"]

        if high_priority:
            report += "\n### HIGH Priority\n"
            for rec in high_priority:
                if "module" in rec:
                    report += f"\n**{rec['module']}**:\n"
                else:
                    report += f"\n**{' & '.join(rec['modules'])}**:\n"
                for action in rec["actions"]:
                    report += f"- {action}\n"

        if medium_priority:
            report += "\n### MEDIUM Priority\n"
            for rec in medium_priority:
                if "module" in rec:
                    report += f"\n**{rec['module']}**:\n"
                else:
                    report += f"\n**{' & '.join(rec['modules'])}**:\n"
                for action in rec["actions"]:
                    report += f"- {action}\n"

    # Harmony assessment
    report += "\n## 🎼 Harmony Assessment\n"

    if audit_results["harmony_score"] >= 0.8:
        report += "✅ **EXCELLENT**: The ecosystem is in harmonious synchrony!\n"
    elif audit_results["harmony_score"] >= 0.6:
        report += "🟡 **GOOD**: The ecosystem is mostly harmonious with some areas for improvement.\n"
    elif audit_results["harmony_score"] >= 0.4:
        report += "🟠 **FAIR**: Several modules need attention to achieve harmony.\n"
    else:
        report += "🔴 **POOR**: Significant work needed to achieve ecosystem harmony.\n"

    return report


def main():
    auditor = EcosystemHarmonyAuditor()
    audit_results = auditor.run_audit()

    # Save JSON results
    json_path = "docs/reports/ECOSYSTEM_HARMONY_AUDIT.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(audit_results, f, indent=2, default=str)

    # Generate and save report
    report = generate_harmony_report(audit_results)
    report_path = "docs/reports/ECOSYSTEM_HARMONY_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)

    print("\n📊 Audit complete!")
    print(f"📋 JSON results: {json_path}")
    print(f"📄 Report: {report_path}")
    print(f"\n🎵 Overall Harmony Score: {audit_results['harmony_score']:.1%}")


if __name__ == "__main__":
    main()
