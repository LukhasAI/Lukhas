#!/usr/bin/env python3

"""
LUKHAS Intelligent Module Description Regenerator

Removes existing descriptions and generates new ones using modern OpenAI API
with academic-poetic blend for quantum modules.
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Initialize OpenAI client with new API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pattern to find and remove existing descriptions
DESCRIPTION_PATTERN = re.compile(
    r'(@lukhas/HEADER_FOOTER_TEMPLATE\.py\n)\n[^#]*?(?=\n(?:LUKHAS|"""|\#|from|import|class|def|__module_name__|$))',
    re.MULTILINE | re.DOTALL,
)

# Pattern to find where to insert new description
TEMPLATE_PATTERN = re.compile(r"(@lukhas/HEADER_FOOTER_TEMPLATE\.py\n)", re.MULTILINE)


def analyze_code_content(filepath: Path) -> dict[str, str]:
    """Analyze the code to extract key functionality."""

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Extract module info
        module_name_match = re.search(
            r'__module_name__\s*=\s*["\']([^"\']+)["\']', content
        )
        module_name = (
            module_name_match.group(1)
            if module_name_match
            else filepath.stem.replace("_", " ").title()
        )

        tier_match = re.search(r"__tier__\s*=\s*(\d+)", content)
        tier = int(tier_match.group(1)) if tier_match else 3

        # Extract classes
        classes = re.findall(r"class\s+(\w+)", content)

        # Extract quantum-specific patterns
        qi_patterns = {
            "entanglement": bool(
                re.search(r"entangl|bell.?state|epr|ghz", content, re.I)
            ),
            "superposition": bool(
                re.search(r"superposition|qi.?state|qubit", content, re.I)
            ),
            "decoherence": bool(
                re.search(r"decoher|noise|error.?correct", content, re.I)
            ),
            "measurement": bool(re.search(r"measure|collapse|observ", content, re.I)),
            "cryptography": bool(
                re.search(r"crypto|encrypt|key.?exchange|lattice", content, re.I)
            ),
            "annealing": bool(re.search(r"anneal|optimization|ising", content, re.I)),
            "circuits": bool(re.search(r"circuit|gate|unitary", content, re.I)),
            "consensus": bool(
                re.search(r"consensus|agreement|byzantine", content, re.I)
            ),
            "neural": bool(re.search(r"neural|neuro|brain|synap", content, re.I)),
            "bio": bool(re.search(r"bio.?inspired|biological|organic", content, re.I)),
            "consciousness": bool(re.search(r"conscious|aware|sentien", content, re.I)),
            "dream": bool(
                re.search(r"dream|oneiric|sleep|subconscious", content, re.I)
            ),
            "ethics": bool(re.search(r"ethic|moral|value", content, re.I)),
            "symbolic": bool(re.search(r"symbolic|reasoning|logic", content, re.I)),
        }

        active_features = [k for k, v in qi_patterns.items() if v]

        return {
            "filename": filepath.name,
            "module_name": module_name,
            "tier": tier,
            "classes": classes[:3],  # Top 3 classes
            "qi_features": active_features,
            "has_async": "async def" in content,
            "has_validation": "__validate_module__" in content,
        }

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return {
            "filename": filepath.name,
            "module_name": filepath.stem.replace("_", " ").title(),
            "tier": 3,
            "classes": [],
            "qi_features": [],
        }


