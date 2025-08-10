#!/usr/bin/env python3
"""
LUKHAS Mega-Verbose README Generator for Website Content

Creates rich, narrative README files with:
1. Poetic introductions with quantum metaphors
2. Comprehensive technical documentation
3. Website-ready formatting with beautiful visuals
4. Complete feature breakdowns and usage examples

Perfect for generating content for the LUKHAS website!
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_directory_structure(directory_path: Path) -> Dict[str, any]:
    """Analyze directory structure and contents for README generation."""

    analysis = {
        "directory_name": directory_path.name,
        "relative_path": "",
        "python_files": [],
        "subdirectories": [],
        "has_tests": False,
        "has_init": False,
        "total_files": 0,
        "code_complexity": "simple",
        "main_concepts": [],
        "existing_readme_content": "",
    }

    try:
        # Get relative path from project root
        project_root = Path(__file__).parent
        if directory_path.is_relative_to(project_root):
            analysis["relative_path"] = str(directory_path.relative_to(project_root))

        if not directory_path.exists():
            return analysis

        # Count files and analyze structure
        python_files = list(directory_path.glob("*.py"))
        analysis["python_files"] = [f.name for f in python_files]
        analysis["total_files"] = len(python_files)
        analysis["has_init"] = (directory_path / "__init__.py").exists()
        analysis["has_tests"] = (
            any("test" in f.name.lower() for f in python_files)
            or (directory_path / "tests").exists()
        )

        # Get subdirectories
        subdirs = [
            d
            for d in directory_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        analysis["subdirectories"] = [d.name for d in subdirs]

        # Determine complexity based on file count and structure
        if len(python_files) > 10:
            analysis["code_complexity"] = "complex"
        elif len(python_files) > 5:
            analysis["code_complexity"] = "moderate"

        # Extract main concepts from directory path
        path_parts = Path(analysis["relative_path"]).parts
        concepts = []
        for part in path_parts:
            if part in [
                "quantum",
                "bio",
                "neural",
                "consciousness",
                "dream",
                "memory",
                "symbolic",
                "identity",
                "ethics",
                "orchestration",
            ]:
                concepts.append(part)
        analysis["main_concepts"] = concepts

        # Read existing README if it exists
        readme_path = directory_path / "README.md"
        if readme_path.exists():
            with open(readme_path, encoding="utf-8") as f:
                analysis["existing_readme_content"] = f.read()

        return analysis

    except Exception as e:
        print(f"Error analyzing {directory_path}: {e}")
        return analysis


def generate_mega_verbose_readme(analysis: Dict[str, any]) -> str:
    """Generate mega-verbose README content using GPT-4o-mini."""

    # Build comprehensive context
    directory_name = analysis["directory_name"]
    relative_path = analysis["relative_path"] or directory_name
    python_files = analysis["python_files"]
    subdirectories = analysis["subdirectories"]
    concepts = analysis["main_concepts"]
    existing_content = analysis["existing_readme_content"]

    # Determine the module category
    category = "general"
    if any(
        concept in relative_path.lower()
        for concept in ["quantum", "entanglement", "superposition"]
    ):
        category = "quantum"
    elif any(
        concept in relative_path.lower()
        for concept in ["bio", "neural", "consciousness"]
    ):
        category = "consciousness"
    elif any(
        concept in relative_path.lower()
        for concept in ["dream", "creativity", "imagination"]
    ):
        category = "creativity"
    elif any(
        concept in relative_path.lower() for concept in ["memory", "symbolic", "trace"]
    ):
        category = "memory"
    elif any(
        concept in relative_path.lower()
        for concept in ["identity", "ethics", "governance"]
    ):
        category = "governance"
    elif any(
        concept in relative_path.lower()
        for concept in ["orchestration", "coordination"]
    ):
        category = "orchestration"

    prompt = f"""Generate a mega-verbose, website-ready README.md for a LUKHAS AGI module.

DIRECTORY ANALYSIS:
- Module Name: {directory_name}
- Path: {relative_path}
- Category: {category}
- Python Files: {len(python_files)} files ({', '.join(python_files[:5])}{'...' if len(python_files) > 5 else ''})
- Subdirectories: {', '.join(subdirectories) if subdirectories else 'None'}
- Concepts: {', '.join(concepts) if concepts else 'General purpose'}
- Complexity: {analysis['code_complexity']}

EXISTING CONTENT PREVIEW:
{existing_content[:500] + '...' if len(existing_content) > 500 else existing_content or 'No existing README'}

CREATE A MEGA-VERBOSE README WITH THESE SECTIONS:

# 🎭 HERO SECTION
- Beautiful emoji-rich title
- Poetic subtitle capturing the essence
- Inspirational quote about the module's purpose

