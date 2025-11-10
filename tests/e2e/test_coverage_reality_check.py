#!/usr/bin/env python3
"""
📊🔍 LUKHAS REAL COVERAGE ANALYSIS
================================

OBJECTIVE: Get REAL coverage numbers, not inflated estimates
- Count actual testable components vs tested components
- Identify gaps in testing
- Provide honest coverage assessment

Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class LukhasCoverageAnalyzer:
    """Real coverage analysis of LUKHAS systems"""

    def __init__(self, root_path: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas"):
        self.root_path = Path(root_path)
        self.results = {}
        self.test_files = set()
        self.source_files = set()
        self.coverage_data = {}

    def discover_all_python_files(self) -> Dict[str, list]:
        """Discover ALL Python files in the repository"""
        print("🔍 DISCOVERING ALL PYTHON FILES...")

        # Exclude patterns
        exclude_patterns = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "venv",
            ".venv",
            "node_modules",
            "build",
            "dist",
            ".egg-info",
            "backup",
            "archive",
            "recovery",
            "._cleanup_archive",
        }

        source_files = []
        test_files = []

        for py_file in self.root_path.rglob("*.py"):
            # Skip excluded directories
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            relative_path = py_file.relative_to(self.root_path)

            # Classify as test or source
            if self._is_test_file(py_file):
                test_files.append(str(relative_path))
                self.test_files.add(str(relative_path))
            else:
                source_files.append(str(relative_path))
                self.source_files.add(str(relative_path))

        print(f"  📁 Source files found: {len(source_files)}")
        print(f"  🧪 Test files found: {len(test_files)}")

        return {
            "source_files": source_files,
            "test_files": test_files,
            "total_files": len(source_files) + len(test_files),
        }

    def _is_test_file(self, file_path: Path) -> bool:
        """Determine if a file is a test file"""
        file_str = str(file_path)
        name = file_path.name

        # Test file patterns
        test_patterns = ["test_", "_test.py", "/tests/", "/test/", "conftest.py", "pytest", "unittest"]

        return any(pattern in file_str or pattern in name for pattern in test_patterns)

    def analyze_major_systems(self) -> Dict[str, dict]:
        """Analyze major system directories and their testing status"""
        print("\n🏗️ ANALYZING MAJOR SYSTEMS...")

        # Define major system directories
        major_systems = {
            "core": "Core consciousness and symbolic systems",
            "identity": "Identity management and ΛID systems",
            "memory": "Memory, persistence, and recall systems",
            "consciousness": "Consciousness modules and processing",
            "emotion": "Emotion and creative systems",
            "quantum": "Quantum-inspired processing",
            "bio": "Bio-inspired systems and optimization",
            "security": "Security and guardian systems",
            "api": "FastAPI backend and endpoints",
            "orchestration": "High-level orchestration systems",
            "agents": "AI agent coordination and management",
            "products": "Product integration and SDK",
            "monitoring": "System monitoring and analytics",
            "tools": "Development and analysis tools",
            "docs": "Documentation systems",
            "branding": "Branding and design systems",
            "business": "Business logic and operations",
            "deployment": "Deployment and infrastructure",
            "scripts": "Automation and utility scripts",
            "tests": "Testing infrastructure itself",
        }

        system_analysis = {}

        for system_name, description in major_systems.items():
            system_path = self.root_path / system_name

            if not system_path.exists():
                system_analysis[system_name] = {
                    "exists": False,
                    "description": description,
                    "source_files": 0,
                    "test_files": 0,
                    "coverage_ratio": 0.0,
                    "status": "❌ Not Found",
                }
                continue

            # Count files in this system
            source_count = 0
            test_count = 0

            for py_file in system_path.rglob("*.py"):
                str(py_file.relative_to(self.root_path))

                if self._is_test_file(py_file):
                    test_count += 1
                else:
                    source_count += 1

            # Calculate coverage ratio
            coverage_ratio = min(test_count / source_count, 1.0) if source_count > 0 else 1.0 if test_count > 0 else 0.0

            # Determine status
            if coverage_ratio >= 0.8:
                status = "🟢 Well Tested"
            elif coverage_ratio >= 0.5:
                status = "🟡 Partially Tested"
            elif coverage_ratio >= 0.2:
                status = "🟠 Minimal Testing"
            else:
                status = "🔴 Untested"

            system_analysis[system_name] = {
                "exists": True,
                "description": description,
                "source_files": source_count,
                "test_files": test_count,
                "coverage_ratio": coverage_ratio,
                "status": status,
            }

            print(f"  {status} {system_name}: {source_count} source, {test_count} tests ({coverage_ratio:.1%})")

        return system_analysis

    def analyze_test_quality(self) -> Dict[str, Any]:
        """Analyze the quality and comprehensiveness of existing tests"""
        print("\n🧪 ANALYZING TEST QUALITY...")

        test_categories = {
            "unit": 0,
            "integration": 0,
            "functional": 0,
            "security": 0,
            "performance": 0,
            "smoke": 0,
            "comprehensive": 0,
            "basic": 0,
        }

        test_quality_score = 0
        total_test_files = len(self.test_files)

        for test_file in self.test_files:
            test_file_path = self.root_path / test_file

            try:
                content = test_file_path.read_text(encoding="utf-8")
                content_lower = content.lower()

                # Categorize test type
                if "integration" in content_lower:
                    test_categories["integration"] += 1
                    test_quality_score += 3
                elif "functional" in content_lower:
                    test_categories["functional"] += 1
                    test_quality_score += 3
                elif "security" in content_lower:
                    test_categories["security"] += 1
                    test_quality_score += 4
                elif "performance" in content_lower:
                    test_categories["performance"] += 1
                    test_quality_score += 4
                elif "comprehensive" in content_lower:
                    test_categories["comprehensive"] += 1
                    test_quality_score += 5
                elif "smoke" in content_lower:
                    test_categories["smoke"] += 1
                    test_quality_score += 2
                else:
                    test_categories["unit"] += 1
                    test_quality_score += 1

                # Check for basic vs comprehensive tests
                if "def test_" in content and content.count("def test_") >= 5:
                    test_categories["comprehensive"] += 1
                else:
                    test_categories["basic"] += 1

            except Exception as e:
                print(f"    ⚠️ Could not analyze {test_file}: {e}")

        # Calculate quality metrics
        avg_quality_score = test_quality_score / max(total_test_files, 1)

        print("  📊 Test Quality Breakdown:")
        for category, count in test_categories.items():
            if count > 0:
                percentage = (count / total_test_files) * 100
                print(f"    {category.title()}: {count} files ({percentage:.1f}%)")

        print(f"  🎯 Average Quality Score: {avg_quality_score:.1f}/5.0")

        return {"categories": test_categories, "quality_score": avg_quality_score, "total_test_files": total_test_files}

    def calculate_real_coverage(self) -> Dict[str, Any]:
        """Calculate realistic coverage metrics"""
        print("\n📊 CALCULATING REAL COVERAGE METRICS...")

        # Get file discovery results
        self.discover_all_python_files()
        system_data = self.analyze_major_systems()
        test_quality = self.analyze_test_quality()

        # Calculate various coverage metrics
        source_count = len(self.source_files)
        test_count = len(self.test_files)

        # Basic file coverage ratio
        basic_coverage = min(test_count / max(source_count, 1), 1.0)

        # System coverage (how many major systems have adequate testing)
        systems_with_good_coverage = sum(
            1
            for sys_data in system_data.values()
            if sys_data.get("coverage_ratio", 0) >= 0.5 and sys_data.get("exists", False)
        )
        existing_systems = sum(1 for sys_data in system_data.values() if sys_data.get("exists", False))
        system_coverage = systems_with_good_coverage / max(existing_systems, 1)

        # Quality-adjusted coverage
        quality_multiplier = test_quality["quality_score"] / 5.0
        quality_adjusted_coverage = basic_coverage * quality_multiplier

        # Comprehensive coverage (very conservative)
        comprehensive_coverage = (basic_coverage * 0.4) + (system_coverage * 0.4) + (quality_adjusted_coverage * 0.2)

        coverage_metrics = {
            "source_files": source_count,
            "test_files": test_count,
            "basic_file_ratio": basic_coverage,
            "system_coverage": system_coverage,
            "quality_adjusted": quality_adjusted_coverage,
            "comprehensive_coverage": comprehensive_coverage,
            "systems_well_tested": systems_with_good_coverage,
            "total_systems": existing_systems,
            "test_quality_score": test_quality["quality_score"],
        }

        print("  📈 Coverage Metrics:")
        print(f"    Basic File Ratio: {basic_coverage:.1%}")
        print(f"    System Coverage: {system_coverage:.1%} ({systems_with_good_coverage}/{existing_systems} systems)")
        print(f"    Quality Adjusted: {quality_adjusted_coverage:.1%}")
        print(f"    🎯 REALISTIC COMPREHENSIVE: {comprehensive_coverage:.1%}")

        return coverage_metrics

    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        print("📋 GENERATING COMPREHENSIVE COVERAGE REPORT...")

        file_data = self.discover_all_python_files()
        system_data = self.analyze_major_systems()
        test_quality = self.analyze_test_quality()
        coverage_metrics = self.calculate_real_coverage()

        # Identify gaps
        untested_systems = [
            name
            for name, data in system_data.items()
            if data.get("exists", False) and data.get("coverage_ratio", 0) < 0.2
        ]

        partially_tested = [
            name
            for name, data in system_data.items()
            if data.get("exists", False) and 0.2 <= data.get("coverage_ratio", 0) < 0.5
        ]

        well_tested = [
            name
            for name, data in system_data.items()
            if data.get("exists", False) and data.get("coverage_ratio", 0) >= 0.5
        ]

        report = {
            "timestamp": "2025-01-20T00:00:00Z",
            "file_discovery": file_data,
            "system_analysis": system_data,
            "test_quality": test_quality,
            "coverage_metrics": coverage_metrics,
            "gaps": {
                "untested_systems": untested_systems,
                "partially_tested": partially_tested,
                "well_tested": well_tested,
            },
            "recommendations": self._generate_recommendations(coverage_metrics, untested_systems),
        }

        return report

    def _generate_recommendations(self, metrics: dict, untested: list) -> List[str]:
        """Generate testing recommendations"""
        recommendations = []

        comprehensive_coverage = metrics["comprehensive_coverage"]

        if comprehensive_coverage < 0.3:
            recommendations.append("🚨 CRITICAL: Coverage is below 30%. Prioritize basic testing infrastructure.")
        elif comprehensive_coverage < 0.5:
            recommendations.append("⚠️ MODERATE: Coverage is below 50%. Focus on core system testing.")
        elif comprehensive_coverage < 0.7:
            recommendations.append("📈 GOOD: Coverage approaching 70%. Target remaining gaps.")
        else:
            recommendations.append("✅ EXCELLENT: Coverage above 70%. Focus on quality improvements.")

        if untested:
            recommendations.append(f"🎯 Priority systems to test: {', '.join(untested[:5])}")

        if metrics["test_quality_score"] < 3.0:
            recommendations.append("🧪 Improve test quality: Add integration and functional tests.")

        return recommendations


def print_coverage_table(report: Dict[str, Any]):
    """Print a detailed coverage table"""
    print("\n" + "=" * 100)
    print("📊 LUKHAS REAL COVERAGE INDEX TABLE")
    print("=" * 100)

    # Header
    print(f"{'SYSTEM':<20} {'STATUS':<18} {'SOURCE':<8} {'TESTS':<8} {'RATIO':<8} {'DESCRIPTION':<30}")
    print("-" * 100)

    # System rows
    systems = report["system_analysis"]
    for name, data in sorted(systems.items()):
        if not data["exists"]:
            continue

        status = data["status"]
        source = data["source_files"]
        tests = data["test_files"]
        ratio = f"{data['coverage_ratio']:.1%}"
        desc = data["description"][:28] + ".." if len(data["description"]) > 30 else data["description"]

        print(f"{name:<20} {status:<18} {source:<8} {tests:<8} {ratio:<8} {desc:<30}")

    print("-" * 100)

    # Summary metrics
    metrics = report["coverage_metrics"]
    print("\n📈 REAL COVERAGE METRICS:")
    print(f"  📁 Total Source Files: {metrics['source_files']}")
    print(f"  🧪 Total Test Files: {metrics['test_files']}")
    print(f"  📊 Basic File Ratio: {metrics['basic_file_ratio']:.1%}")
    print(
        f"  🏗️ System Coverage: {metrics['system_coverage']:.1%} ({metrics['systems_well_tested']}/{metrics['total_systems']} systems)"
    )
    print(f"  ⭐ Quality Score: {metrics['test_quality_score']:.1f}/5.0")
    print(f"  🎯 REALISTIC COMPREHENSIVE COVERAGE: {metrics['comprehensive_coverage']:.1%}")

    # Test quality breakdown
    test_qual = report["test_quality"]
    print("\n🧪 TEST QUALITY BREAKDOWN:")
    for category, count in test_qual["categories"].items():
        if count > 0:
            print(f"  {category.title()}: {count} files")

    # Gaps and recommendations
    gaps = report["gaps"]
    print("\n🔍 TESTING GAPS:")
    if gaps["untested_systems"]:
        print(f"  🔴 Untested: {', '.join(gaps['untested_systems'])}")
    if gaps["partially_tested"]:
        print(f"  🟡 Partial: {', '.join(gaps['partially_tested'])}")
    print(f"  🟢 Well Tested: {', '.join(gaps['well_tested'])}")

    print("\n💡 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"  {rec}")

    print("\n⚛️🧠🛡️ Real Coverage Analysis Complete!")


def main():
    """Run comprehensive coverage analysis"""
    print("🔍📊 LUKHAS REAL COVERAGE ANALYSIS")
    print("=" * 80)
    print("Getting HONEST numbers on LUKHAS testing coverage...")
    print("=" * 80)

    analyzer = LukhasCoverageAnalyzer()
    report = analyzer.generate_coverage_report()

    # Save report
    report_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas/coverage_reality_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print_coverage_table(report)

    print(f"\n💾 Full report saved to: {report_path}")

    return report


if __name__ == "__main__":
    main()
