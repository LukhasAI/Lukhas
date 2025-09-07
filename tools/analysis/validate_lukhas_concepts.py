#!/usr/bin/env python3
"""
LUKHAS Concept Validation Tool
Ensures LUKHAS original concepts are preserved throughout the codebase
"""
from consciousness.qi import qi
import time
import streamlit as st

import json
import re
from collections import defaultdict
from pathlib import Path


class LUKHASConceptValidator:
    def __init__(self):
        # Core LUKHAS concepts that must be preserved
        self.core_concepts = {
            # Memory
            "memory_fold": "Quantum-inspired memory structure",
            "memory_helix": "DNA-like memory with emotional vectors",
            "fold_system": "Memory folding mechanism",
            "memory_cascade": "Chain reaction of memory associations",
            # Dream
            "dream_recall": "Ability to remember and analyze dreams",
            "dream_engine": "Core dream processing system",
            "dream_resonance": "Harmonic patterns in dream states",
            "oneiric": "Related to dreams (Greek origin)",
            "dream_scenario": "Parallel universe scenario generation",
            # Quantum
            "qi_state": "Superposition of possibilities",
            "qi_consciousness": "Quantum-inspired awareness",
            "qi_coherence": "Maintaining quantum properties",
            "qi_entanglement": "Connected states across modules",
            # Bio-Symbolic
            "bio_oscillation": "Biological rhythm patterns",
            "bio_coherence": "Harmony between biological and symbolic",
            "symbolic_mutation": "Evolution of symbolic representations",
            "glyph": "Symbolic communication unit",
            "glyph_token": "Tokenized symbolic unit",
            # Emotional
            "emotional_drift": "Gradual shift in emotional states",
            "emotional_vector": "Direction and magnitude of emotions",
            "emotion_cascade": "Chain reaction of emotional responses",
            "affect_grid": "2D representation of emotional states",
            # Consciousness
            "crista": "Consciousness crystal structure",
            "trace_trail": "Path of consciousness through time",
            # Identity & Governance
            "tier_access": "Multi-level security system",
            "guardian_protocol": "Ethical oversight system",
            # Special Terms
            "lukhas": "The system name itself",
            "": "Pack What Matters",
            "sgi": "Symbolic General Intelligence",
        }

        self.concept_usage = defaultdict(list)
        self.validation_results = {
            "preserved": [],
            "at_risk": [],
            "missing": [],
            "statistics": {},
        }

    def validate_codebase(self, root_path: str = "."):
        """Validate that LUKHAS concepts are preserved"""
        print("🧬 LUKHAS Concept Validation")
        print("=" * 60)
        print("Validating preservation of core LUKHAS concepts...")

        # Scan all Python files
        root = Path(root_path)
        python_files = list(root.rglob("*.py"))

        # Filter out archives
        python_files = [
            f for f in python_files if not any(skip in str(f) for skip in ["._cleanup_archive", "__pycache__", ".git"])
        ]

        print(f"\nScanning {len(python_files)} Python files...")

        # Search for each concept
        for concept in self.core_concepts:
            self._find_concept_usage(concept, python_files)

        # Analyze results
        self._analyze_results()

        # Generate report
        self._generate_report()

    def _find_concept_usage(self, concept: str, files: list[Path]):
        """Find all usages of a concept"""
        pattern = re.compile(r"\b" + re.escape(concept) + r"\b", re.IGNORECASE)

        for file_path in files:
            try:
                content = file_path.read_text()
                matches = pattern.findall(content)

                if matches:
                    # Count exact matches vs case variations
                    exact_matches = sum(1 for m in matches if m == concept)
                    variations = len(matches) - exact_matches

                    self.concept_usage[concept].append(
                        {
                            "file": str(file_path),
                            "exact_matches": exact_matches,
                            "variations": variations,
                            "total": len(matches),
                        }
                    )
            except BaseException:
                pass

    def _analyze_results(self):
        """Analyze concept preservation"""
        for concept, description in self.core_concepts.items():
            usage = self.concept_usage.get(concept, [])

            if not usage:
                self.validation_results["missing"].append(
                    {
                        "concept": concept,
                        "description": description,
                        "severity": ("high" if concept in ["memory_fold", "dream_engine", "qi_state"] else "medium"),
                    }
                )
            else:
                total_exact = sum(u["exact_matches"] for u in usage)
                total_variations = sum(u["variations"] for u in usage)

                if total_variations > total_exact:
                    self.validation_results["at_risk"].append(
                        {
                            "concept": concept,
                            "description": description,
                            "exact_usage": total_exact,
                            "variations": total_variations,
                            "files": len(usage),
                        }
                    )
                else:
                    self.validation_results["preserved"].append(
                        {
                            "concept": concept,
                            "description": description,
                            "usage_count": total_exact + total_variations,
                            "files": len(usage),
                        }
                    )

        # Calculate statistics
        total_concepts = len(self.core_concepts)
        self.validation_results["statistics"] = {
            "total_concepts": total_concepts,
            "preserved": len(self.validation_results["preserved"]),
            "at_risk": len(self.validation_results["at_risk"]),
            "missing": len(self.validation_results["missing"]),
            "preservation_rate": f"{(len(self.validation_results['preserved']) / total_concepts * 100}:.1f}%",
        }

    def _generate_report(self):
        """Generate validation report"""
        # Save detailed report
        report_path = Path("docs/reports/analysis/LUKHAS_CONCEPT_VALIDATION.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        # Print summary
        stats = self.validation_results["statistics"]
        print("\n📊 VALIDATION SUMMARY:")
        print(f"   Total LUKHAS concepts: {stats['total_concepts']}")
        print(f"   ✅ Preserved: {stats['preserved']}")
        print(f"   ⚠️  At risk: {stats['at_risk']}")
        print(f"   ❌ Missing: {stats['missing']}")
        print(f"   Preservation rate: {stats['preservation_rate']}")

        # Show critical information
        if self.validation_results["missing"]:
            print("\n❌ MISSING CONCEPTS (need attention):")
            for missing in self.validation_results["missing"][:5]:
                print(f"   - {missing['concept']}: {missing['description']}")

        if self.validation_results["at_risk"]:
            print("\n⚠️  AT RISK CONCEPTS (inconsistent usage):")
            for at_risk in self.validation_results["at_risk"][:5]:
                print(f" - {at_risk['concept']}: {at_risk['exact_usage']} exact, {at_risk['variations']} variations")

        if self.validation_results["preserved"]:
            print("\n✅ WELL-PRESERVED CONCEPTS:")
            for preserved in sorted(
                self.validation_results["preserved"],
                key=lambda x: x["usage_count"],
                reverse=True,
            )[:10]:
                print(f"   - {preserved['concept']}: {preserved['usage_count']} uses in {preserved['files']} files")

        print(f"\n📄 Full report saved to: {report_path}")

        # Create preservation guidelines
        self._create_preservation_guidelines()

    def _create_preservation_guidelines(self):
        """Create guidelines for preserving concepts"""
        guidelines = """# LUKHAS Concept Preservation Guidelines"

## Critical Concepts to Preserve

Based on the validation analysis, here are the concepts that need special attention:

### Core Memory Concepts
- `memory_fold` - The foundation of LUKHAS memory system
- `memory_helix` - DNA-like structure (future direction)
- `fold_system` - Essential for memory organization

### Dream & Learning Concepts
- `dream_recall` - Core to self-learning capability
- `dream_engine` - Processing system for scenarios
- `dream_scenario` - Parallel universe generation

### Quantum Processing Concepts
- `qi_state` - Fundamental to SGI processing
- `qi_consciousness` - Awareness mechanism
- `qi_entanglement` - Module interconnection

## Preservation Rules

1. **Never Split Concepts**: `memory_fold` stays together, not `memory` + `fold`
2. **Case Sensitivity**: Use exact casing in strings and comments
3. **Documentation**: Always explain concepts in docstrings
4. **Refactoring**: Update all references when changing names
5. **New Features**: Extend concepts rather than replacing them

## Implementation Patterns

```python
# ✅ CORRECT - Preserves concept

class MemoryFold:
    \"\"\"Quantum-inspired memory folding system\"\"\"

    def create_memory_fold(self, content):
        # Preserves the memory_fold concept
        pass

# ❌ INCORRECT - Splits concept

class Memory:

    def create_fold(self, content):
        # This breaks the memory_fold concept
        pass
```

## Future Evolution

As LUKHAS evolves toward 2030, these concepts may expand but should never be lost:
- `memory_fold` → `qi_memory_fold`
- `dream_recall` → `multi_dimensional_dream_recall`
- `emotional_vector` → `empathic_emotional_vector`

Always extend, never replace!
"""

        guidelines_path = Path("docs/LUKHAS_CONCEPT_PRESERVATION.md")
        with open(guidelines_path, "w") as f:
            f.write(guidelines)

        print(f"\n📝 Preservation guidelines created: {guidelines_path}")


def main():
    validator = LUKHASConceptValidator()
    validator.validate_codebase()


if __name__ == "__main__":
    main()
