#!/usr/bin/env python3
"""
lukhas Missing Component Hunter
Advanced search for the 6 remaining specialized components
"""

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ComponentHit:
    component_name: str
    file_path: str
    line_number: int
    context: str
    confidence_score: float
    match_type: str  # 'filename', 'function_name', 'class_name', 'comment', 'variable'


class MissingComponentHunter:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.hits = []

        # Enhanced search patterns for missing components
        self.missing_components = {
            "emotion_engine": {
                "patterns": [
                    r"emotion.*engine",
                    r"emotional.*engine",
                    r"feeling.*engine",
                    r"mood.*engine",
                    r"sentiment.*engine",
                    r"affect.*engine",
                    r"EmotionEngine",
                    r"emotional.*processor",
                    r"emotion.*detector",
                    r"emotion.*analyzer",
                    r"empathy.*engine",
                ],
                "file_patterns": [
                    r"emotion.*\.py",
                    r".*emotion.*\.py",
                    r"feel.*\.py",
                    r"mood.*\.py",
                    r"sentiment.*\.py",
                    r"affect.*\.py",
                    r"empathy.*\.py",
                ],
            },
            "lukhas_sibling": {
                "patterns": [
                    r"lukhas.*sibling",
                    r"sibling.*lukhas",
                    r"brother.*lukhas",
                    r"sister.*lukhas",
                    r"lukhas.*brother",
                    r"lukhas.*sister",
                    r"LucasSibling",
                    r"sibling.*relationship",
                    r"family.*relationship",
                    r"kinship.*lukhas",
                ],
                "file_patterns": [
                    r"lukhas.*\.py",
                    r"sibling.*\.py",
                    r".*sibling.*\.py",
                    r"family.*\.py",
                    r"brother.*\.py",
                    r"sister.*\.py",
                ],
            },
            "accent_adapter": {
                "patterns": [
                    r"accent.*adapter",
                    r"accent.*adaptation",
                    r"voice.*accent",
                    r"accent.*voice",
                    r"AccentAdapter",
                    r"dialect.*adapter",
                    r"pronunciation.*adapter",
                    r"speech.*accent",
                    r"accent.*modifier",
                    r"voice.*style",
                ],
                "file_patterns": [
                    r"accent.*\.py",
                    r".*accent.*\.py",
                    r"dialect.*\.py",
                    r"voice.*style.*\.py",
                    r"pronunciation.*\.py",
                ],
            },
            "memory_helix": {
                "patterns": [
                    r"memory.*helix",
                    r"memory.*spiral",
                    r"helix.*memory",
                    r"spiral.*memory",
                    r"MemoryHelix",
                    r"memory.*structure",
                    r"memory.*geometry",
                    r"memory.*pattern",
                    r"twisted.*memory",
                    r"helical.*memory",
                ],
                "file_patterns": [
                    r"memory.*helix.*\.py",
                    r"helix.*\.py",
                    r"spiral.*\.py",
                    r".*helix.*\.py",
                    r"memory.*structure.*\.py",
                ],
            },
            "voice_profiling": {
                "patterns": [
                    r"voice.*profiling",
                    r"voice.*profile",
                    r"voice.*analysis",
                    r"voice.*analyzer",
                    r"VoiceProfiling",
                    r"voice.*recognition",
                    r"speaker.*profiling",
                    r"vocal.*profiling",
                    r"voice.*characteristics",
                    r"voice.*fingerprint",
                ],
                "file_patterns": [
                    r"voice.*profil.*\.py",
                    r"vocal.*profil.*\.py",
                    r"speaker.*profil.*\.py",
                    r"voice.*analysis.*\.py",
                    r".*voice.*profil.*\.py",
                ],
            },
            "guardian": {
                "patterns": [
                    r"guardian",
                    r"Guardian",
                    r"protection.*system",
                    r"security.*guardian",
                    r"safety.*guardian",
                    r"protective.*system",
                    r"guardian.*system",
                    r"watch.*guardian",
                    r"sentinel.*system",
                    r"guard.*system",
                ],
                "file_patterns": [
                    r"guardian.*\.py",
                    r".*guardian.*\.py",
                    r"protection.*\.py",
                    r"sentinel.*\.py",
                    r"guard.*\.py",
                    r"safety.*\.py",
                ],
            },
        }

        # Directories to exclude (virtual environments, etc.)
        self.exclude_dirs = {
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "site-packages",
            "lib/python",
            "share",
            "include",
            "bin",
            "Scripts",
            "pyvenv.cfg",
        }

    def should_skip_directory(self, dir_path: Path) -> bool:
        """Check if directory should be skipped"""
        dir_name = dir_path.name.lower()

        # Skip if it's an excluded directory
        if dir_name in self.exclude_dirs:
            return True

        # Skip if it contains virtual environment indicators
        if any(indicator in dir_name for indicator in ["venv", "env", "site-packages"]):
            return True

        # Skip if path contains virtual environment patterns
        path_str = str(dir_path).lower()
        return bool(any(pattern in path_str for pattern in ["/lib/python", "/site-packages", "/bin/", "/scripts/"]))

    def search_file_content(self, file_path: Path) -> list[ComponentHit]:
        """Search file content for component patterns"""
        hits = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()

                for component_name, config in self.missing_components.items():
                    for pattern in config["patterns"]:
                        if re.search(pattern.lower(), line_lower):
                            confidence = self.calculate_confidence(pattern, line, file_path)
                            match_type = self.determine_match_type(line, pattern)

                            hit = ComponentHit(
                                component_name=component_name,
                                file_path=str(file_path),
                                line_number=line_num,
                                context=line.strip(),
                                confidence_score=confidence,
                                match_type=match_type,
                            )
                            hits.append(hit)

        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")

        return hits

    def search_filename_patterns(self, file_path: Path) -> list[ComponentHit]:
        """Search filename patterns"""
        hits = []
        filename = file_path.name.lower()

        for component_name, config in self.missing_components.items():
            for pattern in config["file_patterns"]:
                if re.search(pattern.lower(), filename):
                    confidence = 0.9  # High confidence for filename matches

                    hit = ComponentHit(
                        component_name=component_name,
                        file_path=str(file_path),
                        line_number=0,
                        context=f"Filename match: {file_path.name}",
                        confidence_score=confidence,
                        match_type="filename",
                    )
                    hits.append(hit)

        return hits

    def calculate_confidence(self, pattern: str, line: str, file_path: Path) -> float:
        """Calculate confidence score for a match"""
        confidence = 0.5  # Base confidence

        # Higher confidence for exact class/function names
        if pattern[0].isupper():  # CamelCase patterns
            confidence += 0.3

        # Higher confidence for specific file locations
        path_str = str(file_path).lower()
        if any(key in path_str for key in ["core", "engine", "system", "module"]):
            confidence += 0.2

        # Lower confidence for comments
        if line.strip().startswith("#"):
            confidence -= 0.2

        return min(confidence, 1.0)

    def determine_match_type(self, line: str, pattern: str) -> str:
        """Determine the type of match"""
        line_stripped = line.strip()

        if line_stripped.startswith("# "):
            return "comment"
        elif "class " in line_stripped:
            return "class_name"
        elif "def " in line_stripped:
            return "function_name"
        elif "=" in line_stripped:
            return "variable"
        else:
            return "reference"

    def scan_directory(self, directory: Path) -> None:
        """Scan directory for missing components"""
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path / d)]

            for file_name in files:
                if file_name.endswith(".py"):
                    file_path = root_path / file_name

                    # Search filename patterns
                    filename_hits = self.search_filename_patterns(file_path)
                    self.hits.extend(filename_hits)

                    # Search file content
                    content_hits = self.search_file_content(file_path)
                    self.hits.extend(content_hits)

    def hunt_missing_components(self) -> None:
        """Main hunting function"""
        print(f"🔍 Hunting for missing components in: {self.base_path}")

        if self.base_path.exists():
            self.scan_directory(self.base_path)
        else:
            print(f"❌ Directory not found: {self.base_path}")

    def generate_report(self) -> dict:
        """Generate comprehensive report"""
        # Group hits by component
        component_hits = {}
        for hit in self.hits:
            if hit.component_name not in component_hits:
                component_hits[hit.component_name] = []
            component_hits[hit.component_name].append(asdict(hit))

        # Sort hits by confidence
        for component_name in component_hits:
            component_hits[component_name].sort(key=lambda x: x["confidence_score"], reverse=True)

        # Generate summary
        summary = {
            "total_hits": len(self.hits),
            "components_found": len(component_hits),
            "components_searched": len(self.missing_components),
            "hit_breakdown": {name: len(hits) for name, hits in component_hits.items()},
        }

        return {
            "hunt_summary": summary,
            "component_hits": component_hits,
            "missing_components_searched": list(self.missing_components.keys()),
        }

    def save_report(self, report: dict, filename: str = "missing_component_hunt_report.json"):
        """Save hunt report"""
        output_path = self.base_path.parent / filename
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📊 Hunt report saved to: {output_path}")


