#!/usr/bin/env python3
"""
lukhas SYSTEM CRITICAL CONNECTIVITY ISSUES ANALYZER
==============================================
Identifies and categorizes the most critical connectivity issues in the lukhas system.
"""
import streamlit as st

import json
from collections import Counter, defaultdict
from pathlib import Path


class CriticalConnectivityAnalyzer:
    def __init__(self, report_path):
        with open(report_path) as f:
            self.report = json.load(f)

        self.broken_patterns = defaultdict(list)
        self.missing_modules = Counter()
        self.affected_systems = defaultdict(set)

    def analyze_broken_imports(self):
        """Analyze patterns in broken imports."""
        print("🔍 Analyzing broken import patterns...")

        for file_path, broken_imports_str in self.report["details"]["broken_imports"].items():
            # Parse the string representation of set
            broken_imports = eval(broken_imports_str)

            for broken_import in broken_imports:
                # Extract the missing module
                missing_module = broken_import.split(".")[0]
                self.missing_modules[missing_module] += 1

                # Categorize by system
                system = file_path.split("/")[0]
                self.affected_systems[system].add(broken_import)

                # Store pattern
                self.broken_patterns[missing_module].append({"file": file_path, "import": broken_import})

    def identify_critical_issues(self):
        """Identify the most critical connectivity issues."""
        print("🚨 Identifying critical connectivity issues...")

        critical_issues = {
            "missing_core_modules": [],
            "voice_system_issues": [],
            "bio_symbolic_issues": [],
            "cross_system_dependencies": [],
            "orphaned_components": [],
        }

        # Analyze missing modules by frequency
        for module, count in self.missing_modules.most_common():
            if count >= 5:  # High-impact missing modules
                critical_issues["missing_core_modules"].append(
                    {
                        "module": module,
                        "affected_files": count,
                        "examples": [item["file"] for item in self.broken_patterns[module][:3]],
                    }
                )

        # Voice system specific issues
        voice_related = [
            "voice_synthesis",
            "voice_safety_guard",
            "voice_profiling",
            "voice_modulator",
        ]
        for module in voice_related:
            if module in self.broken_patterns:
                critical_issues["voice_system_issues"].extend(self.broken_patterns[module])

        # Bio-symbolic issues
        bio_related = ["bio_symbolic", "bio_awareness", "bio_core"]
        for module in bio_related:
            if module in self.broken_patterns:
                critical_issues["bio_symbolic_issues"].extend(self.broken_patterns[module])

        return critical_issues

    def analyze_isolation_patterns(self):
        """Analyze patterns in isolated files."""
        print("🏝️  Analyzing file isolation patterns...")

        isolated_by_system = defaultdict(list)

        for isolated_file in self.report["details"]["isolated_files"]:
            system = isolated_file.split("/")[0]
            isolated_by_system[system].append(isolated_file)

        return dict(isolated_by_system)

    def generate_action_plan(self, critical_issues, isolation_patterns):
        """Generate actionable remediation plan."""
        action_plan = {
            "immediate_fixes": [],
            "system_restructuring": [],
            "module_consolidation": [],
            "connectivity_improvements": [],
        }

        # Immediate fixes for missing modules
        for issue in critical_issues["missing_core_modules"]:
            if issue["module"] in ["bio_symbolic", "voice_synthesis", "bio_awareness"]:
                action_plan["immediate_fixes"].append(
                    {
                        "priority": "HIGH",
                        "action": f"Create or fix import path for {issue['module']}",
                        "affected_files": issue["affected_files"],
                        "module": issue["module"],
                    }
                )

        # System restructuring needs
        high_isolation_systems = {k: v for k, v in isolation_patterns.items() if len(v) > 50}
        for system, files in high_isolation_systems.items():
            action_plan["system_restructuring"].append(
                {
                    "system": system,
                    "isolated_count": len(files),
                    "recommendation": f"Review {system} module structure and improve internal connectivity",
                }
            )

        return action_plan

    def print_analysis(self, critical_issues, isolation_patterns, action_plan):
        """Print comprehensive analysis."""
        print("\n" + "=" * 80)
        print("🎯 lukhas SYSTEM CRITICAL CONNECTIVITY ANALYSIS")
        print("=" * 80)

        print("\n📊 OVERVIEW:")
        print(f"   Total Files: {self.report['total_files']}")
        print(f"   Broken Imports: {self.report['broken_imports_count']}")
        print(f"   Isolated Files: {self.report['isolated_files_count']}")
        print(f"   Isolation Rate: {(self.report['isolated_files_count'] / self.report['total_files'] * 100)}:.1f}%")

        print("\n🚨 CRITICAL MISSING MODULES:")
        for issue in critical_issues["missing_core_modules"][:5]:
            print(f"   ❌ {issue['module']}: {issue['affected_files']} files affected")
            for example in issue["examples"]:
                print(f"      📄 {example}")

        print(f"\n🎤 VOICE SYSTEM ISSUES ({len(critical_issues['voice_system_issues'])}):")
        for issue in critical_issues["voice_system_issues"][:3]:
            print(f"   📄 {issue['file']}")
            print(f"      ❌ Missing: {issue['import']}")

        print(f"\n🧬 BIO-SYMBOLIC ISSUES ({len(critical_issues['bio_symbolic_issues'])}):")
        for issue in critical_issues["bio_symbolic_issues"][:3]:
            print(f"   📄 {issue['file']}")
            print(f"      ❌ Missing: {issue['import']}")

        print("\n🏝️  ISOLATION BY SYSTEM:")
        for system, files in sorted(isolation_patterns.items(), key=lambda x: len(x[1]), reverse=True)[:8]:
            print(f"   📂 {system}: {len(files)} isolated files")

        print("\n🔧 IMMEDIATE ACTION PLAN:")
        for action in action_plan["immediate_fixes"]:
            print(f"   🚨 {action['priority']}: {action['action']}")
            print(f"      📊 Affects {action['affected_files']} files")

        print("\n🏗️  SYSTEM RESTRUCTURING NEEDED:")
        for item in action_plan["system_restructuring"]:
            print(f"   📂 {item['system']}: {item['isolated_count']} isolated files")
            print(f"      💡 {item['recommendation']}")


def main():
    report_path = "lambda_dependency_report.json"

    if not Path(report_path).exists():
        print(f"❌ Report file {report_path} not found. Run dependency analysis first.")
        return

    analyzer = CriticalConnectivityAnalyzer(report_path)

    # Run analysis
    analyzer.analyze_broken_imports()
    critical_issues = analyzer.identify_critical_issues()
    isolation_patterns = analyzer.analyze_isolation_patterns()
    action_plan = analyzer.generate_action_plan(critical_issues, isolation_patterns)

    # Print results
    analyzer.print_analysis(critical_issues, isolation_patterns, action_plan)

    # Save detailed analysis
    analysis_results = {
        "critical_issues": critical_issues,
        "isolation_patterns": isolation_patterns,
        "action_plan": action_plan,
        "missing_modules": dict(analyzer.missing_modules.most_common(10)),
        "affected_systems": {k: list(v) for k, v in analyzer.affected_systems.items()},
    }

    with open("lambda_critical_connectivity_analysis.json", "w") as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print("\n💾 Detailed analysis saved to: lambda_critical_connectivity_analysis.json")


if __name__ == "__main__":
    main()
