#!/usr/bin/env python3
"""
Modified Intelligent File Integration System for LUKHAS AGI
Works with unused_files_report.json format
"""

import argparse
import ast
import json
import os

# Import all the classes from the original
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_file_integrator import (
    BrandingNormalizer,
    CodeAnalyzer,
    CodeSignature,
    IntegrationMatch,
    SemanticMatcher,
)


class UnusedFileIntegrator:
    """Modified integrator that works with unused files report"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.matcher = SemanticMatcher()
        self.working_signatures: List[CodeSignature] = []
        self.isolated_signatures: List[CodeSignature] = []
        self.integration_matches: List[IntegrationMatch] = []

        # File sets
        self.connected_files: Set[str] = set()
        self.isolated_files: Set[str] = set()

    def load_unused_files_data(self, unused_file: str):
        """Load unused files report"""
        with open(unused_file) as f:
            data = json.load(f)

        # Extract unused files as isolated
        for file_info in data.get("unused_files", []):
            file_path = file_info["path"]
            if file_path.endswith(".py") and not file_path.startswith(".venv"):
                self.isolated_files.add(file_path)

        # Get all Python files in repo as potential connected files
        for root, dirs, files in os.walk(self.repo_path):
            # Skip venv and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    if rel_path not in self.isolated_files:
                        self.connected_files.add(rel_path)

        print(f"📊 Found {len(self.isolated_files)} isolated (unused) files")
        print(f"📊 Found {len(self.connected_files)} connected (used) files")

    def analyze_files(self):
        """Analyze all Python files in the repository"""
        print("🔍 Analyzing connected files...")
        self._analyze_file_set(self.connected_files, self.working_signatures)

        print("🔍 Analyzing isolated files...")
        self._analyze_file_set(self.isolated_files, self.isolated_signatures)

        print(f"✅ Found {len(self.working_signatures)} signatures in connected files")
        print(f"✅ Found {len(self.isolated_signatures)} signatures in isolated files")

    def _analyze_file_set(
        self, file_set: Set[str], signature_list: List[CodeSignature]
    ):
        """Analyze a set of files and extract signatures"""
        for file_path in file_set:
            if file_path.endswith(".py"):
                full_path = self.repo_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, encoding="utf-8") as f:
                            content = f.read()

                        tree = ast.parse(content)
                        analyzer = CodeAnalyzer(file_path)
                        analyzer.visit(tree)
                        signature_list.extend(analyzer.signatures)
                    except Exception as e:
                        print(f"⚠️  Error analyzing {file_path}: {e}")

    def find_integration_matches(self, min_confidence: float = 0.6):
        """Find potential integration matches"""
        print("\n🧮 Finding integration matches...")

        total_comparisons = len(self.isolated_signatures) * len(self.working_signatures)
        comparisons_done = 0

        for isolated_sig in self.isolated_signatures:
            best_matches = []

            for working_sig in self.working_signatures:
                comparisons_done += 1
                if comparisons_done % 10000 == 0:
                    progress = (comparisons_done / total_comparisons) * 100
                    print(f"  Progress: {progress:.1f}%")

                score, reasons = self.matcher.calculate_match_score(
                    isolated_sig, working_sig
                )

                if score >= min_confidence:
                    match = IntegrationMatch(
                        isolated_file=isolated_sig.file_path,
                        target_file=working_sig.file_path,
                        isolated_signature=isolated_sig,
                        target_signature=working_sig,
                        confidence_score=score,
                        match_reasons=reasons,
                        integration_actions=self._generate_integration_actions(
                            isolated_sig, working_sig, score
                        ),
                    )
                    best_matches.append(match)

            # Keep only top matches for each isolated signature
            best_matches.sort(key=lambda m: m.confidence_score, reverse=True)
            self.integration_matches.extend(best_matches[:3])  # Top 3 matches

    def _generate_integration_actions(
        self, isolated_sig: CodeSignature, target_sig: CodeSignature, score: float
    ) -> List[str]:
        """Generate specific integration actions"""
        actions = []

        # High confidence - direct integration
        if score >= 0.85:
            if isolated_sig.type == "class" and target_sig.type == "class":
                actions.append(
                    f"Merge class {isolated_sig.name} into {target_sig.name}"
                )
                actions.append("Consolidate duplicate methods")
                actions.append("Merge class attributes")
            elif isolated_sig.type in ["function", "method"]:
                actions.append(
                    f"Move {isolated_sig.type} {isolated_sig.name} to {target_sig.file_path}"
                )
                actions.append("Update function signature if needed")

        # Always needed
        actions.append("Update import statements: lucas/Lucas -> lukhas/LUKHAS")
        actions.append("Update any string references to old branding")

        # Domain-specific actions
        if isolated_sig.domain == target_sig.domain:
            actions.append(f"Integrate with {isolated_sig.domain} system architecture")

        return actions

    def generate_integration_report(self, output_file: str = "integration_plan.json"):
        """Generate detailed integration report"""
        print("\n📊 Generating integration report...")

        # Group matches by confidence level
        high_confidence = [
            m for m in self.integration_matches if m.confidence_score >= 0.85
        ]
        medium_confidence = [
            m for m in self.integration_matches if 0.7 <= m.confidence_score < 0.85
        ]
        low_confidence = [
            m for m in self.integration_matches if 0.6 <= m.confidence_score < 0.7
        ]

        # Group by domain
        domain_groups = defaultdict(list)
        for match in self.integration_matches:
            domain = match.isolated_signature.domain or "unknown"
            domain_groups[domain].append(match)

        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_isolated_files": len(self.isolated_files),
                "total_connected_files": len(self.connected_files),
                "total_matches_found": len(self.integration_matches),
                "isolated_signatures_analyzed": len(self.isolated_signatures),
                "working_signatures_analyzed": len(self.working_signatures),
            },
            "confidence_summary": {
                "high_confidence_matches": len(high_confidence),
                "medium_confidence_matches": len(medium_confidence),
                "low_confidence_matches": len(low_confidence),
            },
            "domain_summary": {
                domain: len(matches) for domain, matches in domain_groups.items()
            },
            "high_confidence_integrations": self._format_matches(
                high_confidence[:20]
            ),  # Top 20
            "medium_confidence_suggestions": self._format_matches(
                medium_confidence[:20]
            ),
            "branding_updates_needed": self._find_branding_updates(),
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        # Also generate human-readable summary
        self._print_summary(report)

        return report

    def _format_matches(self, matches: List[IntegrationMatch]) -> List[Dict]:
        """Format matches for report"""
        formatted = []

        for match in matches:
            formatted.append(
                {
                    "isolated_file": match.isolated_file,
                    "target_file": match.target_file,
                    "isolated_element": {
                        "name": match.isolated_signature.name,
                        "type": match.isolated_signature.type,
                        "line": match.isolated_signature.line_number,
                    },
                    "target_element": {
                        "name": match.target_signature.name,
                        "type": match.target_signature.type,
                        "line": match.target_signature.line_number,
                    },
                    "confidence_score": round(match.confidence_score, 3),
                    "match_reasons": {
                        k: round(v, 3) for k, v in match.match_reasons.items()
                    },
                    "integration_actions": match.integration_actions,
                }
            )

        return formatted

    def _find_branding_updates(self) -> List[Dict]:
        """Find files that need branding updates"""
        updates = []

        for file_path in self.isolated_files:
            if any(brand in file_path.lower() for brand in ["lucas", "lucλs"]):
                updates.append(
                    {
                        "file": file_path,
                        "suggested_path": BrandingNormalizer.normalize_path(file_path),
                    }
                )

        return updates[:50]  # Top 50

    def _print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "=" * 70)
        print("🎯 INTEGRATION ANALYSIS SUMMARY")
        print("=" * 70)

        meta = report["metadata"]
        print("\n📊 Files Analyzed:")
        print(f"  - Connected files: {meta['total_connected_files']:,}")
        print(f"  - Isolated files: {meta['total_isolated_files']:,}")
        print(
            f"  - Code signatures found: {meta['isolated_signatures_analyzed']:,} (isolated)"
        )
        print(
            f"  - Code signatures found: {meta['working_signatures_analyzed']:,} (working)"
        )

        conf = report["confidence_summary"]
        print("\n🎯 Integration Matches Found:")
        print(f"  - High confidence (≥85%): {conf['high_confidence_matches']}")
        print(f"  - Medium confidence (70-84%): {conf['medium_confidence_matches']}")
        print(f"  - Low confidence (60-69%): {conf['low_confidence_matches']}")

        print("\n🏷️  Domain Distribution:")
        for domain, count in sorted(
            report["domain_summary"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - {domain}: {count} matches")

        print(
            f"\n🔄 Branding Updates Needed: {len(report['branding_updates_needed'])} files"
        )

        if report["high_confidence_integrations"]:
            print("\n✨ Top High-Confidence Integration Opportunities:")
            for i, match in enumerate(report["high_confidence_integrations"][:5], 1):
                print(
                    f"\n  {i}. {match['isolated_element']['name']} → {match['target_element']['name']}"
                )
                print(f"     Score: {match['confidence_score']:.1%}")
                print(f"     From: {match['isolated_file']}")
                print(f"     To: {match['target_file']}")


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent unused file integration system for LUKHAS AGI"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("unused_file", help="Path to unused files report JSON")
    parser.add_argument(
        "-o",
        "--output",
        default="integration_plan.json",
        help="Output file for integration plan",
    )
    parser.add_argument(
        "-c",
        "--min-confidence",
        type=float,
        default=0.6,
        help="Minimum confidence score for matches (0-1)",
    )

    args = parser.parse_args()

    print("🚀 Starting Intelligent Unused File Integration Analysis")
    print(f"📁 Repository: {args.repo_path}")
    print(f"📊 Using unused files data: {args.unused_file}")

    integrator = UnusedFileIntegrator(args.repo_path)

    # Load unused files data
    integrator.load_unused_files_data(args.unused_file)

    # Analyze files
    integrator.analyze_files()

    # Find matches
    integrator.find_integration_matches(args.min_confidence)

    # Generate report
    integrator.generate_integration_report(args.output)

    print(f"\n✅ Integration plan saved to: {args.output}")
    print("\n🎉 Analysis complete!")


if __name__ == "__main__":
    main()
