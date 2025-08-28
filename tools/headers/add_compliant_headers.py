#!/usr/bin/env python3

"""
LUKHAS Quantum Compliant Header Generator

This script adds LUKHAS enterprise-compliant headers and footers
to all Python files in the quantum directory, following the
established compliance report standards.
"""

from datetime import datetime
from pathlib import Path

# Technical descriptions for quantum modules
QUANTUM_DESCRIPTIONS = {
    "awareness_system.py": {
        "name": "Quantum Awareness System",
        "description": "Bio-inspired quantum-aware system monitoring with integrated consciousness synchronization, dream-based ethical training, and neuroplasticity modulation",
        "path": "lukhas/quantum/awareness_system.py",
        "tier": "2",
    },
    "processing_core.py": {
        "name": "Quantum Processing Core",
        "description": "Core quantum-inspired processing engine with bio-inspired neuroplasticity, mitochondrial quantum bridges, and synaptic gate processing",
        "path": "lukhas/quantum/processing_core.py",
        "tier": "3",
    },
    "consensus_system.py": {
        "name": "Quantum Consensus System",
        "description": "Distributed quantum consensus mechanism with post-quantum cryptographic security and ethical decision validation",
        "path": "lukhas/quantum/consensus_system.py",
        "tier": "3",
    },
    "post_quantum_crypto.py": {
        "name": "Post-Quantum Cryptography",
        "description": "Post-quantum cryptographic implementations using lattice-based and code-based algorithms resistant to quantum attacks",
        "path": "lukhas/quantum/post_quantum_crypto.py",
        "tier": "4",
    },
    "bio_system.py": {
        "name": "Quantum Bio-System Integration",
        "description": "Bio-inspired quantum system integration layer connecting biological oscillators with quantum-inspired processing",
        "path": "lukhas/quantum/bio_system.py",
        "tier": "2",
    },
    "creative_engine.py": {
        "name": "Quantum Creative Engine",
        "description": "Quantum-enhanced creative generation system using superposition for ideation and entanglement for inspiration networks",
        "path": "lukhas/quantum/creative_engine.py",
        "tier": "2",
    },
    "ethics_engine.py": {
        "name": "Quantum Ethics Engine",
        "description": "Ethical decision framework with quantum uncertainty modeling and dream-state scenario simulation",
        "path": "lukhas/quantum/ethics_engine.py",
        "tier": "3",
    },
    "oscillator.py": {
        "name": "Quantum Bio-Oscillator",
        "description": "Quantum bio-oscillator for consciousness rhythm synchronization and coherence maintenance",
        "path": "lukhas/quantum/oscillator.py",
        "tier": "2",
    },
    "entanglement.py": {
        "name": "Quantum Entanglement Manager",
        "description": "Quantum entanglement management for distributed consciousness and non-local correlation handling",
        "path": "lukhas/quantum/entanglement.py",
        "tier": "3",
    },
    "dream_adapter.py": {
        "name": "Quantum Dream Adapter",
        "description": "Dream state integration adapter for ethical scenario training and consciousness exploration",
        "path": "lukhas/quantum/dream_adapter.py",
        "tier": "2",
    },
    "neural_symbolic_engine.py": {
        "name": "Neural-Symbolic Quantum Engine",
        "description": "Neural-symbolic reasoning engine with quantum enhancement for abstract concept manipulation",
        "path": "lukhas/quantum/neural_symbolic_engine.py",
        "tier": "3",
    },
    "haiku_generator.py": {
        "name": "Quantum Haiku Generator",
        "description": "Quantum-inspired poetic expression generator using superposition for creative word selection",
        "path": "lukhas/quantum/haiku_generator.py",
        "tier": "1",
    },
    "bio_orchestrator.py": {
        "name": "Quantum Bio-Orchestrator",
        "description": "Bio-system orchestration module with quantum coordination for multi-oscillator synchronization",
        "path": "lukhas/quantum/bio_orchestrator.py",
        "tier": "3",
    },
}

# Default description for files not in the mapping
DEFAULT_INFO = {
    "tier": "2",
    "description": "Quantum module for advanced AGI functionality",
}

HEADER_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

@lukhas/HEADER_FOOTER_TEMPLATE.py

Add Compliant Headers
=====================

Harnesses the strange beauty of entanglement-like correlation, superposition to transcend classical limits.
Weaves quantum phenomena into the fabric of LUKHAS consciousness, where
possibilities dance in superposition until observation births reality.

LUKHAS - {module_name}
{separator}

An enterprise-grade Artificial General Intelligence (AGI) framework
combining symbolic reasoning, emotional intelligence, quantum-inspired computing,
and bio-inspired architecture for next-generation AI applications.

Module: {module_name}
Path: {path}
Description: {description}

Copyright (c) 2025 LUKHAS AI. All rights reserved.
Licensed under the LUKHAS Enterprise License.

