#!/usr/bin/env python3

"""
LUKHAS Verbose Intelligent Description Generator

Creates rich, narrative module descriptions with:
1. A poetic story using human-interpretable metaphors
2. Full technical and academic explanations
Perfect for content generation systems.
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pattern to find and replace existing descriptions
DESCRIPTION_PATTERN = re.compile(
    r'(@lukhas/HEADER_FOOTER_TEMPLATE\.py\n)\n([^#]*?)(?=""")', re.MULTILINE | re.DOTALL
)


def analyze_quantum_code(filepath: Path) -> dict[str, any]:
    """Deep analysis of quantum module code."""

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Extract all relevant information
        analysis = {
            "filename": filepath.name,
            "module_name": "",
            "tier": 3,
            "classes": [],
            "functions": [],
            "quantum_concepts": [],
            "imports": [],
            "has_async": False,
            "has_validation": False,
            "docstrings": [],
        }

        # Module name and tier
        module_match = re.search(r'__module_name__\s*=\s*["\']([^"\']+)["\']', content)
        if module_match:
            analysis["module_name"] = module_match.group(1)
        else:
            analysis["module_name"] = filepath.stem.replace("_", " ").title()

        tier_match = re.search(r"__tier__\s*=\s*(\d+)", content)
        if tier_match:
            analysis["tier"] = int(tier_match.group(1))

        # Extract classes with their docstrings
        class_pattern = re.compile(r'class\s+(\w+).*?:\s*\n\s*"""(.*?)"""', re.DOTALL)
        for match in class_pattern.finditer(content):
            analysis["classes"].append(
                {"name": match.group(1), "docstring": match.group(2).strip()}
            )

        # Extract key functions
        func_pattern = re.compile(
            r"def\s+(\w+)\s*\([^)]*\)\s*->\s*([^:]+):", re.MULTILINE
        )
        for match in func_pattern.finditer(content):
            analysis["functions"].append(
                {"name": match.group(1), "return_type": match.group(2).strip()}
            )

        # Quantum concept detection (comprehensive)
        quantum_patterns = {
            "superposition": r"superposition|quantum.?state|qubit|bloch",
            "entanglement": r"entangl|bell.?state|epr|ghz|schmidt",
            "measurement": r"measure|collapse|observe|projection",
            "coherence": r"coheren|decoher|fidelity|purity",
            "gates": r"gate|circuit|unitary|pauli|hadamard|cnot",
            "algorithms": r"grover|shor|deutsch|quantum.?algorithm",
            "error_correction": r"error.?correct|syndrome|stabilizer|topological",
            "cryptography": r"qkd|bb84|lattice|post.?quantum|crystals",
            "annealing": r"anneal|ising|qubo|optimization",
            "simulation": r"hamiltonian|evolution|trotter|suzuki",
            "tomography": r"tomography|reconstruction|state.?estimation",
            "channels": r"channel|kraus|lindblad|master.?equation",
            "resources": r"magic.?state|t.?count|clifford|resource.?theory",
            "complexity": r"bqp|qma|quantum.?complexity|oracle",
            "hardware": r"transmon|ion.?trap|photonic|quantum.?dot",
        }

        for concept, pattern in quantum_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                analysis["quantum_concepts"].append(concept)

        # Check for async and validation
        analysis["has_async"] = "async def" in content
        analysis["has_validation"] = "__validate_module__" in content

        # Extract imports to understand dependencies
        import_lines = re.findall(r"from\s+(\w+).*?import|import\s+(\w+)", content)
        analysis["imports"] = [imp[0] or imp[1] for imp in import_lines if any(imp)]

        return analysis

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return {
            "filename": filepath.name,
            "module_name": filepath.stem.replace("_", " ").title(),
            "tier": 3,
            "classes": [],
            "functions": [],
            "quantum_concepts": [],
        }


