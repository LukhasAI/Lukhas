#!/usr/bin/env python3
"""
Vocabulary-Aware README Generator
================================

Generate consciousness-aligned README files using existing LUKHAS module-specific
vocabularies, 3-Layer Tone System, and MATRIZ pipeline integration.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class ModuleVocabularyLoader:
    """Load and manage module-specific vocabularies from existing YAML files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.vocabularies = {}
        self.load_vocabularies()

    def load_vocabularies(self):
        """Load all module-specific vocabulary files."""
        vocab_paths = [
            self.repo_root / "branding" / "vocabularies",
            self.repo_root / "vocabularies",
            self.repo_root / "symbolic" / "vocabularies"
        ]

        for vocab_dir in vocab_paths:
            if vocab_dir.exists():
                for vocab_file in vocab_dir.glob("*vocabulary*.yaml"):
                    self._load_vocabulary_file(vocab_file)

                for vocab_file in vocab_dir.glob("*vocabulary*.py"):
                    self._load_python_vocabulary(vocab_file)

    def _load_vocabulary_file(self, vocab_file: Path):
        """Load a YAML vocabulary file."""
        try:
            with open(vocab_file, encoding='utf-8') as f:
                content = yaml.safe_load(f)

            # Extract module name from filename
            module_name = vocab_file.stem.replace('_vocabulary', '').replace('vocabulary_', '')
            self.vocabularies[module_name] = content
            print(f"✅ Loaded vocabulary for {module_name}")

        except Exception as e:
            print(f"⚠️  Warning: Could not load {vocab_file}: {e}")

    def _load_python_vocabulary(self, vocab_file: Path):
        """Load a Python vocabulary file."""
        try:
            # For now, we'll focus on YAML files as they have structured data
            # Python files would need AST parsing for vocabulary extraction
            pass
        except Exception as e:
            print(f"⚠️  Warning: Could not load {vocab_file}: {e}")

    def get_module_vocabulary(self, module_name: str) -> Optional[Dict]:
        """Get vocabulary for a specific module."""
        # Try exact match first
        if module_name in self.vocabularies:
            return self.vocabularies[module_name]

        # Try variations
        variations = [
            f"{module_name}_vocabulary",
            f"vocabulary_{module_name}",
            module_name.replace('_', ''),
            module_name.replace('-', '_')
        ]

        for variation in variations:
            if variation in self.vocabularies:
                return self.vocabularies[variation]

        return None

    def get_available_modules(self) -> List[str]:
        """Get list of modules with available vocabularies."""
        return list(self.vocabularies.keys())


