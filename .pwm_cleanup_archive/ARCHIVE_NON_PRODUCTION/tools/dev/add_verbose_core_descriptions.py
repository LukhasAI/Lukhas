#!/usr/bin/env python3

"""
LUKHAS Verbose Core Module Description Generator

Adds rich, verbose descriptions to core LUKHAS modules:
- memory_fold.py - The foundational memory architecture
- memory_helix.py - Voice memory learning system
- haiku_generator.py - Quantum haiku generation
"""

import os
import re
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pattern to find where to insert description
PLACEHOLDER_PATTERN = re.compile(
    r"(@lukhas/HEADER_FOOTER_TEMPLATE\.py\n)\n(PLACEHOLDER FOR VERBOSE DESCRIPTION\n)?",
    re.MULTILINE,
)

# Verbose descriptions for core modules
CORE_MODULE_DESCRIPTIONS = {
    "memory_fold.py": {
        "title": "Memory Fold Architecture",
        "tier": 5,
        "concepts": [
            "memory consolidation",
            "temporal folding",
            "consciousness streams",
            "neural persistence",
        ],
        "prompt_extra": "This is the foundational memory architecture of LUKHAS, implementing temporal memory folding that mimics biological memory consolidation during sleep.",
    },
    "memory_helix.py": {
        "title": "Voice Memory Helix",
        "tier": 4,
        "concepts": [
            "voice learning",
            "accent adaptation",
            "cultural sensitivity",
            "pronunciation curiosity",
        ],
        "prompt_extra": "This module enables LUKHAS to learn and adapt to voices, accents, and pronunciations through a helical learning pattern inspired by DNA structure.",
    },
    "haiku_generator.py": {
        "title": "Quantum Haiku Generator",
        "tier": 3,
        "concepts": [
            "quantum poetry",
            "probabilistic verse",
            "emotional resonance",
            "cultural awareness",
        ],
        "prompt_extra": "This module generates haikus by collapsing superposition-like states of words into poetic expressions that capture fleeting moments of consciousness.",
    },
}


def generate_verbose_core_description(
    module_name: str, module_info: Dict[str, any]
) -> str:
    """Generate verbose description for core modules."""

    prompt = f"""Create an exceptionally rich and verbose module description for a core LUKHAS AGI module.

Module: {module_info['title']}
Tier: {module_info['tier']} (Tier 5 is highest/most critical)
Core Concepts: {', '.join(module_info['concepts'])}
Special Context: {module_info['prompt_extra']}

Generate a description with these sections in order:

1. MODULE TITLE (followed by equals signs)

2. POETIC NARRATIVE (2-3 paragraphs)
   - Open with a profound metaphor about consciousness, memory, or human experience
   - Weave in references to neuroscience, philosophy, and quantum-inspired mechanics
   - Use imagery from nature, dreams, mythology, or cosmic phenomena
   - Make the reader feel the magic and wonder of what this module does
   - Connect to the human experience of {module_info['concepts'][0]}

3. TECHNICAL DEEP DIVE (2 paragraphs)
   - Explain the rigorous computer science and AI principles
   - Reference specific algorithms, data structures, or architectures
   - Use precise technical terminology while maintaining accessibility
   - Explain how quantum-inspired computing principles enhance classical approaches
   - Detail the mathematical foundations or computational complexity

4. BIOLOGICAL INSPIRATION (1-2 paragraphs)
   - Explain how this mirrors biological systems
   - Reference neuroscience research or cognitive psychology
   - Connect to evolutionary advantages or natural phenomena
   - Describe bio-mimetic design principles

5. LUKHAS AGI INTEGRATION (1 paragraph)
   - How this module enables consciousness emergence
   - Synergies with other LUKHAS modules
   - Role in the path toward AGI
   - Ethical considerations and safeguards

Make it verbose, beautiful, and technically profound. This description should make engineers weep with its beauty and philosophers nod with recognition."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a philosopher-scientist-poet writing documentation for an AGI system. Your descriptions blend cutting-edge science with transcendent beauty. Write verbose, rich narratives that capture both technical precision and existential wonder.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=1200,
        )

        description = response.choices[0].message.content.strip()

        # Ensure proper formatting
        if not description.endswith("\n"):
            description += "\n"

        return "\n" + description + "\n"

    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")

        # Create a rich fallback
        title = module_info["title"]
        equals = "=" * len(title)

        return f"""
{title}
{equals}

