#!/usr/bin/env python3
"""
Functional Orchestrator Analyzer - Phase 2
Analyzes remaining orchestrator files for functional consolidation
"""

import ast
import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List


class FunctionalOrchestratorAnalyzer:
    def __init__(self):
        self.orchestrator_files = []
        self.file_analysis = {}
        self.functional_groups = defaultdict(list)
        self.consolidation_candidates = {}

    def find_remaining_orchestrators(self) -> List[str]:
        """Find all remaining orchestrator files after duplicate removal"""
        orchestrator_files = []

        # Focus on Consolidation-Repo since we kept those files
        for root, dirs, files in os.walk("."):
            # Skip certain directories
            skip_dirs = {
                ".git",
                "__pycache__",
                "node_modules",
                ".pytest_cache",
                "venv",
                "env",
                "archived",
            }
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if file.endswith(".py") and "orchestrat" in file.lower():
                    full_path = os.path.join(root, file)
                    # Only include files that actually exist (not removed duplicates)
                    if os.path.exists(full_path):
                        orchestrator_files.append(full_path)

        self.orchestrator_files = sorted(orchestrator_files)
        return self.orchestrator_files

    def analyze_orchestrator_functionality(self, file_path: str) -> Dict[str, Any]:
        """Analyze the functionality of an orchestrator file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Basic metrics
            lines = content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]

            # Parse AST for deeper analysis
            classes = []
            functions = []
            imports = []
            base_classes = []
            async_methods = []

            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(
                            {
                                "name": node.name,
                                "bases": [self._get_name(base) for base in node.bases],
                                "methods": [
                                    n.name
                                    for n in node.body
                                    if isinstance(n, ast.FunctionDef)
                                ],
                            }
                        )
                        base_classes.extend(
                            [self._get_name(base) for base in node.bases]
                        )

                    elif isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                        if any(
                            isinstance(decorator, ast.Name)
                            and decorator.id == "asyncio"
                            for decorator in node.decorator_list
                        ):
                            async_methods.append(node.name)
                    elif isinstance(node, ast.AsyncFunctionDef):
                        functions.append(node.name)
                        async_methods.append(node.name)

                    elif isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for name in node.names:
                                imports.append(f"{node.module}.{name.name}")

            except SyntaxError:
                pass

            # Categorize functionality based on content analysis
            functionality = self._categorize_functionality(
                file_path, content, classes, functions, imports
            )

            # Analyze architectural patterns
            patterns = self._identify_patterns(content, classes, functions)

            # Check for key orchestrator features
            features = self._identify_features(content, functions)

            analysis = {
                "path": file_path,
                "file_name": os.path.basename(file_path),
                "size_bytes": len(content),
                "total_lines": len(lines),
                "code_lines": len(non_empty_lines),
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "base_classes": base_classes,
                "async_methods": async_methods,
                "functionality_category": functionality,
                "architectural_patterns": patterns,
                "key_features": features,
                "complexity_score": self._calculate_complexity(
                    classes, functions, imports
                ),
                "last_modified": datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat(),
            }

            return analysis

        except Exception as e:
            return {
                "path": file_path,
                "file_name": os.path.basename(file_path),
                "error": str(e),
                "functionality_category": "unknown",
            }

    def _get_name(self, node):
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def _categorize_functionality(
        self,
        file_path: str,
        content: str,
        classes: List,
        functions: List,
        imports: List,
    ) -> str:
        """Categorize orchestrator by primary functionality"""
        path_lower = file_path.lower()
        content_lower = content.lower()

        # Primary categories based on path and content
        if "trio" in path_lower or "golden_trio" in path_lower:
            return "golden_trio"
        elif "agent" in path_lower and any(
            "agent" in cls["name"].lower() for cls in classes
        ):
            return "agent_management"
        elif "colony" in path_lower or "swarm" in path_lower:
            return "colony_swarm"
        elif "brain" in path_lower or any(
            "brain" in cls["name"].lower() for cls in classes
        ):
            return "brain_cognitive"
        elif "memory" in path_lower or any(
            "memory" in cls["name"].lower() for cls in classes
        ):
            return "memory_management"
        elif "bio" in path_lower or any(
            "bio" in cls["name"].lower() for cls in classes
        ):
            return "bio_systems"
        elif "quantum" in path_lower or any(
            "quantum" in cls["name"].lower() for cls in classes
        ):
            return "quantum_processing"
        elif "security" in path_lower or "dast" in path_lower:
            return "security_systems"
        elif "master" in path_lower or "main" in path_lower:
            return "master_control"
        elif "system" in path_lower and any(
            "system" in cls["name"].lower() for cls in classes
        ):
            return "system_orchestration"
        elif "integration" in path_lower or "vendor" in path_lower:
            return "integration_services"
        elif any(word in path_lower for word in ["demo", "example", "test"]):
            return "demo_example"
        elif any(word in path_lower for word in ["migrated", "legacy", "old"]):
            return "legacy_migrated"
        elif any(
            word in path_lower for word in ["specialized", "component", "deployment"]
        ):
            return "specialized_services"
        else:
            return "core_orchestration"

    def _identify_patterns(
        self, content: str, classes: List, functions: List
    ) -> List[str]:
        """Identify architectural patterns used"""
        patterns = []
        content_lower = content.lower()

        # Common orchestrator patterns
        if "async" in content_lower and len([f for f in functions if "async" in f]) > 2:
            patterns.append("async_orchestration")
        if "queue" in content_lower or "task" in content_lower:
            patterns.append("task_queue")
        if "registry" in content_lower or "register" in content_lower:
            patterns.append("registry_pattern")
        if "plugin" in content_lower or "extension" in content_lower:
            patterns.append("plugin_architecture")
        if "event" in content_lower and "handler" in content_lower:
            patterns.append("event_driven")
        if "state" in content_lower and "machine" in content_lower:
            patterns.append("state_machine")
        if "pipeline" in content_lower or "workflow" in content_lower:
            patterns.append("pipeline_workflow")
        if "message" in content_lower and (
            "send" in content_lower or "receive" in content_lower
        ):
            patterns.append("message_passing")
        if "monitor" in content_lower or "health" in content_lower:
            patterns.append("monitoring")
        if "discovery" in content_lower or "service" in content_lower:
            patterns.append("service_discovery")

        return patterns

    def _identify_features(self, content: str, functions: List) -> List[str]:
        """Identify key orchestrator features"""
        features = []
        content_lower = content.lower()

        # Key orchestrator capabilities
        if "initialize" in content_lower or "init" in [f.lower() for f in functions]:
            features.append("initialization")
        if "shutdown" in content_lower or "cleanup" in content_lower:
            features.append("cleanup")
        if "load" in content_lower and "balance" in content_lower:
            features.append("load_balancing")
        if "failover" in content_lower or "fallback" in content_lower:
            features.append("failover")
        if "config" in content_lower or "setting" in content_lower:
            features.append("configuration")
        if "log" in content_lower or "audit" in content_lower:
            features.append("logging_audit")
        if "metric" in content_lower or "performance" in content_lower:
            features.append("metrics")
        if "scale" in content_lower or "resource" in content_lower:
            features.append("scaling")
        if "protocol" in content_lower or "communication" in content_lower:
            features.append("communication")
        if "security" in content_lower or "auth" in content_lower:
            features.append("security")

        return features

    def _calculate_complexity(
        self, classes: List, functions: List, imports: List
    ) -> int:
        """Calculate complexity score for the orchestrator"""
        score = 0

        # Base complexity from structure
        score += len(classes) * 3
        score += len(functions) * 1
        score += len(imports) * 0.5

        # Bonus for class hierarchies
        for cls in classes:
            if cls.get("bases"):
                score += len(cls["bases"]) * 2
            if cls.get("methods"):
                score += len(cls["methods"]) * 1

        return int(score)

    def group_by_functionality(self) -> Dict[str, List[Dict]]:
        """Group orchestrators by functional category"""
        groups = defaultdict(list)

        for file_path, analysis in self.file_analysis.items():
            category = analysis.get("functionality_category", "unknown")
            groups[category].append(analysis)

        # Sort each group by complexity (most complex first)
        for category in groups:
            groups[category].sort(
                key=lambda x: x.get("complexity_score", 0), reverse=True
            )

        return dict(groups)

    def identify_consolidation_candidates(self) -> Dict[str, Any]:
        """Identify which orchestrators can be consolidated"""
        groups = self.group_by_functionality()
        consolidation_plan = {}

        for category, orchestrators in groups.items():
            if len(orchestrators) <= 1:
                # Single file - keep as is
                consolidation_plan[category] = {
                    "action": "keep_single",
                    "files": orchestrators,
                    "recommended_keep": orchestrators[0] if orchestrators else None,
                    "files_to_merge": [],
                    "priority": "none",
                }
            elif category in ["demo_example", "legacy_migrated"]:
                # Archive these categories
                consolidation_plan[category] = {
                    "action": "archive_all",
                    "files": orchestrators,
                    "recommended_keep": None,
                    "files_to_merge": orchestrators,
                    "priority": "high",
                }
            elif len(orchestrators) >= 5:
                # Many files - consolidate to 1-2
                best_candidates = orchestrators[:2]  # Top 2 by complexity
                consolidation_plan[category] = {
                    "action": "consolidate_many",
                    "files": orchestrators,
                    "recommended_keep": best_candidates[0],
                    "files_to_merge": orchestrators[1:],
                    "secondary_keep": (
                        best_candidates[1] if len(best_candidates) > 1 else None
                    ),
                    "priority": "high",
                }
            else:
                # 2-4 files - consolidate to best 1
                consolidation_plan[category] = {
                    "action": "consolidate_few",
                    "files": orchestrators,
                    "recommended_keep": orchestrators[0],
                    "files_to_merge": orchestrators[1:],
                    "priority": "medium",
                }

        return consolidation_plan

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive functional analysis report"""
        groups = self.group_by_functionality()
        consolidation_plan = self.identify_consolidation_candidates()

        # Calculate statistics
        total_files = len(self.orchestrator_files)
        total_size = sum(
            analysis.get("size_bytes", 0) for analysis in self.file_analysis.values()
        )

        # Count actions
        files_to_archive = sum(
            len(plan["files"])
            for plan in consolidation_plan.values()
            if plan["action"] == "archive_all"
        )
        files_to_consolidate = sum(
            len(plan["files_to_merge"])
            for plan in consolidation_plan.values()
            if plan["action"] in ["consolidate_many", "consolidate_few"]
        )
        files_to_keep = total_files - files_to_archive - files_to_consolidate

        # Top orchestrators by complexity
        all_analyses = list(self.file_analysis.values())
        top_complex = sorted(
            all_analyses, key=lambda x: x.get("complexity_score", 0), reverse=True
        )[:10]
        top_largest = sorted(
            all_analyses, key=lambda x: x.get("size_bytes", 0), reverse=True
        )[:10]

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_orchestrator_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "functional_categories": len(groups),
                "files_to_archive": files_to_archive,
                "files_to_consolidate": files_to_consolidate,
                "final_files_estimate": files_to_keep,
            },
            "functional_groups": {
                category: {
                    "count": len(files),
                    "total_size": sum(f.get("size_bytes", 0) for f in files),
                    "avg_complexity": (
                        sum(f.get("complexity_score", 0) for f in files) / len(files)
                        if files
                        else 0
                    ),
                    "files": [f["path"] for f in files],
                }
                for category, files in groups.items()
            },
            "consolidation_plan": consolidation_plan,
            "top_complex_orchestrators": [
                {
                    "path": f["path"],
                    "category": f.get("functionality_category"),
                    "complexity_score": f.get("complexity_score", 0),
                    "size_kb": round(f.get("size_bytes", 0) / 1024, 1),
                    "classes": len(f.get("classes", [])),
                    "functions": len(f.get("functions", [])),
                    "features": f.get("key_features", []),
                }
                for f in top_complex
            ],
            "recommendations": self._generate_recommendations(
                groups, consolidation_plan
            ),
        }

        return report

    def _generate_recommendations(self, groups, consolidation_plan) -> List[str]:
        """Generate consolidation recommendations"""
        recommendations = []

        # High priority actions
        high_priority = [
            cat
            for cat, plan in consolidation_plan.items()
            if plan["priority"] == "high"
        ]
        if high_priority:
            recommendations.append(
                f"IMMEDIATE: Archive/consolidate {len(high_priority)} high-priority categories"
            )

        # Archive recommendations
        archive_categories = [
            cat
            for cat, plan in consolidation_plan.items()
            if plan["action"] == "archive_all"
        ]
        if archive_categories:
            files_count = sum(
                len(consolidation_plan[cat]["files"]) for cat in archive_categories
            )
            recommendations.append(
                f"Archive {files_count} demo/legacy orchestrator files"
            )

        # Consolidation opportunities
        consolidate_categories = [
            cat
            for cat, plan in consolidation_plan.items()
            if plan["action"] in ["consolidate_many", "consolidate_few"]
        ]
        if consolidate_categories:
            files_count = sum(
                len(consolidation_plan[cat]["files_to_merge"])
                for cat in consolidate_categories
            )
            recommendations.append(
                f"Consolidate {files_count} orchestrator files into best implementations"
            )

        # Target final count
        current_total = sum(len(files) for files in groups.values())
        estimated_final = sum(
            (
                1
                if plan["action"]
                in ["keep_single", "consolidate_many", "consolidate_few"]
                else 0
            )
            for plan in consolidation_plan.values()
        )
        if estimated_final > 0:
            reduction_pct = round(
                (current_total - estimated_final) / current_total * 100, 1
            )
            recommendations.append(
                f"Target: Reduce from {current_total} to ~{estimated_final} files ({reduction_pct}% reduction)"
            )

        return recommendations

    def run_analysis(self) -> Dict[str, Any]:
        """Run complete functional analysis"""
        print("🔍 Finding remaining orchestrator files...")
        files = self.find_remaining_orchestrators()
        print(f"Found {len(files)} orchestrator files")

        print("📊 Analyzing functionality...")
        for i, file_path in enumerate(files, 1):
            analysis = self.analyze_orchestrator_functionality(file_path)
            self.file_analysis[file_path] = analysis

            if i % 10 == 0:
                print(f"  Analyzed {i}/{len(files)} files...")

        print("📋 Generating consolidation plan...")
        report = self.generate_report()

        return report