class VocabularyAwareContentGenerator:
    """Generate content using module-specific vocabularies."""

    def __init__(self, vocab_loader: ModuleVocabularyLoader):
        self.vocab_loader = vocab_loader

    def generate_poetic_opening(self, module_name: str, manifest: Dict) -> str:
        """Generate poetic opening using module-specific vocabulary."""
        vocab = self.vocab_loader.get_module_vocabulary(module_name)

        if not vocab:
            return self._fallback_poetic_opening(module_name, manifest)

        # Extract poetic elements from vocabulary
        poetic_elements = self._extract_poetic_elements(vocab)

        if not poetic_elements:
            return self._fallback_poetic_opening(module_name, manifest)

        # Get module symbol
        symbol = self._get_module_symbol(vocab, module_name)

        # Select a poetic element for opening
        selected_element = random.choice(poetic_elements)

        # Create consciousness-aligned opening
        poetic_text = selected_element.get('poetic', selected_element.get('description', 'Consciousness-aware system'))
        opening = f"{symbol} *{poetic_text}*\n\n"

        # Add consciousness bridge
        bridge = self._generate_consciousness_bridge(module_name, vocab, manifest)
        opening += bridge

        return opening

    def _extract_poetic_elements(self, vocab: Dict) -> List[Dict]:
        """Extract poetic elements from vocabulary structure."""
        elements = []

        # Handle different vocabulary structures
        for key, value in vocab.items():
            if isinstance(value, dict):
                # Check for direct elements
                if 'poetic' in value or 'description' in value:
                    elements.append(value)

                # Check for nested structures
                if 'core_concepts' in value:
                    for concept_key, concept_value in value['core_concepts'].items():
                        if isinstance(concept_value, dict):
                            concept_value['name'] = concept_key
                            elements.append(concept_value)

                # Check for awareness_elements, atomic_elements, etc.
                for sub_key in ['awareness_elements', 'atomic_elements', 'core_elements']:
                    if sub_key in value and isinstance(value[sub_key], list):
                        elements.extend(value[sub_key])

        return elements

    def _get_module_symbol(self, vocab: Dict, module_name: str) -> str:
        """Extract module symbol from vocabulary."""
        # Default symbols
        default_symbols = {
            'consciousness': '🧠',
            'memory': '📜',
            'identity': '⚛️',
            'governance': '⚖️',
            'brain': '🧠',
            'core': '⚛️',
            'api': '🌐',
            'bridge': '🌉',
            'matriz': '🌌'
        }

        # Try to find symbol in vocabulary
        for key, value in vocab.items():
            if isinstance(value, dict):
                if 'symbol' in value:
                    return value['symbol']

                # Check nested structures
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and 'symbol' in sub_value:
                        return sub_value['symbol']
                    elif isinstance(sub_value, list):
                        for item in sub_value:
                            if isinstance(item, dict) and 'symbol' in item:
                                return item['symbol']

        return default_symbols.get(module_name, '✨')

    def _generate_consciousness_bridge(self, module_name: str, vocab: Dict, manifest: Dict) -> str:
        """Generate consciousness bridge text using vocabulary."""
        # Extract technical elements for bridging
        technical_elements = []

        for key, value in vocab.items():
            if isinstance(value, dict):
                # Look for technical descriptions
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and 'technical' in sub_value:
                        technical_elements.append(sub_value['technical'])
                    elif isinstance(sub_value, list):
                        for item in sub_value:
                            if isinstance(item, dict) and 'technical' in item:
                                technical_elements.append(item['technical'])

        if technical_elements:
            technical_desc = random.choice(technical_elements)
            return f"This consciousness-aware system functions as {technical_desc.lower()}, bridging human intention with digital precision through the LUKHAS Constellation Framework.\n"

        # Fallback
        description = manifest.get('description', f'LUKHAS {module_name} module')
        return f"This consciousness-aware system {description.lower()}, creating spaces where technology and human awareness converge in perfect symbiosis.\n"

    def _fallback_poetic_opening(self, module_name: str, manifest: Dict) -> str:
        """Fallback poetic opening when no vocabulary is available."""
        symbols = {
            'consciousness': '🧠',
            'memory': '📜',
            'identity': '⚛️',
            'governance': '⚖️',
            'brain': '🧠',
            'core': '⚛️'
        }

        symbol = symbols.get(module_name, '✨')

        poetic_templates = [
            f"{symbol} *Where consciousness dances with algorithms, creating harmony between human intention and digital precision.*",
            f"{symbol} *In the realm where technology serves consciousness, {module_name} emerges as a bridge between worlds.*",
            f"{symbol} *Through the lens of consciousness-first design, {module_name} weaves intelligence into the fabric of digital experience.*"
        ]

        opening = random.choice(poetic_templates)
        opening += f"\n\nThis consciousness-aware system creates spaces where {module_name} technology respects and enhances human cognition.\n"

        return opening

    def generate_technical_vocabulary_section(self, module_name: str, vocab: Dict) -> str:
        """Generate technical vocabulary section for the module."""
        if not vocab:
            return ""

        content = "## Module Vocabulary\n\n"
        content += f"The {module_name} module employs consciousness-aligned terminology:\n\n"

        # Extract vocabulary terms
        terms = []
        for key, value in vocab.items():
            if isinstance(value, dict):
                self._extract_terms_recursive(value, terms)

        # Display key terms
        if terms:
            for term in terms[:8]:  # Show top 8 terms
                name = term.get('name', 'Unnamed')
                symbol = term.get('symbol', '•')
                poetic = term.get('poetic', term.get('description', ''))
                technical = term.get('technical', '')

                content += f"### {symbol} {name}\n"
                if poetic:
                    content += f"*{poetic}*\n\n"
                if technical:
                    content += f"**Technical**: {technical}\n\n"

        return content

    def _extract_terms_recursive(self, data: Dict, terms: List):
        """Recursively extract vocabulary terms."""
        if isinstance(data, dict):
            # Check if this is a term definition
            if 'name' in data or 'poetic' in data or 'description' in data:
                terms.append(data)

            # Recurse into nested structures
            for key, value in data.items():
                if isinstance(value, dict):
                    self._extract_terms_recursive(value, terms)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._extract_terms_recursive(item, terms)