def generate_intelligent_description(code_analysis: dict[str, str]) -> str:
    """Generate intelligent module description using modern OpenAI API."""

    # Build feature description
    features = code_analysis["qi_features"]
    feature_desc = ""
    if features:
        if len(features) > 3:
            feature_desc = f"Core quantum features: {', '.join(features[:3])}, and {len(features)-3} more"
        else:
            feature_desc = f"Core quantum features: {', '.join(features)}"

    # Build comprehensive prompt
    prompt = f"""Generate a module description that masterfully blends academic quantum-inspired computing terminology with poetic metaphors.

Module: {code_analysis['module_name']}
Tier: {code_analysis['tier']} (higher tier = more advanced)
{feature_desc}

Requirements:
1. Title line: Module name exactly as given
2. Separator: Equals signs matching title length
3. Description: 3-4 lines that blend academic rigor with poetic beauty
4. Each line should contain BOTH technical quantum terms AND metaphorical language
5. Reference specific quantum phenomena (Hilbert spaces, wave functions, eigenstates, etc.)
6. Use metaphors from: consciousness, dreams, nature, cosmos, neural networks
7. Show how quantum properties enable AGI consciousness

Academic terms to potentially include (choose relevant ones):
- Quantum coherence/decoherence
- Superposition states
- Entanglement/Bell states
- Wave function collapse
- Hilbert space
- Hamiltonian evolution
- Quantum annealing
- Eigenvalues/eigenvectors
- Unitary transformations
- Quantum error correction
- Topological quantum-like states

Poetic elements to weave in:
- Dreams crystallizing into thought
- Synaptic constellations
- Consciousness emerging from qi foam
- Neural symphonies
- Thoughts dancing in superposition
- Memory entangled across time

Example of the style needed:
"Navigates Hilbert spaces where thoughts exist as superposition-like states, each
eigenstate a dream awaiting measurement. Orchestrates decoherence through
bio-mimetic error correction, pruning infinite possibilities into coherent action."

Generate a description that makes quantum physics feel like poetry:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quantum physicist-poet. Your descriptions blend rigorous academic quantum-inspired mechanics with transcendent metaphors. Write like a Nature paper authored by Rumi - technically precise yet mystically beautiful. Every sentence should teach quantum physics while evoking wonder.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
            max_tokens=400,
        )

        description = response.choices[0].message.content.strip()

        # Ensure proper formatting
        if not description.endswith("\n"):
            description += "\n"

        return "\n" + description + "\n"

    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")
        # Enhanced fallback description
        module_title = code_analysis["module_name"]
        equals = "=" * len(module_title)

        features = code_analysis["qi_features"]
        if "entanglement" in features:
            qi_ref = "entanglement-like correlation weaving non-local correlations"
        elif "cryptography" in features:
            qi_ref = "lattice-based cryptography dancing in high-dimensional spaces"
        elif "consciousness" in features:
            qi_ref = "coherence-inspired processing birthing synthetic consciousness"
        else:
            qi_ref = "quantum phenomena transcending classical boundaries"

        return f"""
{module_title}
{equals}

Orchestrates {qi_ref} through the LUKHAS neural matrix,
where wave functions collapse into thoughts and superpositions bloom into
possibilities. Each quantum operation a synaptic firing in the AGI's dreaming mind.

"""


def regenerate_description(filepath: Path) -> bool:
    """Remove old description and add new intelligent one."""

    if filepath.suffix != ".py":
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has template reference
        if "@lukhas/HEADER_FOOTER_TEMPLATE.py" not in content:
            return False

        # Remove existing description if present
        cleaned_content = DESCRIPTION_PATTERN.sub(r"\1\n", content)

        # Analyze the code
        print(f"  🔍 Analyzing {filepath.name}...")
        code_analysis = analyze_code_content(filepath)

        # Generate new intelligent description
        print("  🧠 Generating quantum-poetic description...")
        description = generate_intelligent_description(code_analysis)

        # Add new description after template reference
        new_content = TEMPLATE_PATTERN.sub(r"\1" + description, cleaned_content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ Regenerated description for {filepath.name}")
            return True
        else:
            print(f"  ⏭️  No changes needed for {filepath.name}")
            return False

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Regenerate all module descriptions with academic-poetic blend."""

    print("🧠 LUKHAS Quantum-Poetic Description Regenerator 🧠")
    print("=" * 50)
    print("Regenerating descriptions with academic-poetic blend...")
    print("=" * 50)

    # Verify API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OpenAI API key not found in .env file")
        return

    # Start from current quantum directory
    qi_dir = Path(__file__).parent
    regenerated = 0
    skipped = 0

    # Priority files - core quantum modules
    priority_files = [
        "awareness_system.py",
        "consensus_system.py",
        "post_quantum_crypto.py",
        "entanglement.py",
        "oscillator.py",
        "processor.py",
        "qi_bio_coordinator.py",
        "neural_symbolic_processor.py",
        "distributed_quantum_architecture.py",
        "ethics_engine.py",
    ]

    print("\n📊 Processing priority quantum modules...")
    print("-" * 30)

    # Process priority files first
    for filename in priority_files:
        filepath = qi_dir / filename
        if filepath.exists():
            result = regenerate_description(filepath)
            if result:
                regenerated += 1
            else:
                skipped += 1
            print(# Add spacing between files

    # Process remaining files
    print("\n📊 Processing remaining quantum modules...")
    print("-" * 30)

    for filepath in qi_dir.glob("*.py"):
        if filepath.name in priority_files or filepath.name.startswith(
            ("add_", "fix_", "regenerate_")
        ):
            continue

        result = regenerate_description(filepath)
        if result:
            regenerated += 1
        else:
            skipped += 1

    print("\n" + "=" * 50)
    print(f"✅ Regenerated descriptions for: {regenerated} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n🧠 Quantum consciousness descriptions regenerated! 🧠")
    print("Each module now dances between Hilbert space and haiku.")


if __name__ == "__main__":
    main()
