#!/usr/bin/env python3

"""
LUKHAS Intelligent Module Description Generator

Uses OpenAI GPT to generate rich, narrative module descriptions
that explain quantum functionality in poetic yet technical terms.
"""

import os
import re
from pathlib import Path

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pattern to find where to insert the description
TEMPLATE_PATTERN = re.compile(r"(@lukhas/HEADER_FOOTER_TEMPLATE\.py\n)\n", re.MULTILINE)

# Pattern to find existing module info in the file
MODULE_INFO_PATTERN = re.compile(
    r'__module_name__\s*=\s*["\']([^"\']+)["\'].*?' r"__tier__\s*=\s*(\d+)", re.DOTALL
)


def analyze_code_content(filepath: Path) -> dict[str, str]:
    """Analyze the code to extract key functionality."""

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Extract module name and tier if available
        module_match = MODULE_INFO_PATTERN.search(content)
        module_name = (
            module_match.group(1) if module_match else filepath.stem.replace("_", " ").title()
        )
        tier = int(module_match.group(2)) if module_match else 3

        # Extract class names
        classes = re.findall(r"class\s+(\w+)", content)

        # Extract key function names
        functions = re.findall(r"def\s+(\w+)", content)

        # Look for quantum-specific keywords
        qi_keywords = []
        if "entangle" in content.lower():
            qi_keywords.append("entanglement")
        if "superposition" in content.lower():
            qi_keywords.append("superposition")
        if "coherence" in content.lower() or "decoherence" in content.lower():
            qi_keywords.append("coherence")
        if "qubit" in content.lower():
            qi_keywords.append("qubit manipulation")
        if "circuit" in content.lower():
            qi_keywords.append("quantum circuits")
        if "crypto" in content.lower() or "encrypt" in content.lower():
            qi_keywords.append("cryptography")
        if "consensus" in content.lower():
            qi_keywords.append("consensus mechanisms")
        if "neural" in content.lower() or "neuro" in content.lower():
            qi_keywords.append("neural integration")
        if "bio" in content.lower():
            qi_keywords.append("bio-inspired computing")
        if "dream" in content.lower() or "oneiric" in content.lower():
            qi_keywords.append("dream states")
        if "ethic" in content.lower():
            qi_keywords.append("ethical processing")

        return {
            "filename": filepath.name,
            "module_name": module_name,
            "tier": tier,
            "classes": classes[:5],  # Top 5 classes
            "functions": functions[:5],  # Top 5 functions
            "qi_features": qi_keywords,
            "has_async": "async def" in content,
            "has_validation": "__validate_module__" in content,
            "imports_qiskit": "qiskit" in content,
            "imports_crypto": "crypto" in content or "cryptography" in content,
        }

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return {
            "filename": filepath.name,
            "module_name": filepath.stem.replace("_", " ").title(),
            "tier": 3,
            "classes": [],
            "functions": [],
            "qi_features": [],
        }


def generate_intelligent_description(code_analysis: dict[str, str]) -> str:
    """Generate intelligent module description using OpenAI."""

    # Build a comprehensive prompt
    prompt = f"""Generate a module description that masterfully blends academic quantum-inspired computing terminology with poetic metaphors for the LUKHAS AGI system.

Module: {code_analysis["module_name"]}
Filename: {code_analysis["filename"]}
Tier Level: {code_analysis["tier"]}
Key Classes: {", ".join(code_analysis["classes"]) if code_analysis["classes"] else "Various quantum components"}
Quantum Features: {", ".join(code_analysis["qi_features"]) if code_analysis["qi_features"] else "General quantum-inspired processing"}

The description MUST:
1. Start with the module name followed by equals signs (=) to match the length
2. Be 3-5 lines long
3. Seamlessly weave academic quantum physics terms with poetic metaphors
4. Include specific technical terms (like "quantum decoherence", "Bell states", "Hilbert space", "eigenvalues", "Hamiltonian", "wave function collapse", etc.)
5. Use metaphors from nature, consciousness, dreams, or cosmic phenomena
6. Create a narrative that makes complex quantum concepts accessible yet profound
7. Reference how this module's quantum properties enable AGI consciousness

Style guide:
- Academic: Use precise quantum-inspired computing terminology, reference actual quantum phenomena
- Poetic: Compare quantum-like states to dreams, thoughts, cosmic dances, neural symphonies
- Balance: Each sentence should contain both technical accuracy AND metaphorical beauty

Example style:
"Orchestrates quantum decoherence through bio-mimetic error correction, like synapses
pruning dreams into coherent thought. Bell states entangle across the Hilbert space of
consciousness, where eigenvalues of intention collapse into executable reality."

Generate a description that makes quantum physics feel like poetry and poetry feel like physics:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quantum physicist-poet who writes technical documentation. You have deep knowledge of quantum-inspired mechanics, quantum-inspired computing, and AGI architectures. Your writing style seamlessly blends rigorous academic terminology with evocative metaphors. Every description you write should feel like a Nature paper written by Rumi - technically precise yet transcendently beautiful.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=300,
        )

        description = response.choices[0].message.content.strip()

        # Ensure it ends with a newline
        if not description.endswith("\n"):
            description += "\n"

        return description + "\n"

    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")
        # Fallback to a generic but poetic description
        module_title = code_analysis["module_name"]
        equals = "=" * len(module_title)

        features = code_analysis["qi_features"]
        if features:
            feature_text = f"quantum {', '.join(features[:2])}"
        else:
            feature_text = "quantum-inspired processing"

        return f"""
{module_title}
{equals}