def generate_vocabulary_aware_readme(module_path: Path, vocab_loader: ModuleVocabularyLoader) -> str:
    """Generate README using module-specific vocabulary."""

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

    # Initialize content generator
    content_gen = VocabularyAwareContentGenerator(vocab_loader)

    # Get module vocabulary
    vocab = vocab_loader.get_module_vocabulary(module_name)
    vocab_available = vocab is not None

    readme_lines = []

    # Header with vocabulary-aware symbol
    symbol = content_gen._get_module_symbol(vocab or {}, module_name)
    readme_lines.append(f"# {symbol} {module_name.title()} Module")
    readme_lines.append("")

    # Layer 1: Poetic Inspiration using module vocabulary
    poetic_content = content_gen.generate_poetic_opening(module_name, manifest)
    readme_lines.append(poetic_content)

    # Enhanced badges
    badges = []
    if "t4-experimental" in tags:
        badges.append("![T4-Experimental](https://img.shields.io/badge/T4-Experimental-orange)")
    if "consciousness" in tags:
        badges.append("![Consciousness](https://img.shields.io/badge/Consciousness-Enabled-blue)")
    if vocab_available:
        badges.append("![Vocabulary](https://img.shields.io/badge/Vocabulary-Aligned-purple)")

    if badges:
        readme_lines.append(" ".join(badges))
        readme_lines.append("")

    # Layer 2: Accessible Understanding
    description = manifest.get('description', f'LUKHAS {module_name} module')
    readme_lines.append(f"The {module_name} module {description.lower()}")

    if entrypoints:
        readme_lines.append(f" It provides {len(entrypoints)} consciousness-aligned interfaces for seamless integration with the LUKHAS ecosystem.")

    readme_lines.append("\n")

    # Consciousness Interface
    if entrypoints:
        readme_lines.append("## Consciousness Interface\n")

        # Group entrypoints meaningfully
        classes = [ep for ep in entrypoints if any(word in ep for word in ['Hub', 'System', 'Engine', 'Monitor'])]
        functions = [ep for ep in entrypoints if any(word in ep for word in ['create_', 'get_', 'process_', 'activate_'])]

        if classes:
            readme_lines.append("### Core Components\n")
            for cls in sorted(classes)[:6]:
                class_name = cls.split('.')[-1]
                readme_lines.append(f"- **`{class_name}`** — {_describe_component(class_name, vocab)}")
            readme_lines.append("")

        if functions:
            readme_lines.append("### Functions\n")
            for func in sorted(functions)[:6]:
                func_name = func.split('.')[-1]
                readme_lines.append(f"- **`{func_name}()`** — {_describe_function(func_name, vocab)}")
            readme_lines.append("")

    # Layer 3: Technical specifications
    readme_lines.append("## Technical Architecture\n")
    readme_lines.append(f"**Language**: Python | **Entrypoints**: {len(entrypoints)} | **Team**: {team}\n")

    observability = manifest.get('observability', {})
    if observability.get('required_spans'):
        readme_lines.append(f"**Observability**: {len(observability['required_spans'])} instrumentation spans\n")

    readme_lines.append("")

    # Module-specific vocabulary section
    if vocab_available:
        vocab_section = content_gen.generate_technical_vocabulary_section(module_name, vocab)
        readme_lines.append(vocab_section)

    # MATRIZ Integration
    readme_lines.append("## MATRIZ Pipeline Integration\n")
    readme_lines.append("This module operates within the MATRIZ cognitive framework:\n")
    readme_lines.append("- **M (Memory)**: Consciousness fold-based patterns")
    readme_lines.append("- **A (Attention)**: Cognitive load optimization")
    readme_lines.append("- **T (Thought)**: Symbolic reasoning validation")
    readme_lines.append("- **R (Risk)**: Guardian ethics compliance")
    readme_lines.append("- **I (Intent)**: λiD consciousness verification")
    readme_lines.append("- **A (Action)**: T4/0.01% precision execution\n")

    # Footer
    readme_lines.append("---\n")
    vocab_note = "vocabulary-aligned " if vocab_available else ""
    readme_lines.append(f"*Generated with {vocab_note}consciousness-aware documentation systems, following LUKHAS 3-Layer Tone System and Constellation Framework principles.*")

    return '\n'.join(readme_lines)