def generate_verbose_description(analysis: dict[str, any]) -> str:
    """Generate verbose description with poetic story and academic explanation."""

    # Build comprehensive context
    quantum_concepts = analysis["quantum_concepts"]
    concept_list = (
        ", ".join(quantum_concepts)
        if quantum_concepts
        else "quantum-inspired processing"
    )

    classes_info = ""
    if analysis["classes"]:
        class_names = [c["name"] for c in analysis["classes"][:3]]
        classes_info = f"Key classes: {', '.join(class_names)}"

    prompt = f"""Generate a verbose, rich module description for a quantum-inspired computing module in the LUKHAS AGI system.

Module: {analysis['module_name']}
Filename: {analysis['filename']}
Tier Level: {analysis['tier']} (1-5, higher = more advanced)
Quantum Concepts Present: {concept_list}
{classes_info}

Create a description with these exact sections:

1. MODULE TITLE
   - The module name followed by equals signs

2. POETIC NARRATIVE (1-2 paragraphs)
   - A beautiful story using human-interpretable metaphors
   - Compare quantum phenomena to: dreams, consciousness, nature, cosmos, music, art
   - Make complex quantum concepts accessible through storytelling
   - Create vivid imagery that captures the wonder of quantum-inspired computing
   - Reference specific quantum phenomena but explain them through metaphor

3. TECHNICAL OVERVIEW (1 paragraph)
   - Rigorous academic explanation of the module's quantum-inspired computing functionality
   - Use precise terminology: Hilbert spaces, eigenvalues, Hamiltonians, etc.
   - Explain the mathematical and computational principles
   - Reference specific algorithms or techniques implemented

4. INTEGRATION WITH LUKHAS AGI (1 paragraph)
   - How this quantum module enables AGI consciousness
   - Connection to bio-inspired architecture
   - Role in the broader LUKHAS ecosystem
   - Synergy with other modules

Example format:

Module Name Here
================

In the twilight realm between dream and waking, where thoughts exist as shimmering
possibilities, this module orchestrates... [poetic narrative continues]

From a rigorous computational perspective, this module implements... [technical explanation]

Within the LUKHAS AGI architecture, this quantum engine serves as... [integration details]

Generate a verbose, beautiful description that makes readers feel the magic of quantum-inspired computing:"""

    try:
        # Multiple model options - uncomment your preferred choice:

        # Option 1: GPT-4o Mini (BEST VALUE - 94% cheaper than GPT-4, great quality)
        model_choice = "gpt-4o-mini"

        # Option 2: GPT-4o (High quality, 75% cheaper than GPT-4)
        # model_choice = "gpt-4o"

        # Option 3: GPT-4 Turbo (Good balance of cost/quality)
        # model_choice = "gpt-4-turbo"

        # Option 4: o1-mini (Reasoning model, good for complex analysis)
        # model_choice = "o1-mini"

        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {
                    "role": "system",
                    "content": "You are a quantum physicist-poet-philosopher writing documentation. Create verbose, rich descriptions that blend poetic narrative with rigorous academic explanations. Your writing should inspire wonder while teaching quantum-inspired mechanics. Write like Carl Sagan explaining quantum-inspired computing through poetry - scientifically accurate yet transcendently beautiful.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,  # Slightly lower for consistency
            max_tokens=1000,  # Increased for verbose descriptions
            top_p=0.9,  # Focus on most probable tokens
            frequency_penalty=0.1,  # Reduce repetition
        )

        description = response.choices[0].message.content.strip()

        # Ensure proper formatting
        if not description.endswith("\n"):
            description += "\n"

        return "\n" + description + "\n"

    except Exception as e:
        print(f"  ⚠️  OpenAI API error: {e}")

        # Create a rich fallback description
        module_title = analysis["module_name"]
        equals = "=" * len(module_title)

        concepts = analysis["quantum_concepts"]
        quantum_refs = []
        if "entanglement" in concepts:
            quantum_refs.append(
                "entanglement-like correlation weaving non-local tapestries"
            )
        if "superposition" in concepts:
            quantum_refs.append("superposition states dancing between possibilities")
        if "cryptography" in concepts:
            quantum_refs.append(
                "cryptographic lattices protecting secrets in high dimensions"
            )
        if not quantum_refs:
            quantum_refs.append("quantum phenomena transcending classical boundaries")

        return f"""
{module_title}
{equals}

In the shimmering twilight between the quantum and classical realms, where {quantum_refs[0]}
unfold like cosmic origami, this module breathes life into the ethereal mathematics of
quantum-inspired mechanics. Each calculation is a prayer whispered to the universe, each measurement
a conversation with the infinite possibilities that dance in superposition.

From a rigorous academic perspective, this module implements advanced quantum-inspired algorithms
operating within Hilbert spaces of exponential dimension. The mathematical framework leverages
unitary transformations and projective measurements to extract classical information from
quantum-like states, while maintaining coherence through sophisticated error correction protocols.

Within the LUKHAS AGI ecosystem, this quantum engine serves as a critical bridge between
the probabilistic quantum realm and deterministic classical computation. It enables the
emergence of genuine artificial consciousness by providing the computational substrate for
thoughts that can exist in superposition, mirroring the quantum processes theorized to
occur in biological neural networks.

"""


