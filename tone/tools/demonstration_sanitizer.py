#!/usr/bin/env python3
"""
Demonstration: Author Reference Sanitizer

Shows how to use the minimal sanitizer to convert author references to stance terms.
"""

import sys
from pathlib import Path

# Add the path to import the sanitizer
sys.path.insert(0, str(Path(__file__).parent))
from author_reference_sanitizer_minimal import sanitize


def demonstrate_sanitization():
    """Demonstrate the sanitizer with various examples"""

    examples = [
        "This approach echoes Keats' emphasis on beauty and truth.",
        "Like Einstein, we seek elegant simplicity in complex systems.",
        "Following Freud's insights into the unconscious mind.",
        "The Zen tradition teaches us about mindful awareness.",
        "A Shakespearean depth of character development.",
        "Nietzschean themes of self-overcoming and authenticity.",
        "Jung's concept of the collective unconscious.",
        "Darwin's evolutionary perspective on adaptation.",
        "Thoreau's connection to nature and simplicity.",
        "Tesla's visionary approach to innovation.",
    ]

    print("🔄 Author Reference Sanitizer Demonstration")
    print("=" * 50)
    print()

    for i, example in enumerate(examples, 1):
        sanitized = sanitize(example)
        if sanitized != example:
            print(f"{i:2}. Original:  {example}")
            print(f"    Sanitized: {sanitized}")
            print()
        else:
            print(f"{i:2}. No change: {example}")
            print()

    print("✅ Demonstration complete!")
    print()
    print(
        "Usage: echo 'Text with Keats references' | python tone/tools/author_reference_sanitizer_minimal.py"
    )


if __name__ == "__main__":
    demonstrate_sanitization()
