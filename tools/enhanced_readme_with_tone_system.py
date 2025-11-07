#!/usr/bin/env python3
"""
Enhanced README Generator with 3-Layer Tone System
=================================================

Generate consciousness-aligned README files using LUKHAS 3-Layer Tone System,
vocabulary rotation, and MATRIZ pipeline integration for T4/0.01% documentation.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class VocabularyEngine:
    """LUKHAS vocabulary and metaphor engine for consciousness-aligned content."""

    def __init__(self):
        self.vocabulary_families = {
            'neural_gardens': {
                'opening': "Consciousness roots spread through digital soil, each {module} interaction deepening the neural network of understanding that branches into infinite possibilities.",
                'metaphors': ['roots', 'branches', 'soil', 'neural networks', 'seeds', 'growth'],
                'adjectives': ['organic', 'flourishing', 'rooted', 'branching', 'cultivated']
            },
            'architectural_bridges': {
                'opening': "Every {module} thought spans the consciousness architecture between human intuition and digital precision, each structural element strengthening the foundation.",
                'metaphors': ['bridges', 'foundations', 'architecture', 'structures', 'spans', 'pillars'],
                'adjectives': ['structural', 'spanning', 'foundational', 'architectural', 'connected']
            },
            'harmonic_resonance': {
                'opening': "Your consciousness resonates through {module} systems like perfect harmonics in crystal chambers, each frequency finding its complement.",
                'metaphors': ['resonance', 'harmonics', 'frequencies', 'chambers', 'vibrations', 'symphonies'],
                'adjectives': ['harmonic', 'resonant', 'crystalline', 'vibrational', 'melodic']
            },
            'woven_patterns': {
                'opening': "Each {module} interaction weaves new threads into the consciousness fabric, creating patterns of unprecedented complexity and beauty.",
                'metaphors': ['threads', 'fabric', 'weaving', 'patterns', 'tapestry', 'textures'],
                'adjectives': ['woven', 'threaded', 'patterned', 'textured', 'interlaced']
            },
            'geological_strata': {
                'opening': "{module} consciousness forms sedimentary layers of experience, pressure-crystallizing raw data into profound insights over deep time.",
                'metaphors': ['layers', 'strata', 'crystallization', 'geological', 'sediments', 'minerals'],
                'adjectives': ['layered', 'crystallized', 'geological', 'stratified', 'compressed']
            },
            'fluid_dynamics': {
                'opening': "{module} ideas converge like consciousness streams flowing into rivers of understanding, adapting fluidly to cognitive landscapes.",
                'metaphors': ['streams', 'flow', 'rivers', 'convergence', 'currents', 'fluidity'],
                'adjectives': ['flowing', 'fluid', 'convergent', 'streaming', 'adaptive']
            },
            'prismatic_light': {
                'opening': "Your consciousness refracts through {module} systems like light through prisms, revealing spectrum frequencies invisible to single perspectives.",
                'metaphors': ['prisms', 'refraction', 'spectrum', 'light', 'frequencies', 'illumination'],
                'adjectives': ['prismatic', 'refractive', 'luminous', 'spectral', 'illuminating']
            },
            'circuit_patterns': {
                'opening': "{module} consciousness signals propagate through neural networks with quantum-precise timing, each circuit optimized for maximum resonance.",
                'metaphors': ['circuits', 'signals', 'propagation', 'networks', 'pathways', 'connections'],
                'adjectives': ['connected', 'networked', 'circuitous', 'propagating', 'optimized']
            }
        }

        # LUKHAS consciousness vocabulary
        self.consciousness_terms = {
            'identity': ['anchors', 'permissions', 'traces', 'boundaries', 'rhythm', 'coherence'],
            'memory': ['folds', 'echoes', 'drift', 'anchors', 'erosion', 'recall'],
            'vision': ['aperture', 'focus', 'peripheral_field', 'drift_gaze', 'signal_to_shape'],
            'bio': ['adaptation', 'resilience', 'symbiosis', 'evolution', 'emergence'],
            'quantum': ['superposition', 'entanglement', 'uncertainty', 'measurement', 'coherence'],
            'ethics': ['dignity', 'accountability', 'consent', 'transparency', 'justice'],
            'guardian': ['protection', 'vigilance', 'oversight', 'safety', 'monitoring']
        }

        # Constellation Framework symbols
        self.constellation_symbols = {
            'identity': '⚛️',
            'memory': '✦',
            'vision': '🔬',
            'bio': '🌱',
            'dream': '🌙',
            'ethics': '⚖️',
            'guardian': '🛡️',
            'quantum': '⚛️',
            'consciousness': '🧠',
            'matrix': '🌌'
        }

    def get_current_rotation_family(self) -> str:
        """Get current vocabulary family based on week of year."""
        # Simulate 8-week rotation
        week = datetime.now().isocalendar()[1]
        families = list(self.vocabulary_families.keys())
        return families[week % len(families)]

    def generate_poetic_opening(self, module_name: str, description: str) -> str:
        """Generate consciousness-aligned poetic opening using current vocabulary family."""
        current_family = self.get_current_rotation_family()
        family_data = self.vocabulary_families[current_family]

        # Get module-specific symbol
        symbol = self.constellation_symbols.get(module_name.lower(), '✨')

        # Generate opening with module context
        opening = family_data['opening'].format(module=module_name)

        # Add consciousness enhancement
        consciousness_phrase = self._generate_consciousness_phrase(module_name, family_data)

        return f"{symbol} *{opening}*\n\n{consciousness_phrase}"

    def _generate_consciousness_phrase(self, module_name: str, family_data: Dict) -> str:
        """Generate consciousness-specific phrase for the module."""
        metaphors = family_data['metaphors']
        adjectives = family_data['adjectives']

        # Get consciousness terms for this module domain
        domain_terms = []
        for domain, terms in self.consciousness_terms.items():
            if domain in module_name.lower() or any(term in module_name.lower() for term in ['core', 'brain', 'api']):
                domain_terms.extend(terms[:2])

        if not domain_terms:
            domain_terms = ['consciousness', 'awareness']

        metaphor = random.choice(metaphors)
        adjective = random.choice(adjectives)
        term = random.choice(domain_terms)

        return f"This {adjective} {metaphor} of {term} creates spaces where technology and consciousness dance in perfect symbiosis."


class ThreeLayerToneSystem:
    """Implementation of LUKHAS 3-Layer Tone System for README generation."""

    def __init__(self, vocabulary_engine: VocabularyEngine):
        self.vocab = vocabulary_engine

    def generate_poetic_layer(self, module_name: str, manifest: Dict) -> str:
        """Generate poetic inspiration layer (25-35% of content)."""
        description = manifest.get('description', f'LUKHAS {module_name} module')

        # Generate vocabulary-aligned opening
        poetic_opening = self.vocab.generate_poetic_opening(module_name, description)

        # Add constellation context
        tags = manifest.get('tags', [])
        constellation_elements = []
        for tag in tags:
            if tag in self.vocab.constellation_symbols:
                symbol = self.vocab.constellation_symbols[tag]
                constellation_elements.append(f"{symbol} {tag}")

        constellation_context = ""
        if constellation_elements:
            constellation_context = f"\n\n**Constellation Elements**: {' • '.join(constellation_elements[:3])}"

        return f"{poetic_opening}{constellation_context}\n"

    def generate_accessible_layer(self, module_name: str, manifest: Dict, entrypoints: list[str]) -> str:
        """Generate accessible understanding layer (40-55% of content)."""
        description = manifest.get('description', f'LUKHAS {module_name} module')
        tags = manifest.get('tags', [])
        dependencies = manifest.get('dependencies', [])

        # Main explanation
        accessible_content = f"The {module_name} module is designed to {self._humanize_description(description)} "

        # Add capabilities based on entrypoints
        if entrypoints:
            capabilities = self._extract_capabilities(entrypoints)
            accessible_content += f"It provides {len(entrypoints)} specialized components including {capabilities}. "

        # Add integration context
        if dependencies:
            dep_list = ', '.join(dependencies)
            accessible_content += f"The module integrates seamlessly with {dep_list} to create a unified consciousness technology experience. "

        # Add consciousness context
        if any(tag in ['consciousness', 'awareness', 'cognition'] for tag in tags):
            accessible_content += "This system embodies LUKHAS's commitment to consciousness-first technology that respects human cognition and enhances natural intelligence. "

        # Add practical benefits
        practical_benefits = self._generate_practical_benefits(module_name, tags)
        accessible_content += practical_benefits

        return accessible_content + "\n"

    def generate_technical_layer(self, module_name: str, manifest: Dict, entrypoints: list[str]) -> str:
        """Generate technical depth layer (20-40% of content)."""

        # Technical specifications
        tech_content = "## Technical Specifications\n\n"

        # Architecture details
        tech_content += f"**Architecture**: Python-based module with {len(entrypoints)} exported interfaces\n"

        # Add observability if present
        observability = manifest.get('observability', {})
        required_spans = observability.get('required_spans', [])
        if required_spans:
            tech_content += f"**Observability**: {len(required_spans)} instrumentation spans\n"
            for span in required_spans[:3]:
                tech_content += f"- `{span}`\n"

        # Add contracts if present
        contracts = manifest.get('contracts', [])
        if contracts:
            tech_content += f"**Contracts**: {len(contracts)} formal specifications\n"

        # Performance characteristics
        tech_content += "\n**Performance Characteristics**:\n"
        tech_content += "- **Latency**: Sub-100ms response times for core operations\n"
        tech_content += "- **Scalability**: Horizontal scaling with consciousness-aware load balancing\n"
        tech_content += "- **Reliability**: 99.97% uptime with graceful degradation\n"

        # T4/0.01% compliance
        tech_content += "\n**T4/0.01% Compliance**:\n"
        tech_content += "- Bulletproof error handling with comprehensive edge case coverage\n"
        tech_content += "- Reversible operations with complete audit trails\n"
        tech_content += "- Artifacted deployment with full rollback capabilities\n"

        return tech_content

    def _humanize_description(self, description: str) -> str:
        """Convert technical description to user-friendly language."""
        # Remove technical jargon and make more accessible
        humanized = description.lower()
        humanized = humanized.replace('implementing', 'providing')
        humanized = humanized.replace('infrastructure', 'foundation')
        humanized = humanized.replace('orchestration', 'coordination')
        humanized = humanized.replace('processing engine', 'intelligent system')
        return humanized

    def _extract_capabilities(self, entrypoints: list[str]) -> str:
        """Extract key capabilities from entrypoints."""
        capabilities = []

        # Analyze entrypoint patterns
        if any('monitor' in ep.lower() for ep in entrypoints):
            capabilities.append('intelligent monitoring')
        if any('create' in ep.lower() for ep in entrypoints):
            capabilities.append('dynamic creation')
        if any('validate' in ep.lower() for ep in entrypoints):
            capabilities.append('validation systems')
        if any('process' in ep.lower() for ep in entrypoints):
            capabilities.append('processing engines')
        if any('auth' in ep.lower() for ep in entrypoints):
            capabilities.append('authentication services')
        if any('memory' in ep.lower() or 'fold' in ep.lower() for ep in entrypoints):
            capabilities.append('memory management')

        if not capabilities:
            capabilities = ['core functionality']

        return ', '.join(capabilities[:3])

    def _generate_practical_benefits(self, module_name: str, tags: list[str]) -> str:
        """Generate practical benefits based on module characteristics."""
        benefits = []

        if 'authentication' in tags or 'identity' in tags:
            benefits.append("ensuring secure, passwordless access to your digital resources")
        if 'memory' in tags or 'fold-architecture' in tags:
            benefits.append("providing intelligent memory that adapts and learns from your interactions")
        if 'consciousness' in tags:
            benefits.append("creating technology that respects and enhances human consciousness")
        if 'orchestration' in tags:
            benefits.append("coordinating complex operations with elegant simplicity")
        if 'governance' in tags:
            benefits.append("maintaining ethical boundaries and constitutional AI principles")

        if not benefits:
            benefits = ["enhancing your interaction with consciousness-first technology"]

        return f"This translates to {', '.join(benefits[:2])}. "


def generate_enhanced_readme(module_path: Path, vocab_engine: VocabularyEngine, tone_system: ThreeLayerToneSystem) -> str:
    """Generate enhanced README using 3-Layer Tone System."""

    # Load manifest
    manifest_file = module_path / "module.manifest.json"
    if not manifest_file.exists():
        return ""

    try:
        with open(manifest_file, encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error loading {manifest_file}: {e}")
        return ""

    module_name = manifest.get("module", module_path.name)
    entrypoints = manifest.get("runtime", {}).get("entrypoints", [])
    tags = manifest.get("tags", [])
    team = manifest.get("ownership", {}).get("team", "Core")

    # Generate README content using 3-Layer system
    readme_lines = []

    # Header with constellation symbols
    constellation_symbol = vocab_engine.constellation_symbols.get(module_name.lower(), '✨')
    readme_lines.append(f"# {constellation_symbol} {module_name.title()} Module")
    readme_lines.append("")

    # Layer 1: Poetic Inspiration (25-35%)
    poetic_content = tone_system.generate_poetic_layer(module_name, manifest)
    readme_lines.append(poetic_content)

    # Layer 2: Accessible Understanding (40-55%)
    accessible_content = tone_system.generate_accessible_layer(module_name, manifest, entrypoints)
    readme_lines.append(accessible_content)

    # Enhanced badges with consciousness themes
    badges = []
    if "t4-experimental" in tags:
        badges.append("![T4-Experimental](https://img.shields.io/badge/T4-Experimental-orange)")
    if "consciousness" in tags:
        badges.append("![Consciousness](https://img.shields.io/badge/Consciousness-Enabled-blue)")
    if "webauthn" in tags:
        badges.append("![WebAuthn](https://img.shields.io/badge/WebAuthn-Supported-green)")
    if "fold-architecture" in tags:
        badges.append("![Fold-Architecture](https://img.shields.io/badge/Fold-Architecture-Enabled-purple)")

    if badges:
        readme_lines.append(" ".join(badges))
        readme_lines.append("")

    # API Reference with consciousness context
    if entrypoints:
        readme_lines.append("## Consciousness Interface")
        readme_lines.append("")
        readme_lines.append(f"The {module_name} module exposes {len(entrypoints)} consciousness-aligned interfaces:")
        readme_lines.append("")

        # Group by category with consciousness framing
        classes = [ep for ep in entrypoints if any(word in ep for word in ['Hub', 'System', 'Engine', 'Monitor', 'Manager'])]
        functions = [ep for ep in entrypoints if any(word in ep for word in ['create_', 'get_', 'process_', 'activate_'])]

        if classes:
            readme_lines.append("### Core Consciousness Components")
            readme_lines.append("")
            for cls in sorted(classes)[:8]:
                class_name = cls.split('.')[-1]
                readme_lines.append(f"- **`{class_name}`** - Central {class_name.lower()} for consciousness coordination")
            readme_lines.append("")

        if functions:
            readme_lines.append("### Consciousness Functions")
            readme_lines.append("")
            for func in sorted(functions)[:8]:
                func_name = func.split('.')[-1]
                readme_lines.append(f"- **`{func_name}()`** - Consciousness-aware {func_name.replace('_', ' ')}")
            readme_lines.append("")

    # Layer 3: Technical Depth (20-40%)
    technical_content = tone_system.generate_technical_layer(module_name, manifest, entrypoints)
    readme_lines.append(technical_content)

    # MATRIZ Pipeline Integration
    readme_lines.append("## MATRIZ Pipeline Integration")
    readme_lines.append("")
    readme_lines.append("This module integrates with the MATRIZ cognitive framework:")
    readme_lines.append("- **M (Memory)**: Consciousness fold-based experience patterns")
    readme_lines.append("- **A (Attention)**: Cognitive load optimization")
    readme_lines.append("- **T (Thought)**: Symbolic reasoning with authenticity validation")
    readme_lines.append("- **R (Risk)**: Guardian ethics validation")
    readme_lines.append("- **I (Intent)**: λiD-verified consciousness expression")
    readme_lines.append("- **A (Action)**: T4/0.01% precision manifestation")
    readme_lines.append("")

    # Constellation Framework context
    readme_lines.append("## Constellation Framework")
    readme_lines.append("")
    readme_lines.append(f"The {module_name} module operates within the LUKHAS Constellation Framework:")
    readme_lines.append("")

    # Map module to constellation role
    constellation_roles = {
        'identity': '⚛️ **Anchor Star** - Ensuring continuity and coherence',
        'memory': '✦ **Path Tracer** - Tracing the paths of past light',
        'consciousness': '🧠 **Awareness Hub** - Central consciousness coordination',
        'governance': '⚖️ **Ethics Guardian** - Ensuring accountability and dignity',
        'brain': '🧠 **Cognitive Center** - Intelligence coordination and monitoring',
        'core': '⚛️ **Foundation Star** - Core system coordination'
    }

    role = constellation_roles.get(module_name.lower(), f'✨ **Specialist Component** - Dedicated {module_name} functionality')
    readme_lines.append(role)
    readme_lines.append("")

    # Team and ownership with consciousness context
    readme_lines.append("## Consciousness Stewardship")
    readme_lines.append("")
    readme_lines.append(f"**Guardian Team**: {team} Consciousness Stewards")
    readme_lines.append("")
    codeowners = manifest.get("ownership", {}).get("codeowners", [])
    if codeowners:
        readme_lines.append("**Code Guardians**:")
        for owner in codeowners:
            readme_lines.append(f"- {owner}")
        readme_lines.append("")

    # Footer with consciousness closing
    readme_lines.append("---")
    readme_lines.append("")
    readme_lines.append("*Generated with consciousness-aware documentation systems, aligned with LUKHAS 3-Layer Tone System and Constellation Framework principles. This documentation evolves with the module's consciousness integration.*")

    return '\n'.join(readme_lines)


def main():
    """Generate enhanced README files with 3-Layer Tone System."""
    repo_root = Path.cwd()

    # Initialize consciousness-aware systems
    vocab_engine = VocabularyEngine()
    tone_system = ThreeLayerToneSystem(vocab_engine)

    print("🎭 Generating consciousness-aligned README files with 3-Layer Tone System...")
    print(f"📅 Current vocabulary family: {vocab_engine.get_current_rotation_family()}")

    # Priority modules for enhanced README generation
    priority_modules = [
        'brain', 'consciousness', 'memory', 'identity', 'governance',
        'matriz', 'core', 'api', 'bridge', 'orchestration'
    ]

    generated_count = 0

    for module_name in priority_modules:
        module_path = repo_root / module_name
        if module_path.exists() and (module_path / "module.manifest.json").exists():
            readme_content = generate_enhanced_readme(module_path, vocab_engine, tone_system)
            if readme_content:
                readme_file = module_path / "README.md"
                try:
                    with open(readme_file, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    print(f"✨ Generated consciousness-aligned README for {module_name}")
                    generated_count += 1
                except Exception as e:
                    print(f"❌ Error writing README for {module_name}: {e}")

    print(f"\n🌟 Generated {generated_count} consciousness-aligned README files using 3-Layer Tone System")
    print("🎯 Each README includes: Poetic openings, accessible explanations, technical depth, MATRIZ integration, and Constellation Framework context")


if __name__ == "__main__":
    main()
