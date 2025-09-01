#!/usr/bin/env python3
"""
LUKHAS Concept Scanner
Finds and reports on LUKHAS-specific concepts throughout the codebase
"""

import ast
import re
from collections import defaultdict
from pathlib import Path


class LukhasConceptScanner:
    def __init__(self):
        self.root_path = Path(".")

        # Core LUKHAS concepts to track
        self.core_concepts = {
            # Memory concepts
            "memory_fold": "DNA-helix memory structure",
            "fold_system": "Memory folding system",
            "memory_helix": "Helical memory organization",
            "memory_cascade": "Cascading memory effects",
            # Dream concepts
            "dream_recall": "Parallel universe exploration",
            "dream_engine": "Dream generation system",
            "oneiric": "Dream-related processing",
            "dream_state": "Dream consciousness state",
            # Quantum concepts
            "qi_state": "Quantum superposition states",
            "qi_consciousness": "Quantum-aware consciousness",
            "qi_coherence": "Quantum system coherence",
            "qi_entanglement": "Memory entanglement",
            # Bio concepts
            "bio_oscillation": "Biological rhythm patterns",
            "bio_coherence": "Bio-symbolic alignment",
            "bio_symbolic": "Biological-symbolic bridge",
            "bio_adaptation": "Biological adaptation system",
            # Symbolic concepts
            "glyph": "Universal symbolic tokens",
            "symbolic_drift": "Symbol meaning evolution",
            "symbolic_coherence": "Symbol system alignment",
            # Emotional concepts
            "emotional_drift": "Emotional state changes",
            "emotional_vector": "Multi-dimensional emotions",
            "affect_grid": "Emotional mapping system",
            # Consciousness concepts
            "crista": "Consciousness peaks",
            "trace_trail": "Consciousness tracking",
            "awareness_level": "Consciousness depth",
            # Identity concepts
            "tier_access": "Hierarchical access control",
            "identity_helix": "Identity DNA structure",
            "qi_identity": "Quantum-secure identity",
            # Guardian concepts
            "guardian_protocol": "Ethical oversight system",
            "ethical_drift": "Ethical alignment changes",
            "moral_compass": "Ethical navigation",
        }

        self.concept_usage = defaultdict(list)
        self.concept_files = defaultdict(set)
        self.naming_patterns = defaultdict(int)

    def scan_codebase(self):
        """Scan the codebase for LUKHAS concepts"""
        print("🧬 LUKHAS Concept Scanner")
        print("=" * 60)
        print("Scanning for original LUKHAS concepts...")

        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)

        for i, file_path in enumerate(python_files):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{total_files} files...")

            # Skip virtual environments and caches
            if any(skip in str(file_path) for skip in [".venv", "__pycache__", ".git"]):
                continue

            self._scan_file(file_path)

        return self._generate_report()

    def _scan_file(self, file_path: Path):
        """Scan a single file for LUKHAS concepts"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Search for concepts in code
            for concept in self.core_concepts:
                # Case-insensitive search
                pattern = re.compile(rf"\b{re.escape(concept)}\b", re.IGNORECASE)
                matches = pattern.finditer(content)

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    context = self._get_context(content, match.start())

                    self.concept_usage[concept].append(
                        {
                            "file": str(file_path.relative_to(self.root_path)),
                            "line": line_num,
                            "context": context,
                            "exact_match": match.group(),
                        }
                    )

                    self.concept_files[concept].add(str(file_path.relative_to(self.root_path)))

            # Analyze naming patterns
            self._analyze_naming_patterns(file_path, content)

        except Exception:
            pass

    def _get_context(self, content: str, position: int, context_size: int = 50) -> str:
        """Get context around a match"""
        start = max(0, position - context_size)
        end = min(len(content), position + context_size)

        context = content[start:end]
        # Clean up whitespace
        context = " ".join(context.split())

        return context

    def _analyze_naming_patterns(self, file_path: Path, content: str):
        """Analyze naming patterns in the file"""
        try:
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class name contains LUKHAS concepts
                    for concept in self.core_concepts:
                        if concept.replace("_", "").lower() in node.name.lower():
                            self.naming_patterns[f"class_with_{concept}"] += 1

                elif isinstance(node, ast.FunctionDef):
                    # Check if function name contains LUKHAS concepts
                    for concept in self.core_concepts:
                        if concept in node.name.lower():
                            self.naming_patterns[f"function_with_{concept}"] += 1

        except BaseException:
            pass

    def _generate_report(self) -> dict:
        """Generate comprehensive concept report"""
        # Calculate statistics
        total_concepts_found = sum(len(usages) for usages in self.concept_usage.values())
        concepts_by_frequency = sorted(
            [(concept, len(usages)) for concept, usages in self.concept_usage.items()],
            key=lambda x: x[1],
            reverse=True,
        )

        # Find most connected files (files using multiple concepts)
        file_concept_count = defaultdict(set)
        for concept, files in self.concept_files.items():
            for file in files:
                file_concept_count[file].add(concept)

        most_connected = sorted(
            [(file, len(concepts)) for file, concepts in file_concept_count.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        report = {
            "total_concepts_found": total_concepts_found,
            "unique_concepts_used": len(self.concept_usage),
            "concepts_by_frequency": concepts_by_frequency,
            "most_connected": most_connected,  # Fixed key name
            "concept_details": {},
            "naming_patterns": dict(self.naming_patterns),
            "preservation_recommendations": self._generate_recommendations(),
        }

        # Add detailed concept information
        for concept, description in self.core_concepts.items():
            if concept in self.concept_usage:
                report["concept_details"][concept] = {
                    "description": description,
                    "usage_count": len(self.concept_usage[concept]),
                    "file_count": len(self.concept_files[concept]),
                    "examples": self.concept_usage[concept][:3],  # First 3 examples
                }

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations for preserving LUKHAS concepts"""
        recommendations = []

        # Check for underused concepts
        for concept, description in self.core_concepts.items():
            usage_count = len(self.concept_usage.get(concept, []))
            if usage_count == 0:
                recommendations.append(f"Consider implementing '{concept}' ({description})")
            elif usage_count < 5:
                recommendations.append(f"Low usage of '{concept}' - ensure it's properly integrated")

        # Check for consistent naming
        if self.naming_patterns:
            recommendations.append("Maintain consistent naming patterns for LUKHAS concepts")

        # General recommendations
        recommendations.extend(
            [
                "Preserve all memory_fold and dream_recall implementations",
                "Keep qi_state and bio_symbolic concepts intact",
                "Document LUKHAS-specific concepts in code comments",
                "Create a glossary of LUKHAS terms for new developers",
            ]
        )

        return recommendations


