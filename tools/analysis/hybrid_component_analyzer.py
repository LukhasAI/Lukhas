#!/usr/bin/env python3
"""
 Hybrid Component Analyzer - Identifies quantum-hybrid subdirectories
Runs scenarios to discover natural inter-module relationships
"""
from consciousness.qi import qi
import time
import streamlit as st

import ast
import json
import os
from collections import defaultdict
from datetime import datetime, timezone


class HybridComponentAnalyzer:
    def __init__(self):
        self.module_dirs = [
            "consciousness",
            "memory",
            "emotion",
            "quantum",
            "bio",
            "governance",
            "orchestration",
            "bridge",
            "identity",
            "reasoning",
            "creativity",
            "core",
        ]
        self.hybrid_patterns = defaultdict(list)
        self.cross_references = defaultdict(set)
        self.shared_concepts = defaultdict(set)
        self.scenario_results = {}

    def analyze_imports(self, file_path):
        """Analyze imports to find cross-module dependencies"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

            return imports
        except BaseException:
            return []

    def identify_hybrid_subdirs(self, module_path):
        """Identify subdirectories that reference multiple modules"""
        module_name = os.path.basename(module_path)
        subdirs = {}

        for root, _dirs, files in os.walk(module_path):
            if ".venv" in root or "._cleanup_archive" in root:
                continue

            subdir_name = os.path.relpath(root, module_path)
            if subdir_name == ".":
                continue

            # Analyze all Python files in this subdirectory
            cross_module_refs = defaultdict(int)
            concept_keywords = set()

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)

                    # Check imports
                    imports = self.analyze_imports(file_path)
                    for imp in imports:
                        for other_module in self.module_dirs:
                            if other_module != module_name and other_module in imp:
                                cross_module_refs[other_module] += 1

                    # Check content for concepts
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read().lower()

                        # Look for key concepts
                        concepts = {
                            "emotion": [
                                "emotion",
                                "affect",
                                "mood",
                                "feeling",
                                "sentiment",
                            ],
                            "memory": ["memory", "fold", "recall", "store", "retrieve"],
                            "consciousness": [
                                "conscious",
                                "aware",
                                "reflect",
                                "perceive",
                            ],
                            "quantum": [
                                "quantum",
                                "superposition",
                                "entangle",
                                "collapse",
                            ],
                            "colony": ["colony", "swarm", "collective", "distributed"],
                            "tag": ["tag", "glyph", "symbol", "label", "hormone"],
                            "ethics": ["ethic", "moral", "guardian", "governance"],
                        }

                        for concept, keywords in concepts.items():
                            if any(kw in content for kw in keywords):
                                concept_keywords.add(concept)

                    except BaseException:
                        pass

            if cross_module_refs or len(concept_keywords) > 1:
                subdirs[subdir_name] = {
                    "cross_refs": dict(cross_module_refs),
                    "concepts": list(concept_keywords),
                    "hybrid_score": len(cross_module_refs) + len(concept_keywords),
                }

        return subdirs

    def run_scenario_analysis(self):
        """Run different scenarios to identify hybrid patterns"""

        # Scenario 1: Emotional Memory Processing
        print("Running Scenario 1: Emotional Memory Processing...")
        self.scenario_results["emotional_memory"] = self.analyze_scenario(
            trigger_modules=["emotion"],
            target_concepts=["memory", "fold", "affect"],
            description="Processing emotional memories",
        )

        # Scenario 2: Conscious Decision Making
        print("Running Scenario 2: Conscious Decision Making...")
        self.scenario_results["conscious_decision"] = self.analyze_scenario(
            trigger_modules=["consciousness"],
            target_concepts=["decision", "choice", "ethic", "memory"],
            description="Making conscious ethical decisions",
        )

        # Scenario 3: Quantum Pattern Recognition
        print("Running Scenario 3: Quantum Pattern Recognition...")
        self.scenario_results["qi_pattern"] = self.analyze_scenario(
            trigger_modules=["quantum"],
            target_concepts=["pattern", "recognition", "memory", "conscious"],
            description="Quantum-enhanced pattern recognition",
        )

        # Scenario 4: Stress Response
        print("Running Scenario 4: System Stress Response...")
        self.scenario_results["stress_response"] = self.analyze_scenario(
            trigger_modules=["governance", "guardian"],
            target_concepts=["stress", "emergency", "fallback", "protect"],
            description="System under stress or attack",
        )

        # Scenario 5: Colony Communication
        print("Running Scenario 5: Colony Communication...")
        self.scenario_results["colony_comm"] = self.analyze_scenario(
            trigger_modules=["orchestration"],
            target_concepts=["colony", "swarm", "propagate", "signal"],
            description="Inter-colony communication",
        )

    def analyze_scenario(self, trigger_modules, target_concepts, description):
        """Analyze a specific scenario to find involved components"""
        involved_components = defaultdict(list)

        for module_dir in self.module_dirs:
            if not os.path.exists(module_dir):
                continue

            for root, _dirs, files in os.walk(module_dir):
                if ".venv" in root or "._cleanup_archive" in root:
                    continue

                for file in files:
                    if not file.endswith(".py"):
                        continue

                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read().lower()

                        # Check if file is relevant to scenario
                        relevance_score = 0

                        # Check for trigger module references
                        for trigger in trigger_modules:
                            if trigger in content:
                                relevance_score += 2

                        # Check for target concepts
                        for concept in target_concepts:
                            if concept in content:
                                relevance_score += 1

                        if relevance_score >= 2:
                            subdir = os.path.relpath(root, module_dir)
                            involved_components[module_dir].append(
                                {
                                    "subdir": subdir,
                                    "file": file,
                                    "score": relevance_score,
                                }
                            )

                    except BaseException:
                        pass

        return {
            "description": description,
            "triggers": trigger_modules,
            "concepts": target_concepts,
            "involved": dict(involved_components),
        }

    def identify_hormone_tags(self):
        """Identify tag types that act as hormones (signals)"""
        hormone_patterns = {
            "stress": ["error", "exception", "panic", "critical", "emergency"],
            "reward": ["success", "complete", "achieve", "reward", "positive"],
            "communication": ["signal", "message", "propagate", "broadcast"],
            "regulation": ["throttle", "limit", "control", "regulate", "balance"],
            "bonding": ["connect", "link", "bind", "attach", "couple"],
        }

        tag_hormones = defaultdict(list)

        # Search for tag definitions and usage
        for root, _dirs, files in os.walk("."):
            if ".venv" in root or "._cleanup_archive" in root:
                continue

            for file in files:
                if file.endswith(".py") and "tag" in file.lower():
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read().lower()

                        for hormone_type, patterns in hormone_patterns.items():
                            if any(pattern in content for pattern in patterns):
                                module = root.split(os.sep)[1] if len(root.split(os.sep)) > 1 else "root"
                                tag_hormones[hormone_type].append({"module": module, "file": file, "path": file_path})
                    except BaseException:
                        pass

        return dict(tag_hormones)

    def generate_hybrid_mapping(self):
        """Generate the final hybrid component mapping"""
        hybrid_map = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "modules": {},
            "scenarios": self.scenario_results,
            "hormone_tags": self.identify_hormone_tags(),
            "cross_module_matrix": defaultdict(dict),
        }

        # Analyze each module
        for module in self.module_dirs:
            if not os.path.exists(module):
                continue

            print(f"Analyzing {module}...")
            subdirs = self.identify_hybrid_subdirs(module)

            # Filter to only highly hybrid subdirectories
            hybrid_subdirs = {name: info for name, info in subdirs.items() if info["hybrid_score"] >= 3}

            hybrid_map["modules"][module] = {
                "subdirectories": subdirs,
                "hybrid_components": hybrid_subdirs,
                "hybrid_count": len(hybrid_subdirs),
            }

            # Build cross-module matrix
            for subdir, info in subdirs.items():
                for other_module in info["cross_refs"]:
                    if module not in hybrid_map["cross_module_matrix"][other_module]:
                        hybrid_map["cross_module_matrix"][other_module][module] = []
                    hybrid_map["cross_module_matrix"][other_module][module].append(subdir)

        return hybrid_map

    def generate_neuroplastic_map(self):
        """Generate a map showing how modules reorganize under stress"""
        neuroplastic_map = {
            "normal_hierarchy": [
                "core",
                "consciousness",
                "memory",
                "quantum",
                "emotion",
                "governance",
                "bridge",
            ],
            "stress_responses": {
                "ethical_conflict": {
                    "trigger": "High ethical uncertainty",
                    "new_hierarchy": ["governance", "core", "consciousness", "quantum"],
                    "suppressed": ["emotion", "creativity"],
                    "enhanced": ["ethics", "reasoning"],
                },
                "memory_overload": {
                    "trigger": "Memory capacity exceeded",
                    "new_hierarchy": ["memory", "quantum", "core"],
                    "suppressed": ["creativity", "bridge"],
                    "enhanced": ["compression", "fold_system"],
                },
                "external_attack": {
                    "trigger": "Security threat detected",
                    "new_hierarchy": ["governance", "identity", "core"],
                    "suppressed": ["bridge", "creativity"],
                    "enhanced": ["guardian", "firewall"],
                },
                "emotional_trauma": {
                    "trigger": "Severe emotional distress",
                    "new_hierarchy": ["emotion", "memory", "governance"],
                    "suppressed": ["quantum", "reasoning"],
                    "enhanced": ["mood_regulation", "trauma_vault"],
                },
            },
        }

        return neuroplastic_map


def main():
    analyzer = HybridComponentAnalyzer()

    print("===  Hybrid Component Analysis ===")
    print("Identifying quantum-hybrid subdirectories...\n")

    # Run scenario analysis
    analyzer.run_scenario_analysis()

    # Generate hybrid mapping
    hybrid_map = analyzer.generate_hybrid_mapping()

    # Generate neuroplastic map
    neuroplastic_map = analyzer.generate_neuroplastic_map()

    # Save results
    results = {
        "hybrid_mapping": hybrid_map,
        "neuroplastic_responses": neuroplastic_map,
        "summary": {
            "total_hybrid_components": sum(m["hybrid_count"] for m in hybrid_map["modules"].values()),
            "most_connected_modules": sorted(
                [(m, len(hybrid_map["cross_module_matrix"].get(m, {}))) for m in analyzer.module_dirs],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        },
    }

    # Save to file
    output_path = "docs/reports/analysis/_HYBRID_COMPONENT_MAPPING.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nAnalysis complete! Results saved to {output_path}")

    # Print summary
    print("\n=== Summary ===")
    print(f"Total hybrid components found: {results['summary']['total_hybrid_components']}")
    print("\nMost connected modules:")
    for module, connections in results["summary"]["most_connected_modules"]:
        print(f"  {module}: {connections} connections")

    # Print key hybrid subdirectories
    print("\n=== Key Hybrid Subdirectories ===")
    for module, data in hybrid_map["modules"].items():
        if data["hybrid_components"]:
            print(f"\n{module.upper()}:")
            for subdir, info in data["hybrid_components"].items():
                print(f"  {subdir}:")
                print(f"    - Cross-refs: {', '.join(info['cross_refs'].keys())}")
                print(f"    - Concepts: {', '.join(info['concepts'])}")


if __name__ == "__main__":
    main()