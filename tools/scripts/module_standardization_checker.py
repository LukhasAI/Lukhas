#!/usr/bin/env python3
"""
LUKHAS Module Standardization Checker
Checks which modules meet enterprise standards
"""
from consciousness.qi import qi
import streamlit as st
from datetime import timezone

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Required structure for standardized modules
REQUIRED_STRUCTURE = {
    "files": [
        "README.md",
        "__init__.py",
        "requirements.txt",
        "setup.py",
        ".env.example",
    ],
    "directories": [
        "core",
        "models",
        "api",
        "utils",
        "config",
        "docs",
        "tests",
        "examples",
        "benchmarks",
    ],
    "docs": [
        "docs/API.md",
        "docs/ARCHITECTURE.md",
        "docs/CONCEPTS.md",
        "docs/EXAMPLES.md",
    ],
    "config": ["config/default.yaml", "config/schema.json"],
    "tests": ["tests/unit", "tests/integration", "tests/fixtures"],
}

# Core modules to check (from standardization plan)
CORE_MODULES = [
    "core",
    "memory",
    "consciousness",
    "dream",
    "quantum",
    "identity",
    "orchestration",
    "reasoning",
    "emotion",
    "bio",
    "symbolic",
    "ethics",
    "governance",
    "learning",
    "creativity",
    "voice",
    "bridge",
    "api",
    "security",
    "compliance",
]