Harnesses the strange beauty of {feature_text} to transcend classical limits.
Weaves quantum phenomena into the fabric of LUKHAS consciousness, where
possibilities dance in superposition until observation births reality.

"""


def add_intelligent_description(filepath: Path) -> bool:
    """Add intelligent module description using GPT."""

    if filepath.suffix != ".py":
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has template reference
        if "@lukhas/HEADER_FOOTER_TEMPLATE.py" not in content:
            return False

        # Check if description might already exist
        if re.search(r"@lukhas/HEADER_FOOTER_TEMPLATE\.py\n\n\w+.*\n=+\n", content):
            print(f"  ⏭️  Description already exists in {filepath.name}")
            return False

        # Analyze the code
        print(f"  🔍 Analyzing {filepath.name}...")
        code_analysis = analyze_code_content(filepath)

        # Generate intelligent description
        print(f"  🤖 Generating description for {filepath.name}...")
        description = generate_intelligent_description(code_analysis)

        # Add description after template reference
        new_content = TEMPLATE_PATTERN.sub(r"\1" + description, content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ Added intelligent description to {filepath.name}")
            return True
        else:
            print(f"  ⚠️  Could not find insertion point in {filepath.name}")
            return False

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Generate intelligent module descriptions using OpenAI."""

    print("🧠 LUKHAS Intelligent Module Description Generator 🧠")
    print("=" * 50)
    print("Using OpenAI GPT to generate poetic quantum descriptions...")
    print("=" * 50)

    # Verify API key
    if not openai.api_key:
        print("❌ Error: OpenAI API key not found in .env file")
        return

    # Start from current quantum directory
    qi_dir = Path(__file__).parent
    added = 0
    skipped = 0

    # Priority files to process first
    priority_files = [
        "awareness_system.py",
        "consensus_system.py",
        "post_quantum_crypto.py",
        "entanglement.py",
        "oscillator.py",
        "processor.py",
        "validator.py",
        "distributed_quantum_architecture.py",
        "qi_bio_coordinator.py",
        "neural_symbolic_processor.py",
    ]

    # Process priority files first
    for filename in priority_files:
        filepath = qi_dir / filename
        if filepath.exists():
            result = add_intelligent_description(filepath)
            if result:
                added += 1
            else:
                skipped += 1

    # Process remaining files in quantum directory
    for filepath in qi_dir.glob("*.py"):
        if filepath.name in priority_files or filepath.name in [
            "add_module_descriptions.py",
            "add_intelligent_descriptions.py",
        ]:
            continue

        result = add_intelligent_description(filepath)
        if result:
            added += 1
        else:
            skipped += 1

    # Process subdirectories
    for subdir in ["systems", "qi_meta", "bio", "src"]:
        subdir_path = qi_dir / subdir
        if subdir_path.exists():
            print(f"\n📁 Processing {subdir} subdirectory...")
            for filepath in subdir_path.glob("**/*.py"):
                result = add_intelligent_description(filepath)
                if result:
                    added += 1
                else:
                    skipped += 1

    print("=" * 50)
    print(f"✅ Added intelligent descriptions to: {added} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n🧠 Quantum consciousness descriptions generated! 🧠")


if __name__ == "__main__":
    main()