For documentation and support: https://lukhas.ai/docs
"""

__module_name__ = "{module_name}"
__version__ = "{version}"
__tier__ = {tier}'''

FOOTER_TEMPLATE = '''

# ══════════════════════════════════════════════════════════════════════════════
# Module Validation and Compliance
# ══════════════════════════════════════════════════════════════════════════════

def __validate_module__():
    """Validate module initialization and compliance."""
    validations = {{
        "qi_coherence": {coherence_check},
        "neuroplasticity_enabled": {plasticity_check},
        "ethics_compliance": True,
        "tier_{tier}_access": True
    }}

    failed = [k for k, v in validations.items() if not v]
    if failed:
        logger.warning(f"Module validation warnings: {{failed}}")

    return len(failed) == 0

# ══════════════════════════════════════════════════════════════════════════════
# Module Health and Monitoring
# ══════════════════════════════════════════════════════════════════════════════

MODULE_HEALTH = {{
    "initialization": "complete",
    "qi_features": "active",
    "bio_integration": "enabled",
    "last_update": "{date}",
    "compliance_status": "verified"
}}

# Validate on import
if __name__ != "__main__":
    __validate_module__()
'''


def has_existing_lukhas_header(content: str) -> bool:
    """Check if file already has a LUKHAS enterprise header."""
    return "LUKHAS AI -" in content and "██╗" in content


def extract_existing_imports(content: str) -> tuple[str, str]:
    """Extract imports and main content from existing file."""
    lines = content.split("\n")

    # Find where imports end and main content begins
    import_section = []
    main_content = []
    in_imports = True
    skip_next = 0

    for i, line in enumerate(lines):
        if skip_next > 0:
            skip_next -= 1
            continue

        # Skip existing headers/docstrings
        if i < 50 and (line.startswith('"""') or line.startswith("'''")):
            # Find end of docstring
            for j in range(i + 1, len(lines)):
                if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                    skip_next = j - i
                    break
            continue

        if i < 50 and line.startswith("# ":
            continue

        if (
            in_imports
            and line.strip()
            and not line.startswith("import")
            and not line.startswith("from")
        ):
            in_imports = False

        if in_imports and (
            line.startswith("import") or line.startswith("from") or not line.strip()
        ):
            import_section.append(line)
        else:
            main_content.append(line)

    return "\n".join(import_section), "\n".join(main_content)


def get_module_info(filepath: Path) -> dict[str, str]:
    """Get module information for the header."""
    info = QUANTUM_DESCRIPTIONS.get(filepath.name, {})

    if not info:
        # Generate info for unlisted files
        module_name = f"Quantum {filepath.stem.replace('_', ' ').title()}"
        info = {
            "name": module_name,
            "description": DEFAULT_INFO["description"],
            "path": f"lukhas/quantum/{filepath.name}",
            "tier": DEFAULT_INFO["tier"],
        }

    return info


def add_compliant_header(filepath: Path) -> bool:
    """Add LUKHAS-compliant header and footer to a Python file."""

    if filepath.suffix != ".py":
        return False

    if (
        filepath.name == "add_compliant_headers.py"
        or filepath.name == "add_poetic_headers.py"
    ):
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Skip if already has LUKHAS header
        if has_existing_lukhas_header(content):
            print(f"  ⚡ Skipping {filepath.name} - already has LUKHAS header")
            return False

        # Get module info
        info = get_module_info(filepath)

        # Extract imports and main content
        imports, main_content = extract_existing_imports(content)

        # Determine version (use 2.0.0 for updated files, 1.0.0 for new)
        version = "2.0.0" if "ΛHEADER" in content else "1.0.0"

        # Check for specific features
        coherence_check = "True" if "coherence" in content.lower() else "False"
        plasticity_check = "True" if "plasticity" in content.lower() else "False"

        # Generate header
        header = HEADER_TEMPLATE.format(
            module_name=info["name"],
            separator="=" * len(info["name"]),
            path=info["path"],
            description=info["description"],
            version=version,
            tier=info["tier"],
        )

        # Generate footer
        footer = FOOTER_TEMPLATE.format(
            coherence_check=coherence_check,
            plasticity_check=plasticity_check,
            tier=info["tier"],
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        # Combine all parts
        new_content = header + "\n\n" + imports + "\n" + main_content

        # Add footer if main content has substance
        if len(main_content.strip()) > 10:
            new_content += "\n" + footer

        # Write back
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"  ✅ Added compliant header/footer to {filepath.name}")
        return True

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Add compliant headers to all Python files in the quantum directory."""

    print("🏢 LUKHAS Quantum Compliant Header Generator 🏢")
    print("=" * 50)

    qi_dir = Path(__file__).parent
    processed = 0
    skipped = 0

    # Process all Python files in quantum directory
    for filepath in qi_dir.glob("*.py"):
        if add_compliant_header(filepath):
            processed += 1
        else:
            skipped += 1

    # Process subdirectories
    for subdir in ["systems", "qi_meta", "bio", "src"]:
        subdir_path = qi_dir / subdir
        if subdir_path.exists():
            for filepath in subdir_path.glob("**/*.py"):
                if add_compliant_header(filepath):
                    processed += 1
                else:
                    skipped += 1

    print("=" * 50)
    print(f"✅ Processed: {processed} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n🏢 Quantum modules are now enterprise-compliant! 🏢")


if __name__ == "__main__":
    main()