class ModuleStandardizationChecker:
    def __init__(self, base_path: Path = Path(".")):
        self.base_path = base_path
        self.results = {}

    def check_module(self, module_name: str) -> dict[str, any]:
        """Check if a module meets standardization requirements"""
        module_path = self.base_path / module_name

        if not module_path.exists():
            return {
                "exists": False,
                "score": 0,
                "missing": "Module directory not found",
            }

        results = {
            "exists": True,
            "score": 0,
            "total_checks": 0,
            "passed_checks": 0,
            "missing_files": [],
            "missing_dirs": [],
            "missing_docs": [],
            "missing_config": [],
            "missing_tests": [],
            "has_lukhas_concepts": False,
            "file_count": 0,
            "recommendations": [],
        }

        # Count total files
        results["file_count"] = sum(1 for _ in module_path.rglob("*") if _.is_file())

        # Check required files
        for req_file in REQUIRED_STRUCTURE["files"]:
            results["total_checks"] += 1
            file_path = module_path / req_file
            if file_path.exists():
                results["passed_checks"] += 1
            else:
                results["missing_files"].append(req_file)

        # Check required directories
        for req_dir in REQUIRED_STRUCTURE["directories"]:
            results["total_checks"] += 1
            dir_path = module_path / req_dir
            if dir_path.exists() and dir_path.is_dir():
                results["passed_checks"] += 1
            else:
                results["missing_dirs"].append(req_dir)

        # Check documentation
        for req_doc in REQUIRED_STRUCTURE["docs"]:
            results["total_checks"] += 1
            doc_path = module_path / req_doc
            if doc_path.exists():
                results["passed_checks"] += 1
            else:
                results["missing_docs"].append(req_doc)

        # Check config files
        for req_config in REQUIRED_STRUCTURE["config"]:
            results["total_checks"] += 1
            config_path = module_path / req_config
            if config_path.exists():
                results["passed_checks"] += 1
            else:
                results["missing_config"].append(req_config)

        # Check test structure
        for req_test in REQUIRED_STRUCTURE["tests"]:
            results["total_checks"] += 1
            test_path = module_path / req_test
            if test_path.exists():
                results["passed_checks"] += 1
            else:
                results["missing_tests"].append(req_test)

        # Check for LUKHAS concepts
        init_file = module_path / "__init__.py"
        if init_file.exists():
            content = init_file.read_text()
            if any(
                concept in content
                for concept in [
                    "lukhas",
                    "memory_fold",
                    "dream_recall",
                    "qi_coherence",
                    "glyph",
                ]
            ):
                results["has_lukhas_concepts"] = True
                results["passed_checks"] += 1
            results["total_checks"] += 1

        # Calculate score
        if results["total_checks"] > 0:
            results["score"] = (results["passed_checks"] / results["total_checks"]) * 100

        # Generate recommendations
        if results["missing_files"]:
            results["recommendations"].append(f"Create missing files: {', '.join(results['missing_files']}")
        if results["missing_dirs"]:
            results["recommendations"].append(f"Create missing directories: {', '.join(results['missing_dirs']}")
        if results["missing_docs"]:
            results["recommendations"].append("Add comprehensive documentation")
        if results["missing_tests"]:
            results["recommendations"].append("Implement test suite")
        if not results["has_lukhas_concepts"]:
            results["recommendations"].append("Integrate LUKHAS concepts into module")

        return results

    def check_all_modules(self) -> dict[str, any]:
        """Check all core modules"""
        print("🔍 Checking module standardization...\n")

        for module in CORE_MODULES:
            self.results[module] = self.check_module(module)

            # Display progress
            result = self.results[module]
            if result["exists"]:
                status = "✅" if result["score"] >= 80 else "⚠️" if result["score"] >= 50 else "❌"
                print(f"{status} {module:<15} Score: {result['score']:>5.1f}% | Files: {result['file_count']:>4}")
            else:
                print(f"❌ {module:<15} Not found")

        return self.results

    def generate_report(self) -> dict[str, any]:
        """Generate detailed standardization report"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_modules": len(CORE_MODULES),
                "existing_modules": sum(1 for r in self.results.values() if r.get("exists", False)),
                "fully_compliant": sum(1 for r in self.results.values() if r.get("score", 0) >= 95),
                "partially_compliant": sum(1 for r in self.results.values() if 50 <= r.get("score", 0) < 95),
                "non_compliant": sum(1 for r in self.results.values() if r.get("score", 0) < 50),
                "average_score": 0,
            },
            "modules": {},
            "priority_actions": [],
        }

        # Calculate average score
        scores = [r["score"] for r in self.results.values() if r.get("exists", False)]
        if scores:
            report["summary"]["average_score"] = sum(scores) / len(scores)

        # Add module details
        for module, result in self.results.items():
            if result.get("exists", False):
                report["modules"][module] = {
                    "score": result["score"],
                    "file_count": result["file_count"],
                    "has_lukhas_concepts": result["has_lukhas_concepts"],
                    "missing_components": {
                        "files": result["missing_files"],
                        "directories": result["missing_dirs"],
                        "documentation": result["missing_docs"],
                        "config": result["missing_config"],
                        "tests": result["missing_tests"],
                    },
                    "recommendations": result["recommendations"],
                }

        # Determine priority actions
        # Priority 1: Core modules with low scores
        for module in ["core", "memory", "consciousness", "dream", "quantum"]:
            if module in self.results and self.results[module].get("score", 0) < 80:
                report["priority_actions"].append(
                    {
                        "module": module,
                        "action": f"Standardize {module} module (current score: {self.results[module]['score']:.1f}%)",
                        "priority": "HIGH",
                    }
                )

        # Priority 2: Missing critical documentation
        for module, result in self.results.items():
            if result.get("exists", False) and len(result.get("missing_docs", [])) > 2:
                report["priority_actions"].append(
                    {
                        "module": module,
                        "action": "Add missing documentation",
                        "priority": "MEDIUM",
                    }
                )

        # Priority 3: Missing tests
        for module, result in self.results.items():
            if result.get("exists", False) and len(result.get("missing_tests", [])) > 0:
                report["priority_actions"].append(
                    {
                        "module": module,
                        "action": "Implement test suite",
                        "priority": "MEDIUM",
                    }
                )

        return report

    def save_report(self, report: dict[str, any], output_path: Optional[Path] = None):
        """Save report to file"""
        if output_path is None:
            output_path = self.base_path / "docs" / "reports" / "module_standardization_report.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {output_path}")


def print_summary(report: dict[str, any]):
    """Print a summary of the standardization status"""
    print("\n" + "=" * 60)
    print("LUKHAS MODULE STANDARDIZATION SUMMARY")
    print("=" * 60)

    summary = report["summary"]
    print("\n📊 Overall Status:")
    print(f"   Total modules: {summary['total_modules']}")
    print(f"   Existing: {summary['existing_modules']}")
    print(f"   Average score: {summary['average_score']:.1f}%")

    print("\n📈 Compliance Levels:")
    print(f"   ✅ Fully compliant (95%+): {summary['fully_compliant']}")
    print(f"   ⚠️  Partially compliant (50-94%): {summary['partially_compliant']}")
    print(f"   ❌ Non-compliant (<50%): {summary['non_compliant']}")

    print("\n🎯 Priority Actions:")
    high_priority = [a for a in report["priority_actions"] if a["priority"] == "HIGH"]
    for action in high_priority[:5]:  # Show top 5 high priority
        print(f"   🔴 {action['module']}: {action['action']}")


def main():
    """Main standardization check"""
    print(
        """
╔═══════════════════════════════════════════════════════╗
║      LUKHAS Module Standardization Checker v1.0       ║
║                                                       ║
║  Checking 20 core modules for enterprise standards    ║
╚═══════════════════════════════════════════════════════╝
    """
    )

    checker = ModuleStandardizationChecker()

    # Check all modules
    checker.check_all_modules()

    # Generate report
    report = checker.generate_report()

    # Print summary
    print_summary(report)

    # Save report
    checker.save_report(report)

    print("\n💡 Quick Actions:")
    print("   1. Use module_generator.py to create standardized modules")
    print("   2. Run consolidate_sparse_modules.py to clean up")
    print("   3. Focus on HIGH priority modules first")
    print("   4. Preserve LUKHAS concepts in all modules")

    # Suggest next module to standardize
    lowest_score_module = min(
        ((m, r) for m, r in checker.results.items() if r.get("exists", False)),
        key=lambda x: x[1]["score"],
        default=(None, None),
    )

    if lowest_score_module[0]:
        print("\n🚀 Suggested next action:")
        print(f"   python tools/scripts/module_generator.py {lowest_score_module[0]} --force")


if __name__ == "__main__":
    main()
