#!/usr/bin/env python3
"""
Orphaned Module Auditor for LUKHAS AI
Helps audit AI/AGI system logic that appears unused but may be valuable
Trinity Framework: ⚛️🧠🛡️
"""
from consciousness.qi import qi
import time
import streamlit as st

import ast
import json
from pathlib import Path


class OrphanedModuleAuditor:
    def __init__(self):
        # Load the usage report
        with open("module_usage_report.json") as f:
            self.report = json.load(f)

        # Critical AI/AGI modules that should NEVER be auto-archived
        self.critical_modules = {
            "consciousness",
            "memory",
            "identity",
            "governance",
            "quantum",
            "bio",
            "emotion",
            "reasoning",
            "orchestration",
            "symbolic",
            "universal_language",
            "vivox",
            "qim",
            "NIAS_THEORY",
            "constellation",
            "guardian",
            "lukhas",
        }

        # Value indicators in code
        self.value_indicators = {
            "constellation_framework": ["⚛️", "🧠", "🛡️", "Trinity"],
            "consciousness": ["consciousness", "awareness", "sentience"],
            "agi_concepts": [
                "AGI",
                "artificial general",
                "meta-learning",
                "self-aware",
            ],
            "quantum": ["quantum", "superposition", "entanglement", "collapse"],
            "bio_inspired": ["bio-inspired", "neural", "synaptic", "neuroplastic"],
            "ethics": ["ethical", "guardian", "consent", "privacy"],
            "memory": ["fold", "episodic", "semantic", "memory"],
            "advanced_ai": ["transformer", "attention", "reasoning", "symbolic"],
        }

    def analyze_file_value(self, file_path: str) -> dict:
        """Analyze a file to determine its potential value"""
        full_path = Path(file_path)
        if not full_path.exists():
            return {"exists": False}

        analysis = {
            "exists": True,
            "size_kb": full_path.stat().st_size / 1024,
            "has_docstring": False,
            "has_classes": False,
            "has_functions": False,
            "line_count": 0,
            "import_count": 0,
            "value_indicators": [],
            "complexity_score": 0,
            "has_tests": False,
            "last_modified": full_path.stat().st_mtime,
        }

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
                analysis["line_count"] = len(lines)

                # Check for value indicators
                for category, keywords in self.value_indicators.items():
                    for keyword in keywords:
                        if keyword in content:
                            analysis["value_indicators"].append(f"{category}:{keyword}")

                # Parse AST
                tree = ast.parse(content)

                # Check for docstring
                if ast.get_docstring(tree):
                    analysis["has_docstring"] = True

                # Count classes, functions, imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        analysis["has_classes"] = True
                        analysis["complexity_score"] += 5
                    elif isinstance(node, ast.FunctionDef):
                        analysis["has_functions"] = True
                        analysis["complexity_score"] += 2
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        analysis["import_count"] += 1

                # Check if there's a corresponding test
                test_patterns = [
                    f"tests/test_{Path(file_path).stem}.py",
                    f"tests/{Path(file_path).parent}/test_{Path(file_path).stem}.py",
                ]
                for pattern in test_patterns:
                    if Path(pattern).exists():
                        analysis["has_tests"] = True
                        break

        except Exception as e:
            analysis["parse_error"] = str(e)

        # Calculate value score
        analysis["value_score"] = self._calculate_value_score(analysis)

        return analysis

    def _calculate_value_score(self, analysis: dict) -> int:
        """Calculate a value score for the file"""
        score = 0

        # Size and complexity
        if analysis.get("line_count", 0) > 100:
            score += 10
        if analysis.get("has_classes"):
            score += 20
        if analysis.get("has_functions"):
            score += 10
        if analysis.get("has_docstring"):
            score += 15

        # Value indicators (most important)
        score += len(analysis.get("value_indicators", [])) * 25

        # Has tests
        if analysis.get("has_tests"):
            score += 30

        # Import complexity
        if analysis.get("import_count", 0) > 5:
            score += 10

        return score

    def audit_orphaned_files(self, limit: int = 50) -> dict:
        """Audit orphaned files and categorize by value"""
        never_imported = self.report["never_imported"][:limit]

        audit_results = {
            "high_value": [],  # Score > 100
            "medium_value": [],  # Score 50-100
            "low_value": [],  # Score < 50
            "safe_to_archive": [],  # No AI/AGI value
            "needs_review": [],  # Contains critical keywords but low score
        }

        for file_path in never_imported:
            # Skip test files and obvious non-critical files
            if file_path.startswith("tests/") or "__pycache__" in file_path:
                continue

            # Check if it's in a critical module
            is_critical = any(module in file_path for module in self.critical_modules)

            # Analyze the file
            analysis = self.analyze_file_value(file_path)
            analysis["file_path"] = file_path
            analysis["is_critical_module"] = is_critical

            # Categorize based on value score
            score = analysis.get("value_score", 0)

            if score > 100:
                audit_results["high_value"].append(analysis)
            elif score >= 50:
                audit_results["medium_value"].append(analysis)
            elif is_critical or len(analysis.get("value_indicators", [])) > 0:
                audit_results["needs_review"].append(analysis)
            elif not is_critical and score < 20:
                audit_results["safe_to_archive"].append(analysis)
            else:
                audit_results["low_value"].append(analysis)

        return audit_results

    def generate_audit_report(self, audit_results: dict):
        """Generate a detailed audit report"""
        print("\n🔍 ORPHANED MODULE AUDIT REPORT")
        print("=" * 80)
        print("⚠️  IMPORTANT: All AI/AGI system logic must be audited individually")
        print("=" * 80)

        # High value files
        if audit_results["high_value"]:
            print("\n🌟 HIGH VALUE FILES (Score > 100) - DO NOT DELETE")
            print("-" * 80)
            for file in audit_results["high_value"][:10]:
                self._print_file_summary(file)

        # Needs review
        if audit_results["needs_review"]:
            print("\n⚠️  NEEDS MANUAL REVIEW (Contains AI/AGI concepts)")
            print("-" * 80)
            for file in audit_results["needs_review"][:10]:
                self._print_file_summary(file)

        # Medium value
        if audit_results["medium_value"]:
            print("\n📊 MEDIUM VALUE FILES (Score 50-100)")
            print("-" * 80)
            for file in audit_results["medium_value"][:5]:
                self._print_file_summary(file)

        # Safe to archive
        if audit_results["safe_to_archive"]:
            print("\n✅ POTENTIALLY SAFE TO ARCHIVE (No AI value detected)")
            print("-" * 80)
            for file in audit_results["safe_to_archive"][:5]:
                print(f"  - {file['file_path']} (Score: {file['value_score']})")

        # Summary
        print("\n📈 SUMMARY")
        print("-" * 80)
        print(f"High value files: {len(audit_results['high_value'])}")
        print(f"Need review: {len(audit_results['needs_review'])}")
        print(f"Medium value: {len(audit_results['medium_value'])}")
        print(f"Low value: {len(audit_results['low_value'])}")
        print(f"Safe to archive: {len(audit_results['safe_to_archive'])}")

    def _print_file_summary(self, file_analysis: dict):
        """Print a summary of file analysis"""
        path = file_analysis["file_path"]
        score = file_analysis["value_score"]
        indicators = file_analysis.get("value_indicators", [])

        print(f"\n📄 {path}")
        print(
            f"   Score: {score} | Lines: {file_analysis.get('line_count', 0)} | "
            f"Size: {file_analysis.get('size_kb', 0):.1f}KB"
        )

        if indicators:
            print(f"   AI/AGI Indicators: {', '.join(indicators[:3])}")

        if file_analysis.get("has_classes"):
            print("   ✓ Contains classes")
        if file_analysis.get("has_tests"):
            print("   ✓ Has test coverage")
        if file_analysis.get("is_critical_module"):
            print("   ⚠️  CRITICAL MODULE - Manual review required")


def main():
    auditor = OrphanedModuleAuditor()

    print("🔍 Auditing orphaned modules for AI/AGI value...")
    print("⚠️  This tool helps identify valuable code - DO NOT auto-delete anything!")

    # Audit the first 100 orphaned files
    audit_results = auditor.audit_orphaned_files(limit=100)

    # Generate report
    auditor.generate_audit_report(audit_results)

    # Save detailed audit to JSON
    audit_path = Path("orphaned_modules_audit.json")
    with open(audit_path, "w") as f:
        # Convert to serializable format
        serializable_results = {}
        for category, files in audit_results.items():
            serializable_results[category] = []
            for file in files:
                file_copy = file.copy()
                # Remove non-serializable items
                if "last_modified" in file_copy:
                    file_copy["last_modified"] = str(file_copy["last_modified"])
                serializable_results[category].append(file_copy)

        json.dump(serializable_results, f, indent=2)

    print(f"\n💾 Detailed audit saved to: {audit_path}")
    print("\n⚠️  REMEMBER: Manually review each file before archiving!")
    print("   These modules may contain valuable AI/AGI innovations")


if __name__ == "__main__":
    main()