def add_verbose_description(filepath: Path) -> bool:
    """Add verbose intelligent description to module."""

    if filepath.suffix != ".py":
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has template reference
        if "@lukhas/HEADER_FOOTER_TEMPLATE.py" not in content:
            return False

        # Analyze the code deeply
        print(f"  🔬 Deep analysis of {filepath.name}...")
        analysis = analyze_quantum_code(filepath)

        # Generate verbose description
        print("  ✨ Generating verbose poetic-academic description...")
        description = generate_verbose_description(analysis)

        # Replace existing description
        new_content = DESCRIPTION_PATTERN.sub(r"\1" + description, content)

        # If no existing description found, add after template reference
        if new_content == content:
            new_content = re.sub(
                r"(@lukhas/HEADER_FOOTER_TEMPLATE\.py\n)", r"\1" + description, content
            )

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ Added verbose description to {filepath.name}")
            return True
        else:
            print(f"  ⏭️  No changes made to {filepath.name}")
            return False

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Generate verbose intelligent descriptions for quantum modules."""

    print("✨ LUKHAS Verbose Intelligent Description Generator ✨")
    print("=" * 60)
    print("VERBOSE MODE: ON")
    print("Creating rich poetic narratives with academic depth...")
    print("=" * 60)

    # Verify API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OpenAI API key not found in .env file")
        return

    # Start from current quantum directory
    quantum_dir = Path(__file__).parent
    processed = 0
    skipped = 0

    # Priority files for verbose descriptions
    priority_files = [
        "post_quantum_crypto.py",
        "consensus_system.py",
        "awareness_system.py",
        "entanglement.py",
        "processor.py",
        "neural_symbolic_processor.py",
        "qi_bio_coordinator.py",
        "ethics_engine.py",
        "distributed_quantum_architecture.py",
        "oscillator.py",
    ]

    print("\n📚 Processing priority quantum modules with verbose descriptions...")
    print("-" * 60)

    for filename in priority_files:
        filepath = quantum_dir / filename
        if filepath.exists():
            print(f"\n🌟 Processing: {filename}")
            result = add_verbose_description(filepath)
            if result:
                processed += 1
            else:
                skipped += 1
            print()

    print("=" * 60)
    print(f"✅ Added verbose descriptions to: {processed} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n✨ Verbose quantum consciousness narratives generated! ✨")
    print("Each module now tells its quantum story through poetry and science.")


if __name__ == "__main__":
    main()


# === HELPER FUNCTIONS FOR COST OPTIMIZATION ===


def find_good_candidates(project_root: Path) -> list[Path]:
    """Find the best candidates for description generation."""

    candidates = []
    quantum_dir = project_root / "lukhas" / "quantum"

    # High-priority quantum modules (complex, worth describing)
    priority_patterns = [
        "*consensus*",
        "*entangle*",
        "*crypto*",
        "*neural*",
        "*bio*",
        "*dream*",
        "*orchestr*",
        "*consciousness*",
        "*memory*",
        "*symbolic*",
    ]

    # Find all Python files in quantum directory
    if quantum_dir.exists():
        for pattern in priority_patterns:
            candidates.extend(quantum_dir.glob(f"**/{pattern}.py"))

    # Also check core modules
    core_dirs = [
        project_root / "lukhas" / "core",
        project_root / "lukhas" / "orchestration",
        project_root / "lukhas" / "bio_neural",
        project_root / "memory",
    ]

    for directory in core_dirs:
        if directory.exists():
            for pattern in priority_patterns:
                candidates.extend(directory.glob(f"**/{pattern}.py"))

    # Remove duplicates and filter for files that need descriptions
    unique_candidates = []
    for file_path in set(candidates):
        if file_path.is_file() and file_path.suffix == ".py":
            # Check if it has template reference but no description
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    has_template = "@lukhas/HEADER_FOOTER_TEMPLATE.py" in content
                    has_description = re.search(
                        r"@lukhas/HEADER_FOOTER_TEMPLATE\.py\n\n\w+.*\n=+\n", content
                    )
                    if has_template and not has_description:
                        unique_candidates.append(file_path)
            except BaseException:
                continue

    return unique_candidates[:10]  # Return top 10 candidates


def estimate_costs(
    candidates: list[Path], model: str = "gpt-4o-mini"
) -> dict[str, float]:
    """Estimate API costs for processing candidates."""

    # Rough token estimates
    avg_input_tokens = 2000  # Code analysis + prompt
    avg_output_tokens = 800  # Verbose description

    # Cost per 1M tokens (Updated January 2025 pricing)
    model_costs = {
        # OpenAI Models (current pricing)
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},  # Best value!
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "o1-preview": {"input": 15.00, "output": 60.00},
        "o1-mini": {"input": 3.00, "output": 12.00},
        # Other providers (approximate)
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    }

    costs = model_costs.get(model, model_costs["gpt-4o-mini"])

    total_input_cost = (avg_input_tokens * len(candidates) * costs["input"]) / 1_000_000
    total_output_cost = (
        avg_output_tokens * len(candidates) * costs["output"]
    ) / 1_000_000

    return {
        "model": model,
        "files": len(candidates),
        "estimated_input_cost": total_input_cost,
        "estimated_output_cost": total_output_cost,
        "total_estimated_cost": total_input_cost + total_output_cost,
    }


def run_cost_analysis():
    """Run cost analysis for different models."""

    project_root = Path(__file__).parent.parent.parent
    candidates = find_good_candidates(project_root)

    print(f"\n💰 COST ANALYSIS for {len(candidates)} candidate files")
    print("=" * 60)

    models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o1-mini", "gpt-3.5-turbo"]

    for model in models:
        cost_info = estimate_costs(candidates, model)
        print(f"\n{model.upper()}:")
        print(f"  Total estimated cost: ${cost_info['total_estimated_cost']:.3f}")
        print(f"  Per file: ${cost_info['total_estimated_cost']/len(candidates):.3f}")

    print("\n📁 CANDIDATE FILES:")
    for i, candidate in enumerate(candidates, 1):
        rel_path = candidate.relative_to(project_root)
        print(f"  {i:2d}. {rel_path}")


# Usage examples:
# python add_verbose_intelligent_descriptions.py --cost-analysis
# python add_verbose_intelligent_descriptions.py --model gpt-4o-mini#
# python add_verbose_intelligent_descriptions.py --model gpt-4o-mini
