#!/usr/bin/env python3
"""
LUKHAS 2030 Duplicate Logic Detector
Finds duplicate functionality while preserving the SGI vision
"""
import ast
import json
import os
from collections import defaultdict


class DuplicateDetector:
    def __init__(self, root_path="."):
        self.root_path = root_path
        self.function_signatures = defaultdict(list)
        self.class_structures = defaultdict(list)
        self.import_patterns = defaultdict(list)
        self.similar_names = defaultdict(list)

    def analyze_file(self, filepath: str):
        """Analyze a Python file for patterns"""
        try:
            with open(filepath) as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig = self._get_function_signature(node)
                    self.function_signatures[sig].append((filepath, node.name))

                    # Check for similar names
                    base_name = node.name.lower().replace("_", "")
                    self.similar_names[base_name].append((filepath, node.name))

                elif isinstance(node, ast.ClassDef):
                    struct = self._get_class_structure(node)
                    self.class_structures[struct].append((filepath, node.name))

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    pattern = self._get_import_pattern(node)
                    self.import_patterns[pattern].append(filepath)

        except Exception:
            pass

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature for comparison"""
        args = [arg.arg for arg in node.args.args]
        # Get return type if annotated
        returns = ast.unparse(node.returns) if node.returns else "None"
        return f"{len(args)}:{returns}"

    def _get_class_structure(self, node: ast.ClassDef) -> str:
        """Extract class structure for comparison"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        return ":".join(sorted(methods))

    def _get_import_pattern(self, node) -> str:
        """Extract import pattern"""
        if isinstance(node, ast.Import):
            return f"import:{','.join(n.name for n in node.names)}"
        else:
            return f"from:{node.module}:{','.join(n.name for n in node.names)}"

    def find_duplicates(self):
        """Walk the codebase and find duplicates"""
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    self.analyze_file(filepath)

        # Generate report
        report = {
            "duplicate_functions": {},
            "similar_classes": {},
            "common_imports": {},
            "naming_patterns": {},
        }

        # Find duplicate functions
        for sig, locations in self.function_signatures.items():
            if len(locations) > 1:
                report["duplicate_functions"][sig] = locations

        # Find similar classes
        for struct, locations in self.class_structures.items():
            if len(locations) > 1 and struct:  # Non-empty structure
                report["similar_classes"][struct] = locations

        # Find common import patterns
        for pattern, files in self.import_patterns.items():
            if len(files) > 5:  # Used in many files
                report["common_imports"][pattern] = len(files)

        # Find naming patterns (potential duplicates)
        for base_name, locations in self.similar_names.items():
            if len(locations) > 2:
                report["naming_patterns"][base_name] = locations

        return report


class ConsolidationPlanner:
    """Plans consolidation while preserving LUKHAS 2030 vision"""

    def __init__(self, duplicate_report: dict):
        self.report = duplicate_report

    def generate_plan(self) -> dict:
        """Generate consolidation plan preserving SGI architecture"""
        plan = {
            "memory_consolidation": self._plan_memory_consolidation(),
            "dream_consolidation": self._plan_dream_consolidation(),
            "emotion_consolidation": self._plan_emotion_consolidation(),
            "qi_consolidation": self._plan_quantum_consolidation(),
            "utility_extraction": self._plan_utility_extraction(),
        }
        return plan

    def _plan_memory_consolidation(self) -> dict:
        """Consolidate memory systems into DNA-like helix"""
        return {
            "target": "memory/helix/",
            "description": "Unified DNA-like memory with emotional vectors",
            "merge_candidates": [
                "memory/folding/",
                "memory/systems/",
                "memory/emotional_memory.py",
                "symbolic/features/memory/",
            ],
            "preserve": [
                "Immutable helix structure",
                "Emotional vector integration",
                "EU compliance (right to erase)",
                "Forensic capabilities",
                "Causal chain preservation",
            ],
        }

    def _plan_dream_consolidation(self) -> dict:
        """Consolidate dream systems for quantum-state learning"""
        return {
            "target": "dream/qi_learning/",
            "description": "Multi-parallel scenario generation for self-training",
            "merge_candidates": [
                "dream/engine/",
                "dream/oneiric/",
                "creativity/generators/",
            ],
            "preserve": [
                "Parallel scenario generation",
                "Self-training on unexperienced outcomes",
                "Past experience analysis",
                "Decision outcome prediction",
            ],
        }

    def _plan_emotion_consolidation(self) -> dict:
        """Consolidate emotion recognition with memory"""
        return {
            "target": "emotion/integrated/",
            "description": "Emotion-feeling-memory integration",
            "merge_candidates": ["emotion/", "bio/personality/", "personality/"],
            "preserve": [
                "Emotion recognition",
                "Feeling linkage",
                "Memory integration",
                "Mood regulation",
            ],
        }

    def _plan_quantum_consolidation(self) -> dict:
        """Consolidate quantum processing"""
        return {
            "target": "quantum/sgi_core/",
            "description": "Quantum-inspired SGI processing",
            "merge_candidates": ["quantum/", "architectures/qi_inspired/"],
            "preserve": [
                "Multi-state processing",
                "Quantum-resistant security",
                "Parallel computation",
            ],
        }

    def _plan_utility_extraction(self) -> dict:
        """Extract common utilities"""
        return {
            "target": "core/utilities/",
            "description": "Shared utilities and helpers",
            "extract_from": "all_modules",
            "patterns": [
                "Logger classes",
                "Config loaders",
                "Base classes",
                "Common decorators",
            ],
        }


def main():
    print("🧠 LUKHAS 2030 Duplicate Detection & Consolidation Planning")
    print("=" * 60)

    # Run duplicate detection
    detector = DuplicateDetector()
    report = detector.find_duplicates()

    # Save detailed report
    with open("tools/analysis/duplicate_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Generate consolidation plan
    planner = ConsolidationPlanner(report)
    plan = planner.generate_plan()

    # Save consolidation plan
    with open("tools/analysis/consolidation_plan.json", "w") as f:
        json.dump(plan, f, indent=2)

    # Print summary
    print("\n📊 Duplicate Detection Summary:")
    print(f"  - Duplicate functions: {len(report['duplicate_functions'])}")
    print(f"  - Similar classes: {len(report['similar_classes'])}")
    print(f"  - Common imports: {len(report['common_imports'])}")
    print(f"  - Similar names: {len(report['naming_patterns'])}")

    print("\n🎯 Consolidation Plan Created:")
    for module, details in plan.items():
        if "target" in details:
            print(f"  - {module}: → {details['target']}")

    print("\n✅ Reports saved to:")
    print("  - tools/analysis/duplicate_report.json")
    print("  - tools/analysis/consolidation_plan.json")


if __name__ == "__main__":
    main()