def main():
    """Main execution"""
    # Hunt in both infrastructure and core directories
    directories = [
        "/Users/A_G_I/CodexGPT_Lukhas/infrastructure",
        "/Users/A_G_I/CodexGPT_Lukhas/lukhas/core",
        "/Users/A_G_I/CodexGPT_Lukhas/core_systems",
    ]

    all_hits = []

    for directory in directories:
        if os.path.exists(directory):
            print(f"\n🎯 Hunting in: {directory}")
            hunter = MissingComponentHunter(directory)
            hunter.hunt_missing_components()

            if hunter.hits:
                all_hits.extend(hunter.hits)
                print(f"✅ Found {len(hunter.hits)} potential hits in {directory}")
            else:
                print(f"❌ No hits found in {directory}")

    if all_hits:
        # Create consolidated report
        consolidated_hunter = MissingComponentHunter("/Users/A_G_I/CodexGPT_Lukhas")
        consolidated_hunter.hits = all_hits

        report = consolidated_hunter.generate_report()
        consolidated_hunter.save_report(report)

        # Print summary
        print("\n🎯 MISSING COMPONENT HUNT SUMMARY:")
        print(f"📁 Total hits found: {report['hunt_summary']['total_hits']}")
        print(f"🎨 Components with hits: {report['hunt_summary']['components_found']}/6")

        print("\n✅ COMPONENT HITS FOUND:")
        for component, count in report["hunt_summary"]["hit_breakdown"].items():
            print(f"  • {component}: {count} hits")

        print("\n🔍 TOP HITS BY CONFIDENCE:")
        for component_name, hits in report["component_hits"].items():
            if hits:
                top_hit = hits[0]  # Highest confidence
                print(f"  • {component_name}: {top_hit['confidence_score']:.2f} - {top_hit['file_path']}")
                print(f"    Context: {top_hit['context'][:100]}...")
    else:
        print("❌ No hits found for missing components")


if __name__ == "__main__":
    main()

# Λ Systems 2025 www.lukhas.ai
