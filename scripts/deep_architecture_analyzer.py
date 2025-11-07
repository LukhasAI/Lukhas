#!/usr/bin/env python3
"""
LUKHAS Deep Architecture Analyzer
Exposes the true module structure and duplications
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict


class DeepArchitectureAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.module_hierarchy = defaultdict(dict)
        self.duplications = defaultdict(list)
        self.file_counts = defaultdict(int)
        self.import_analysis = defaultdict(set)

    def analyze_directory_tree(self, base_path: Path, prefix: str = "") -> Dict:
        """Recursively analyze directory structure"""
        structure = {
            "path": str(base_path),
            "python_files": 0,
            "subdirs": {},
            "total_files": 0,
            "depth": len(prefix.split('.')) if prefix else 0
        }

        if not base_path.exists() or not base_path.is_dir():
            return structure

        # Count Python files in this directory
        py_files = list(base_path.glob("*.py"))
        structure["python_files"] = len(py_files)
        structure["total_files"] = len(py_files)

        # Analyze subdirectories
        for subdir in base_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.') and subdir.name != '__pycache__':
                subdir_prefix = f"{prefix}.{subdir.name}" if prefix else subdir.name
                sub_analysis = self.analyze_directory_tree(subdir, subdir_prefix)
                structure["subdirs"][subdir.name] = sub_analysis
                structure["total_files"] += sub_analysis["total_files"]

        return structure

    def find_module_duplications(self) -> Dict:
        """Find modules with similar names across different locations"""
        module_names = defaultdict(list)

        # Scan lukhas modules
        lukhas_path = self.root_path / "lukhas"
        if lukhas_path.exists():
            for item in lukhas_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    module_names[item.name].append(f"lukhas/{item.name}")

        # Scan candidate top-level modules
        candidate_path = self.root_path / "candidate"
        if candidate_path.exists():
            for item in candidate_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    module_names[item.name].append(f"candidate/{item.name}")

        # Scan candidate/core modules (the mega-module)
        candidate_core_path = self.root_path / "candidate" / "core"
        if candidate_core_path.exists():
            for item in candidate_core_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    module_names[item.name].append(f"candidate/core/{item.name}")

        # Find duplications
        duplications = {name: locations for name, locations in module_names.items() if len(locations) > 1}
        return duplications

    def analyze_candidate_core_explosion(self) -> Dict:
        """Deep analysis of the candidate/core mega-module"""
        core_path = self.root_path / "candidate" / "core"
        if not core_path.exists():
            return {"error": "candidate/core not found"}

        analysis = {
            "total_subdirs": 0,
            "total_python_files": 0,
            "depth_analysis": defaultdict(list),
            "largest_submodules": [],
            "potential_modules": [],  # Could be broken out as separate modules
            "nested_structure": {}
        }

        # Recursive analysis
        def analyze_recursively(path: Path, depth: int = 0) -> Dict:
            if depth > 10:  # Prevent infinite recursion
                return {"truncated": True, "reason": "max_depth_exceeded"}

            result = {
                "python_files": len(list(path.glob("*.py"))),
                "subdirs": {},
                "total_files_recursive": 0
            }

            analysis["total_python_files"] += result["python_files"]
            result["total_files_recursive"] = result["python_files"]

            for subdir in path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.') and subdir.name != '__pycache__':
                    analysis["total_subdirs"] += 1
                    analysis["depth_analysis"][depth].append(str(subdir.relative_to(core_path)))

                    sub_result = analyze_recursively(subdir, depth + 1)
                    result["subdirs"][subdir.name] = sub_result
                    result["total_files_recursive"] += sub_result["total_files_recursive"]

            return result

        analysis["nested_structure"] = analyze_recursively(core_path)

        # Find largest submodules
        submodule_sizes = []
        for subdir in core_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                file_count = len(list(subdir.glob("**/*.py")))
                submodule_sizes.append((subdir.name, file_count))

        analysis["largest_submodules"] = sorted(submodule_sizes, key=lambda x: x[1], reverse=True)

        # Identify potential separate modules (>20 files or >3 subdirs)
        for subdir in core_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                file_count = len(list(subdir.glob("**/*.py")))
                subdir_count = len([d for d in subdir.iterdir() if d.is_dir() and not d.name.startswith('.')])

                if file_count > 20 or subdir_count > 3:
                    analysis["potential_modules"].append({
                        "name": subdir.name,
                        "files": file_count,
                        "subdirs": subdir_count,
                        "suggestion": f"candidate.{subdir.name}",
                        "current_location": f"candidate/core/{subdir.name}"
                    })

        return analysis

    def compare_overlapping_modules(self) -> Dict:
        """Compare overlapping modules to understand differences"""
        comparisons = {}
        duplications = self.find_module_duplications()

        for module_name, locations in duplications.items():
            comparison = {
                "module_name": module_name,
                "locations": locations,
                "file_counts": {},
                "unique_files": {},
                "common_patterns": []
            }

            for location in locations:
                full_path = self.root_path / location
                if full_path.exists():
                    py_files = list(full_path.glob("**/*.py"))
                    comparison["file_counts"][location] = len(py_files)

                    # Get unique filenames (without extensions)
                    filenames = {f.stem for f in py_files}
                    comparison["unique_files"][location] = list(filenames)

            # Find common patterns
            if len(comparison["unique_files"]) > 1:
                file_sets = [set(files) for files in comparison["unique_files"].values()]
                common_files = set.intersection(*file_sets)
                comparison["common_patterns"] = list(common_files)

            comparisons[module_name] = comparison

        return comparisons

    def generate_architectural_debt_report(self) -> Dict:
        """Generate comprehensive architectural debt analysis"""
        duplications = self.find_module_duplications()
        core_analysis = self.analyze_candidate_core_explosion()
        overlaps = self.compare_overlapping_modules()

        return {
            "summary": {
                "total_duplicated_concepts": len(duplications),
                "candidate_core_subdirs": core_analysis.get("total_subdirs", 0),
                "candidate_core_files": core_analysis.get("total_python_files", 0),
                "potential_separate_modules": len(core_analysis.get("potential_modules", [])),
                "architectural_debt_score": self.calculate_debt_score(duplications, core_analysis)
            },
            "duplications": duplications,
            "candidate_core_explosion": core_analysis,
            "overlap_analysis": overlaps,
            "recommendations": self.generate_refactoring_recommendations(duplications, core_analysis, overlaps)
        }

    def calculate_debt_score(self, duplications: Dict, core_analysis: Dict) -> float:
        """Calculate architectural debt score (0-100, higher = more debt)"""
        score = 0

        # Duplication penalty
        score += len(duplications) * 10

        # Mega-module penalty
        core_subdirs = core_analysis.get("total_subdirs", 0)
        if core_subdirs > 50:
            score += 30
        elif core_subdirs > 20:
            score += 15

        # File concentration penalty
        core_files = core_analysis.get("total_python_files", 0)
        if core_files > 1000:
            score += 25
        elif core_files > 500:
            score += 15

        return min(score, 100)

    def generate_refactoring_recommendations(self, duplications: Dict, core_analysis: Dict, overlaps: Dict) -> list[str]:
        """Generate specific refactoring recommendations"""
        recommendations = []

        # Duplication recommendations
        for module_name, locations in duplications.items():
            if len(locations) > 2:
                recommendations.append(f"CRITICAL: '{module_name}' exists in {len(locations)} locations: {', '.join(locations)}. Consolidate immediately.")
            else:
                recommendations.append(f"HIGH: Merge duplicate '{module_name}' modules: {' vs '.join(locations)}")

        # Mega-module recommendations
        potential_modules = core_analysis.get("potential_modules", [])
        if len(potential_modules) > 10:
            recommendations.append(f"CRITICAL: candidate/core contains {len(potential_modules)} submodules that should be extracted")

        for module in potential_modules[:5]:  # Top 5 candidates
            recommendations.append(f"EXTRACT: Move candidate/core/{module['name']} ({module['files']} files) to candidate/{module['name']}")

        # Architectural recommendations
        core_files = core_analysis.get("total_python_files", 0)
        if core_files > 1000:
            recommendations.append("URGENT: candidate/core mega-module needs immediate decomposition")

        return recommendations


if __name__ == "__main__":
    analyzer = DeepArchitectureAnalyzer("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    print("=== LUKHAS Deep Architecture Analysis ===\n")

    report = analyzer.generate_architectural_debt_report()

    print("SUMMARY:")
    for key, value in report["summary"].items():
        print(f"  {key}: {value}")

    print(f"\nDUPLICATIONS ({len(report['duplications'])}):")
    for name, locations in report["duplications"].items():
        print(f"  {name}: {locations}")

    print("\nCANDIDATE/CORE TOP SUBMODULES:")
    largest = report["candidate_core_explosion"].get("largest_submodules", [])[:10]
    for name, count in largest:
        print(f"  {name}: {count} files")

    print("\nRECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")

    print("\nFull analysis saved to JSON...")
    with open("/Users/agi_dev/LOCAL-REPOS/Lukhas/temp_deep_analysis.json", "w") as f:
        json.dump(report, f, indent=2)
