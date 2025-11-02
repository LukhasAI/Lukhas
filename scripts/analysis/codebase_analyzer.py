#!/usr/bin/env python3
"""
Codebase Analyzer - Systematic analysis tool for messy codebases
Helps identify naming inconsistencies, misplaced files, and organizational issues
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path


class CodebaseAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files = []
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)

    def scan_codebase(self) -> dict:
        """Main scanning function that analyzes the entire codebase"""
        print(f"🔍 Analyzing codebase at: {self.root_path}")

        # Collect all Python files
        self._collect_files()

        # Run all analyses
        self._analyze_naming_patterns()
        self._analyze_file_placement()
        self._analyze_imports()
        self._analyze_duplicates()
        self._analyze_stub_files()
        self._find_documentation_in_code()

        return self._generate_report()

    def _collect_files(self):
        """Collect all Python files and basic info"""
        for py_file in self.root_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            file_info = {
                "path": py_file,
                "relative_path": py_file.relative_to(self.root_path),
                "name": py_file.name,
                "stem": py_file.stem,
                "parent": py_file.parent.name,
                "size": py_file.stat().st_size,
                "lines": self._count_lines(py_file),
            }
            self.files.append(file_info)
            self.stats["total_files"] += 1
            self.stats["total_lines"] += file_info["lines"]

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                return len(f.readlines())
        except Exception as e:
            logger.debug(f"Expected optional failure: {e}")
            return 0

    def _analyze_naming_patterns(self):
        """Analyze naming inconsistencies"""
        print("📝 Analyzing naming patterns...")

        # Common problematic patterns
        bad_patterns = {
            "redundant_prefixes": [
                r"qi_.*\.py$",
                r"bio_bio_.*\.py$",
                r"symbolic_bio_.*\.py$",
            ],
            "vague_names": [r"^(system|core|hub|main|base|utils?)\.py$"],
            "inconsistent_adapters": [r".*adapt(er|ation|or).*\.py$"],
            "placeholder_names": [r".*(temp|tmp|test|placeholder|stub|mock).*\.py$"],
            "documentation_files": [r".*(doc|readme|index|header).*\.py$"],
            "unclear_purpose": [r".*(bulletproof|inspiration|misc|random).*\.py$"],
        }

        for file_info in self.files:
            filename = file_info["name"]

            for category, patterns in bad_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, filename, re.IGNORECASE):
                        self.issues[category].append(
                            {
                                "file": str(file_info["relative_path"]),
                                "reason": f"Matches pattern: {pattern}",
                                "lines": file_info["lines"],
                            }
                        )

        # Find naming inconsistencies within similar concepts
        self._find_concept_inconsistencies()

    def _find_concept_inconsistencies(self):
        """Find files that should probably be named consistently"""
        concepts = defaultdict(list)

        # Group files by concept keywords
        concept_keywords = [
            "adapter",
            "oscillator",
            "quantum",
            "bio",
            "symbolic",
            "system",
            "engine",
            "processor",
            "manager",
            "coordinator",
            "optimizer",
            "cellular",
            "hormone",
            "awareness",
            "neural",
        ]

        for file_info in self.files:
            filename = file_info["stem"].lower()
            for keyword in concept_keywords:
                if keyword in filename:
                    concepts[keyword].append(file_info)

        # Find inconsistencies within concepts
        for concept, files in concepts.items():
            if len(files) > 1:
                names = [f["stem"] for f in files]
                # Check for inconsistent naming patterns
                variations = self._find_naming_variations(names, concept)
                if variations:
                    self.issues["concept_inconsistencies"].append(
                        {
                            "concept": concept,
                            "files": [str(f["relative_path"]) for f in files],
                            "variations": variations,
                        }
                    )

    def _find_naming_variations(self, names: list[str], concept: str) -> list[str]:
        """Find different ways the same concept is named"""
        variations = []
        patterns = [f"{concept}_.*", f".*_{concept}", f".*{concept}.*", f"{concept}.*"]

        found_patterns = set()
        for name in names:
            for pattern in patterns:
                if re.match(pattern, name, re.IGNORECASE):
                    found_patterns.add(pattern)

        if len(found_patterns) > 1:
            variations = list(found_patterns)

        return variations

    def _analyze_file_placement(self):
        """Analyze if files are in the correct directories"""
        print("📁 Analyzing file placement...")

        # Expected directory purposes
        expected_purposes = {
            "bio": ["biological", "cellular", "hormone", "neural", "organic"],
            "core": ["fundamental", "base", "essential", "primary"],
            "processing": ["process", "compute", "transform", "pipeline"],
            "quantum": ["quantum", "oscillator", "entangle", "superposition"],
            "awareness": ["consciousness", "perception", "attention", "aware"],
            "states": ["state", "status", "condition", "mode"],
            "governance": ["ethics", "policy", "rule", "compliance"],
            "orchestration": ["orchestrat", "coordinat", "manage", "control"],
        }

        for file_info in self.files:
            parent_dir = file_info["parent"]
            filename = file_info["stem"].lower()

            # Check if file seems misplaced
            for expected_dir, keywords in expected_purposes.items():
                if parent_dir != expected_dir:
                    for keyword in keywords:
                        if keyword in filename:
                            self.issues["misplaced_files"].append(
                                {
                                    "file": str(file_info["relative_path"]),
                                    "current_dir": parent_dir,
                                    "suggested_dir": expected_dir,
                                    "reason": f"Contains '{keyword}' keyword",
                                }
                            )
                            break

    def _analyze_imports(self):
        """Analyze import patterns and dependencies"""
        print("🔗 Analyzing imports...")

        for file_info in self.files:
            try:
                with open(file_info["path"], encoding="utf-8") as f:
                    content = f.read()

                # Find import statements
                imports = re.findall(r"^(?:from|import)\s+([^\s]+)", content, re.MULTILINE)

                # Check for problematic imports
                for imp in imports:
                    if "qi." in imp:
                        # Check if imported module might not exist due to renaming
                        parts = imp.split(".")
                        if len(parts) > 1:
                            potential_issues = [
                                "system_orchestrator",
                                "bio_optimization_adapter",
                                "qi_hub",
                                "bulletproof_system",
                            ]

                            for issue in potential_issues:
                                if issue in imp:
                                    self.issues["broken_imports"].append(
                                        {
                                            "file": str(file_info["relative_path"]),
                                            "import": imp,
                                            "reason": f"Likely broken import: {issue}",
                                        }
                                    )
            except Exception:
                continue

    def _analyze_duplicates(self):
        """Find potential duplicate files"""
        print("🔄 Analyzing duplicates...")

        # Group by similar names
        similar_names = defaultdict(list)

        for file_info in self.files:
            # Normalize name for comparison
            normalized = re.sub(r"[_-]", "", file_info["stem"].lower())
            normalized = re.sub(r"(adapter|adaptor|system|engine|manager)$", "", normalized)

            if len(normalized) > 3:  # Skip very short names
                similar_names[normalized].append(file_info)

        # Find groups with multiple files
        for normalized_name, files in similar_names.items():
            if len(files) > 1:
                self.issues["potential_duplicates"].append(
                    {
                        "normalized_name": normalized_name,
                        "files": [{"path": str(f["relative_path"]), "lines": f["lines"]} for f in files],
                    }
                )

    def _analyze_stub_files(self):
        """Find stub/placeholder files with minimal content"""
        print("📄 Analyzing stub files...")

        for file_info in self.files:
            if file_info["lines"] < 20:  # Very small files
                try:
                    with open(file_info["path"], encoding="utf-8") as f:
                        content = f.read().strip()

                    # Check for common stub patterns
                    stub_indicators = [
                        "pass",
                        "todo",
                        "placeholder",
                        "not implemented",
                        "quarantined",
                    ]

                    if any(indicator in content.lower() for indicator in stub_indicators):
                        self.issues["stub_files"].append(
                            {
                                "file": str(file_info["relative_path"]),
                                "lines": file_info["lines"],
                                "reason": "Contains stub indicators",
                            }
                        )
                except Exception:
                    continue

    def _find_documentation_in_code(self):
        """Find documentation files mixed with code"""
        print("📚 Finding documentation in code directories...")

        doc_patterns = [r".*\.(md|txt|rst|doc)$", r".*(readme|index|doc|header).*\.py$"]

        for file_info in self.files:
            for pattern in doc_patterns:
                if re.search(pattern, str(file_info["relative_path"]), re.IGNORECASE):
                    # Skip if already in docs directory
                    if "docs" not in str(file_info["relative_path"]):
                        self.issues["documentation_in_code"].append(
                            {
                                "file": str(file_info["relative_path"]),
                                "type": "documentation file in code directory",
                            }
                        )

    def _generate_report(self) -> dict:
        """Generate comprehensive analysis report"""
        print("📊 Generating report...")

        report = {
            "summary": {
                "total_files": self.stats["total_files"],
                "total_lines": self.stats["total_lines"],
                "total_issues": sum(len(issues) for issues in self.issues.values()),
                "issue_categories": len(self.issues),
            },
            "issues": dict(self.issues),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> list[dict]:
        """Generate actionable recommendations"""
        recommendations = []

        # Priority recommendations based on issues found
        if self.issues["stub_files"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Remove stub files",
                    "description": f"Remove {len(self.issues['stub_files'])} stub/placeholder files",
                    "files": [issue["file"] for issue in self.issues["stub_files"]],
                }
            )

        if self.issues["redundant_prefixes"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Fix redundant prefixes",
                    "description": f"Rename {len(self.issues['redundant_prefixes'])} files with redundant prefixes",
                    "files": [issue["file"] for issue in self.issues["redundant_prefixes"]],
                }
            )

        if self.issues["documentation_in_code"]:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Move documentation",
                    "description": f"Move {len(self.issues['documentation_in_code'])} documentation files to docs/",
                    "files": [issue["file"] for issue in self.issues["documentation_in_code"]],
                }
            )

        if self.issues["misplaced_files"]:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Reorganize file placement",
                    "description": f"Move {len(self.issues['misplaced_files'])} misplaced files to appropriate directories",
                    "affected_files": len(self.issues["misplaced_files"]),
                }
            )

        if self.issues["potential_duplicates"]:
            recommendations.append(
                {
                    "priority": "LOW",
                    "action": "Review duplicates",
                    "description": f"Review {len(self.issues['potential_duplicates'])} potential duplicate file groups",
                    "affected_groups": len(self.issues["potential_duplicates"]),
                }
            )

        return recommendations

    def print_report(self, report: dict):
        """Print a human-readable report"""
        print("\n" + "=" * 60)
        print("🔍 CODEBASE ANALYSIS REPORT")
        print("=" * 60)

        # Summary
        summary = report["summary"]
        print("\n📊 SUMMARY:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Total lines: {summary['total_lines']:,}")
        print(f"  Issues found: {summary['total_issues']}")
        print(f"  Issue categories: {summary['issue_categories']}")

        # Issues by category
        print("\n🚨 ISSUES BY CATEGORY:")
        for category, issues in report["issues"].items():
            if issues:
                print(f"\n  {category.replace('_', ' ').title()}: {len(issues)} issues")
                for _i, issue in enumerate(issues[:3]):  # Show first 3
                    if "file" in issue:
                        print(f"    • {issue['file']}")
                    elif "files" in issue:
                        print(f"    • Group: {len(issue['files'])} files")
                if len(issues) > 3:
                    print(f"    ... and {len(issues) - 3} more")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            print(f"\n  {priority_color.get(rec['priority'], '⚪')} {rec['priority']} PRIORITY")
            print(f"    Action: {rec['action']}")
            print(f"    Description: {rec['description']}")

        print("\n" + "=" * 60)

    def save_report(self, report: dict, filename: str = "codebase_analysis.json"):
        """Save report to JSON file"""
        # Convert Path objects to strings for JSON serialization
        json_report = json.loads(json.dumps(report, default=str))

        with open(filename, "w") as f:
            json.dump(json_report, f, indent=2)

        print(f"📝 Report saved to: {filename}")


def main():
    """Main function to run the analyzer"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python codebase_analyzer.py <path_to_codebase>")
        sys.exit(1)

    codebase_path = sys.argv[1]

    if not os.path.exists(codebase_path):
        print(f"Error: Path '{codebase_path}' does not exist")
        sys.exit(1)

    analyzer = CodebaseAnalyzer(codebase_path)
    report = analyzer.scan_codebase()
    analyzer.print_report(report)
    analyzer.save_report(report)


if __name__ == "__main__":
    main()
