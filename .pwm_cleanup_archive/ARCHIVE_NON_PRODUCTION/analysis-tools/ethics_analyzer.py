#!/usr/bin/env python3
"""
Ethics Module Analyzer
Analyzes ethics files to find patterns, duplicates, and consolidation opportunities
"""
import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class EthicsAnalyzer:
    def __init__(self):
        self.patterns = {
            "guardian": ["guard", "guardian", "protect", "shield"],
            "validator": ["validat", "check", "verify", "assess"],
            "monitor": ["monitor", "track", "watch", "observ"],
            "compliance": ["complian", "policy", "rule", "regulation"],
            "safety": ["safety", "safe", "harm", "risk"],
            "governance": ["govern", "dao", "decision", "vote"],
            "audit": ["audit", "log", "trace", "record"],
            "emergency": ["emergency", "override", "kill", "stop"],
            "simulation": ["simul", "test", "scenario", "dilemma"],
            "bridge": ["bridge", "connect", "integrat", "adapter"],
        }

    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single Python file"""
        result = {
            "path": filepath,
            "classes": [],
            "functions": [],
            "imports": [],
            "patterns": [],
            "size": os.path.getsize(filepath),
            "is_test": "test" in filepath.lower(),
        }

        try:
            with open(filepath) as f:
                content = f.read()

            # Check patterns in filename and content
            file_lower = filepath.lower()
            content_lower = content.lower()

            for pattern_name, keywords in self.patterns.items():
                if any(kw in file_lower or kw in content_lower for kw in keywords):
                    result["patterns"].append(pattern_name)

            # Parse AST
            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        result["classes"].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith("_"):
                            result["functions"].append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            result["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            result["imports"].append(node.module)

            except SyntaxError:
                result["parse_error"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    def find_similar_files(self, analyses: List[Dict]) -> List[List[str]]:
        """Find files with similar functionality"""
        similar_groups = []
        processed = set()

        for i, file1 in enumerate(analyses):
            if file1["path"] in processed:
                continue

            group = [file1["path"]]

            for j, file2 in enumerate(analyses[i + 1 :], i + 1):
                if file2["path"] in processed:
                    continue

                # Check similarity
                if self.are_similar(file1, file2):
                    group.append(file2["path"])
                    processed.add(file2["path"])

            if len(group) > 1:
                similar_groups.append(group)
                processed.add(file1["path"])

        return similar_groups

    def are_similar(self, file1: Dict, file2: Dict) -> bool:
        """Check if two files are similar enough to consolidate"""
        # Pattern overlap
        pattern_overlap = len(set(file1["patterns"]) & set(file2["patterns"]))

        # Class/function name similarity
        classes1 = set(file1["classes"])
        classes2 = set(file2["classes"])
        functions1 = set(file1["functions"])
        functions2 = set(file2["functions"])

        class_overlap = len(classes1 & classes2)
        function_overlap = len(functions1 & functions2)

        # Similar if:
        # - Share 2+ patterns
        # - Share classes or many functions
        # - Have very similar names

        if pattern_overlap >= 2:
            return True

        if class_overlap > 0 and (classes1 or classes2):
            return True

        if function_overlap >= 3:
            return True

        # Check filename similarity
        name1 = Path(file1["path"]).stem.lower()
        name2 = Path(file2["path"]).stem.lower()

        # Remove common prefixes/suffixes
        for term in ["ethical_", "ethics_", "_engine", "_system", "_manager"]:
            name1 = name1.replace(term, "")
            name2 = name2.replace(term, "")

        return name1 == name2 or (name1 in name2) or (name2 in name1)


def main():
    # Load unused files
    with open("analysis-tools/unused_files_report.json") as f:
        unused_files = json.load(f)["unused_files"]

    # Get all ethics files
    all_ethics_files = []
    for root, dirs, files in os.walk("ethics"):
        for f in files:
            if f.endswith(".py"):
                all_ethics_files.append(os.path.join(root, f))

    # Separate unused ethics files
    unused_paths = {f["path"] for f in unused_files}
    unused_ethics = [f for f in all_ethics_files if f in unused_paths]
    connected_ethics = [f for f in all_ethics_files if f not in unused_paths]

    analyzer = EthicsAnalyzer()

    print("🔍 Analyzing Ethics Module")
    print("=" * 60)

    # Analyze all files
    all_analyses = []
    unused_analyses = []
    connected_analyses = []

    for filepath in all_ethics_files:
        analysis = analyzer.analyze_file(filepath)
        all_analyses.append(analysis)

        if filepath in unused_ethics:
            unused_analyses.append(analysis)
        else:
            connected_analyses.append(analysis)

    # Find patterns in unused files
    pattern_count = defaultdict(int)
    for analysis in unused_analyses:
        for pattern in analysis["patterns"]:
            pattern_count[pattern] += 1

    print("\n📊 Statistics:")
    print(f"Total ethics files: {len(all_ethics_files)}")
    print(f"Connected files: {len(connected_ethics)}")
    print(f"Unused files: {len(unused_ethics)}")

    print("\n🎯 Common patterns in unused files:")
    for pattern, count in sorted(
        pattern_count.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {pattern}: {count} files")

    # Find similar files that could be consolidated
    print("\n🔄 Potential consolidations:")
    similar_unused = analyzer.find_similar_files(unused_analyses)

    for group in similar_unused:
        print(f"\n  Group of {len(group)} similar unused files:")
        for f in group:
            print(f"    - {f}")

    # Check if unused files duplicate connected functionality
    print("\n⚠️  Unused files that might duplicate connected functionality:")

    for unused in unused_analyses[:10]:  # Check first 10
        for connected in connected_analyses:
            if analyzer.are_similar(unused, connected):
                print(f"\n  {unused['path']}")
                print(f"    Similar to connected: {connected['path']}")
                print(
                    f"    Shared patterns: {set(unused['patterns']) & set(connected['patterns'])}"
                )
                break

    # Save detailed report
    report = {
        "summary": {
            "total_files": len(all_ethics_files),
            "connected_files": len(connected_ethics),
            "unused_files": len(unused_ethics),
            "pattern_distribution": dict(pattern_count),
        },
        "similar_groups": similar_unused,
        "unused_analyses": unused_analyses,
        "connected_analyses": connected_analyses,
    }

    with open("analysis-tools/ethics_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Full report saved to: analysis-tools/ethics_analysis.json")


if __name__ == "__main__":
    main()