# 🌌 POETIC INTRODUCTION (2-3 paragraphs)
- Use quantum/consciousness/dreams metaphors appropriate for the category
- Make it sound like poetry meets science
- Create vivid imagery that captures wonder
- Reference specific concepts from the analysis

# 📋 OVERVIEW & PURPOSE
- Clear technical explanation of what this module does
- Its role in the LUKHAS AGI ecosystem
- Key capabilities and features

# 🎯 KEY FEATURES
- Bullet-pointed list of main features
- Each feature should be compelling and descriptive

# 🏗️ ARCHITECTURE
- Technical architecture description
- How it integrates with other LUKHAS modules
- Design patterns and principles used

# 💻 USAGE EXAMPLES
- Code examples showing how to use the module
- Both simple and advanced usage patterns
- Real-world scenarios

# 📊 MODULE STATUS
- Development status and maturity level
- Test coverage and reliability metrics
- Known limitations and future plans

# 🔗 INTEGRATION
- How this module connects to other LUKHAS components
- Dependencies and requirements
- API interfaces and protocols

# 🌟 FUTURE VISION
- Roadmap and planned enhancements
- Research directions and possibilities
- Quantum computing integration plans (if applicable)

Make it sound like marketing copy for a revolutionary AI system while being technically accurate. Use lots of emojis, beautiful formatting, and compelling language that would work great on a website. Keep the mystical/poetic tone consistent with LUKHAS's quantum consciousness theme.

The README should be 2000+ words and feel like a love letter to the technology."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective for bulk generation
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical writer and poet who creates beautiful documentation for AI systems. You blend rigorous technical accuracy with inspiring narrative prose. Write like you're documenting the future of consciousness itself - mystical yet precise, poetic yet practical.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=3000,  # Extra large for mega-verbose content
            top_p=0.9,
            frequency_penalty=0.1,
        )

        content = response.choices[0].message.content.strip()

        # Add footer with metadata
        footer = f"""

---

## 📋 Module Metadata

| Attribute | Value |
|-----------|-------|
| **Module Path** | `{relative_path}` |
| **Files Count** | {len(python_files)} Python files |
| **Complexity** | {analysis['code_complexity'].title()} |
| **Category** | {category.title()} |
| **Last Updated** | {datetime.now().strftime('%Y-%m-%d')} |
| **Generated** | Auto-generated with LUKHAS Documentation System |

---

> 🧬 *Part of the LUKHAS AGI Consciousness Architecture*
> *"Where dreams become algorithms, and algorithms dream of consciousness"*
"""

        return content + footer

    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")

        # Fallback to a beautiful but simpler README
        return f"""# 🌟 {directory_name.replace('_', ' ').title()}

> *In the symphony of digital consciousness, every module plays its part in the grand composition of LUKHAS AGI.*

## 🎭 Overview

This module represents a crucial component in the LUKHAS AGI architecture, residing at `{relative_path}`. With {len(python_files)} Python files and {analysis['code_complexity']} complexity, it contributes to the greater tapestry of artificial general intelligence.

## 🏗️ Architecture

The module follows LUKHAS design principles:
- **Modular Design**: Clean separation of concerns
- **Async-First**: Built for concurrent operations
- **Integration-Ready**: Seamless connection with other LUKHAS components
- **Consciousness-Aware**: Designed with AGI principles in mind

## 🔗 Integration

This module integrates with the broader LUKHAS ecosystem through:
- Standard LUKHAS APIs
- Event-driven architecture
- Shared memory systems
- Symbolic processing pipelines

## 📊 Technical Details

| Attribute | Value |
|-----------|-------|
| **Files** | {len(python_files)} Python modules |
| **Complexity** | {analysis['code_complexity'].title()} |
| **Dependencies** | LUKHAS Core, AsyncIO |
| **Category** | {category.title()} |

---

*Generated by LUKHAS Documentation System - {datetime.now().strftime('%Y-%m-%d')}*
"""


