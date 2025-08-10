#!/usr/bin/env python3
"""
High Confidence Matcher - Find files with 75%+ and 85%+ match scores
"""

import argparse
import ast
import difflib
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class SimplifiedMatch:
    """Simplified match result"""

    isolated_file: str
    target_file: str
    confidence_score: float
    match_type: str  # 'name', 'pattern', 'import'
    details: str


class HighConfidenceMatcher:
    """Fast matcher for finding high-confidence integration opportunities"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.isolated_files: List[str] = []
        self.connected_signatures: Dict[str, Set[str]] = defaultdict(
            set
        )  # file -> signatures
        self.high_matches_85: List[SimplifiedMatch] = []
        self.high_matches_75: List[SimplifiedMatch] = []

        # Branding patterns
        self.branding_map = {"lucas": "lukhas", "Lucas": "LUKHAS", "LUCAS": "LUKHAS"}

    def load_files(self, unused_file: str):
        """Load unused files and scan connected files"""
        # Load unused files
        with open(unused_file) as f:
            data = json.load(f)

        for file_info in data.get("unused_files", []):
            file_path = file_info["path"]
            if (
                file_path.endswith(".py")
                and not file_path.startswith(".venv")
                and not file_path.startswith("tests/")
                and file_info["size_bytes"] > 500
            ):
                self.isolated_files.append(file_path)

        print(f"📊 Found {len(self.isolated_files)} isolated files to analyze")

        # Quick scan of connected files for signatures
        self._scan_connected_files()

    def _scan_connected_files(self):
        """Quick scan of main system files for class/function names"""
        key_directories = [
            "core",
            "memory",
            "consciousness",
            "reasoning",
            "creativity",
            "voice",
            "identity",
            "bridge",
        ]

        print("🔍 Scanning connected system files...")

        for directory in key_directories:
            dir_path = self.repo_path / directory
            if not dir_path.exists():
                continue

            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [
                    d for d in dirs if not d.startswith(".") and d != "__pycache__"
                ]

                for file in files:
                    if file.endswith(".py"):
                        rel_path = os.path.relpath(
                            os.path.join(root, file), self.repo_path
                        )
                        self._extract_signatures(rel_path)

        print(
            f"✅ Found signatures in {len(self.connected_signatures)} connected files"
        )

    def _extract_signatures(self, file_path: str):
        """Extract class and function names from a file"""
        full_path = self.repo_path / file_path
        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.connected_signatures[file_path].add(f"class:{node.name}")
                elif isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if not node.name.startswith("_"):
                        self.connected_signatures[file_path].add(f"func:{node.name}")
        except:
            pass

    def find_high_confidence_matches(self):
        """Find matches with confidence >= 75%"""
        print("\n🎯 Finding high-confidence matches...")

        analyzed = 0
        for isolated_file in self.isolated_files:
            analyzed += 1
            if analyzed % 100 == 0:
                print(f"  Progress: {analyzed}/{len(self.isolated_files)} files")

            full_path = self.repo_path / isolated_file
            if not full_path.exists():
                continue

            try:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract signatures from isolated file
                isolated_sigs = self._get_file_signatures(content)

                # Check for direct matches
                for connected_file, connected_sigs in self.connected_signatures.items():
                    score, match_type, details = self._calculate_match_score(
                        isolated_file,
                        isolated_sigs,
                        connected_file,
                        connected_sigs,
                        content,
                    )

                    if score >= 0.85:
                        self.high_matches_85.append(
                            SimplifiedMatch(
                                isolated_file,
                                connected_file,
                                score,
                                match_type,
                                details,
                            )
                        )
                    elif score >= 0.75:
                        self.high_matches_75.append(
                            SimplifiedMatch(
                                isolated_file,
                                connected_file,
                                score,
                                match_type,
                                details,
                            )
                        )

            except Exception:
                pass

    def _get_file_signatures(self, content: str) -> Set[str]:
        """Extract signatures from file content"""
        signatures = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    signatures.add(f"class:{node.name}")
                    # Normalize branding in class names
                    for old, new in self.branding_map.items():
                        if old in node.name:
                            normalized = node.name.replace(old, new)
                            signatures.add(f"class:{normalized}")

                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    signatures.add(f"func:{node.name}")
        except:
            pass

        return signatures

    def _calculate_match_score(
        self,
        isolated_file: str,
        isolated_sigs: Set[str],
        connected_file: str,
        connected_sigs: Set[str],
        content: str,
    ) -> Tuple[float, str, str]:
        """Calculate match score between files"""
        # Direct signature matches
        if isolated_sigs and connected_sigs:
            common_sigs = isolated_sigs & connected_sigs
            if common_sigs:
                score = len(common_sigs) / min(len(isolated_sigs), len(connected_sigs))
                if score >= 0.75:
                    details = (
                        f"Matching signatures: {', '.join(sorted(common_sigs)[:3])}"
                    )
                    return score, "signature", details

        # File name similarity (with branding normalization)
        iso_name = Path(isolated_file).stem.lower()
        conn_name = Path(connected_file).stem.lower()

        # Normalize branding
        for old, new in self.branding_map.items():
            iso_name = iso_name.replace(old.lower(), new.lower())

        name_score = difflib.SequenceMatcher(None, iso_name, conn_name).ratio()
        if name_score >= 0.75:
            return name_score, "name", f"Name similarity: {iso_name} ~ {conn_name}"

        # Domain-based matching
        iso_parts = isolated_file.split("/")
        conn_parts = connected_file.split("/")

        # Check if they share domain keywords
        domains = [
            "memory",
            "voice",
            "consciousness",
            "reasoning",
            "creativity",
            "identity",
            "quantum",
            "emotion",
            "ethics",
        ]

        for domain in domains:
            if domain in isolated_file.lower() and domain in connected_file.lower():
                # Check for related functionality
                if any(
                    sig in connected_sigs
                    for sig in isolated_sigs
                    if domain in sig.lower()
                ):
                    return 0.75, "domain", f"Same domain: {domain}"

        return 0.0, "none", ""

    def generate_report(self, output_file: str):
        """Generate high-confidence matches report"""
        # Sort by confidence score
        self.high_matches_85.sort(key=lambda m: m.confidence_score, reverse=True)
        self.high_matches_75.sort(key=lambda m: m.confidence_score, reverse=True)

        report = {
            "summary": {
                "total_isolated_files": len(self.isolated_files),
                "matches_85_plus": len(self.high_matches_85),
                "matches_75_plus": len(self.high_matches_75)
                + len(self.high_matches_85),
                "unique_isolated_85": len(
                    set(m.isolated_file for m in self.high_matches_85)
                ),
                "unique_isolated_75": len(
                    set(
                        m.isolated_file
                        for m in self.high_matches_75 + self.high_matches_85
                    )
                ),
            },
            "matches_85_plus": [
                {
                    "isolated_file": m.isolated_file,
                    "target_file": m.target_file,
                    "confidence": round(m.confidence_score, 3),
                    "match_type": m.match_type,
                    "details": m.details,
                }
                for m in self.high_matches_85[:50]  # Top 50
            ],
            "matches_75_to_84": [
                {
                    "isolated_file": m.isolated_file,
                    "target_file": m.target_file,
                    "confidence": round(m.confidence_score, 3),
                    "match_type": m.match_type,
                    "details": m.details,
                }
                for m in self.high_matches_75[:50]  # Top 50
            ],
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 70)
        print("🎯 HIGH CONFIDENCE MATCHES SUMMARY")
        print("=" * 70)
        print("\n📊 Results:")
        print(
            f"  - Total isolated files analyzed: {report['summary']['total_isolated_files']}"
        )
        print(
            f"  - Matches with 85%+ confidence: {report['summary']['matches_85_plus']}"
        )
        print(
            f"  - Matches with 75%+ confidence: {report['summary']['matches_75_plus']}"
        )
        print(
            f"  - Unique files with 85%+ match: {report['summary']['unique_isolated_85']}"
        )
        print(
            f"  - Unique files with 75%+ match: {report['summary']['unique_isolated_75']}"
        )

        if self.high_matches_85:
            print("\n✨ Top 85%+ Confidence Matches:")
            for i, match in enumerate(self.high_matches_85[:10], 1):
                print(f"\n  {i}. {match.isolated_file}")
                print(f"     → {match.target_file}")
                print(f"     Confidence: {match.confidence_score:.1%}")
                print(f"     Type: {match.match_type}")
                print(f"     {match.details}")

        return report


def main():
    parser = argparse.ArgumentParser(
        description="High confidence matcher for LUKHAS AGI"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("unused_file", help="Path to unused files report JSON")
    parser.add_argument(
        "-o",
        "--output",
        default="high_confidence_matches.json",
        help="Output file for matches",
    )

    args = parser.parse_args()

    print("🚀 Starting High Confidence Match Analysis")
    print(f"📁 Repository: {args.repo_path}")
    print(f"📊 Using unused files data: {args.unused_file}")

    matcher = HighConfidenceMatcher(args.repo_path)

    # Load files
    matcher.load_files(args.unused_file)

    # Find matches
    matcher.find_high_confidence_matches()

    # Generate report
    matcher.generate_report(args.output)

    print(f"\n✅ High confidence matches saved to: {args.output}")
    print("\n🎉 Analysis complete!")


if __name__ == "__main__":
    main()
