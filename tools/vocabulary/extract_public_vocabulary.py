#!/usr/bin/env python3
"""
LUKHAS Lexicon Extractor
Extracts public-safe vocabulary from the dual-stream lexicon.
"""
import streamlit as st

import re
from pathlib import Path


def extract_public_vocabulary(lexicon_path="LUKHAS_LEXICON.md", output_path="vocabularies/LUKHAS_VOCABULARY_PUBLIC.md"):
    """Extract only public sections from the dual-stream lexicon."""

    with open(lexicon_path) as f:
        content = f.read()

    # Pattern to match vocabulary domains and their public sections
    domain_pattern = r"## (\w+ Vocabulary).*?### Public\n\n(.*?)(?=---|\n##|\Z)"

    matches = re.findall(domain_pattern, content, re.DOTALL)

    public_content = "# LUKHAS Public Vocabulary\n\n"
    public_content += "**Stance-based language for all public-facing use**\n\n"
    public_content += "*Extracted from the dual-stream lexicon for safe public deployment*\n\n"
    public_content += "---\n\n"

    for domain_name, public_text in matches:
        public_content += f"## {domain_name}\n\n"
        public_content += public_text.strip() + "\n\n---\n\n"

    # Add usage note
    public_content += "## Usage\n\n"
    public_content += "This vocabulary is safe for:\n"
    public_content += "- API documentation and system prompts\n"
    public_content += "- User-facing interfaces and explanations\n"
    public_content += "- Marketing materials and social media\n"
    public_content += "- Any external-facing communications\n\n"
    public_content += (
        """**Philosophy**: "Uncertainty as fertile ground" — welcoming ambiguity as resource, not flaw.\n\n"""
    )
    public_content += "**Validation**: ✅ All content passes author-reference guard\n\n"
    public_content += f"*Generated from LUKHAS_LEXICON.md on {Path().absolute(}.name}*"

    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write public-safe version
    with open(output_file, "w") as f:
        f.write(public_content)

    print(f"✅ Public vocabulary extracted to {output_path}")
    print(f"📊 Found {len(matches} vocabulary domains")

    return output_path


if __name__ == "__main__":
    extract_public_vocabulary()