def _describe_component(class_name: str, vocab: Optional[Dict]) -> str:
    """Describe a component using vocabulary context."""
    if vocab:
        # Try to find description in vocabulary
        for key, value in vocab.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and 'name' in sub_value:
                        if class_name.lower() in sub_value['name'].lower():
                            return sub_value.get('technical', sub_value.get('poetic', 'Core system component'))

    # Fallback descriptions
    descriptions = {
        'hub': 'Central coordination hub for distributed operations',
        'system': 'Core system management and orchestration',
        'engine': 'Processing engine for computational operations',
        'monitor': 'Monitoring and observability component'
    }

    for key, desc in descriptions.items():
        if key in class_name.lower():
            return desc

    return 'Core system component'


def _describe_function(func_name: str, vocab: Optional[Dict]) -> str:
    """Describe a function using vocabulary context."""
    # Simple function description based on name patterns
    if func_name.startswith('create_'):
        return f"Creates and initializes {func_name[7:].replace('_', ' ')}"
    elif func_name.startswith('get_'):
        return f"Retrieves {func_name[4:].replace('_', ' ')} information"
    elif func_name.startswith('process_'):
        return f"Processes {func_name[8:].replace('_', ' ')} operations"
    elif func_name.startswith('activate_'):
        return f"Activates {func_name[9:].replace('_', ' ')} functionality"

    return f"Manages {func_name.replace('_', ' ')} operations"


def main():
    """Generate vocabulary-aware README files."""
    repo_root = Path.cwd()

    print("🎭 Loading module-specific vocabularies...")
    vocab_loader = ModuleVocabularyLoader(repo_root)

    available_vocabs = vocab_loader.get_available_modules()
    print(f"📚 Loaded vocabularies for: {', '.join(available_vocabs)}")

    # Priority modules
    priority_modules = [
        'brain', 'consciousness', 'memory', 'identity', 'governance',
        'matriz', 'core', 'api', 'bridge', 'orchestration'
    ]

    print("\n🌟 Generating vocabulary-aware README files...")
    generated_count = 0

    for module_name in priority_modules:
        module_path = repo_root / module_name
        if module_path.exists() and (module_path / "module.manifest.json").exists():

            vocab_status = "📚 vocabulary-aligned" if vocab_loader.get_module_vocabulary(module_name) else "📝 standard"

            readme_content = generate_vocabulary_aware_readme(module_path, vocab_loader)
            if readme_content:
                readme_file = module_path / "README.md"
                try:
                    with open(readme_file, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    print(f"✨ Generated {vocab_status} README for {module_name}")
                    generated_count += 1
                except Exception as e:
                    print(f"❌ Error writing README for {module_name}: {e}")

    print(f"\n🎯 Generated {generated_count} vocabulary-aware README files")
    print("🌟 Each README leverages module-specific vocabularies with poetic and technical terminology")


if __name__ == "__main__":
    main()