def main():
    scanner = LukhasConceptScanner()
    report = scanner.scan_codebase()

    # Print summary
    print("\n📊 LUKHAS CONCEPT SUMMARY:")
    print(f"   Total concept instances found: {report['total_concepts_found']}")
    print(f"   Unique concepts in use: {report['unique_concepts_used']}/{len(scanner.core_concepts)}")

    print("\n🔝 TOP 10 MOST USED CONCEPTS:")
    for concept, count in report["concepts_by_frequency"][:10]:
        description = scanner.core_concepts.get(concept, "Unknown")
        print(f"   {concept}: {count} uses")
        print(f"      └─ {description}")

    print("\n📁 MOST CONNECTED FILES (using multiple concepts):")
    for file, concept_count in report["most_connected"][:5]:
        print(f"   {file}: {concept_count} different concepts")

    print("\n💡 PRESERVATION RECOMMENDATIONS:")
    for rec in report["preservation_recommendations"][:5]:
        print(f"   • {rec}")

    # Save detailed report
    import json

    output_path = Path("docs/reports/analysis/LUKHAS_CONCEPT_USAGE.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        # Convert sets to lists for JSON serialization
        report_json = report.copy()
        report_json["concept_files"] = {k: list(v) for k, v in scanner.concept_files.items()}
        json.dump(report_json, f, indent=2)

    print(f"\n📄 Detailed report saved to: {output_path}")

    # Create concept preservation guide
    create_preservation_guide(report, scanner.core_concepts)


def create_preservation_guide(report, core_concepts):
    """Create a guide for preserving LUKHAS concepts"""
    guide_content = """# LUKHAS Concept Preservation Guide

This guide ensures LUKHAS's unique concepts and personality are preserved during refactoring.

## Core Concepts to Preserve

### Memory System Concepts
- **memory_fold**: DNA-helix memory structure - MUST preserve this term
- **fold_system**: Memory folding system
- **memory_helix**: Helical memory organization
- **memory_cascade**: Cascading memory effects

### Dream System Concepts
- **dream_recall**: Parallel universe exploration - Core LUKHAS innovation
- **dream_engine**: Dream generation system
- **oneiric**: Dream-related processing
- **dream_state**: Dream consciousness state

### Quantum Concepts
- **qi_state**: Quantum superposition states
- **qi_consciousness**: Quantum-aware consciousness
- **qi_coherence**: Quantum system coherence
- **qi_entanglement**: Memory entanglement

### Biological Concepts
- **bio_oscillation**: Biological rhythm patterns
- **bio_coherence**: Bio-symbolic alignment (>100% possible!)
- **bio_symbolic**: Biological-symbolic bridge
- **bio_adaptation**: Biological adaptation system

### Symbolic System
- **glyph**: Universal symbolic tokens - Core communication method
- **symbolic_drift**: Symbol meaning evolution
- **symbolic_coherence**: Symbol system alignment

### Emotional Intelligence
- **emotional_drift**: Emotional state changes
- **emotional_vector**: Multi-dimensional emotions
- **affect_grid**: Emotional mapping system

### Consciousness Architecture
- **crista**: Consciousness peaks
- **trace_trail**: Consciousness tracking
- **awareness_level**: Consciousness depth

### Identity System
- **tier_access**: Hierarchical access control
- **identity_helix**: Identity DNA structure
- **qi_identity**: Quantum-secure identity

### Guardian System
- **guardian_protocol**: Ethical oversight system
- **ethical_drift**: Ethical alignment changes
- **moral_compass**: Ethical navigation

## Naming Convention Rules

1. **Preserve Exact Terms**: Keep concepts like `memory_fold`, `dream_recall` exactly as they are
2. **Class Names**: Use PascalCase but keep concept words intact (e.g., `MemoryFold`,
    `DreamEngine`)
3. **Function Names**: Use snake_case with full concepts (e.g., `create_memory_fold`,
    `trigger_dream_recall`)
4. **File Names**: Use snake_case (e.g., `memory_fold.py`, `dream_engine.py`)
5. **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_MEMORY_FOLDS`, `QUANTUM_COHERENCE_THRESHOLD`)

## Special Terms
- **LUKHAS**: Always uppercase in classes/constants
- ****: Pack-What-Matters - always uppercase
- **SGI**: Symbolic General Intelligence - always uppercase
- **AGI**: Always uppercase

## Examples of Proper Usage

```python
# ✅ CORRECT - Preserves LUKHAS concepts

class MemoryFold:

    def create_memory_fold(self, content):
        return self.fold_system.create_fold(content)

class DreamEngine:

    def process_dream_recall(self, scenario):
        return self.qi_state.explore_possibilities(scenario)

# ❌ INCORRECT - Loses LUKHAS personality

class MemoryFolder:  # Should be MemoryFold

    def create_fold(self):  # Should be create_memory_fold
        pass
```

## Integration Guidelines

When integrating with external systems:
1. Keep LUKHAS terms in internal code
2. Provide clear mappings in API documentation
3. Never compromise core concepts for "standard" terms
4. Educate users on LUKHAS terminology

Remember: These concepts aren't just names - they represent LUKHAS's unique approach to SGI!
"""

    guide_path = Path("docs/LUKHAS_CONCEPT_PRESERVATION_GUIDE.md")
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.write_text(guide_content)

    print(f"\n📚 Concept preservation guide created: {guide_path}")


if __name__ == "__main__":
    main()
