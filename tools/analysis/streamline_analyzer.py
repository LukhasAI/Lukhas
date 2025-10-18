#!/usr/bin/env python3
"""
 Streamline Analyzer
======================
Focused redundancy analysis and streamlining recommendations for LUKHAS
"""

import ast
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class StreamlineAnalyzer:
    """Analyzes specific modules for streamlining opportunities"""

    def __init__(self):
        self.root_path = Path.cwd()
        self.key_modules = [
            "core",
            "consciousness",
            "memory",
            "orchestration",
            "governance",
            "api",
            "feedback",
            "dashboard",
        ]
        self.findings = {
            "duplicate_functions": [],
            "similar_classes": [],
            "redundant_imports": [],
            "consolidation_opportunities": [],
            "unused_code": [],
        }

    def analyze(self) -> dict[str, Any]:
        """Run focused streamlining analysis"""
        logger.info("🔍 Analyzing LUKHAS r streamlining opportunities...\n")

        # Analyze key modules
        for module in self.key_modules:
            logger.info(f"📂 Analyzing {module} module...")
            self._analyze_module(module)

        # Find cross-module redundancies
        self._find_cross_module_redundancies()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        # Create report
        report = {
            "summary": self._generate_summary(),
            "findings": self.findings,
            "recommendations": recommendations,
            "streamlining_plan": self._create_streamlining_plan(),
        }

        # Save report
        report_path = self.root_path / "docs" / "reports" / "REAMLINE_REPORT.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        self._print_summary(report)

        return report

    def _analyze_module(self, module_name: str):
        """Analyze a specific module for redundancies"""
        module_path = self.root_path / module_name
        if not module_path.exists():
            return

        # Collect module functions and classes
        functions = defaultdict(list)
        classes = defaultdict(list)
        imports = defaultdict(int)

        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                relative_path = py_file.relative_to(self.root_path)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private and magic methods for now
                        if not node.name.startswith("_"):
                            func_sig = self._get_function_signature(node)
                            functions[func_sig].append(
                                {
                                    "file": str(relative_path),
                                    "name": node.name,
                                    "lines": (
                                        node.lineno,
                                        node.end_lineno or node.lineno,
                                    ),
                                }
                            )

                    elif isinstance(node, ast.ClassDef):
                        class_sig = self._get_class_signature(node)
                        classes[class_sig].append({"file": str(relative_path), "name": node.name})

                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports[node.module] += 1

            except Exception:
                pass  # Skip files with syntax errors

        # Find duplicates within module
        for func_sig, occurrences in functions.items():
            if len(occurrences) > 1:
                self.findings["duplicate_functions"].append(
                    {
                        "module": module_name,
                        "signature": func_sig,
                        "occurrences": occurrences,
                    }
                )

        for class_sig, occurrences in classes.items():
            if len(occurrences) > 1:
                self.findings["similar_classes"].append(
                    {
                        "module": module_name,
                        "signature": class_sig,
                        "occurrences": occurrences,
                    }
                )

        # Find common imports
        common_imports = {imp: count for imp, count in imports.items() if count > 5}
        if common_imports:
            self.findings["redundant_imports"].append({"module": module_name, "imports": common_imports})

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get normalized function signature"""
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]
        return f"{node.name}({','.join(args)})"

    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Get class signature based on public methods"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                methods.append(item.name)
        return f"{node.name}[{','.join(sorted(methods))}]"

    def _find_cross_module_redundancies(self):
        """Find redundancies across modules"""
        logger.info("\n🔎 Finding cross-module redundancies...")

        # Common patterns across modules
        patterns = {
            "logger_initialization": {"files": [], "pattern": "get_logger(__name__)}"},
            "config_loading": {"files": [], "pattern": "json.load"},
            "error_handling": {"files": [], "pattern": "try/except with logging"},
            "async_initialization": {"files": [], "pattern": "async def initialize"},
        }

        # Find similar interfaces across modules
        interface_classes = defaultdict(list)

        for module in self.key_modules:
            module_path = self.root_path / module
            if module_path.exists():
                for py_file in module_path.rglob("*.py"):
                    try:
                        with open(py_file, encoding="utf-8") as f:
                            content = f.read()

                        # Check for common patterns
                        if "get_logger(__name__)" in content:
                            patterns["logger_initialization"]["files"].append(str(py_file.relative_to(self.root_path)))
                        if "json.load" in content:
                            patterns["config_loading"]["files"].append(str(py_file.relative_to(self.root_path)))
                        if "async def initialize" in content:
                            patterns["async_initialization"]["files"].append(str(py_file.relative_to(self.root_path)))

                        # Find interface classes
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                if "Interface" in node.name or "Base" in node.name:
                                    interface_classes[node.name].append(str(py_file.relative_to(self.root_path)))

                    except Exception:
                        pass

        # Report common patterns
        for pattern_name, pattern_data in patterns.items():
            if len(pattern_data["files"]) > 10:
                self.findings["consolidation_opportunities"].append(
                    {
                        "type": "common_pattern",
                        "name": pattern_name,
                        "description": pattern_data["pattern"],
                        "occurrences": len(pattern_data["files"]),
                        "sample_files": pattern_data["files"][:5],
                    }
                )

        # Report similar interfaces
        for interface_name, files in interface_classes.items():
            if len(files) > 1:
                self.findings["consolidation_opportunities"].append(
                    {
                        "type": "duplicate_interface",
                        "name": interface_name,
                        "files": files,
                    }
                )

    def _generate_summary(self) -> dict[str, Any]:
        """Generate analysis summary"""
        return {
            "modules_analyzed": len(self.key_modules),
            "duplicate_functions": len(self.findings["duplicate_functions"]),
            "similar_classes": len(self.findings["similar_classes"]),
            "redundant_import_patterns": len(self.findings["redundant_imports"]),
            "consolidation_opportunities": len(self.findings["consolidation_opportunities"]),
            "estimated_reduction": self._estimate_code_reduction(),
        }

    def _estimate_code_reduction(self) -> dict[str, Any]:
        """Estimate potential code reduction"""
        # Conservative estimates
        duplicate_functions = (
            sum(len(f["occurrences"]) - 1 for f in self.findings["duplicate_functions"]) * 20
        )  # Average 20 lines per function

        similar_classes = (
            sum(len(c["occurrences"]) - 1 for c in self.findings["similar_classes"]) * 50
        )  # Average 50 lines per class

        pattern_consolidation = len(self.findings["consolidation_opportunities"]) * 10

        return {
            "lines": duplicate_functions + similar_classes + pattern_consolidation,
            "percentage": 5,  # Conservative 5% reduction estimate
        }

    def _generate_recommendations(self) -> list[dict[str, Any]]:
        """Generate specific recommendations"""
        recommendations = []

        # High priority: Remove exact duplicates
        if self.findings["duplicate_functions"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Remove duplicate functions",
                    "description": "Consolidate duplicate function implementations",
                    "impact": "Immediate code reduction and improved maintainability",
                    "examples": [
                        f"{f['occurrences'][0]['name']} in {f['module']}"
                        for f in self.findings["duplicate_functions"][:3]
                    ],
                }
            )

        # Medium priority: Consolidate similar classes
        if self.findings["similar_classes"]:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Merge similar classes",
                    "description": "Combine classes with identical interfaces",
                    "impact": "Reduce class hierarchy complexity",
                    "examples": [
                        f"{c['occurrences'][0]['name']} in {c['module']}" for c in self.findings["similar_classes"][:3]
                    ],
                }
            )

        # Create common utilities
        pattern_opportunities = [
            o for o in self.findings["consolidation_opportunities"] if o["type"] == "common_pattern"
        ]
        if pattern_opportunities:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Create common utility module",
                    "description": "Extract common patterns into shared utilities",
                    "impact": "Reduce boilerplate and improve consistency",
                    "patterns": [p["name"] for p in pattern_opportunities],
                }
            )

        # Centralize imports
        if self.findings["redundant_imports"]:
            recommendations.append(
                {
                    "priority": "LOW",
                    "action": "Centralize common imports",
                    "description": "Create common import modules for frequently used dependencies",
                    "impact": "Cleaner import sections and easier dependency management",
                    "modules": [r["module"] for r in self.findings["redundant_imports"]],
                }
            )

        return recommendations

    def _create_streamlining_plan(self) -> dict[str, Any]:
        """Create actionable streamlining plan"""
        return {
            "phase1": {
                "name": "Remove Duplicates",
                "duration": "1-2 days",
                "tasks": [
                    "Identify and remove exact duplicate functions",
                    "Merge identical class implementations",
                    "Update imports and references",
                ],
            },
            "phase2": {
                "name": "Create Common Utilities",
                "duration": "2-3 days",
                "tasks": [
                    "Create common.utils module",
                    "Extract logger initialization utility",
                    "Create config loading utilities",
                    "Standardize error handling patterns",
                ],
            },
            "phase3": {
                "name": "Consolidate Interfaces",
                "duration": "3-4 days",
                "tasks": [
                    "Create centralized interface definitions",
                    "Update module imports",
                    "Remove redundant interface classes",
                    "Update documentation",
                ],
            },
            "phase4": {
                "name": "Optimize Module Communication",
                "duration": "1 week",
                "tasks": [
                    "Implement event-driven communication",
                    "Reduce direct module dependencies",
                    "Create message passing interfaces",
                    "Optimize GLYPH token usage",
                ],
            },
        }

    def _print_summary(self, report: dict[str, Any]):
        """Print analysis summary"""
        print("\n" + "=" * 80)
        print("📊 STREAMLINING ANALYSIS SUMMARY")
        print("=" * 80)

        summary = report["summary"]
        print("\n📈 Analysis Results:")
        print(f"   Modules analyzed: {summary['modules_analyzed']}")
        print(f"   Duplicate functions found: {summary['duplicate_functions']}")
        print(f"   Similar classes found: {summary['similar_classes']}")
        print(f"   Consolidation opportunities: {summary['consolidation_opportunities']}")
        print(
            f"   Estimated code reduction: {summary['estimated_reduction']['lines']} lines (~{summary['estimated_reduction']['percentage']}%)"
        )

        if report["recommendations"]:
            print("\n💡 Top Recommendations:")
            for rec in report["recommendations"][:3]:
                print(f"\n   [{rec['priority']}] {rec['action']}")
                print(f"   {rec['description']}")
                print(f"   Impact: {rec['impact']}")

        plan = report["streamlining_plan"]
        print("\n📋 Streamlining Plan:")
        for phase_key, phase in plan.items():
            print(f"\n   {phase_key.upper()}: {phase['name']} ({phase['duration']})")
            for task in phase["tasks"][:2]:
                print(f"      - {task}")

        print("\n✅ Full report saved to: docs/reports/REAMLINE_REPORT.json")
        print("=" * 80)


def main():
    """Run streamlining analysis"""
    analyzer = StreamlineAnalyzer()
    analyzer.analyze()


if __name__ == "__main__":
    main()