def main():
    """Main function"""
    analyzer = FunctionalOrchestratorAnalyzer()
    report = analyzer.run_analysis()

    # Save report
    with open("functional_orchestrator_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("🎭 FUNCTIONAL ORCHESTRATOR ANALYSIS - PHASE 2")
    print("=" * 80)

    summary = report["summary"]
    print("\n📊 Summary:")
    print(f"  Total orchestrator files: {summary['total_orchestrator_files']}")
    print(f"  Total size: {summary['total_size_mb']} MB")
    print(f"  Functional categories: {summary['functional_categories']}")
    print(f"  Files to archive: {summary['files_to_archive']}")
    print(f"  Files to consolidate: {summary['files_to_consolidate']}")
    print(f"  Estimated final count: {summary['final_files_estimate']}")

    print("\n📂 Functional Categories:")
    groups = report["functional_groups"]
    for category, info in sorted(
        groups.items(), key=lambda x: x[1]["count"], reverse=True
    ):
        print(
            f"  {category:20} {info['count']:3} files ({info['total_size']/1024:.0f} KB)"
        )

    print("\n🎯 Top 5 Most Complex Orchestrators:")
    for i, orch in enumerate(report["top_complex_orchestrators"][:5], 1):
        print(f"  {i}. {orch['path']}")
        print(
            f"     Category: {orch['category']} | Complexity: {orch['complexity_score']} | Size: {orch['size_kb']} KB"
        )
        print(
            f"     Features: {', '.join(orch['features'][:3])}{'...' if len(orch['features']) > 3 else ''}"
        )

    print("\n💡 Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")

    print(
        "\n✅ Analysis complete! Report saved to: functional_orchestrator_analysis.json"
    )


if __name__ == "__main__":
    main()