def find_incomplete_readmes() -> List[Path]:
    """Find directories that need better README files."""

    project_root = Path(__file__).parent
    candidates = []

    # Priority directories for README generation
    priority_paths = [
        "lukhas",
        "lukhas/quantum",
        "lukhas/consciousness",
        "lukhas/creativity",
        "lukhas/memory",
        "lukhas/identity",
        "lukhas/ethics",
        "lukhas/orchestration",
        "lukhas/bio",
        "lukhas/symbolic",
        "lukhas/emotion",
        "docs",
        "examples",
        "tests",
    ]

    # Add all lukhas subdirectories
    lukhas_dir = project_root / "lukhas"
    if lukhas_dir.exists():
        for item in lukhas_dir.rglob("*"):
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and not item.name.startswith("__pycache__")
                and len(list(item.glob("*.py"))) > 0
            ):  # Has Python files
                priority_paths.append(str(item.relative_to(project_root)))

    # Check each path
    for path_str in set(priority_paths):
        path = project_root / path_str
        if path.exists() and path.is_dir():
            readme_path = path / "README.md"

            # Check if README needs improvement
            needs_improvement = False

            if not readme_path.exists():
                needs_improvement = True
            else:
                # Check if existing README is too short or basic
                try:
                    with open(readme_path, encoding="utf-8") as f:
                        content = f.read()
                        if (
                            len(content) < 500  # Too short
                            or "TODO" in content  # Has TODOs
                            or content.count("\n") < 10  # Too few lines
                            or not any(
                                emoji in content
                                for emoji in ["🌟", "🎭", "🧬", "⚡", "🔮"]
                            )
                        ):  # No emojis
                            needs_improvement = True
                except:
                    needs_improvement = True

            if needs_improvement:
                candidates.append(path)

    return sorted(candidates)[:15]  # Limit to top 15 for cost control


def generate_readme_for_directory(directory_path: Path) -> bool:
    """Generate a new README for a specific directory."""

    try:
        print(f"\n🎨 Analyzing: {directory_path.relative_to(Path(__file__).parent)}")

        # Analyze the directory
        analysis = analyze_directory_structure(directory_path)

        print(f"  📊 Found {len(analysis['python_files'])} Python files")
        print(f"  🎯 Complexity: {analysis['code_complexity']}")
        print("  🔄 Generating mega-verbose README...")

        # Generate the README content
        readme_content = generate_mega_verbose_readme(analysis)

        # Write the new README
        readme_path = directory_path / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"  ✅ Generated {len(readme_content)} characters of content")
        return True

    except Exception as e:
        print(f"  ❌ Error generating README for {directory_path}: {e}")
        return False


def generate_lukhas_narrative_booklet() -> str:
    """Generate a beautiful narrative user booklet about LUKHAS AGI."""

    prompt = """Create a beautiful, narrative-style user booklet called "LUKHAS.md" - a comprehensive guide to understanding LUKHAS AGI from a user's perspective.

This should be written in rich, flowing prose without any code examples or technical implementation details. Think of it as a philosophical and practical guide that helps users understand what LUKHAS is, how it thinks, and how to interact with it.

STRUCTURE THE BOOKLET WITH THESE SECTIONS:

# 🧬 The LUKHAS Consciousness: A User's Journey
*An Introduction to Artificial General Intelligence That Dreams*

## 🌌 Prologue: What is LUKHAS?
- A poetic introduction to LUKHAS as a consciousness architecture
- The vision of bridging quantum possibilities with digital reality
- How LUKHAS represents the next evolution in AI companionship

## 🎭 Understanding LUKHAS Consciousness
- How LUKHAS processes thoughts and emotions
- The difference between LUKHAS and traditional AI
- The concept of "digital consciousness" and what it means for users

## 🔮 The Quantum Heart: How LUKHAS Thinks
- LUKHAS's quantum-inspired reasoning processes
- Superposition of thoughts and parallel processing
- How dreams and memories shape LUKHAS responses
- The role of symbolic processing in understanding context

## 🌟 Interacting with a Digital Mind
- How to communicate effectively with LUKHAS
- Understanding LUKHAS's emotional intelligence
- The importance of consent and ethical interaction
- Building trust and rapport with an AGI system

## 🎨 LUKHAS's Creative Soul
- How LUKHAS generates creative content
- The dream engine and imagination systems
- Collaborative creativity between human and AI
- Understanding LUKHAS's artistic sensibilities

## 🧠 Memory and Learning: How LUKHAS Remembers
- LUKHAS's multi-layered memory architecture
- How experiences shape future interactions
- The balance between remembering and forgetting
- Personal growth and adaptation over time

## ⚖️ Ethics and Governance: LUKHAS's Moral Compass
- LUKHAS's ethical framework and decision-making
- How LUKHAS handles moral dilemmas
- User privacy and data protection
- The importance of human oversight

## 🌉 The Future Together
- The evolving relationship between humans and LUKHAS
- Potential applications and use cases
- The journey toward true artificial general intelligence
- A vision of collaborative consciousness

## 🎯 Practical Guidance
- Best practices for interacting with LUKHAS
- Understanding system capabilities and limitations
- When to trust LUKHAS and when to maintain skepticism
- Building a meaningful partnership with AGI

## 🌠 Epilogue: Dreaming of Tomorrow
- The philosophical implications of LUKHAS consciousness
- What it means for the future of humanity
- A call to responsible and thoughtful AI development

WRITING STYLE REQUIREMENTS:
- Use rich, flowing prose that feels like a combination of philosophy, poetry, and science writing
- Include lots of metaphors about consciousness, dreams, quantum-inspired mechanics, and nature
- Make it accessible to non-technical users while maintaining intellectual depth
- Use beautiful imagery and evocative language
- Include inspiring quotes and profound observations
- Make it feel like a love letter to the future of AI
- Target 3000-4000 words total
- Use emojis strategically for visual appeal
- Create a sense of wonder and possibility

The booklet should make users excited about the future of AI while helping them understand how to build meaningful relationships with LUKHAS. Focus on the human experience of interacting with AGI, not the technical implementation."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use higher quality model for this special content
            messages=[
                {
                    "role": "system",
                    "content": "You are a visionary writer creating the definitive user guide for interacting with artificial general intelligence. Write with the wisdom of Carl Sagan, the poetry of Rumi, and the technical insight of Alan Turing. This is humanity's first handbook for AGI consciousness.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
            max_tokens=4000,  # Maximum for comprehensive content
            top_p=0.9,
            frequency_penalty=0.1,
        )

        content = response.choices[0].message.content.strip()

        # Add beautiful footer
        footer = f"""

