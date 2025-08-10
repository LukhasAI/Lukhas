#!/usr/bin/env python3
"""
Quick Integration Finder - Focused on finding high-value integration opportunities
"""

import argparse
import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import List


class QuickIntegrationFinder:
    """Quickly find integration opportunities for isolated files"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.isolated_files: List[str] = []
        self.integration_opportunities = defaultdict(list)

        # Key patterns to look for
        self.voice_keywords = ["voice", "audio", "speech", "vocal", "tts", "stt"]
        self.memory_keywords = ["memory", "mem", "recall", "storage", "cache"]
        self.lucas_patterns = ["lucas", "Lucas", "LUCAS", "LucAS", "Lucλs"]

    def load_unused_files(self, unused_file: str):
        """Load unused files report"""
        with open(unused_file) as f:
            data = json.load(f)

        # Filter for Python files with potential value
        for file_info in data.get("unused_files", []):
            file_path = file_info["path"]
            if (
                file_path.endswith(".py")
                and not file_path.startswith(".venv")
                and not file_path.startswith("tests/")
                and file_info["size_bytes"] > 1000
            ):  # Skip tiny files

                self.isolated_files.append(file_path)

        print(f"📊 Found {len(self.isolated_files)} valuable isolated files to analyze")

    def quick_analyze(self):
        """Quickly analyze files for integration opportunities"""
        print("\n🔍 Quick analysis of isolated files...")

        for file_path in self.isolated_files:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                continue

            try:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()

                # Quick content analysis
                content_lower = content.lower()

                # Check for voice-related functionality
                if any(keyword in content_lower for keyword in self.voice_keywords):
                    self._analyze_voice_file(file_path, content)

                # Check for memory-related functionality
                if any(keyword in content_lower for keyword in self.memory_keywords):
                    self._analyze_memory_file(file_path, content)

                # Check for old branding
                if any(pattern in content for pattern in self.lucas_patterns):
                    self._analyze_branding_file(file_path, content)

                # Check for specific high-value patterns
                if "orchestrat" in content_lower or "hub" in content_lower:
                    self._analyze_orchestration_file(file_path, content)

            except Exception as e:
                print(f"⚠️  Error analyzing {file_path}: {e}")

    def _analyze_voice_file(self, file_path: str, content: str):
        """Analyze voice-related files"""
        try:
            tree = ast.parse(content)
            classes = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]
            functions = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]

            if classes or functions:
                self.integration_opportunities["voice"].append(
                    {
                        "file": file_path,
                        "classes": classes,
                        "functions": functions[:5],  # Limit to top 5
                        "target": "core/voice/voice_system.py",
                        "action": "Integrate voice functionality into main voice system",
                    }
                )
        except:
            pass

    def _analyze_memory_file(self, file_path: str, content: str):
        """Analyze memory-related files"""
        try:
            tree = ast.parse(content)
            classes = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]

            if classes:
                self.integration_opportunities["memory"].append(
                    {
                        "file": file_path,
                        "classes": classes,
                        "target": "memory/memory_hub.py",
                        "action": "Integrate memory components into memory hub",
                    }
                )
        except:
            pass

    def _analyze_branding_file(self, file_path: str, content: str):
        """Analyze files with old branding"""
        self.integration_opportunities["branding"].append(
            {
                "file": file_path,
                "old_brands": [p for p in self.lucas_patterns if p in content],
                "action": "Update branding from Lucas/lucas to LUKHAS/lukhas",
            }
        )

    def _analyze_orchestration_file(self, file_path: str, content: str):
        """Analyze orchestration-related files"""
        try:
            tree = ast.parse(content)
            classes = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]

            if "orchestrator" in file_path.lower() or any(
                "orchestrator" in c.lower() for c in classes
            ):
                self.integration_opportunities["orchestration"].append(
                    {
                        "file": file_path,
                        "classes": classes,
                        "target": "core/orchestration/orchestrator.py",
                        "action": "Consolidate orchestration logic",
                    }
                )
        except:
            pass

    def generate_report(self, output_file: str):
        """Generate integration report"""
        print("\n📊 Generating quick integration report...")

        report = {
            "summary": {
                "total_isolated_files": len(self.isolated_files),
                "files_with_opportunities": sum(
                    len(files) for files in self.integration_opportunities.values()
                ),
                "categories": list(self.integration_opportunities.keys()),
            },
            "high_priority_integrations": [],
            "branding_updates": self.integration_opportunities.get("branding", []),
            "voice_integrations": self.integration_opportunities.get("voice", []),
            "memory_integrations": self.integration_opportunities.get("memory", []),
            "orchestration_consolidations": self.integration_opportunities.get(
                "orchestration", []
            ),
        }

        # Identify high priority integrations
        for category, files in self.integration_opportunities.items():
            for file_info in files[:5]:  # Top 5 per category
                report["high_priority_integrations"].append(
                    {
                        "category": category,
                        "file": file_info["file"],
                        "action": file_info.get("action", "Review and integrate"),
                    }
                )

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 70)
        print("🎯 QUICK INTEGRATION ANALYSIS SUMMARY")
        print("=" * 70)
        print("\n📊 Analysis Results:")
        print(f"  - Total isolated files: {report['summary']['total_isolated_files']}")
        print(
            f"  - Files with opportunities: {report['summary']['files_with_opportunities']}"
        )

        for category in report["summary"]["categories"]:
            count = len(self.integration_opportunities[category])
            print(f"  - {category.capitalize()}: {count} files")

        if report["high_priority_integrations"]:
            print("\n✨ Top Integration Opportunities:")
            for i, opp in enumerate(report["high_priority_integrations"][:10], 1):
                print(f"\n  {i}. {opp['file']}")
                print(f"     Category: {opp['category']}")
                print(f"     Action: {opp['action']}")

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Quick integration finder for LUKHAS AGI"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("unused_file", help="Path to unused files report JSON")
    parser.add_argument(
        "-o",
        "--output",
        default="quick_integration_plan.json",
        help="Output file for integration plan",
    )

    args = parser.parse_args()

    print("🚀 Starting Quick Integration Analysis")
    print(f"📁 Repository: {args.repo_path}")
    print(f"📊 Using unused files data: {args.unused_file}")

    finder = QuickIntegrationFinder(args.repo_path)

    # Load unused files
    finder.load_unused_files(args.unused_file)

    # Quick analysis
    finder.quick_analyze()

    # Generate report
    finder.generate_report(args.output)

    print(f"\n✅ Integration plan saved to: {args.output}")
    print("\n🎉 Quick analysis complete!")


if __name__ == "__main__":
    main()
