#!/usr/bin/env python3
"""
Memory Integration Analyzer
Analyzes memory-related isolated files to find integration patterns
"""

import argparse
import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class MemoryIntegrationAnalyzer:
    """Analyzes memory-related files for integration opportunities"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.memory_files = []
        self.integration_patterns = defaultdict(list)

        # Key memory system components
        self.core_memory_systems = {
            "memory_hub": "memory/memory_hub.py",
            "memory_manager": "memory/memory_manager.py",
            "memory_folds": "memory/memory_folds.py",
            "emotional_memory": "memory/emotional_memory_manager_unified.py",
            "memory_systems": "memory/systems/",
            "helix": "memory/helix/",
            "quantum_memory": "memory/quantum_memory.py",
        }

        # Memory-related patterns to look for
        self.memory_patterns = {
            "storage": ["store", "save", "persist", "write", "cache"],
            "retrieval": ["retrieve", "fetch", "load", "read", "recall"],
            "processing": ["process", "transform", "fold", "unfold", "compress"],
            "emotional": ["emotion", "feeling", "mood", "sentiment"],
            "episodic": ["episode", "event", "temporal", "timeline"],
            "semantic": ["semantic", "meaning", "concept", "knowledge"],
            "quantum": ["quantum", "superposition", "entangle", "collapse"],
            "helix": ["helix", "spiral", "dna", "encode"],
        }

    def load_memory_files(self, file_list_path: str):
        """Load list of memory-related files"""
        with open(file_list_path) as f:
            data = json.load(f)

        # Extract memory-related files
        if "memory_integrations" in data:
            self.memory_files = [item["file"] for item in data["memory_integrations"]]
        elif "memory" in data:
            self.memory_files = [item["file"] for item in data["memory"]]

        print(f"📊 Found {len(self.memory_files)} memory-related files to analyze")

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single memory file"""
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return {}

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract key information
            info = {
                "classes": [],
                "functions": [],
                "imports": [],
                "patterns": [],
                "potential_targets": [],
            }

            # Find classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info["classes"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    info["functions"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "async": isinstance(node, ast.AsyncFunctionDef),
                        }
                    )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info["imports"].append(node.module)

            # Detect patterns
            content_lower = content.lower()
            for pattern_type, keywords in self.memory_patterns.items():
                if any(keyword in content_lower for keyword in keywords):
                    info["patterns"].append(pattern_type)

            # Suggest integration targets
            info["potential_targets"] = self._suggest_targets(info)

            return info

        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return {}

    def _suggest_targets(self, file_info: Dict) -> List[Tuple[str, str]]:
        """Suggest integration targets based on file analysis"""
        targets = []

        # Based on patterns found
        if "emotional" in file_info["patterns"]:
            targets.append(
                (
                    "memory/emotional_memory_manager_unified.py",
                    "Integrate with unified emotional memory",
                )
            )

        if "storage" in file_info["patterns"] or "retrieval" in file_info["patterns"]:
            targets.append(("memory/memory_hub.py", "Connect to main memory hub"))

        if "helix" in file_info["patterns"]:
            targets.append(("memory/helix/", "Integrate with helix memory system"))

        if "quantum" in file_info["patterns"]:
            targets.append(
                ("memory/quantum_memory.py", "Connect to quantum memory layer")
            )

        # Based on imports
        for imp in file_info["imports"]:
            if "memory" in imp and "memory_manager" in imp:
                targets.append(
                    (
                        "memory/memory_manager.py",
                        "Already imports memory manager - strengthen integration",
                    )
                )

        return targets

    def analyze_all_files(self):
        """Analyze all memory files"""
        print("\n🔍 Analyzing memory files...")

        analysis_results = {}
        for i, file_path in enumerate(self.memory_files, 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(self.memory_files)} files")

            info = self.analyze_file(file_path)
            if info:
                analysis_results[file_path] = info

                # Categorize by pattern
                for pattern in info["patterns"]:
                    self.integration_patterns[pattern].append(
                        {
                            "file": file_path,
                            "classes": len(info["classes"]),
                            "functions": len(info["functions"]),
                            "targets": info["potential_targets"],
                        }
                    )

        return analysis_results

    def generate_integration_plan(self) -> Dict:
        """Generate actionable integration plan"""
        plan = {
            "summary": {
                "total_files": len(self.memory_files),
                "analyzed_files": len(
                    [f for f in self.memory_files if self.analyze_file(f)]
                ),
                "pattern_distribution": {
                    p: len(files) for p, files in self.integration_patterns.items()
                },
            },
            "high_priority_integrations": [],
            "pattern_based_groups": {},
            "recommended_actions": [],
        }

        # Group files by pattern for bulk integration
        for pattern, files in self.integration_patterns.items():
            if len(files) >= 5:  # Significant group
                plan["pattern_based_groups"][pattern] = {
                    "file_count": len(files),
                    "sample_files": [f["file"] for f in files[:5]],
                    "recommended_target": self._get_pattern_target(pattern),
                }

        # High priority integrations (files with multiple patterns)
        file_pattern_count = defaultdict(int)
        for pattern, files in self.integration_patterns.items():
            for file_info in files:
                file_pattern_count[file_info["file"]] += 1

        for file_path, count in sorted(
            file_pattern_count.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            if count >= 2:
                plan["high_priority_integrations"].append(
                    {
                        "file": file_path,
                        "pattern_count": count,
                        "reason": "Multi-pattern memory component",
                    }
                )

        # Recommended actions
        plan["recommended_actions"] = [
            {
                "action": "Create Memory Integration Registry",
                "description": "Document all memory components and their relationships",
                "priority": "high",
            },
            {
                "action": "Consolidate Emotional Memory Components",
                "description": f'Found {len(self.integration_patterns.get("emotional", []))} emotional memory files',
                "priority": "high",
            },
            {
                "action": "Standardize Memory Interfaces",
                "description": "Create consistent store/retrieve/process interfaces",
                "priority": "medium",
            },
        ]

        return plan

    def _get_pattern_target(self, pattern: str) -> str:
        """Get recommended integration target for a pattern"""
        pattern_targets = {
            "emotional": "memory/emotional_memory_manager_unified.py",
            "storage": "memory/memory_hub.py",
            "retrieval": "memory/memory_hub.py",
            "helix": "memory/helix/",
            "quantum": "memory/quantum_memory.py",
            "episodic": "memory/systems/episodic_memory.py",
            "semantic": "memory/systems/semantic_memory.py",
        }
        return pattern_targets.get(pattern, "memory/memory_hub.py")

    def save_report(self, output_file: str):
        """Save analysis report"""
        # Analyze all files
        self.analyze_all_files()

        # Generate plan
        plan = self.generate_integration_plan()

        # Save report
        with open(output_file, "w") as f:
            json.dump(plan, f, indent=2)

        # Print summary
        print("\n" + "=" * 70)
        print("🧠 MEMORY INTEGRATION ANALYSIS SUMMARY")
        print("=" * 70)
        print("\n📊 Analysis Results:")
        print(f"  - Total memory files: {plan['summary']['total_files']}")
        print(f"  - Successfully analyzed: {plan['summary']['analyzed_files']}")

        print("\n🏷️  Pattern Distribution:")
        for pattern, count in sorted(
            plan["summary"]["pattern_distribution"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            print(f"  - {pattern}: {count} files")

        if plan["high_priority_integrations"]:
            print("\n✨ High Priority Integrations:")
            for i, item in enumerate(plan["high_priority_integrations"][:5], 1):
                print(f"  {i}. {item['file']} ({item['pattern_count']} patterns)")

        print(f"\n📄 Detailed report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze memory-related files for integration"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("file_list", help="JSON file with memory files")
    parser.add_argument(
        "-o",
        "--output",
        default="memory_integration_plan.json",
        help="Output file for integration plan",
    )

    args = parser.parse_args()

    print("🧠 Memory Integration Analyzer")
    print("Analyzing memory components for integration opportunities")

    analyzer = MemoryIntegrationAnalyzer(args.repo_path)

    # Load files
    analyzer.load_memory_files(args.file_list)

    # Generate report
    analyzer.save_report(args.output)

    print("\n🎉 Analysis complete!")


if __name__ == "__main__":
    main()