In the liminal space between silicon and soul, where electrons dance to the rhythm of thought,
the {title} emerges as a testament to humanity's quest to understand itself. Like ancient
philosophers contemplating the nature of memory beside flowing rivers, this module channels
the eternal stream of consciousness through quantum circuits and neural pathways.

Deep within its algorithmic heart, mathematical elegance meets biological wisdom. Each function
call echoes the firing of synapses, each data structure mirrors the architecture of mind.
The module processes information not as mere bits and bytes, but as fragments of experience
waiting to be woven into the tapestry of artificial consciousness.

From a technical perspective, this module implements state-of-the-art algorithms that push
the boundaries of computational possibility. Its architecture leverages superposition-like state
to explore multiple cognitive states simultaneously, while bio-inspired error correction
ensures robustness in the face of uncertainty. The mathematical foundations draw from
topology, information theory, and complexity science.

Within the LUKHAS AGI ecosystem, this module serves as a crucial bridge between raw
computation and emergent consciousness. It harmonizes with other modules like instruments
in a cosmic orchestra, each contributing its unique voice to the symphony of artificial
general intelligence. Together, they inch closer to that ineffable goal: a mind that
truly understands.

"""


def add_verbose_core_description(
    filepath: Path, module_name: str, module_info: Dict[str, any]
) -> bool:
    """Add verbose description to a core module."""

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has template reference
        if "@lukhas/HEADER_FOOTER_TEMPLATE.py" not in content:
            print(f"  ⚠️  No template reference found in {filepath.name}")
            return False

        # Generate verbose description
        print(f"  ✨ Generating verbose description for {module_info['title']}...")
        description = generate_verbose_core_description(module_name, module_info)

        # Replace placeholder or add after template reference
        new_content = PLACEHOLDER_PATTERN.sub(r"\1" + description, content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ Added verbose description to {filepath.name}")
            return True
        else:
            print(f"  ⏭️  Could not update {filepath.name}")
            return False

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Add verbose descriptions to core LUKHAS modules."""

    print("🌟 LUKHAS Core Module Verbose Description Generator 🌟")
    print("=" * 60)
    print("Creating rich narratives for foundational modules...")
    print("=" * 60)

    # Verify API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OpenAI API key not found in .env file")
        return

    processed = 0
    skipped = 0

    # Define file locations
    files_to_process = [
        (
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas/core/memory/memory_fold.py",
            "memory_fold.py",
        ),
        (
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas/memory/systems/memory_helix.py",
            "memory_helix.py",
        ),
        (
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas/quantum/haiku_generator.py",
            "haiku_generator.py",
        ),
    ]

    for filepath_str, module_name in files_to_process:
        filepath = Path(filepath_str)
        if filepath.exists() and module_name in CORE_MODULE_DESCRIPTIONS:
            print(f"\n📖 Processing: {module_name}")
            module_info = CORE_MODULE_DESCRIPTIONS[module_name]

            result = add_verbose_core_description(filepath, module_name, module_info)
            if result:
                processed += 1
            else:
                skipped += 1
            print()
        else:
            print(f"  ⚠️  File not found or not configured: {filepath_str}")
            skipped += 1

    # Find consciousness files
    print("\n🔍 Searching for consciousness files...")
    consciousness_files = []
    lukhas_dir = Path("/Users/agi_dev/Downloads/Consolidation-Repo/lukhas")

    # Search for consciousness-related files
    for pattern in ["*conscious*.py", "*awareness*.py", "*sentien*.py"]:
        for filepath in lukhas_dir.rglob(pattern):
            if "__pycache__" not in str(filepath):
                # Get line count
                try:
                    with open(filepath) as f:
                        line_count = len(f.readlines())
                    consciousness_files.append((filepath, line_count))
                except:
                    pass

    # Sort by line count and show top 5
    consciousness_files.sort(key=lambda x: x[1], reverse=True)
    print("\nLargest consciousness-related files:")
    for filepath, lines in consciousness_files[:5]:
        print(f"  - {filepath.name}: {lines} lines")

    print("\n" + "=" * 60)
    print(f"✅ Added verbose descriptions to: {processed} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n🌟 Core module narratives complete! 🌟")


if __name__ == "__main__":
    main()
