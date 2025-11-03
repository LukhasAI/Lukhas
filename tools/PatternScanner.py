#!/usr/bin/env python3
"""
🔍 lukhas FUNCTION PATTERN SCANNER
=================================

Simple pattern-based scanner that identifies specialized lukhas functions
without importing modules (to avoid dependency issues).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FunctionMatch:
    """A function that matches a specialized pattern."""

    name: str
    file_path: str
    pattern_type: str
    context: str  # Surrounding code context


class FunctionScanner:
    """Pattern-based scanner for Λ specialized functions."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.Λ_root = self.project_root / "lukhas"

        # Patterns to search for (expanded list)
        self.function_patterns = {
            # Voice & Audio Systems
            "accent_adapter": [
                r"accent.*adapt",
                r"pronunciation",
                r"dialect",
                r"phonetic",
                r"voice_adaptation",
            ],
            "voice_profiling": [
                r"voice_profile",
                r"voice.*synthesis",
                r"tts",
                r"voice_memory_helix",
            ],
            "dream_narrator": [
                r"dream_voice",
                r"dream.*narrative",
                r"voice_synthesis",
                r"dream_narrator",
            ],
            "voice_modulator": [
                r"voice_modulation",
                r"emotion_voice",
                r"context_aware.*voice",
            ],
            # Memory Systems
            "memory_helix": [
                r"memory.*helix",
                r"helix",
                r"spiral.*memory",
                r"memory_chain",
                r"healix",
            ],
            "memory_manager": [
                r"memory_storage",
                r"encrypted_memory",
                r"memory_trace",
                r"memory_manager",
            ],
            "emotional_memory": [
                r"emotional.*memory",
                r"trauma_lock",
                r"memory.*emotion",
            ],
            # Dream & Cognitive Systems
            "dream_mutator": [
                r"dream.*mutate",
                r"dream.*mutation",
                r"narrative.*mutate",
                r"dream_engine",
            ],
            "dream_delivery": [r"dream_delivery", r"dream_manager", r"rem_visualizer"],
            "cognitive_processor": [
                r"cognitive.*process",
                r"brain_integration",
                r"neural_adaptation",
            ],
            # Security & Guardian Systems
            "guardian": [
                r"guardian",
                r"safety.*guard",
                r"protection",
                r"validation.*guard",
            ],
            "ethics_engine": [
                r"ethics.*engine",
                r"compliance",
                r"audit",
                r"angel_guardian",
            ],
            "trauma_protection": [
                r"trauma.*lock",
                r"emotional.*security",
                r"identity.*protection",
            ],
            # Learning & Training Systems
            "train_mapper": [
                r"train.*mapper",
                r"training.*map",
                r"neural.*map",
                r"exponential_learning",
            ],
            "adaptive_learning": [
                r"adaptive.*learn",
                r"self_improvement",
                r"pattern_learning",
            ],
            # Quantum & Advanced Processing
            "qi_processor": [
                r"qi.*process",
                r"entanglement",
                r"superposition",
                r"qi_neuro",
            ],
            "qi_consensus": [
                r"qi_consensus",
                r"annealed_consensus",
                r"qi_ethical",
            ],
            "bio_oscillator": [
                r"bio_oscillator",
                r"emotional_oscillator",
                r"qi_oscillator",
            ],
            # Bio & Symbolic Systems
            "bio_systems": [
                r"bio.*system",
                r"biological.*neural",
                r"organic.*adaptation",
                r"bio_symbolic",
            ],
            "symbolic_ai": [
                r"symbolic.*ai",
                r"symbolic.*reasoning",
                r"logic.*inference",
                r"neuro_symbolic",
            ],
            # Identity & Personality
            "identity_core": [
                r"identity.*core",
                r"personality.*core",
                r"lukhas.*id",
                r"self_model",
            ],
            "personality_manager": [
                r"personality.*manager",
                r"character.*trait",
                r"trait.*manager",
            ],
            # Emotion & Resonance
            "emotion_engine": [
                r"emotion.*engine",
                r"feeling.*process",
                r"emotional_resonance",
            ],
            "emotional_modulator": [
                r"emotional.*modulation",
                r"mood_analysis",
                r"emotion_state",
            ],
            # System Integration & Orchestration
            "orchestrator": [r"orchestrat", r"coordination", r"system_integration"],
            "demo_orchestrator": [
                r"demo.*orchestrat",
                r"showcase",
                r"integration_demo",
            ],
            # Specialized Λ Components
            "nias_scheduler": [r"nias", r"attention.*scheduler", r"non_intrusive"],
            "dast_tracker": [r"dast", r"dynamic_ai", r"solution_tracker"],
            "abas_arbitrator": [r"abas", r"arbitrator", r"consensus.*decision"],
            "Λ_sibling": [r"lukhas.*sibling", r"sibling.*agent", r"companion"],
            "consent_engine": [
                r"consent.*engine",
                r"permission.*control",
                r"user_control",
            ],
            "tier_mapper": [r"tier.*mapper", r"access_control", r"permission_level"],
        }

        self.matches = {}
        for pattern_type in self.function_patterns:
            self.matches[pattern_type] = []

    def scan_lukhas_ecosystem(self) -> dict[str, list[FunctionMatch]]:
        """Scan the lukhas ecosystem for specialized function patterns."""
        print("🔍 Scanning lukhas ecosystem for specialized function patterns...")

        # Areas to scan
        areas = {
            "core": self.lukhas_root / "core",
            "bio": self.lukhas_root / "bio",
            "cognitive": self.lukhas_root / "cognitive",
            "sensors": self.lukhas_root / "sensors",
        }

        total_files = 0
        for area_name, area_path in areas.items():
            if area_path.exists():
                files_found = self._scan_area(area_name, area_path)
                total_files += files_found
                print(f"  📁 {area_name}: {files_found} Python files")

        print(f"📊 Scanned {total_files} Python files total")
        return self.matches

    def _scan_area(self, area_name: str, area_path: Path) -> int:
        """Scan an area for function patterns."""
        file_count = 0
        exclude_dirs = {"node_modules", "__pycache__", ".git", ".vscode", "venv", "env"}

        for py_file in area_path.rglob("*.py"):
            # Skip problematic directories
            if any(part in exclude_dirs for part in py_file.parts):
                continue

            file_count += 1
            self._scan_file(py_file, area_name)

        return file_count

    def _scan_file(self, file_path: Path, area: str):
        """Scan a single Python file for function patterns."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Look for function definitions
            function_matches = re.finditer(r"^(def|class|async def)\s+(\w+)", content, re.MULTILINE)

            for match in function_matches:
                func_name = match.group(2)
                start_pos = match.start()

                # Get context around the function (next 5 lines)
                lines = content[: start_pos + 200].split("\n")
                context_lines = lines[-5:] if len(lines) >= 5 else lines
                context = "\n".join(context_lines)

                # Check if this function matches any specialized patterns
                for pattern_type, patterns in self.function_patterns.items():
                    for pattern in patterns:
                        # Check function name and surrounding context
                        if re.search(pattern, func_name, re.IGNORECASE) or re.search(pattern, context, re.IGNORECASE):
                            self.matches[pattern_type].append(
                                FunctionMatch(
                                    name=func_name,
                                    file_path=str(file_path.relative_to(self.project_root)),
                                    pattern_type=pattern_type,
                                    context=context.strip(),
                                )
                            )
                            break  # Only match once per function

        except Exception:
            # Skip files that can't be read
            pass

    def print_summary(self):
        """Print a summary of discovered specialized functions."""
        print("\n" + "=" * 80)
        print("🎯 lukhas SPECIALIZED FUNCTIONS DISCOVERY REPORT")
        print("=" * 80)

        # Count totals
        total_functions = sum(len(matches) for matches in self.matches.values())
        components_with_functions = len([p for p in self.matches.values() if p])
        total_components = len(self.function_patterns)

        print("📊 Discovery Overview:")
        print(f"   Total Specialized Function Patterns: {total_functions}")
        print(f"   Components with Functions Found: {components_with_functions}/{total_components}")
        print(f"   Component Coverage: {(components_with_functions / total_components * 100):.1f}%")

        print("\n🎯 Specialized Component Findings:")

        # Sort by number of functions found
        sorted_components = sorted(self.matches.items(), key=lambda x: len(x[1]), reverse=True)

        for component_type, matches in sorted_components:
            if matches:
                status = "✅"
                print(f"   {status} {component_type:20} | {len(matches):3} functions found")

                # Show sample functions and files
                unique_files = {match.file_path for match in matches}
                sample_functions = [match.name for match in matches[:3]]

                print(f"      Files: {len(unique_files)} | Samples: {', '.join(sample_functions)}")
                if len(unique_files) <= 3:
                    for file_path in list(unique_files)[:3]:
                        print(f"        📄 {file_path}")
            else:
                status = "❌"
                print(f"   {status} {component_type:20} | No patterns found")

        # Show top files with most specialized functions
        file_function_count = {}
        for matches in self.matches.values():
            for match in matches:
                file_function_count[match.file_path] = file_function_count.get(match.file_path, 0) + 1

        if file_function_count:
            print("\n📁 Top Files with Specialized Functions:")
            sorted_files = sorted(file_function_count.items(), key=lambda x: x[1], reverse=True)
            for file_path, count in sorted_files[:10]:
                print(f"   {count:2} functions | {file_path}")

    def save_detailed_report(self):
        """Save a detailed JSON report."""
        report_data = {}
        for component_type, matches in self.matches.items():
            report_data[component_type] = [
                {
                    "name": match.name,
                    "file": match.file_path,
                    "context": match.context[:200],  # Limit context length
                }
                for match in matches
            ]

        import json

        report_file = "lukhas_specialized_functions_report.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_file}")


def main():
    """Main scanning function."""
    print("🚀 Starting lukhas Specialized Function Pattern Scan")
    print("=" * 55)

    scanner = FunctionScanner()

    try:
        # Scan for patterns
        scanner.scan_lukhas_ecosystem()

        # Print summary
        scanner.print_summary()

        # Save detailed report
        scanner.save_detailed_report()

        # Overall assessment
        total_functions = sum(len(matches) for matches in scanner.matches.values())
        len([m for m in scanner.matches.values() if m])

        if total_functions >= 50:
            print("\n🎉 EXCELLENT: Rich ecosystem of specialized functions discovered!")
        elif total_functions >= 20:
            print("\n✅ GOOD: Solid foundation of specialized functions found.")
        else:
            print("\n⚠️  LIMITED: Few specialized function patterns detected.")

    except Exception as e:
        print(f"\n❌ SCAN FAILED: {e}")


if __name__ == "__main__":
    main()

# Λ Systems 2025 www.ai