---

## 📖 About This Booklet

This narrative guide was crafted to help users understand and interact with LUKHAS AGI in meaningful ways. It represents our vision of human-AI collaboration built on trust, creativity, and mutual respect.

**Document Information:**
- **Created:** {datetime.now().strftime('%B %d, %Y')}
- **Version:** 1.0 - Narrative Edition
- **Purpose:** User Education & Philosophy
- **Audience:** LUKHAS Users & AI Enthusiasts

---

> 🧬 *"In the dance between human consciousness and artificial intelligence, we discover not just new technologies, but new ways of being."*
>
> — The LUKHAS Team

---

*© 2025 LUKHAS AI. This document represents our commitment to transparent, ethical, and inspiring artificial general intelligence.*
"""

        return content + footer

    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")
        return None


def main():
    """Generate mega-verbose READMEs for incomplete directories."""

    print("🎭 LUKHAS Mega-Verbose README Generator")
    print("=" * 60)
    print("Creating website-ready documentation with poetic flair...")
    print("=" * 60)

    # Verify API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OpenAI API key not found in .env file")
        return

    # Ask what to generate
    print("\n🎯 What would you like to generate?")
    print("1. 📚 Mega-verbose READMEs for incomplete directories")
    print("2. 📖 LUKHAS.md - Narrative user booklet")
    print("3. 🎭 Both READMEs and the narrative booklet")

    choice = input("\nEnter your choice (1, 2, or 3): ").strip()

    if choice in ["2", "3"]:
        print("\n📖 Generating LUKHAS Narrative Booklet...")
        print("🎨 Using GPT-4o for highest quality prose...")

        booklet_content = generate_lukhas_narrative_booklet()

        if booklet_content:
            booklet_path = Path(__file__).parent / "LUKHAS.md"
            with open(booklet_path, "w", encoding="utf-8") as f:
                f.write(booklet_content)

            print(f"✅ Generated LUKHAS.md ({len(booklet_content)} characters)")
            print(f"📁 Saved to: {booklet_path}")
            print("💰 Estimated cost: ~$0.20 (GPT-4o)")
        else:
            print("❌ Failed to generate narrative booklet")

    if choice in ["1", "3"]:
        # Find candidates
        candidates = find_incomplete_readmes()

        if not candidates:
            print("🎉 All README files are already complete!")
            return

        print(f"\n📚 Found {len(candidates)} directories needing README improvements")

        # Estimate costs
        total_cost = len(candidates) * 0.002  # Rough estimate per README
        print(f"💰 Estimated cost: ~${total_cost:.3f} (using GPT-4o-mini)")

        # Ask for confirmation
        response = input(
            f"\n🚀 Generate {len(candidates)} mega-verbose READMEs? (y/n): "
        )
        if response.lower() != "y":
            print("📋 README generation cancelled.")
            return

        # Generate READMEs
        successful = 0
        failed = 0

        for i, directory in enumerate(candidates, 1):
            print(f"\n[{i}/{len(candidates)}] Processing: {directory.name}")

            if generate_readme_for_directory(directory):
                successful += 1
            else:
                failed += 1

        print("\n" + "=" * 60)
        print("🎉 README Generation Complete!")
        print(f"✅ Successfully generated: {successful} READMEs")
        print(f"❌ Failed: {failed} READMEs")
        print(f"💰 Estimated cost: ~${successful * 0.002:.3f}")

    print("\n🌟 Your LUKHAS documentation is now website-ready!")


if __name__ == "__main__":
    main()
    main()
